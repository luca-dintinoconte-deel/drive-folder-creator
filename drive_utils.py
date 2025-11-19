import os
import logging
import base64
import json
from googleapiclient.discovery import build
from google.oauth2 import service_account
import google.auth

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SCOPES = ['https://www.googleapis.com/auth/drive']

def get_drive_service():
    """Authenticates and returns the Google Drive service."""
    try:
        # Check for base64 encoded service account JSON
        service_account_json_b64 = os.environ.get('GOOGLE_SERVICE_ACCOUNT_JSON')
        if not service_account_json_b64:
            raise ValueError("GOOGLE_SERVICE_ACCOUNT_JSON environment variable is not set")

        try:
            decoded_json = base64.b64decode(service_account_json_b64)
            service_account_info = json.loads(decoded_json)
            creds = service_account.Credentials.from_service_account_info(
                service_account_info, scopes=SCOPES
            )
            return build('drive', 'v3', credentials=creds)
        except Exception as e:
            logger.error(f"Failed to load credentials from GOOGLE_SERVICE_ACCOUNT_JSON: {e}")
            raise

    except Exception as e:
        logger.error(f"Failed to authenticate: {e}")
        raise

def create_folder(service, name, parent_id=None):
    """Creates a folder in Google Drive."""
    file_metadata = {
        'name': name,
        'mimeType': 'application/vnd.google-apps.folder'
    }
    if parent_id:
        file_metadata['parents'] = [parent_id]

    try:
        file = service.files().create(
            body=file_metadata,
            fields='id, webViewLink',
            supportsAllDrives=True
        ).execute()
        logger.info(f"Created folder '{name}' with ID: {file.get('id')}")
        return file
    except Exception as e:
        logger.error(f"Failed to create folder '{name}': {e}")
        raise

def create_org_structure(org_name, parent_drive_id):
    """
    Creates the organization folder structure in the specified Shared Drive.
    
    Args:
        org_name (str): The name of the organization.
        parent_drive_id (str): The ID of the Google Shared Drive (or parent folder).
        
    Returns:
        dict: A dictionary containing the ID and URL of the top-level folder.
    """
    service = get_drive_service()

    # 1. Create top-level Organization folder
    logger.info(f"Creating top-level folder for organization: {org_name}")
    org_folder = create_folder(service, org_name, parent_drive_id)
    org_folder_id = org_folder.get('id')
    org_folder_url = org_folder.get('webViewLink')

    # 2. Create nested folders
    subfolders = [
        "Sales/Pre-sales",
        "Onboarding",
        "Post Onboarding",
        "Legal Notices"
    ]

    for folder_name in subfolders:
        create_folder(service, folder_name, org_folder_id)

    return {
        "id": org_folder_id,
        "url": org_folder_url
    }
