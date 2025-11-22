import json
import os
from datetime import datetime

class BookmarkManager:
    """Manages assignment bookmarks"""
    
    def __init__(self, bookmarks_file="bookmarks.json"):
        self.bookmarks_file = bookmarks_file
        self._load_bookmarks()
    
    def _load_bookmarks(self):
        """Load bookmarks from file"""
        if os.path.exists(self.bookmarks_file):
            try:
                with open(self.bookmarks_file, 'r', encoding='utf-8') as f:
                    self.bookmarks = json.load(f)
            except:
                self.bookmarks = {}
        else:
            self.bookmarks = {}
    
    def _save_bookmarks(self):
        """Save bookmarks to file"""
        try:
            with open(self.bookmarks_file, 'w', encoding='utf-8') as f:
                json.dump(self.bookmarks, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving bookmarks: {e}")
            return False
    
    def add_bookmark(self, assignment_id, course_name, title, course_id=""):
        """Add an assignment to bookmarks"""
        self.bookmarks[assignment_id] = {
            'course_name': course_name,
            'course_id': course_id,
            'title': title,
            'bookmarked_at': datetime.now().isoformat()
        }
        return self._save_bookmarks()
    
    def remove_bookmark(self, assignment_id):
        """Remove an assignment from bookmarks"""
        if assignment_id in self.bookmarks:
            del self.bookmarks[assignment_id]
            return self._save_bookmarks()
        return False
    
    def is_bookmarked(self, assignment_id):
        """Check if an assignment is bookmarked"""
        return assignment_id in self.bookmarks
    
    def toggle_bookmark(self, assignment_id, course_name="", title="", course_id=""):
        """Toggle bookmark status"""
        if self.is_bookmarked(assignment_id):
            return self.remove_bookmark(assignment_id)
        else:
            return self.add_bookmark(assignment_id, course_name, title, course_id)
    
    def get_bookmarks(self, course_filter=None):
        """Get all bookmarks, optionally filtered by course"""
        if course_filter:
            return {
                k: v for k, v in self.bookmarks.items() 
                if v.get('course_name') == course_filter or v.get('course_id') == course_filter
            }
        return self.bookmarks
    
    def get_all_courses(self):
        """Get list of all courses with bookmarks"""
        courses = set()
        for bookmark in self.bookmarks.values():
            courses.add(bookmark.get('course_name', 'Unknown'))
        return sorted(list(courses))
