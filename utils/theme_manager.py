import json
import os

class ThemeManager:
    """Manages user theme preferences (light/dark mode)"""
    
    def __init__(self, settings_file="theme_settings.json"):
        self.settings_file = settings_file
    
    def get_theme(self):
        """Get current theme preference"""
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r') as f:
                    data = json.load(f)
                    return data.get('theme', 'dark')
            except:
                return 'dark'
        return 'dark'
    
    def set_theme(self, theme):
        """Save theme preference"""
        try:
            with open(self.settings_file, 'w') as f:
                json.dump({'theme': theme}, f)
            return True
        except Exception as e:
            print(f"Error saving theme: {e}")
            return False
