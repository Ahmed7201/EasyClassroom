import os
import json
from datetime import datetime

class TeacherCache:
    """Cache teacher profile data to avoid repeated API calls and 429 errors."""
    
    def __init__(self, base_path="Downloads"):
        self.base_path = base_path
    
    def _get_cache_path(self, course_name):
        """Get the cache file path for a course."""
        safe_name = "".join([c for c in course_name if c.isalpha() or c.isdigit() or c==' ']).rstrip()
        course_dir = os.path.join(self.base_path, safe_name, "Teachers")
        os.makedirs(course_dir, exist_ok=True)
        return os.path.join(course_dir, "cache.json")
    
    def get_teachers(self, course_name):
        """Retrieve cached teacher data for a course."""
        cache_path = self._get_cache_path(course_name)
        
        if not os.path.exists(cache_path):
            return None
        
        try:
            with open(cache_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('teachers', [])
        except Exception as e:
            print(f"Error reading cache: {e}")
            return None
    
    def save_teachers(self, course_name, teachers):
        """Save teacher data to cache."""
        cache_path = self._get_cache_path(course_name)
        
        try:
            # Extract only necessary fields
            cached_teachers = []
            for teacher in teachers:
                profile = teacher.get('profile', {})
                cached_teachers.append({
                    'name': profile.get('name', {}).get('fullName', 'Unknown'),
                    'email': profile.get('emailAddress', ''),
                    'photoUrl': profile.get('photoUrl', ''),
                    'userId': teacher.get('userId', '')
                })
            
            data = {
                'teachers': cached_teachers,
                'cached_at': datetime.now().isoformat()
            }
            
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            return True
        except Exception as e:
            print(f"Error saving cache: {e}")
            return False
    
    def clear_cache(self, course_name):
        """Clear cached teacher data for a course."""
        cache_path = self._get_cache_path(course_name)
        if os.path.exists(cache_path):
            try:
                os.remove(cache_path)
                return True
            except Exception as e:
                print(f"Error clearing cache: {e}")
                return False
        return True
