"""
Webhook Handler for Meeting Transcript Automation
Receives transcripts from Zoom/Google Meet/Fireflies and processes them
"""

from flask import Flask, request, jsonify
from transcript_processor import process_transcript
import json
from datetime import datetime

app = Flask(__name__)


@app.route('/webhook/transcript', methods=['POST'])
def handle_transcript_webhook():
    """
    Webhook endpoint to receive meeting transcripts.
    
    Expected JSON payload:
    {
        "transcript": "meeting transcript text",
        "meeting_date": "YYYY-MM-DD" (optional, defaults to today),
        "meeting_id": "unique_meeting_id",
        "attendees": ["email1@example.com", "email2@example.com"]
    }
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data or 'transcript' not in data:
            return jsonify({
                "error": "Missing required field: transcript"
            }), 400
        
        transcript = data['transcript']
        meeting_date = data.get('meeting_date', datetime.now().strftime("%Y-%m-%d"))
        meeting_id = data.get('meeting_id', 'unknown')
        attendees = data.get('attendees', [])
        
        # Process transcript
        result_json = process_transcript(transcript, meeting_date)
        result = json.loads(result_json)
        
        # Add metadata
        result['meeting_id'] = meeting_id
        result['attendees'] = attendees
        result['processed_at'] = datetime.now().isoformat()
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({
            "error": f"Processing failed: {str(e)}"
        }), 500


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({"status": "healthy"}), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
