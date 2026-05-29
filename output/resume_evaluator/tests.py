import unittest
from main import read_file, read_pdf, read_docx, evaluate_resume
from parser import ResumeParser
from ats_checker import ATSChecker
from scorer import calculate_score
from suggestions import generate_suggestions

class TestResumeParser(unittest.TestCase):

    def test_read_file_txt(self):
        content = read_file('sample_resume.txt')
        self.assertIsInstance(content, str)
        self.assertIn('Education', content)

    def test_read_pdf(self):
        content = read_pdf('sample_resume.pdf')
        self.assertIsInstance(content, str)
        self.assertIn('Skills', content)

    def test_read_docx(self):
        content = read_docx('sample_resume.docx')
        self.assertIsInstance(content, str)
        self.assertIn('Experience', content)

    def test_parse_resume(self):
        parser = ResumeParser('sample_resume.txt')
        content = parser.parse_resume()
        self.assertIsInstance(content, str)
        self.assertIn('Education', content)

    def test_is_ats_friendly(self):
        parser = ResumeParser('sample_resume.txt')
        score, suggestions = parser.is_ats_friendly()
        self.assertIsInstance(score, int)
        self.assertIsInstance(suggestions, list)

class TestATSChecker(unittest.TestCase):

    def test_check_ats_friendly(self):
        ats_checker = ATSChecker('Sample resume text with Education, Skills, Experience')
        results = ats_checker.check_ats_friendly()
        self.assertIsInstance(results, dict)
        self.assertIn('keywords', results)
        self.assertIn('sections', results)
        self.assertIn('formatting', results)

class TestScorer(unittest.TestCase):

    def test_calculate_score(self):
        ats_results = {
            'keywords': True,
            'sections': True,
            'formatting': True
        }
        score = calculate_score(ats_results)
        self.assertEqual(score, 100)

class TestSuggestions(unittest.TestCase):

    def test_generate_suggestions(self):
        ats_results = {
            'keywords': False,
            'sections': True,
            'formatting': False
        }
        suggestions = generate_suggestions(ats_results)
        self.assertIsInstance(suggestions, list)
        self.assertGreater(len(suggestions), 0)

if __name__ == '__main__':
    unittest.main()