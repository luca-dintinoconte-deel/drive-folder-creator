import os
import json
from drive_utils import create_org_structure

def lambda_handler(event, context):
    """
    AWS Lambda entry point.
    Expects event with 'organizationName'.
    Environment Variable: GOOGLE_SHARED_DRIVE_ID
    """
    target_drive_id = os.environ.get('GOOGLE_SHARED_DRIVE_ID')
    if not target_drive_id:
        return {
            'statusCode': 500,
            'body': json.dumps({"error": "GOOGLE_SHARED_DRIVE_ID environment variable is not set"})
        }

    # Handle different event structures (API Gateway vs direct invocation)
    if 'body' in event:
        try:
            body = json.loads(event['body'])
        except:
            body = event['body']
    else:
        body = event

    org_name = body.get('organizationName')
    if not org_name:
        return {
            'statusCode': 400,
            'body': json.dumps({"error": "Missing 'organizationName' in payload"})
        }

    try:
        result = create_org_structure(org_name, target_drive_id)
        return {
            'statusCode': 200,
            'body': json.dumps(result)
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({"error": str(e)})
        }
