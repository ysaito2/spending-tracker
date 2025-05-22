from fastapi import FastAPI, HTTPException, UploadFile, File
import uvicorn
import os
import logging
from logging.handlers import RotatingFileHandler
from dotenv import load_dotenv
from model import UploadResponse, AuthResponse
from rossum_client import authenticate, upload_document, export_annotations

# Load environment variables
load_dotenv()

# Validate required environment variables
required_vars = ["ROSSUM_URL", "ROSSUM_USERNAME", "ROSSUM_PASSWORD", "QUEUE_ID"]
missing_vars = [var for var in required_vars if not os.getenv(var)]
if missing_vars:
    raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")

# Create logs directory if it doesn't exist
log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)

# Configure logging
log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
formatter = logging.Formatter(log_format)

# File handler (with rotation)
log_file = os.path.join(log_dir, 'api.log')
file_handler = RotatingFileHandler(
    log_file,
    maxBytes=10*1024*1024,  # 10MB
    backupCount=5
)
file_handler.setFormatter(formatter)
file_handler.setLevel(logging.DEBUG)

# Console handler
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
console_handler.setLevel(logging.DEBUG)

# Configure root logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(file_handler)
logger.addHandler(console_handler)

app = FastAPI()

@app.get("/")
def root():
    logger.debug("Root endpoint accessed")
    return {"message": "Receipt Processing API"}

@app.post("/auth", response_model=AuthResponse)
def get_auth_token():
    """
    Get authentication token for Rossum API
    """
    logger.debug("Authentication request received")
    try:
        token = authenticate()
        logger.debug("Authentication successful")
        return AuthResponse(token=token)
    except Exception as e:
        logger.error(f"Authentication failed: {str(e)}")
        return AuthResponse(token="", error=str(e))

@app.post("/upload", response_model=UploadResponse)
def upload_receipt(file: UploadFile = File(...)):
    """
    Upload a receipt image to Rossum
    """
    logger.debug(f"Upload request received for file: {file.filename}")
    try:
        # Create temp directory if it doesn't exist
        temp_dir = "data/receipts"
        os.makedirs(temp_dir, exist_ok=True)
        logger.debug(f"Using temp directory: {temp_dir}")

        # Save the uploaded file temporarily
        file_path = os.path.join(temp_dir, file.filename)
        logger.debug(f"Saving file to: {file_path}")
        with open(file_path, "wb") as buffer:
            content = file.file.read()
            buffer.write(content)
        logger.debug("File saved successfully")

        # Upload to Rossum
        logger.debug("Uploading to Rossum...")
        response = upload_document(file_path)
        logger.debug(f"Rossum upload response: {response}")
        
        # Clean up the temporary file
        os.remove(file_path)
        logger.debug("Temporary file cleaned up")

        return UploadResponse(
            message="Receipt uploaded successfully",
            document_id=response.get("id")
        )
    except Exception as e:
        logger.error(f"Upload failed: {str(e)}")
        # Clean up the temporary file if it exists
        if os.path.exists(file_path):
            logger.debug("Cleaning up temporary file after error")
            os.remove(file_path)
        return UploadResponse(
            message="Failed to upload receipt",
            error=str(e)
        )

@app.get("/export")
def get_annotations():
    """
    Export annotations from Rossum
    """
    logger.debug("Export request received") 
    try: 
        payload = export_annotations()
        logger.debug("Exported successfully")
        return payload
    except Exception as e:
        logger.error(f"Export failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    logger.info(f"Starting FastAPI server on {os.getenv('FASTAPI_HOST', '0.0.0.0')}:{os.getenv('FASTAPI_PORT', '8000')}")
    uvicorn.run("app.api:app", 
                host=os.getenv('FASTAPI_HOST', '0.0.0.0'), 
                port=int(os.getenv('FASTAPI_PORT', '8000')), 
                reload=True)
