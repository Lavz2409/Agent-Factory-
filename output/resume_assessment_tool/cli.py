import argparse
import re
import os

def load_resume(file_path):
    with open(file_path, 'r') as file:
        return file.read()

def is_ats_friendly(resume_text):
    score = 0
    suggestions = []

    # Check for presence of proper sections
    sections = ['Education', 'Skills', 'Experience']
    for section in sections:
        if re.search(r'\b' + section + r'\b', resume_text, re.IGNORECASE):
            score += 10
        else:
            suggestions.append(f"Add a section for {section}.")

    # Check for keywords
    keywords = ['Python', 'AI', 'Machine Learning', 'Data Analysis']
    for keyword in keywords:
        if re.search(r'\b' + keyword + r'\b', resume_text, re.IGNORECASE):
            score += 5
        else:
            suggestions.append(f"Include relevant keyword: {keyword}.")

    # Check for simple formatting
    if re.search(r'[^\w\s,.]', resume_text):
        suggestions.append("Remove special characters for simpler formatting.")
    else:
        score += 10

    return score, suggestions

def main(args):
    parser = argparse.ArgumentParser(description='Analyze if a resume is ATS-friendly.')
    parser.add_argument('resume', type=str, help='Path to the resume file or resume text')
    parsed_args = parser.parse_args(args)

    # Determine if input is a file path or direct text
    if os.path.isfile(parsed_args.resume):
        resume_text = load_resume(parsed_args.resume)
    else:
        resume_text = parsed_args.resume

    score, suggestions = is_ats_friendly(resume_text)

    print(f"Resume ATS-friendliness score: {score}/100")
    if suggestions:
        print("Suggestions to improve your resume:")
        for suggestion in suggestions:
            print(f"- {suggestion}")

if __name__ == '__main__':
    import sys
    main(sys.argv[1:])