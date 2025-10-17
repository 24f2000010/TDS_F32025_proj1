"""
Utilities for handling attachments and data URIs
"""

import os
import base64
import logging
import mimetypes
from pathlib import Path

logger = logging.getLogger(__name__)

class AttachmentProcessor:
    def __init__(self, temp_dir):
        self.temp_dir = Path(temp_dir)
        self.temp_dir.mkdir(exist_ok=True)
    
    def process_attachments(self, attachments):
        """
        Process a list of attachments and save them to the temporary directory
        
        Args:
            attachments (list): List of attachment dictionaries with 'name' and 'url' keys
        
        Returns:
            list: List of processed file information
        """
        if not attachments:
            return []
        
        processed_files = []
        
        for attachment in attachments:
            try:
                file_info = self._process_single_attachment(attachment)
                if file_info:
                    processed_files.append(file_info)
            except Exception as e:
                logger.error(f"Error processing attachment {attachment.get('name', 'unknown')}: {str(e)}")
        
        return processed_files
    
    def _process_single_attachment(self, attachment):
        """
        Process a single attachment
        
        Args:
            attachment (dict): Attachment dictionary with 'name' and 'url' keys
        
        Returns:
            dict: Processed file information or None if failed
        """
        name = attachment.get('name', 'unknown')
        url = attachment.get('url', '')
        
        if not url.startswith('data:'):
            logger.warning(f"Attachment {name} is not a data URI, skipping")
            return None
        
        try:
            # Parse data URI
            header, data = url.split(',', 1)
            
            # Extract MIME type and encoding
            mime_type = header.split(';')[0].split(':')[1]
            encoding = 'base64'  # Default encoding
            
            if ';' in header:
                encoding_part = header.split(';')[1].strip()
                if encoding_part.startswith('base64'):
                    encoding = 'base64'
            
            # Decode the data
            if encoding == 'base64':
                file_data = base64.b64decode(data)
            else:
                # For other encodings, treat as plain text
                file_data = data.encode('utf-8')
            
            # Determine file extension from MIME type
            extension = self._get_extension_from_mime_type(mime_type)
            if extension and not name.endswith(extension):
                name = f"{name}.{extension}"
            
            # Save file
            file_path = self.temp_dir / name
            with open(file_path, 'wb') as f:
                f.write(file_data)
            
            logger.info(f"Processed attachment: {name} ({len(file_data)} bytes)")
            
            return {
                'name': name,
                'path': str(file_path),
                'mime_type': mime_type,
                'size': len(file_data),
                'original_url': url
            }
            
        except Exception as e:
            logger.error(f"Error processing attachment {name}: {str(e)}")
            return None
    
    def _get_extension_from_mime_type(self, mime_type):
        """Get file extension from MIME type"""
        mime_to_ext = {
            'image/png': 'png',
            'image/jpeg': 'jpg',
            'image/gif': 'gif',
            'image/svg+xml': 'svg',
            'text/plain': 'txt',
            'text/csv': 'csv',
            'application/json': 'json',
            'application/pdf': 'pdf',
            'text/markdown': 'md',
            'text/html': 'html',
            'application/javascript': 'js',
            'text/css': 'css'
        }
        
        return mime_to_ext.get(mime_type, None)
    
    def create_data_uri(self, file_path, mime_type=None):
        """
        Create a data URI from a file
        
        Args:
            file_path (str): Path to the file
            mime_type (str): MIME type (auto-detected if not provided)
        
        Returns:
            str: Data URI or None if failed
        """
        try:
            file_path = Path(file_path)
            
            if not file_path.exists():
                logger.error(f"File not found: {file_path}")
                return None
            
            # Detect MIME type if not provided
            if not mime_type:
                mime_type, _ = mimetypes.guess_type(str(file_path))
                if not mime_type:
                    mime_type = 'application/octet-stream'
            
            # Read file data
            with open(file_path, 'rb') as f:
                file_data = f.read()
            
            # Encode as base64
            encoded_data = base64.b64encode(file_data).decode('utf-8')
            
            # Create data URI
            data_uri = f"data:{mime_type};base64,{encoded_data}"
            
            logger.info(f"Created data URI for {file_path} ({len(file_data)} bytes)")
            return data_uri
            
        except Exception as e:
            logger.error(f"Error creating data URI for {file_path}: {str(e)}")
            return None
    
    def cleanup(self):
        """Clean up temporary files"""
        try:
            if self.temp_dir.exists():
                import shutil
                shutil.rmtree(self.temp_dir)
                logger.info("Cleaned up temporary files")
        except Exception as e:
            logger.warning(f"Error cleaning up temporary files: {str(e)}")
    
    def get_file_info(self, file_path):
        """Get information about a file"""
        try:
            file_path = Path(file_path)
            if not file_path.exists():
                return None
            
            stat = file_path.stat()
            mime_type, _ = mimetypes.guess_type(str(file_path))
            
            return {
                'name': file_path.name,
                'path': str(file_path),
                'size': stat.st_size,
                'mime_type': mime_type or 'application/octet-stream',
                'modified': stat.st_mtime
            }
        except Exception as e:
            logger.error(f"Error getting file info for {file_path}: {str(e)}")
            return None
