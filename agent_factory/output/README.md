# 📦 Project Overview

The project is a command-line interface (CLI) tool called "resume_ats_checker" designed to evaluate resumes for compatibility with Applicant Tracking Systems (ATS). It analyzes the resume text to check for essential keywords, proper sections, and simple formatting. The tool assigns a score from 0 to 100 based on these factors and provides suggestions for improvement. This tool is implemented using Python and operates entirely offline without relying on external APIs.

### Key Features
- **Keyword Detection**: Identifies relevant skills and experience keywords within the resume.
- **Section Verification**: Ensures the presence of necessary sections like Education, Skills, and Experience.
- **Formatting Check**: Validates that the resume uses simple formatting without special characters or tables.
- **Scoring and Suggestions**: Provides a comprehensive score and actionable suggestions to enhance ATS compatibility.

# 🔄 Architecture & Execution Flow

1. **User Input**: The user provides resume text either directly or via a file through the CLI.
2. **Keyword Check**: The tool scans the resume for relevant keywords.
3. **Section Check**: It verifies the presence of essential sections.
4. **Formatting Check**: The tool checks the resume for simple formatting.
5. **Scoring**: A score is calculated based on the results of the checks.
6. **Suggestions**: Suggestions are generated to improve the resume.
7. **Output**: The score and suggestions are displayed to the user.

### Component Interaction
- **CLI (cli.py)**: Handles user input and invokes the main logic.
- **ATS Checker (ats_checker.py)**: Performs checks for keywords, sections, and formatting.
- **Scoring (scoring.py)**: Calculates the score and generates suggestions based on the ATS results.

### Data Flow Diagram
```
[User Input] --> [CLI] --> [ATS Checker] --> [Scoring] --> [Output]
```

# 📁 Generated Files

| File                      | Purpose                                             |
|---------------------------|-----------------------------------------------------|
| `main.py`                 | Entry point for the CLI tool, handles user input and output. |
| `ats_checker.py`          | Contains core logic for checking ATS compatibility. |
| `scoring.py`              | Implements scoring and suggestion mechanisms.       |
| `cli.py`                  | Defines the command-line interface using Click.     |
| `tests/test_ats_checker.py` | Unit tests for ATS checking logic.                |
| `tests/test_scoring.py`   | Unit tests for scoring and suggestion logic.        |
| `tests/test_cli.py`       | Integration tests for the CLI.                      |

# 📚 Libraries & Frameworks

| Library  | Type       | Purpose                                         | Install Command          |
|----------|------------|-------------------------------------------------|--------------------------|
| `click`  | Third-party| Facilitates the creation of command-line interfaces. | `pip install click`      |
| `pytest` | Third-party| Framework for writing and running tests.        | `pip install pytest`     |
| `re`     | Stdlib     | Provides regular expression matching operations.| N/A                      |

# ⚙️ Setup & Installation

1. Ensure Python 3.8 or higher is installed.
2. Install necessary packages:
   ```bash
   pip install click
   pip install pytest
   ```
3. No additional `.env` or configuration setup is required.

# ▶️ Commands to Run

To execute the resume ATS checker, use the following command:
```bash
python main.py --resume-file path/to/resume.txt
```
Or provide the resume text directly:
```bash
python main.py --resume-text "Your resume text here"
```

# 🧪 Test Cases

| #  | Input                                   | Expected Output                                | Pass Criteria                             |
|----|-----------------------------------------|------------------------------------------------|-------------------------------------------|
| 1  | Resume with all keywords and sections   | Score: 100, No suggestions                     | Score is 100, suggestions list is empty   |
| 2  | Resume missing keywords                 | Score < 100, Suggests adding keywords          | Score less than 100, keywords suggestion  |
| 3  | Resume missing sections                 | Score < 100, Suggests adding sections          | Score less than 100, sections suggestion  |
| 4  | Poorly formatted resume                 | Score < 100, Suggests improving formatting     | Score less than 100, formatting suggestion|
| 5  | Empty resume                            | Score: 0, Suggests adding keywords and sections| Score is 0, multiple suggestions          |

# 🔍 Manual Testing Steps

1. Open a terminal.
2. Navigate to the directory containing the project files.
3. Run the CLI tool with a sample resume file using the command:
   ```bash
   python main.py --resume-file path/to/sample_resume.txt
   ```
4. Observe the output score and suggestions.
5. Modify the resume to include more keywords and sections.
6. Re-run the tool and verify that the score increases and suggestions decrease.

# 🚀 Future Improvements

- **Enhanced Keyword Detection**: Implement a more sophisticated keyword detection using NLP techniques.
- **Customizable Keyword Lists**: Allow users to provide their own list of keywords relevant to specific job applications.
- **Section Detection Flexibility**: Improve section detection to handle variations in section naming and order.
- **GUI Version**: Develop a graphical user interface for users who prefer not to use the command line.