import os
from flask import Flask, request, jsonify
from drive_utils import create_org_structure

app = Flask(__name__)

@app.route('/', methods=['POST'])
def create_drive_folders():
    """
    Cloud Run entry point.
    Expects JSON: {"organizationName": "Example Corp"}
    Environment Variable: GOOGLE_SHARED_DRIVE_ID
    """
    target_drive_id = os.environ.get('GOOGLE_SHARED_DRIVE_ID')
    if not target_drive_id:
        return jsonify({"error": "GOOGLE_SHARED_DRIVE_ID environment variable is not set"}), 500

    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid JSON payload"}), 400

    org_name = data.get('organizationName')
    if not org_name:
        return jsonify({"error": "Missing 'organizationName' in payload"}), 400

    try:
        result = create_org_structure(org_name, target_drive_id)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    # Cloud Run sets PORT environment variable
    port = int(os.environ.get('PORT', 8080))
    app.run(debug=True, host='0.0.0.0', port=port)
