import click
import re
from pathlib import Path

# Function to read text from a file
def read_file(file_path: str) -> str:
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"The file {file_path} does not exist.")
    
    if path.suffix.lower() == '.pdf':
        return read_pdf(file_path)
    elif path.suffix.lower() == '.docx':
        return read_docx(file_path)
    else:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()

# Placeholder for PDF reading function
def read_pdf(file_path: str) -> str:
    # Implement PDF reading logic here
    return "PDF reading not implemented yet."

# Placeholder for DOCX reading function
def read_docx(file_path: str) -> str:
    # Implement DOCX reading logic here
    return "DOCX reading not implemented yet."

# Function to check if resume is ATS-friendly
def evaluate_resume(text: str) -> (int, list):
    score = 0
    suggestions = []

    # Check for presence of key sections
    sections = ['Education', 'Skills', 'Experience']
    for section in sections:
        if re.search(rf'\b{section}\b', text, re.IGNORECASE):
            score += 20
        else:
            suggestions.append(f"Add a section for {section}.")

    # Check for presence of keywords
    keywords = ['Python', 'AI', 'Machine Learning', 'Data Analysis']
    keyword_count = sum(1 for keyword in keywords if re.search(rf'\b{keyword}\b', text, re.IGNORECASE))
    score += min(keyword_count * 10, 20)

    if keyword_count == 0:
        suggestions.append("Include relevant keywords such as skills and technologies.")

    # Check for simple formatting
    if re.search(r'[^\w\s,.]', text):
        suggestions.append("Avoid using special characters or complex formatting.")
    else:
        score += 20

    return score, suggestions

@click.command()
@click.argument('file_path', type=click.Path(exists=True))
def cli(file_path: str):
    """CLI tool to evaluate if a resume is ATS-friendly."""
    try:
        resume_text = read_file(file_path)
        score, suggestions = evaluate_resume(resume_text)
        click.echo(f"Resume Score: {score}/100")
        if suggestions:
            click.echo("Suggestions to improve your resume:")
            for suggestion in suggestions:
                click.echo(f"- {suggestion}")
    except Exception as e:
        click.echo(f"Error: {str(e)}")

if __name__ == '__main__':
    cli()