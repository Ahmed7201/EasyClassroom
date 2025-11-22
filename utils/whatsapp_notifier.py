import requests
import urllib.parse
from datetime import datetime
import pytz

class WhatsAppNotifier:
    def __init__(self, phone_number, api_key, timezone='Africa/Cairo'):
        """
        Initialize WhatsApp notifier using CallMeBot API
        phone_number: Format +201127063811
        api_key: Get from https://www.callmebot.com/blog/free-api-whatsapp-messages/
        timezone: User's timezone (default: Africa/Cairo)
        """
        self.phone_number = phone_number
        self.api_key = api_key
        self.base_url = "https://api.callmebot.com/whatsapp.php"
        self.timezone = pytz.timezone(timezone)
    
    def send_message(self, message):
        """Send a WhatsApp message via CallMeBot"""
        try:
            # URL encode the message
            encoded_message = urllib.parse.quote(message)
            
            # Build the request URL
            url = f"{self.base_url}?phone={self.phone_number}&text={encoded_message}&apikey={self.api_key}"
            
            # Send the request
            response = requests.get(url)
            
            if response.status_code == 200:
                return True, "Message sent successfully!"
            else:
                return False, f"Failed: {response.status_code}"
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    def _format_time(self, dt):
        """Convert datetime to user's timezone and format as 12-hour with AM/PM"""
        if dt.tzinfo is None:
            dt = pytz.utc.localize(dt)
        local_dt = dt.astimezone(self.timezone)
        return local_dt.strftime('%b %d, %I:%M %p')
    
    def format_daily_summary(self, assignments):
        """Format assignments into a daily summary message"""
        if not assignments:
            return "✅ No pending assignments today!"
        
        now = datetime.now(pytz.utc)
        local_now = now.astimezone(self.timezone)
        message = f"📚 Daily Assignment Summary\n"
        message += f"📅 {local_now.strftime('%B %d, %Y - %I:%M %p')}\n\n"
        
        # Sort by urgency (deadline)
        sorted_assignments = sorted(
            [a for a in assignments if a.get('deadline') and a['deadline'] > now],
            key=lambda x: x['deadline']
        )
        
        for idx, assignment in enumerate(sorted_assignments, 1):
            days_left = (assignment['deadline'] - now).days
            
            # Urgency emoji
            if days_left < 2:
                emoji = "🔴"
            elif days_left < 5:
                emoji = "🟠"
            else:
                emoji = "🟢"
            
            course_name = assignment.get('course_name', 'Unknown Course')
            title = assignment['title']
            due_time = self._format_time(assignment['deadline'])
            
            message += f"{emoji} {idx}. [{course_name}] {title}\n"
            message += f"   Due: {due_time} ({days_left} days left)\n\n"
        
        return message
    
    def format_new_assignment_alert(self, assignment):
        """Format a new assignment alert"""
        now = datetime.now(pytz.utc)
        
        if assignment.get('deadline'):
            days_left = (assignment['deadline'] - now).days
            due_time = self._format_time(assignment['deadline'])
            
            # Urgency emoji
            if days_left < 2:
                emoji = "🔴"
            elif days_left < 5:
                emoji = "🟠"
            else:
                emoji = "🟢"
            
            message = f"🚨 New Assignment Posted!\n\n"
            message += f"Course: {assignment.get('course_name', 'Unknown')}\n"
            message += f"Title: {assignment['title']}\n"
            message += f"Due: {due_time} ({days_left} days left) {emoji}\n"
        else:
            message = f"🚨 New Material Posted!\n\n"
            message += f"Course: {assignment.get('course_name', 'Unknown')}\n"
            message += f"Title: {assignment['title']}\n"
        
        return message
    
    def test_connection(self):
        """Test WhatsApp connection"""
        local_now = datetime.now(self.timezone)
        test_message = f"✅ Google Classroom Assistant connected successfully!\n"
        test_message += f"📅 Test sent at: {local_now.strftime('%B %d, %Y - %I:%M %p')}"
        return self.send_message(test_message)
