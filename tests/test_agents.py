from app.agents import AgenticCoder


def test_agentic_coder_falls_back_when_model_is_unavailable():
    agent = AgenticCoder(model_client=None)
    result = agent.predict("Assessment: uncomplicated malaria")
    assert result.codes
    assert result.used_fallback is True


def test_agentic_coder_sends_only_retrieved_candidates_to_model():
    seen = {}

    class FakeModel:
        def choose(self, candidates, note):
            seen["count"] = len(candidates)
            return [candidates[0]["code"]]

    result = AgenticCoder(model_client=FakeModel()).predict("Assessment: malaria")
    assert seen["count"] <= 20
    assert result.codes
