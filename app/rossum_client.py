import requests
import os
from dotenv import load_dotenv 

load_dotenv()

ROSSUM_URL = os.getenv("ROSSUM_URL")
ROSSUM_USERNAME = os.getenv("ROSSUM_USERNAME")
ROSSUM_PASSWORD = os.getenv("ROSSUM_PASSWORD")
QUEUE_ID = os.getenv("QUEUE_ID")

def authenticate():
    """
    Authenticate with Rossum API using username and password
    """
    response = requests.post(
        f"{ROSSUM_URL}/api/v1/auth/login",
        json={"username": ROSSUM_USERNAME, "password": ROSSUM_PASSWORD}
    )
    response.raise_for_status()
    return response.json()["key"]


def upload_document(file_path):
    """
    Upload a document to Rossum queue.
    
    Args:
        file_path (str): Path to the document file to upload
        
    Returns:
        dict: Response from Rossum API containing document details
    """
    # Get authentication token
    token = authenticate()
    
    # Prepare headers with authentication
    headers = {
        "Authorization": f"Token {token}",
        "Content-Type": "application/octet-stream"
    }
    
    # Prepare the file for upload
    with open(file_path, 'rb') as file:
        file_data = file.read()
        # Upload to Rossum
        response = requests.post(
            f"{ROSSUM_URL}/api/v1/uploads/{os.path.basename(file_path)}?queue={QUEUE_ID}",
            headers=headers,
            data=file_data
        )
        
        response.raise_for_status()
        return response.json() 
    

def export_annotations():
    """
    Export all annotations of queue
        
    Returns:
        dict: Response from Rossum API containing document details
    """
    # Get authentication token
    token = authenticate()
    
    # Prepare headers with authentication
    headers = {
        "Authorization": f"Token {token}",
        "Content-Type": "application/octet-stream"
    }
    
    # export annotations from Rossum
    response = requests.get(
        f"{ROSSUM_URL}/api/v1/queues/{QUEUE_ID}/export?format=json&status=exported",
        headers=headers,
    )
    
    response.raise_for_status()
    return response.json() 
