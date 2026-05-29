```
import click
import os
from resume_parser import parse_resume
from resume_analyzer import analyze_resume

@click.command()
@click.argument('input_path', type=click.Path(exists=True))
def cli(input_path: str):
    """
    Command Line Interface for analyzing resumes.

    INPUT_PATH: Path to the resume file (plain text or PDF).
    """
    # Check if the input path is a file
    if not os.path.isfile(input_path):
        click.echo("The provided path is not a file.")
        return

    # Parse the resume
    try:
        resume_text = parse_resume(input_path)
    except Exception as e:
        click.echo(f"Error parsing resume: {e}")
        return

    # Analyze the resume
    try:
        score, suggestions = analyze_resume(resume_text)
    except Exception as e:
        click.echo(f"Error analyzing resume: {e}")
        return

    # Output the results
    click.echo(f"Resume Score: {score}/100")
    click.echo("Suggestions for Improvement:")
    for suggestion in suggestions:
        click.echo(f"- {suggestion}")

if __name__ == '__main__':
    cli()
```