```
import pytest
from core import analyze_resume

@pytest.mark.parametrize("resume_text, expected_score, expected_suggestions", [
    # Test case 1: Ideal resume with all sections and keywords
    ("Education: MIT\nSkills: Python, AI\nExperience: 5 years in AI development",
     100, []),

    # Test case 2: Missing Skills section
    ("Education: MIT\nExperience: 5 years in AI development",
     70, ["Add a Skills section with relevant keywords."]),

    # Test case 3: Missing Experience section
    ("Education: MIT\nSkills: Python, AI",
     70, ["Add an Experience section with relevant details."]),

    # Test case 4: Missing Education section
    ("Skills: Python, AI\nExperience: 5 years in AI development",
     70, ["Add an Education section."]),

    # Test case 5: No sections, only keywords
    ("Python, AI, 5 years",
     50, ["Add Education, Skills, and Experience sections."]),

    # Test case 6: Poor formatting with special characters
    ("Education: MIT\nSkills: Python, AI\nExperience: 5 years in AI development!!!",
     80, ["Remove special characters for better formatting."]),

    # Test case 7: Completely empty resume
    ("",
     0, ["Add Education, Skills, and Experience sections."]),
])
def test_analyze_resume(resume_text, expected_score, expected_suggestions):
    score, suggestions = analyze_resume(resume_text)
    assert score == expected_score
    assert suggestions == expected_suggestions
```