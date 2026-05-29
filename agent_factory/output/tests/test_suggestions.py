```
import pytest
from rules.suggestions import generate_suggestions

@pytest.mark.parametrize("ats_results, expected_suggestions", [
    (
        {"keywords": {"skills": False, "experience": True}, "sections": {"Education": True, "Skills": False, "Experience": True}, "formatting": True},
        ["Add more skills to improve keyword match.", "Include a 'Skills' section."]
    ),
    (
        {"keywords": {"skills": True, "experience": False}, "sections": {"Education": False, "Skills": True, "Experience": True}, "formatting": False},
        ["Add more experience to improve keyword match.", "Include an 'Education' section.", "Simplify formatting."]
    ),
    (
        {"keywords": {"skills": True, "experience": True}, "sections": {"Education": True, "Skills": True, "Experience": True}, "formatting": True},
        []
    ),
    (
        {"keywords": {"skills": False, "experience": False}, "sections": {"Education": False, "Skills": False, "Experience": False}, "formatting": False},
        [
            "Add more skills to improve keyword match.",
            "Add more experience to improve keyword match.",
            "Include an 'Education' section.",
            "Include a 'Skills' section.",
            "Include an 'Experience' section.",
            "Simplify formatting."
        ]
    ),
])
def test_generate_suggestions(ats_results, expected_suggestions):
    suggestions = generate_suggestions(ats_results)
    assert suggestions == expected_suggestions
```