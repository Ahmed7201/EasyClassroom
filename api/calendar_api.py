from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from datetime import datetime, timedelta
import pytz

class CalendarClient:
    def __init__(self, creds):
        self.service = build('calendar', 'v3', credentials=creds)
    
    def get_upcoming_events(self, max_results=50):
        """Fetch upcoming calendar events"""
        try:
            now = datetime.utcnow().isoformat() + 'Z'
            events_result = self.service.events().list(
                calendarId='primary',
                timeMin=now,
                maxResults=max_results,
                singleEvents=True,
                orderBy='startTime',
                # Fetch ALL event details
                fields='items(id,summary,description,location,start,end,attendees,creator,organizer,htmlLink,colorId,status)'
            ).execute()
            return events_result.get('items', [])
        except HttpError as error:
            print(f"An error occurred: {error}")
            return []
    
    def create_event(self, summary, description, start_time, end_time, course_name="", event_type=""):
        """Create a calendar event"""
        try:
            event = {
                'summary': f"[{event_type}] {summary}" if event_type else summary,
                'description': f"Course: {course_name}\n\n{description}" if course_name else description,
                'start': {
                    'dateTime': start_time.isoformat(),
                    'timeZone': 'UTC',
                },
                'end': {
                    'dateTime': end_time.isoformat(),
                    'timeZone': 'UTC',
                },
                'reminders': {
                    'useDefault': False,
                    'overrides': [
                        {'method': 'popup', 'minutes': 6 * 60},   # 6 hours before
                        {'method': 'popup', 'minutes': 24 * 60},  # 1 day before
                    ],
                },
            }
            
            event = self.service.events().insert(calendarId='primary', body=event).execute()
            return event.get('id'), event.get('htmlLink')
        except HttpError as error:
            print(f"An error occurred: {error}")
            return None, None
    
    def delete_event(self, event_id):
        """Delete a calendar event"""
        try:
            self.service.events().delete(calendarId='primary', eventId=event_id).execute()
            return True
        except HttpError as error:
            print(f"An error occurred: {error}")
            return False
    
    def sync_assignments(self, assignments, course_name):
        """Sync upcoming assignments to calendar"""
        synced_count = 0
        now = datetime.now(pytz.utc)
        
        for assignment in assignments:
            if assignment['deadline'] and assignment['deadline'] > now:
                # Create event
                summary = assignment['title']
                description = assignment.get('description', 'No description')
                start_time = assignment['deadline'] - timedelta(hours=6)  # 6 hours before deadline
                end_time = assignment['deadline']
                
                event_id, link = self.create_event(
                    summary, 
                    description, 
                    start_time, 
                    end_time,
                    course_name,
                    assignment['type']
                )
                
                if event_id:
                    synced_count += 1
        
        return synced_count
    
    def delete_past_events(self, days_ago=7):
        """Delete events older than specified days"""
        try:
            time_min = (datetime.utcnow() - timedelta(days=days_ago)).isoformat() + 'Z'
            time_max = datetime.utcnow().isoformat() + 'Z'
            
            events_result = self.service.events().list(
                calendarId='primary',
                timeMin=time_min,
                timeMax=time_max,
                singleEvents=True
            ).execute()
            
            events = events_result.get('items', [])
            deleted_count = 0
            
            for event in events:
                if self.delete_event(event['id']):
                    deleted_count += 1
            
            return deleted_count
        except HttpError as error:
            print(f"An error occurred: {error}")
            return 0

    def update_event(self, event_id, start_time, end_time):
        """Update a calendar event's time"""
        try:
            event = self.service.events().get(calendarId='primary', eventId=event_id).execute()
            
            event['start']['dateTime'] = start_time.isoformat()
            event['end']['dateTime'] = end_time.isoformat()
            
            updated_event = self.service.events().update(
                calendarId='primary', 
                eventId=event_id, 
                body=event
            ).execute()
            
            return True
        except HttpError as error:
            print(f"An error occurred: {error}")
            return False
