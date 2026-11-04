from app.ollama_client import OllamaClient


def test_client_posts_model_and_prompt_to_local_endpoint():
    calls = []

    def fake_post(url, payload, timeout):
        calls.append((url, payload, timeout))
        return {"message": {"content": '{"codes":["1F40.Z"]}'}}

    client = OllamaClient(post=fake_post, model="gemma4:e4b")
    assert client.choose([{"code": "1F40.Z", "title": "Malaria"}], "malaria") == ["1F40.Z"]
    assert calls[0][1]["model"] == "gemma4:e4b"
