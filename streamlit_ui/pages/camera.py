import streamlit as st
import io
from PIL import Image
import os
from datetime import datetime
import sys

# Add the app directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from api_client import api_client

# Create temp directory if it doesn't exist
temp_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data/reciepts')
os.makedirs(temp_dir, exist_ok=True)

# Header with back button
col1, col2 = st.columns([6, 1])
if st.button("← Back to Dashboard", 
             use_container_width=True):
    st.switch_page("main.py")

picture = st.camera_input("Take a photo of your receipt")

if picture:    
    if st.button("✅ Use This Photo", type="primary", use_container_width=True):
        # Convert the image to bytes
        image_bytes = picture.getvalue()
        
        # Convert to PIL Image
        image = Image.open(io.BytesIO(image_bytes))
        
        # Generate unique filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"receipt_{timestamp}.jpg"
        filepath = os.path.join(temp_dir, filename)
        
        # Save the image to temp directory
        image.save(filepath, format='JPEG')
        
        try:
            # Upload to API
            response = api_client.upload_receipt(filepath)
            if response.get('error'):
                st.error(f"Upload failed: {response['error']}")
            else:
                st.success("Receipt uploaded successfully!")
                st.write(f"Document ID: {response.get('document_id')}")
        except Exception as e:
            st.error(f"Error: {str(e)}")
            st.write(f"Image saved locally at: {filepath}")
        
        st.switch_page("main.py") 