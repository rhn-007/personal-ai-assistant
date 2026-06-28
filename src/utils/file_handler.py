"""
File Handling Utilities
"""

import os
import mimetypes
from pathlib import Path
from typing import Optional, List
from utils.logger import setup_logger

logger = setup_logger(__name__)


class FileHandler:
    """Handle file operations for the assistant"""
    
    ALLOWED_EXTENSIONS = {
        'txt', 'pdf', 'md', 'json', 'yaml', 'yml',
        'csv', 'xlsx', 'xls', 'doc', 'docx'
    }
    
    MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
    
    @staticmethod
    def read_file(file_path: str) -> Optional[str]:
        """
        Read file contents
        
        Args:
            file_path: Path to file
            
        Returns:
            File contents or None if error
        """
        try:
            if not os.path.exists(file_path):
                logger.error(f"File not found: {file_path}")
                return None
            
            if not FileHandler.is_allowed(file_path):
                logger.error(f"File type not allowed: {file_path}")
                return None
            
            if os.path.getsize(file_path) > FileHandler.MAX_FILE_SIZE:
                logger.error(f"File too large: {file_path}")
                return None
            
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        
        except Exception as e:
            logger.error(f"Error reading file {file_path}: {e}")
            return None
    
    @staticmethod
    def write_file(file_path: str, content: str) -> bool:
        """
        Write content to file
        
        Args:
            file_path: Path to file
            content: Content to write
            
        Returns:
            True if successful, False otherwise
        """
        try:
            Path(file_path).parent.mkdir(parents=True, exist_ok=True)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logger.info(f"File written: {file_path}")
            return True
        
        except Exception as e:
            logger.error(f"Error writing file {file_path}: {e}")
            return False
    
    @staticmethod
    def is_allowed(file_path: str) -> bool:
        """Check if file type is allowed"""
        ext = Path(file_path).suffix.lower().lstrip('.')
        return ext in FileHandler.ALLOWED_EXTENSIONS
    
    @staticmethod
    def get_file_info(file_path: str) -> dict:
        """Get information about a file"""
        try:
            path = Path(file_path)
            return {
                'name': path.name,
                'size': path.stat().st_size,
                'extension': path.suffix,
                'mime_type': mimetypes.guess_type(file_path)[0]
            }
        except Exception as e:
            logger.error(f"Error getting file info: {e}")
            return {}
    
    @staticmethod
    def list_files(directory: str, extension: Optional[str] = None) -> List[str]:
        """
        List files in directory
        
        Args:
            directory: Directory path
            extension: Optional file extension filter (e.g., 'txt')
            
        Returns:
            List of file paths
        """
        try:
            path = Path(directory)
            
            if not path.exists():
                return []
            
            if extension:
                pattern = f"*.{extension}"
            else:
                pattern = "*"
            
            return [str(f) for f in path.glob(pattern) if f.is_file()]
        
        except Exception as e:
            logger.error(f"Error listing files: {e}")
            return []
