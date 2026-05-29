# resume_evaluator

## 1. Project Overview

The `resume_evaluator` project is a command-line interface (CLI) tool designed to assess the ATS-friendliness of resumes. Applicant Tracking Systems (ATS) are widely used by employers to filter job applications, and resumes that are not ATS-friendly may be overlooked. This tool evaluates resumes by checking for the presence of essential keywords, proper section structuring, and simple formatting. It then provides a score and suggestions for improvement. This tool is intended for job seekers who want to optimize their resumes for ATS compatibility.

## 2. Agents Involved

- **PlannerAgent**: Outlined the project requirements and defined the scope of the tool.
- **ResearcherAgent**: Investigated the best practices for ATS-friendly resumes and the technologies suitable for building the tool.
- **ArchitectAgent**: Designed the system architecture, ensuring modularity and separation of concerns.
- **CoderAgent**: Implemented the code for parsing, checking, scoring, and generating suggestions.
- **WrapperAgent**: Developed the CLI interface using Click and ensured seamless integration of all components.

## 3. Architecture Summary

The architecture of `resume_evaluator` follows a modular design pattern, with distinct components for parsing resumes, checking ATS-friendly features, scoring, and suggesting improvements. The CLI interface is built using Click, which facilitates user interaction. Parsing strategies are implemented for different file types (PDF and DOCX) using PyPDF2 and python-docx. The system processes input data, evaluates it against predefined rules, and outputs results in a user-friendly format.

## 4. Tech Stack & Libraries

- **Python**: The primary programming language used for development.
- **PyPDF2**: Library for reading PDF files.
- **python-docx**: Library for reading DOCX files.
- **pandas**: Used for data manipulation and analysis.
- **click**: Used to create the command-line interface.

## 5. Project Structure

```
C:\Agent factory\output\resume_evaluator
│
├── main.py
│   └── Entry point for the CLI tool using Click.
│
├── parser.py
│   └── Contains logic for parsing resume files (PDF, DOCX) and plain text.
│
├── ats_checker.py
│   └── Implements checks for ATS-friendly features.
│
├── scorer.py
│   └── Calculates a score based on ATS checks.
│
├── suggestions.py
│   └── Generates suggestions for improving the resume.
│
└── tests.py
    └── Contains unit tests for all modules.
```

## 6. How to Build

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd resume_evaluator
   ```

2. **Install dependencies**:
   Ensure you have Python installed, then run:
   ```bash
   pip install -r requirements.txt
   ```

## 7. How to Run

1. **Navigate to the project directory**:
   ```bash
   cd C:\Agent factory\output\resume_evaluator
   ```

2. **Run the CLI tool**:
   ```bash
   python main.py --help
   ```

   To evaluate a resume, use:
   ```bash
   python main.py evaluate --file <path-to-resume-file>
   ```

## 8. Environment Variables

No environment variables are required for running this project.

## 9. Notes & Caveats

- **Known Limitations**: The tool uses rule-based logic and does not incorporate machine learning, which may limit its adaptability to diverse resume formats.
- **TODOs**: Future versions could integrate machine learning models to enhance accuracy and flexibility.
- **Security Notes**: Ensure that resumes do not contain sensitive information before processing them with the tool.