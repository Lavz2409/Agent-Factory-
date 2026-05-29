import pytest
from resume_parser import parse_resume, extract_sections, extract_keywords, evaluate_resume

def test_parse_resume():
    resume_text = """
    John Doe
    Email: john.doe@example.com
    Phone: 123-456-7890

    Education
    Bachelor of Science in Computer Science
    University of Example, 2015-2019

    Experience
    Software Developer at TechCorp, 2019-Present
    - Developed software solutions for clients

    Skills
    Python, Java, SQL
    """
    parsed_resume = parse_resume(resume_text)
    assert isinstance(parsed_resume, dict)
    assert 'sections' in parsed_resume
    assert 'keywords' in parsed_resume

def test_extract_sections():
    text = """
    Education
    Bachelor of Science in Computer Science
    University of Example, 2015-2019

    Experience
    Software Developer at TechCorp, 2019-Present
    - Developed software solutions for clients

    Skills
    Python, Java, SQL
    """
    sections = extract_sections(text)
    assert isinstance(sections, dict)
    assert 'Education' in sections
    assert 'Experience' in sections
    assert 'Skills' in sections

def test_extract_keywords():
    text = "Python, Java, SQL, software, developer, client"
    keywords = extract_keywords(text)
    assert isinstance(keywords, dict)
    assert keywords.get('Python') == 1
    assert keywords.get('Java') == 1
    assert keywords.get('SQL') == 1

def test_evaluate_resume():
    sections = {
        'Education': 'Bachelor of Science in Computer Science',
        'Experience': 'Software Developer at TechCorp',
        'Skills': 'Python, Java, SQL'
    }
    keywords = {
        'Python': 1,
        'Java': 1,
        'SQL': 1,
        'software': 1,
        'developer': 1
    }
    score, suggestions = evaluate_resume(sections, keywords)
    assert isinstance(score, int)
    assert 0 <= score <= 100
    assert isinstance(suggestions, list)