from datetime import datetime
import pytz
import re

class OrganizationRules:
    """Smart file organization rules"""
    
    @staticmethod
    def detect_week_number(assignment):
        """Detect week number from assignment deadline or creation time"""
        # Try to use deadline first
        if assignment.get('deadline'):
            deadline = assignment['deadline']
            if isinstance(deadline, str):
                import dateutil.parser
                deadline = dateutil.parser.isoparse(deadline)
            
            # Get week number from deadline
            week_num = deadline.isocalendar()[1]
            return f"Week {week_num}"
        
        # Fallback to creation time
        if assignment.get('creationTime'):
            try:
                import dateutil.parser
                created = dateutil.parser.isoparse(assignment['creationTime'])
                week_num = created.isocalendar()[1]
                return f"Week {week_num}"
            except:
                pass
        
        return "Unscheduled"
    
    @staticmethod
    def extract_topic(assignment):
        """Extract topic from assignment"""
        # First try the topic field
        if assignment.get('topic'):
            topic = assignment['topic']
            # Clean up topic name
            topic = topic.strip()
            if topic and topic != "":
                return topic
        
        # Try to extract from title using common patterns
        title = assignment.get('title', '')
        
        # Pattern: "Week X: Topic" or "Topic - Assignment"
        patterns = [
            r'Week\s+\d+[:\-]\s*(.+?)(?:\s*[-:]\s*\w+\s*\d+)?$',
            r'^(.+?)\s*[-:]\s*(?:Assignment|Lab|Quiz|Exam|HW)',
            r'^(.+?)\s*\d+$'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, title, re.IGNORECASE)
            if match:
                topic = match.group(1).strip()
                if topic:
                    return topic
        
        return "General"
    
    @staticmethod
    def get_organized_path(course_name, assignment):
        """Generate organized path: Course/Week X - Topic/Assignment"""
        week = OrganizationRules.detect_week_number(assignment)
        topic = OrganizationRules.extract_topic(assignment)
        
        # Clean course name
        safe_course = "".join([c for c in course_name if c.isalpha() or c.isdigit() or c in ' -_']).strip()
        
        # Create folder structure
        folder_name = f"{week} - {topic}"
        
        return f"{safe_course}/{folder_name}"
