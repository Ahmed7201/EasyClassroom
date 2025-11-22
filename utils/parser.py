import re
from datetime import datetime

class AcademicParser:
    def __init__(self):
        self.categories = {
            'QUIZ': ['quiz', 'test', 'exam', 'midterm', 'final', 'mt'],
            'LAB': ['lab', 'practical', 'experiment'],
            'PROJECT': ['project', 'milestone', 'proposal', 'report'],
            'ASSIGNMENT': ['assignment', 'hw', 'homework', 'problem set', 'sheet'],
            'LECTURE': ['lecture', 'slide', 'presentation', 'notes', 'chapter'],
            'TUTORIAL': ['tutorial', 'recitation'],
            'GRADE': ['grade', 'score', 'result']
        }

    def parse_item(self, title, description="", materials=None):
        """
        Parses a raw item (assignment/material) and returns structured metadata.
        """
        title_lower = title.lower()
        desc_lower = (description or "").lower()
        
        # 1. Categorization
        category = "UNCATEGORIZED"
        for cat, keywords in self.categories.items():
            if any(k in title_lower for k in keywords):
                category = cat
                break
        
        # Refine Quiz vs Exam
        if category == 'QUIZ':
            if any(x in title_lower for x in ['midterm', 'mt']):
                category = 'MIDTERM'
            elif 'final' in title_lower:
                category = 'FINAL'

        # 2. Indexing (Extract Number)
        # Matches: "Lab 3", "Lab03", "Lab #3", "L3", "Sheet 4"
        index = None
        match = re.search(r'(?:^|\s|#|[a-z])(\d+)(?:$|\s|:)', title_lower)
        if match:
            index = int(match.group(1))

        # 3. Topic Extraction (Simple Heuristic)
        # Remove common words and category names to find the topic
        topic = title
        remove_words = [k for kw in self.categories.values() for k in kw] + \
                       ['week', 'unit', 'part', 'pdf', 'docx', 'ppt']
        
        for word in remove_words:
            topic = re.sub(r'\b' + re.escape(word) + r'\b', '', topic, flags=re.IGNORECASE)
        
        topic = re.sub(r'\d+', '', topic).strip(' -_#:')
        if len(topic) < 3: # If topic is too short, it's probably just "Lab 3"
            topic = None

        return {
            'category': category,
            'index': index,
            'topic': topic,
            'original_title': title
        }

    def enrich_course_data(self, course_works):
        """
        Takes a list of raw course works and returns enriched, sorted data.
        """
        enriched = []
        for work in course_works:
            metadata = self.parse_item(work['title'], work.get('description'))
            
            # Merge metadata
            work.update({
                'smart_category': metadata['category'],
                'smart_index': metadata['index'],
                'smart_topic': metadata['topic']
            })
            enriched.append(work)
            
        # Sort by Category then Index
        enriched.sort(key=lambda x: (x['smart_category'], x.get('smart_index') or 999))
        return enriched
