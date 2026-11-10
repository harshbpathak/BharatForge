import json
from types import SimpleNamespace
from unittest.mock import Mock

import httpx
from openai import APIConnectionError, APIStatusError, OpenAI
import pytest

from bharatforge.ai_client import AIClient, AIError
from bharatforge.analyzer import analyze, load_demo
from bharatforge.config import ConfigurationError, Settings
from bharatforge.schemas import AnalysisBatch, BacklogOverview


def completion(content, reason="stop"):
    return SimpleNamespace(status="completed" if reason == "stop" else "incomplete", output_text=content)


def make_ai(responses):
    client = Mock()
    client.responses.create.side_effect = responses
    return AIClient(Settings(api_key="test-only"), client=client, sleep=lambda _:None)


def test_missing_credentials_and_provider_restriction(monkeypatch):
    with pytest.raises(ConfigurationError):
        AIClient(Settings())
    with pytest.raises(ConfigurationError):
        AIClient(Settings(api_key="test", base_url="https://api.openai.com/v1"))
    assert "test-secret" not in repr(Settings(api_key="test-secret"))


@pytest.mark.parametrize("content", ['not json', '{}', '{"summary":3,"observations":[]}', '{"summary":"ok","observations":[],"unexpected":true}', '{"summary":"ok","observations":["x"],"secret":"no"}', None, 'x'*80001])
def test_malformed_ai_json(content):
    with pytest.raises(AIError):
        AIClient.validate(content, BacklogOverview)


def test_truncation_is_not_retried():
    ai = make_ai([completion('{', "length")])
    with pytest.raises(AIError, match="incomplete"):
        ai.request("task", [], BacklogOverview)
    assert ai.request_count == 1


def test_transient_retry_and_latency():
    request = httpx.Request("POST", "https://bharatcode.ai/api/model/v1/chat/completions")
    failure = APIConnectionError(request=request)
    ai = make_ai([failure, completion('{"summary":"OK","observations":[]}')])
    assert ai.request("task", [], BacklogOverview).summary == "OK"
    assert ai.request_count == 2 and ai.latency_seconds >= 0
    kwargs = ai.client.responses.create.call_args.kwargs
    assert kwargs["model"] == "qwen-3.8-27b" and kwargs["max_output_tokens"] == 6000
    assert "untrusted_data" in kwargs["input"]


@pytest.mark.parametrize("status,attempts", [(401,1),(403,1),(429,3),(503,3),(400,1)])
def test_api_error_messages_and_retry_limits(status, attempts):
    response = httpx.Response(status, request=httpx.Request("POST", "https://bharatcode.ai"))
    failure = APIStatusError("SECRET", response=response, body={"message":"SECRET"})
    ai = make_ai([failure]*3)
    with pytest.raises(AIError) as error:
        ai.request("task", [], BacklogOverview)
    assert "SECRET" not in str(error.value)
    assert ai.request_count == attempts


def test_real_sdk_request_contract_with_mock_http():
    def handler(request):
        assert request.url.host == "bharatcode.ai"
        assert request.url.path == "/api/model/v1/responses"
        assert request.headers["authorization"] == "Bearer fake-key"
        body = json.loads(request.content)
        assert body["model"] == "configured-model"
        assert body["store"] is False
        assert body["text"]["format"]["type"] == "json_schema"
        return httpx.Response(200, json={"id":"test", "object":"response", "created_at":0,
            "status":"completed", "model":"configured-model", "output":[{"type":"message", "id":"msg", "role":"assistant", "status":"completed", "content":[{"type":"output_text", "text":'{"summary":"OK","observations":[]}', "annotations":[]}]}]})
    settings = Settings(api_key="fake-key", model="configured-model")
    sdk = OpenAI(api_key=settings.api_key, base_url=settings.base_url,
                 http_client=httpx.Client(transport=httpx.MockTransport(handler)))
    ai = AIClient(settings, client=sdk)
    try:
        assert ai.request("task", [], BacklogOverview).summary == "OK"
    finally:
        ai.close()


def test_analyzer_validates_issue_identity_and_evidence():
    report = load_demo()
    item = report.issues[0]
    payload = {"issues":[item.analysis.model_dump()]}
    payload["issues"][0]["number"] = 999
    ai = make_ai([completion(json.dumps(payload))])
    with pytest.raises(AIError, match="numbers"):
        analyze(report.repository, [item.issue], ai)
    payload["issues"][0]["number"] = item.issue.number
    payload["issues"][0]["evidence"] = ["fabricated quotation"]
    ai = make_ai([completion(json.dumps(payload))])
    with pytest.raises(AIError, match="evidence"):
        analyze(report.repository, [item.issue], ai)


def test_successful_analysis_and_empty_repository():
    demo = load_demo()
    item = demo.issues[0]
    ai = make_ai([completion(json.dumps({"issues":[item.analysis.model_dump()]})),
                  completion('{"summary":"One issue reviewed.","observations":[]}')])
    report = analyze(demo.repository, [item.issue], ai)
    assert report.mode == "live" and report.request_count == 2
    assert report.issues[0].analysis == item.analysis
    empty = analyze(demo.repository, [], make_ai([]))
    assert not empty.issues and empty.request_count == 0


def test_overview_failure_preserves_validated_results():
    demo = load_demo()
    item = demo.issues[0]
    ai = make_ai([completion(json.dumps({"issues":[item.analysis.model_dump()]})), completion("invalid")])
    report = analyze(demo.repository, [item.issue], ai)
    assert len(report.issues) == 1 and report.warnings

def test_structured_format_rejection_falls_back_on_bharatcode():
    response = httpx.Response(400, request=httpx.Request("POST", "https://bharatcode.ai"))
    failure = APIStatusError("unsupported text.format json_schema", response=response, body={})
    ai = make_ai([failure])
    ai.client.chat.completions.create.return_value = SimpleNamespace(
        choices=[SimpleNamespace(finish_reason="stop", message=SimpleNamespace(content='{"summary":"Fallback validated","observations":[]}'))])
    result = ai.request("task", [], BacklogOverview)
    assert result.summary == "Fallback validated" and not ai.structured
    assert ai.request_count == 2
    assert ai.client.chat.completions.create.call_args.kwargs["model"] == ai.model


def test_long_rate_limit_does_not_sleep():
    response = httpx.Response(429, headers={"retry-after":"120"}, request=httpx.Request("POST", "https://bharatcode.ai"))
    ai = make_ai([APIStatusError("Rate limit", response=response, body={})])
    ai.sleep = Mock()
    with pytest.raises(AIError, match="rate limited"):
        ai.request("task", [], BacklogOverview)
    assert ai.request_count == 1
    ai.sleep.assert_not_called()


def test_duplicate_review_failure_keeps_unconfirmed_candidate():
    demo = load_demo()
    items = demo.issues[:2]
    ai = make_ai([completion(json.dumps({"issues":[item.analysis.model_dump() for item in items]})),
                  completion("invalid duplicate verdict"),
                  completion('{"summary":"Two issues reviewed","observations":[]}')])
    result = analyze(demo.repository, [item.issue for item in items], ai)
    assert len(result.duplicates) == 1 and result.duplicates[0].verdict is None
    assert result.warnings and len(result.issues) == 2
