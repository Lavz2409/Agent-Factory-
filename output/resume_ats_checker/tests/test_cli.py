import subprocess
import pytest

def run_cli_command(args):
    """Helper function to run the CLI command with given arguments."""
    result = subprocess.run(
        ['python', 'cli.py'] + args,
        capture_output=True,
        text=True
    )
    return result

def test_cli_with_text_input():
    """Test the CLI with direct resume text input."""
    resume_text = "John Doe\nExperience: 5 years in software development\nSkills: Python, Java\nEducation: B.Sc. in Computer Science"
    result = run_cli_command(['--resume-text', resume_text])
    assert result.returncode == 0
    assert "Score" in result.stdout
    assert "Suggestions" in result.stdout

def test_cli_with_file_input(tmp_path):
    """Test the CLI with resume text from a file."""
    resume_file = tmp_path / "resume.txt"
    resume_file.write_text("Jane Doe\nExperience: 3 years in data analysis\nSkills: SQL, Python\nEducation: M.Sc. in Data Science")
    
    result = run_cli_command(['--resume-file', str(resume_file)])
    assert result.returncode == 0
    assert "Score" in result.stdout
    assert "Suggestions" in result.stdout

def test_cli_missing_input():
    """Test the CLI when no input is provided."""
    result = run_cli_command([])
    assert result.returncode != 0
    assert "Error" in result.stderr

def test_cli_invalid_file():
    """Test the CLI with an invalid file path."""
    result = run_cli_command(['--resume-file', 'non_existent_file.txt'])
    assert result.returncode != 0
    assert "Error" in result.stderr

def test_cli_help():
    """Test the CLI help command."""
    result = run_cli_command(['--help'])
    assert result.returncode == 0
    assert "Usage" in result.stdout
    assert "Options" in result.stdout