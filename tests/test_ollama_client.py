from app.ollama_client import OllamaClient


def test_client_posts_model_and_prompt_to_local_endpoint():
    calls = []

    def fake_post(url, payload, timeout):
        calls.append((url, payload, timeout))
        return {"message": {"content": '{"codes":["1F40.Z"]}'}}

    client = OllamaClient(post=fake_post, model="gemma4:e4b")
    assert client.choose([{"code": "1F40.Z", "title": "Malaria"}], "malaria") == ["1F40.Z"]
    assert calls[0][1]["model"] == "gemma4:e4b"


def test_client_uses_ollama_host_environment(monkeypatch):
    monkeypatch.setenv("OLLAMA_HOST", "http://host.docker.internal:11434")
    client = OllamaClient(post=lambda *_: {"message": {"content": '{"codes":[]}'}})
    assert client.endpoint == "http://host.docker.internal:11434/api/chat"


def test_malformed_model_response_is_counted_without_crashing():
    client = OllamaClient(post=lambda *_: {"message": {"content": "not json"}})
    assert client.choose([], "note") == []
    assert client.stats["calls"] == 1
    assert client.stats["parse_failures"] == 1


def test_timeout_is_counted_and_returns_empty_codes():
    def fake_post(*_):
        raise TimeoutError("slow")

    client = OllamaClient(post=fake_post)
    assert client.choose([], "note") == []
    assert client.stats["timeouts"] == 1

