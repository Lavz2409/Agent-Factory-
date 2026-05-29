import pytest
from ats_checker import (
    check_keywords,
    check_sections,
    check_formatting,
    calculate_score,
    generate_suggestions,
    check_ats_friendly
)

def test_check_keywords():
    resume_text = "Experienced software engineer with skills in Python, Java, and C++."
    assert check_keywords(resume_text) > 0
    assert check_keywords("No relevant skills mentioned.") == 0

def test_check_sections():
    resume_text = "Education: B.Sc. in Computer Science\nSkills: Python, Java\nExperience: 5 years in software development"
    assert check_sections(resume_text) == 3
    assert check_sections("No sections here.") == 0

def test_check_formatting():
    well_formatted_resume = "Education: B.Sc. in Computer Science\nSkills: Python, Java\nExperience: 5 years in software development"
    poorly_formatted_resume = "Education: B.Sc. in Computer Science | Skills: Python, Java | Experience: 5 years in software development"
    assert check_formatting(well_formatted_resume) is True
    assert check_formatting(poorly_formatted_resume) is False

def test_calculate_score():
    assert calculate_score(5, 3, True) == 100
    assert calculate_score(0, 0, False) == 0

def test_generate_suggestions():
    suggestions = generate_suggestions(0, 0, False)
    assert "Add more relevant keywords" in suggestions
    assert "Include proper sections" in suggestions
    assert "Improve formatting" in suggestions

def test_check_ats_friendly():
    resume_text = "Education: B.Sc. in Computer Science\nSkills: Python, Java\nExperience: 5 years in software development"
    result = check_ats_friendly(resume_text)
    assert result['score'] == 100
    assert result['suggestions'] == []

    resume_text = "No sections or keywords."
    result = check_ats_friendly(resume_text)
    assert result['score'] < 100
    assert len(result['suggestions']) > 0