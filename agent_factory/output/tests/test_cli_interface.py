```
import pytest
from click.testing import CliRunner
from main import cli

@pytest.fixture
def sample_resume_file(tmp_path):
    resume_content = """John Doe
    123 Main St, Anytown, USA
    johndoe@example.com
    (123) 456-7890

    Education
    Bachelor of Science in Computer Science
    Anytown University, 2015

    Skills
    Python, Java, SQL, Machine Learning

    Experience
    Software Developer at TechCorp, 2016-2020
    Developed various applications using Python and Java.
    """
    resume_file = tmp_path / "resume.txt"
    resume_file.write_text(resume_content)
    return resume_file

def test_cli_interface_with_text_input():
    runner = CliRunner()
    resume_text = """Jane Doe
    456 Elm St, Othertown, USA
    janedoe@example.com
    (987) 654-3210

    Education
    Master of Science in Data Science
    Othertown University, 2018

    Skills
    Data Analysis, R, Python, SQL

    Experience
    Data Analyst at DataCorp, 2018-2022
    Conducted data analysis using R and Python.
    """
    result = runner.invoke(cli, ['--text', resume_text])
    assert result.exit_code == 0
    assert "Resume Score:" in result.output
    assert "Suggestions:" in result.output

def test_cli_interface_with_file_input(sample_resume_file):
    runner = CliRunner()
    result = runner.invoke(cli, ['--file', str(sample_resume_file)])
    assert result.exit_code == 0
    assert "Resume Score:" in result.output
    assert "Suggestions:" in result.output

def test_cli_interface_missing_sections():
    runner = CliRunner()
    resume_text = """John Smith
    789 Pine St, Sometown, USA
    johnsmith@example.com
    (555) 123-4567

    Skills
    HTML, CSS, JavaScript
    """
    result = runner.invoke(cli, ['--text', resume_text])
    assert result.exit_code == 0
    assert "Resume Score:" in result.output
    assert "Suggestions:" in result.output
    assert "Consider adding sections" in result.output

def test_cli_interface_special_characters():
    runner = CliRunner()
    resume_text = """Emily White
    321 Oak St, Newcity, USA
    emilywhite@example.com
    (321) 654-0987

    Education
    Bachelor of Arts in Graphic Design
    Newcity College, 2017

    Skills
    Adobe Photoshop, Illustrator, InDesign

    Experience
    Graphic Designer at DesignStudio, 2017-2021
    Created designs for various clients using Adobe Suite.
    """
    result = runner.invoke(cli, ['--text', resume_text])
    assert result.exit_code == 0
    assert "Resume Score:" in result.output
    assert "Suggestions:" in result.output
```