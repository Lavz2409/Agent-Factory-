```
import pytest
from resume_parser import parse_resume
from resume_analyzer import analyze_resume
from main import evaluate_resume

@pytest.fixture
def sample_resume_text():
    return """
    John Doe
    123 Main Street
    Anytown, USA 12345
    (123) 456-7890
    johndoe@email.com

    Objective
    Seeking a challenging position in software development.

    Education
    Bachelor of Science in Computer Science
    Anytown University, Anytown, USA
    Graduated: May 2020

    Skills
    - Python
    - Java
    - SQL
    - Team Leadership

    Experience
    Software Developer, Tech Company
    June 2020 - Present
    - Developed web applications using Python and Java.
    - Collaborated with cross-functional teams.
    """

def test_parse_resume(sample_resume_text):
    parsed = parse_resume(sample_resume_text)
    assert "Education" in parsed
    assert "Skills" in parsed
    assert "Experience" in parsed
    assert "Python" in parsed["Skills"]
    assert "Software Developer" in parsed["Experience"]

def test_analyze_resume(sample_resume_text):
    parsed = parse_resume(sample_resume_text)
    analysis = analyze_resume(parsed)
    assert isinstance(analysis, dict)
    assert "score" in analysis
    assert "suggestions" in analysis
    assert 0 <= analysis["score"] <= 100

def test_evaluate_resume(sample_resume_text):
    result = evaluate_resume(sample_resume_text)
    assert isinstance(result, dict)
    assert "score" in result
    assert "suggestions" in result
    assert 0 <= result["score"] <= 100

def test_resume_with_missing_sections():
    resume_text = """
    Jane Doe
    456 Another St
    Othercity, USA 67890
    (987) 654-3210
    janedoe@email.com

    Skills
    - Project Management
    - Agile Methodologies
    """
    result = evaluate_resume(resume_text)
    assert result["score"] < 50
    assert "Education" in result["suggestions"]
    assert "Experience" in result["suggestions"]

def test_resume_with_special_characters():
    resume_text = """
    Bob Smith
    789 Different Rd
    Sometown, USA 54321
    (321) 987-6543
    bobsmith@email.com

    Education
    Bachelor of Arts in History
    Some University, Sometown, USA
    Graduated: May 2018

    Skills
    - Research & Analysis
    - Communication

    Experience
    Research Assistant, History Department
    January 2019 - Present
    - Assisted in research projects.
    - Managed data & reports.
    """
    result = evaluate_resume(resume_text)
    assert result["score"] > 50
    assert "Avoid special characters" not in result["suggestions"]
```