from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import pandas as pd
from datetime import datetime
import dateutil.parser
import pytz
from utils.parser import AcademicParser

class ClassroomClient:
    def __init__(self, creds):
        self.service = build('classroom', 'v1', credentials=creds)
        self.drive_service = build('drive', 'v3', credentials=creds)
        self.parser = AcademicParser()

    def get_user_profile(self):
        """Fetches the user's Google Profile using Oauth2 API."""
        try:
            # Use Oauth2 API for better profile info (photo)
            oauth2_service = build('oauth2', 'v2', credentials=self.service._http.credentials)
            user_info = oauth2_service.userinfo().get().execute()
            
            # Map to expected format
            return {
                'name': {'fullName': user_info.get('name')},
                'photoUrl': user_info.get('picture'),
                'emailAddress': user_info.get('email')
            }
        except Exception as e:
            print(f"Error fetching profile: {e}")
            # Fallback to Classroom API
            try:
                return self.service.userProfiles().get(userId='me').execute()
            except:
                return None

    def get_teachers(self, course_id, course_name=None, use_cache=True):
        """Fetches teachers (including TAs) for a course with caching support."""
        from utils.teacher_cache import TeacherCache
        
        cache = TeacherCache()
        
        # Try to get from cache first
        if use_cache and course_name:
            cached_teachers = cache.get_teachers(course_name)
            if cached_teachers:
                # Convert cached data back to expected format
                teachers = []
                for ct in cached_teachers:
                    teachers.append({
                        'userId': ct.get('userId'),
                        'profile': {
                            'name': {'fullName': ct.get('name')},
                            'emailAddress': ct.get('email'),
                            'photoUrl': ct.get('photoUrl')
                        }
                    })
                return teachers
        
        # Cache miss or disabled - fetch from API
        try:
            results = self.service.courses().teachers().list(courseId=course_id).execute()
            teachers = results.get('teachers', [])
            
            # Attempt to fetch photos if missing (with rate limiting awareness)
            for teacher in teachers:
                profile = teacher.get('profile', {})
                if 'photoUrl' not in profile and 'userId' in teacher:
                    try:
                        full_profile = self.service.userProfiles().get(userId=teacher['userId']).execute()
                        if 'photoUrl' in full_profile:
                            teacher['profile']['photoUrl'] = full_profile['photoUrl']
                    except HttpError as e:
                        if e.resp.status == 429:
                            print(f"Rate limit hit for teacher photos. Skipping remaining.")
                            break
                        pass
                    except:
                        pass
            
            # Save to cache if course_name provided
            if course_name:
                cache.save_teachers(course_name, teachers)
                        
            return teachers
        except HttpError as error:
            print(f"An error occurred: {error}")
            return []

    def get_courses(self):
        """Fetches all active courses."""
        try:
            results = self.service.courses().list(courseStates=['ACTIVE']).execute()
            courses = results.get('courses', [])
            return courses
        except HttpError as error:
            print(f"An error occurred: {error}")
            return []

    def get_course_work(self, course_id):
        """Fetches all coursework AND materials for a course."""
        try:
            # 1. Fetch Assignments/Quizzes
            results = self.service.courses().courseWork().list(courseId=course_id).execute()
            works = results.get('courseWork', [])
            
            # 2. Fetch Materials (Slides, Books, etc.)
            mat_results = self.service.courses().courseWorkMaterials().list(courseId=course_id).execute()
            materials = mat_results.get('courseWorkMaterial', [])
            
            # Merge lists
            all_items = works + materials
            
            processed_works = []
            for work in all_items:
                # Smart Parsing
                title = work.get('title', '')
                metadata = self.parser.parse_item(title, work.get('description'))
                
                # Determine Type
                # If it came from courseWorkMaterials, force type to LECTURE/MATERIAL unless parsed otherwise
                is_material = 'dueTime' not in work and 'dueDate' not in work and 'workType' not in work
                
                if is_material:
                    if metadata['category'] == 'UNCATEGORIZED':
                        display_type = 'MATERIAL'
                    else:
                        display_type = metadata['category']
                else:
                    display_type = metadata['category']

                # Deadline formatting
                due_date = work.get('dueDate')
                due_time = work.get('dueTime')
                deadline = None
                
                if due_date:
                    year = due_date.get('year')
                    month = due_date.get('month')
                    day = due_date.get('day')
                    # Default to end of day if no time specified
                    hour = due_time.get('hours', 23) if due_time else 23
                    minute = due_time.get('minutes', 59) if due_time else 59
                    # Google Classroom dates are in UTC by default if not specified, 
                    # but usually the API returns them as naive. We treat them as UTC for conversion.
                    deadline = datetime(year, month, day, hour, minute, tzinfo=pytz.utc)
                elif 'creationTime' in work:
                    # For materials without deadline, use creation time for sorting
                    pass

                processed_works.append({
                    'id': work['id'],
                    'title': work['title'],
                    'description': work.get('description', ''),
                    'type': display_type,
                    'index': metadata['index'],
                    'topic': metadata['topic'],
                    'deadline': deadline,
                    'creationTime': work.get('creationTime'), # Useful for sorting materials
                    'link': work.get('alternateLink'),
                    'materials': work.get('materials', []),
                    'max_points': work.get('maxPoints'),
                    'workType': work.get('workType', 'MATERIAL' if is_material else 'ASSIGNMENT')
                })
                
            return processed_works
        except HttpError as error:
            print(f"An error occurred: {error}")
            return []

    def get_my_submissions(self, course_id, course_work_id):
        """Fetches user's submission and grades."""
        try:
            results = self.service.courses().courseWork().studentSubmissions().list(
                courseId=course_id,
                courseWorkId=course_work_id,
                userId='me'
            ).execute()
            submissions = results.get('studentSubmissions', [])
            if submissions:
                sub = submissions[0]
                return {
                    'state': sub.get('state'), # TURNED_IN, RETURNED, CREATED
                    'assigned_grade': sub.get('assignedGrade'),
                    'draft_grade': sub.get('draftGrade')
                }
            return None
        except HttpError as error:
            return None
