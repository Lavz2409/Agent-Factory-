import click
import re

def check_keywords(resume_text):
    keywords = ["Python", "Java", "Project Management", "Data Analysis"]
    found_keywords = [kw for kw in keywords if kw.lower() in resume_text.lower()]
    return len(found_keywords), found_keywords

def check_sections(resume_text):
    sections = ["Education", "Skills", "Experience"]
    found_sections = [section for section in sections if section.lower() in resume_text.lower()]
    return len(found_sections), found_sections

def check_formatting(resume_text):
    # Check for special characters and simple formatting
    if re.search(r'[^\w\s,.]', resume_text):
        return False
    return True

def calculate_score(keywords_count, sections_count, formatting_ok):
    score = (keywords_count * 20) + (sections_count * 20)
    if formatting_ok:
        score += 40
    return min(score, 100)

def generate_suggestions(keywords_count, sections_count, formatting_ok):
    suggestions = []
    if keywords_count < 3:
        suggestions.append("Include more relevant keywords.")
    if sections_count < 3:
        suggestions.append("Ensure you have sections for Education, Skills, and Experience.")
    if not formatting_ok:
        suggestions.append("Avoid using special characters and complex formatting.")
    return suggestions

@click.command()
@click.option('--resume-file', type=click.File('r'), help='Path to the resume file.')
@click.option('--resume-text', type=str, help='Resume text input directly.')
def main(resume_file, resume_text):
    if resume_file:
        resume_text = resume_file.read()
    elif not resume_text:
        click.echo("Please provide resume text either through --resume-file or --resume-text.")
        return

    keywords_count, found_keywords = check_keywords(resume_text)
    sections_count, found_sections = check_sections(resume_text)
    formatting_ok = check_formatting(resume_text)

    score = calculate_score(keywords_count, sections_count, formatting_ok)
    suggestions = generate_suggestions(keywords_count, sections_count, formatting_ok)

    click.echo(f"Resume Score: {score}/100")
    click.echo(f"Found Keywords: {', '.join(found_keywords)}")
    click.echo(f"Found Sections: {', '.join(found_sections)}")
    if suggestions:
        click.echo("Suggestions for Improvement:")
        for suggestion in suggestions:
            click.echo(f"- {suggestion}")

if __name__ == '__main__':
    main()