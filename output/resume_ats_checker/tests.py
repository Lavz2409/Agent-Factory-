import unittest
from parser import parse_resume, read_text_from_file, read_text_from_pdf, read_text_from_docx, check_ats_friendly
from checker import check_ats_friendly as checker_check_ats_friendly
from scorer import score_resume

class TestResumeParser(unittest.TestCase):

    def test_read_text_from_file(self):
        text = read_text_from_file('sample.txt')
        self.assertIsInstance(text, str)
        self.assertGreater(len(text), 0)

    def test_read_text_from_pdf(self):
        text = read_text_from_pdf('sample.pdf')
        self.assertIsInstance(text, str)
        self.assertGreater(len(text), 0)

    def test_read_text_from_docx(self):
        text = read_text_from_docx('sample.docx')
        self.assertIsInstance(text, str)
        self.assertGreater(len(text), 0)

    def test_parse_resume(self):
        parsed_data = parse_resume('sample.txt')
        self.assertIsInstance(parsed_data, dict)
        self.assertIn('text', parsed_data)

    def test_check_ats_friendly(self):
        resume_text = "Sample resume text with skills and experience."
        score, suggestions = check_ats_friendly(resume_text)
        self.assertIsInstance(score, int)
        self.assertIsInstance(suggestions, list)

    def test_checker_check_ats_friendly(self):
        parsed_data = {'text': "Sample resume text with skills and experience."}
        results = checker_check_ats_friendly(parsed_data)
        self.assertIsInstance(results, dict)
        self.assertIn('score', results)
        self.assertIn('suggestions', results)

    def test_score_resume(self):
        check_results = {'score': 80, 'suggestions': ['Add more skills']}
        score = score_resume(check_results)
        self.assertIsInstance(score, int)
        self.assertEqual(score, 80)

if __name__ == '__main__':
    unittest.main()