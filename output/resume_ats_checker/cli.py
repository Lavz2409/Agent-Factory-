import click
from main import main

@click.command()
@click.option('--resume-file', type=click.File('r'), help='Path to the resume file.')
@click.option('--resume-text', type=str, help='Resume text as a string.')
def cli(resume_file, resume_text):
    """
    Command-line interface for checking if a resume is ATS-friendly.
    """
    if resume_file:
        resume_text = resume_file.read()
    
    if not resume_text:
        click.echo("Error: Please provide either a resume file or resume text.")
        return

    main(resume_file, resume_text)

if __name__ == '__main__':
    cli()