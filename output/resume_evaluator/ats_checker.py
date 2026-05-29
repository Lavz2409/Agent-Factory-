import re

class ATSChecker:
    def __init__(self, resume_text: str):
        self.resume_text = resume_text
        self.keywords = ['Python', 'Java', 'Project Management', 'Team Leadership']
        self.sections = ['Education', 'Skills', 'Experience']
        self.special_characters = r'[@_!#$%^&*()<>?/\|}{~:]'
    
    def check_ats_friendly(self) -> dict:
        score = 0
        suggestions = []

        # Check for presence of keywords
        keyword_score, keyword_suggestions = self._check_keywords()
        score += keyword_score
        suggestions.extend(keyword_suggestions)

        # Check for presence of proper sections
        section_score, section_suggestions = self._check_sections()
        score += section_score
        suggestions.extend(section_suggestions)

        # Check for simple formatting
        formatting_score, formatting_suggestions = self._check_formatting()
        score += formatting_score
        suggestions.extend(formatting_suggestions)

        return {
            'score': score,
            'suggestions': suggestions
        }

    def _check_keywords(self):
        found_keywords = [keyword for keyword in self.keywords if keyword.lower() in self.resume_text.lower()]
        missing_keywords = list(set(self.keywords) - set(found_keywords))
        
        if missing_keywords:
            suggestion = f"Consider adding these keywords: {', '.join(missing_keywords)}."
            return (20, [suggestion])
        return (20, [])

    def _check_sections(self):
        found_sections = [section for section in self.sections if section.lower() in self.resume_text.lower()]
        missing_sections = list(set(self.sections) - set(found_sections))
        
        if missing_sections:
            suggestion = f"Ensure your resume includes the following sections: {', '.join(missing_sections)}."
            return (30, [suggestion])
        return (30, [])

    def _check_formatting(self):
        if re.search(self.special_characters, self.resume_text):
            suggestion = "Avoid using special characters or complex formatting."
            return (0, [suggestion])
        return (50, [])

# Example usage:
# checker = ATSChecker(resume_text)
# result = checker.check_ats_friendly()
# print("Score:", result['score'])
# print("Suggestions:", result['suggestions'])