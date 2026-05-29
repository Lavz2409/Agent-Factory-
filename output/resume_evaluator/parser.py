import re
from PyPDF2 import PdfReader
from docx import Document

class ResumeParser:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.text = self.parse_resume()

    def parse_resume(self) -> str:
        if self.file_path.endswith('.pdf'):
            return self._parse_pdf()
        elif self.file_path.endswith('.docx'):
            return self._parse_docx()
        else:
            return self._parse_txt()

    def _parse_pdf(self) -> str:
        try:
            with open(self.file_path, 'rb') as file:
                reader = PdfReader(file)
                text = ''
                for page in reader.pages:
                    text += page.extract_text()
                return text
        except Exception as e:
            print(f"Error reading PDF file: {e}")
            return ""

    def _parse_docx(self) -> str:
        try:
            doc = Document(self.file_path)
            text = '\n'.join([para.text for para in doc.paragraphs])
            return text
        except Exception as e:
            print(f"Error reading DOCX file: {e}")
            return ""

    def _parse_txt(self) -> str:
        try:
            with open(self.file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            print(f"Error reading text file: {e}")
            return ""

    def is_ats_friendly(self) -> (int, list):
        score = 0
        suggestions = []

        # Check for required sections
        required_sections = ['Education', 'Skills', 'Experience']
        for section in required_sections:
            if re.search(rf'\b{section}\b', self.text, re.IGNORECASE):
                score += 20
            else:
                suggestions.append(f"Add a '{section}' section.")

        # Check for keywords
        keywords = ['Python', 'Java', 'Project Management', 'Data Analysis']
        keyword_matches = [keyword for keyword in keywords if re.search(rf'\b{keyword}\b', self.text, re.IGNORECASE)]
        score += 10 * len(keyword_matches)
        if len(keyword_matches) < len(keywords):
            suggestions.append("Include more relevant keywords: " + ", ".join(set(keywords) - set(keyword_matches)))

        # Check for simple formatting
        if re.search(r'[^\w\s,.]', self.text):
            suggestions.append("Avoid using special characters or complex formatting.")
        else:
            score += 20

        return min(score, 100), suggestions

def parse_resume(file_path: str) -> str:
    parser = ResumeParser(file_path)
    return parser.text