import pytest
from rules.ats_check import check_ats_friendly

@pytest.mark.parametrize("resume_text, expected", [
    (
        "John Doe\n\nEducation\nBachelor of Science in Computer Science\n\nSkills\nPython, Java, C++\n\nExperience\nSoftware Developer at XYZ Corp",
        {
            "has_keywords": True,
            "has_proper_sections": True,
            "has_simple_formatting": True
        }
    ),
    (
        "Jane Doe\n\nExperience\nWorked at ABC Inc.",
        {
            "has_keywords": False,
            "has_proper_sections": False,
            "has_simple_formatting": True
        }
    ),
    (
        "John Smith\n\nEducation\nBachelor of Arts\n\nSkills\nCommunication, Teamwork\n\nExperience\nManager at DEF Ltd",
        {
            "has_keywords": True,
            "has_proper_sections": True,
            "has_simple_formatting": True
        }
    ),
    (
        "Invalid Resume\n\nEducation\nBachelor of Arts\n\nSkills\nCommunication, Teamwork\n\nExperience\nManager at DEF Ltd\n\nTable\n| Header | Value |\n|--------|-------|",
        {
            "has_keywords": True,
            "has_proper_sections": True,
            "has_simple_formatting": False
        }
    ),
])
def test_check_ats_friendly(resume_text, expected):
    result = check_ats_friendly(resume_text)
    assert result == expected