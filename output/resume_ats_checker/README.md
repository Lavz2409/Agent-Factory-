# 📦 Project Overview

The `resume_ats_checker` project is a command-line interface (CLI) tool designed to evaluate resumes for ATS (Applicant Tracking System) compatibility. It analyzes resume text for the presence of essential keywords, proper sectioning, and simple formatting. The tool provides a score from 0 to 100 and offers suggestions for improvement, ensuring that resumes are optimized for ATS parsing.

**Key Features:**
- Parses resume text from plain text, PDF, or DOCX files.
- Checks for the presence of keywords and essential sections.
- Evaluates formatting simplicity.
- Provides a score and suggestions for ATS optimization.
- Operates entirely offline without external API dependencies.

# 🔄 Architecture & Execution Flow

1. **User Input**: The user provides a resume file path via the CLI.
2. **Parsing**: The `parser.py` module reads and extracts text from the resume file.
3. **Checking**: The `checker.py` module evaluates the parsed text for ATS-friendly features such as keywords, sections, and formatting.
4. **Scoring**: The `scorer.py` module calculates a score based on the checks and generates improvement suggestions.
5. **Output**: Results, including the score and suggestions, are displayed in the terminal.

- **Agent Interaction**: The `main.py` script orchestrates the flow by invoking functions from `parser.py`, `checker.py`, and `scorer.py`.
- **Data Flow**: Resume text flows from the parser to the checker, where it is analyzed, and then to the scorer for final evaluation and feedback.

# 📁 Generated Files Explanation

| File       | Purpose                                                                 |
|------------|-------------------------------------------------------------------------|
| main.py    | Entry point for the CLI tool using Click to handle user interactions.   |
| parser.py  | Handles parsing of resume text and files, extracting necessary content. |
| checker.py | Performs ATS-friendly checks on parsed data to identify issues.         |
| scorer.py  | Calculates the ATS score and generates suggestions for improvement.     |
| tests.py   | Contains unit tests to ensure all modules function correctly.           |

# 📚 Libraries & Dependencies

**Standard Library:**
- `re`: For regular expression operations.
- `unittest`: For testing the modules.

**Third-Party Libraries:**
- `click`: For building the command-line interface.
- `PyPDF2`: For reading text from PDF files.
- `python-docx`: For reading text from DOCX files.

# ⚙️ Setup Instructions

**Environment Requirements:**
- Python 3.8 or higher

**Installation Commands:**
```bash
# Clone the repository
git clone https://github.com/yourusername/resume_ats_checker.git
cd resume_ats_checker

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`

# Install dependencies
pip install -r requirements.txt
```

# ▶️ Commands to Run

Execute the tool with the following command:
```bash
python main.py /path/to/resume/file
```

# 🧪 Test Cases

| Test                         | Input                      | Expected Output                            |
|------------------------------|----------------------------|--------------------------------------------|
| Test text file parsing       | `sample.txt`               | Parsed text as a string                    |
| Test PDF file parsing        | `sample.pdf`               | Parsed text as a string                    |
| Test DOCX file parsing       | `sample.docx`              | Parsed text as a string                    |
| Test ATS-friendly check      | Resume text with keywords  | Score and suggestions for improvement      |
| Test scoring and suggestions | Parsed resume data         | Score between 0-100 and improvement tips   |

# 🔍 Manual Testing Steps

1. **Prepare Test Files**: Create sample resume files in TXT, PDF, and DOCX formats.
2. **Run the CLI Tool**: Execute the command `python main.py /path/to/sample.txt`.
3. **Verify Output**: Check that the score and suggestions are displayed correctly.
4. **Repeat**: Test with different resume files to ensure consistent results.

# 🚀 Future Improvements

- **Enhanced Keyword Detection**: Implement machine learning models to better identify relevant keywords and phrases.
- **GUI Interface**: Develop a graphical user interface to make the tool more accessible to non-technical users.
- **Multilingual Support**: Extend parsing and checking capabilities to support resumes in multiple languages.