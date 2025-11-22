import io
import os
import subprocess
import platform
from googleapiclient.http import MediaIoBaseDownload
from googleapiclient.errors import HttpError
from utils.organization_rules import OrganizationRules

class DriveDownloader:
    def __init__(self, drive_service, use_smart_organization=True):
        self.service = drive_service
        self.use_smart_organization = use_smart_organization

    def download_file(self, file_id, file_name, mime_type, destination_folder, assignment=None, course_name=None):
        """Downloads a file from Drive to the local file system.
        
        Args:
            file_id: Drive file ID
            file_name: Name of the file
            mime_type: MIME type of the file
            destination_folder: Base destination folder
            assignment: Assignment metadata (for smart organization)
            course_name: Course name (for smart organization)
        """
        # Use smart organization if enabled and metadata is available
        if self.use_smart_organization and assignment and course_name:
            organized_path = OrganizationRules.get_organized_path(course_name, assignment)
            # Clean assignment title for folder name
            assignment_title = assignment.get('title', 'Assignment')
            safe_title = "".join([c for c in assignment_title if c.isalpha() or c.isdigit() or c in ' -_']).strip()
            destination_folder = os.path.join(destination_folder, organized_path, safe_title)
        
        if not os.path.exists(destination_folder):
            os.makedirs(destination_folder)

        file_path = os.path.join(destination_folder, file_name)
        
        # Handle Google Docs/Sheets/Slides (Export links)
        if 'application/vnd.google-apps' in mime_type:
            if 'document' in mime_type:
                mime_type = 'application/pdf'
                file_name += '.pdf'
                file_path = os.path.join(destination_folder, file_name)
            elif 'spreadsheet' in mime_type:
                mime_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                file_name += '.xlsx'
                file_path = os.path.join(destination_folder, file_name)
            elif 'presentation' in mime_type:
                mime_type = 'application/pdf'
                file_name += '.pdf'
                file_path = os.path.join(destination_folder, file_name)
            else:
                return False, "Unsupported Google Doc type"
            
            request = self.service.files().export_media(fileId=file_id, mimeType=mime_type)
        else:
            request = self.service.files().get_media(fileId=file_id)

        fh = io.FileIO(file_path, 'wb')
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        try:
            while done is False:
                status, done = downloader.next_chunk()
            return True, file_path
        except HttpError as e:
            return False, str(e)

    def batch_download(self, files_to_download, progress_callback=None):
        """Download multiple files with progress tracking.
        
        Args:
            files_to_download: List of dicts with file_id, file_name, mime_type, destination_folder, 
                             and optionally assignment and course_name
            progress_callback: Optional callback function(current, total) for progress updates
        
        Returns:
            List of tuples (success, file_path_or_error)
        """
        results = []
        total = len(files_to_download)
        
        for idx, file_info in enumerate(files_to_download):
            success, result = self.download_file(
                file_info['file_id'],
                file_info['file_name'],
                file_info['mime_type'],
                file_info['destination_folder'],
                file_info.get('assignment'),
                file_info.get('course_name')
            )
            results.append((success, result))
            
            if progress_callback:
                progress_callback(idx + 1, total)
        
        return results

    def open_file(self, file_path):
        """Opens a file with the default system application."""
        try:
            if platform.system() == 'Darwin':       # macOS
                subprocess.call(('open', file_path))
            elif platform.system() == 'Windows':    # Windows
                os.startfile(file_path)
            else:                                   # linux variants
                subprocess.call(('xdg-open', file_path))
            return True
        except Exception as e:
            print(f"Error opening file: {e}")
            return False

