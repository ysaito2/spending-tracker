import requests
import os
from typing import Optional, Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get environment variables with defaults
FASTAPI_URL = os.getenv("FASTAPI_URL", "http://localhost:8000")
ROSSUM_URL = os.getenv("ROSSUM_URL")
ROSSUM_USERNAME = os.getenv("ROSSUM_USERNAME")
ROSSUM_PASSWORD = os.getenv("ROSSUM_PASSWORD")
QUEUE_ID = os.getenv("QUEUE_ID")

# Validate required environment variables
if not all([ROSSUM_URL, ROSSUM_USERNAME, ROSSUM_PASSWORD, QUEUE_ID]):
    raise ValueError("Missing required environment variables. Please check your .env file.")

class APIClient:
    def __init__(self):
        self.base_url = FASTAPI_URL
        self._token: Optional[str] = None

    def _get_headers(self) -> Dict[str, str]:
        """Get headers for API requests"""
        headers = {'Content-Type': 'application/json'}
        if self._token:
            headers['Authorization'] = f'Bearer {self._token}'
        return headers

    def authenticate(self) -> bool:
        """Get authentication token from the API"""
        try:
            response = requests.post(f"{self.base_url}/auth")
            response.raise_for_status()
            data = response.json()
            self._token = data.get('token')
            return bool(self._token)
        except Exception as e:
            print(f"Authentication failed: {str(e)}")
            return False

    def upload_receipt(self, file_path: str) -> Dict[str, Any]:
        """Upload a receipt image to the API"""
        try:
            with open(file_path, 'rb') as file:
                files = {'file': (os.path.basename(file_path), file, 'image/jpeg')}
                response = requests.post(
                    f"{self.base_url}/upload",
                    files=files
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            print(f"Upload failed: {str(e)}")
            return {'message': 'Upload failed', 'error': str(e)}
    
    def export_annotations(self) -> Dict[str, Any]:
        """Upload a receipt image to the API"""
        try:
            response = requests.get(
                f"{self.base_url}/export",
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Export failed: {str(e)}")
            return {'message': 'Export failed', 'error': str(e)}

# Create a singleton instance
api_client = APIClient() 