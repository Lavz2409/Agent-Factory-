# 📦 Project Overview

The `resume_ats_checker` project is a command-line interface (CLI) tool designed to evaluate resumes for Applicant Tracking System (ATS) compatibility. It analyzes resume text to ensure it contains necessary keywords, proper sections, and simple formatting. The tool provides a score from 0 to 100 and offers suggestions for improving the resume's ATS-friendliness.

**Key Features:**
- Parses resume text to identify key sections and keywords.
- Evaluates the resume against ATS-friendly criteria.
- Provides a score indicating the resume's ATS compatibility.
- Offers suggestions for improving the resume.
- Operates entirely in the terminal without using external APIs.

# 🔄 Architecture & Execution Flow

1. **User Input**: The user provides a resume file path as input to the CLI tool.
2. **Resume Parsing**: The `resume_parser.py` module reads the resume text and extracts sections like Education, Skills, and Experience.
3. **ATS Check**: The `ats_checker.py` module evaluates the parsed resume for ATS-friendly criteria, such as keyword presence and formatting.
4. **Scoring and Suggestions**: The tool calculates a score and generates improvement suggestions using the `suggestions.py` module.
5. **Output**: The results, including the score and suggestions, are displayed in the terminal.

**Agent Interaction**: The main entry point (`main.py`) coordinates the flow by invoking functions from `resume_parser.py`, `ats_checker.py`, and `suggestions.py`.

**Data Flow**: The resume text is parsed into structured data, which is then analyzed for ATS compatibility. The analysis results are formatted and output to the user.

# 📁 Generated Files Explanation

| File                         | Purpose                                                                 |
|------------------------------|-------------------------------------------------------------------------|
| `main.py`                    | Entry point for the CLI tool using Click.                               |
| `resume_parser.py`           | Contains logic for parsing resume text and extracting relevant sections.|
| `ats_checker.py`             | Implements checks for ATS-friendly criteria and calculates scores.      |
| `suggestions.py`             | Generates suggestions for improving the resume.                         |
| `tests/test_resume_parser.py`| Tests for resume parsing logic.                                         |
| `tests/test_ats_checker.py`  | Tests for ATS checks and scoring logic.                                 |
| `tests/test_suggestions.py`  | Tests for suggestion generation logic.                                  |

# 📚 Libraries & Dependencies

**Standard Library:**
- `os`
- `re`
- `typing`

**Third-Party Libraries:**
- `click` (for CLI interface)
- `pytest` (for testing)

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
pip install click pytest
```

# ▶️ Commands to Run

To execute the project, use the following command in the terminal:
```bash
python main.py /path/to/resume.txt
```
Replace `/path/to/resume.txt` with the actual path to the resume file you wish to analyze.

# 🧪 Test Cases

| Test                | Input                                      | Expected Output                                        |
|---------------------|--------------------------------------------|--------------------------------------------------------|
| Parse Resume        | Resume text with sections and keywords     | Dictionary with parsed sections and keywords           |
| ATS Check           | Parsed resume with missing sections        | Score < 100, suggestions to add missing sections       |
| Suggestion Generation | Parsed resume with complex formatting    | Suggestions to simplify formatting                     |

# 🔍 Manual Testing Steps

1. Prepare a sample resume text file with various sections and keywords.
2. Open a terminal and navigate to the project directory.
3. Activate the virtual environment.
4. Run the CLI tool using the command: `python main.py /path/to/resume.txt`.
5. Observe the output score and suggestions for accuracy.
6. Modify the resume to include/exclude sections or keywords and rerun the tool to test different scenarios.

# 🚀 Future Improvements

- **Enhanced Keyword Detection**: Implement machine learning models to improve keyword detection beyond simple regex matching.
- **GUI Version**: Develop a graphical user interface for users who prefer not to use the command line.
- **Integration with Resume Databases**: Allow users to compare their resume against industry-specific databases for more tailored suggestions.