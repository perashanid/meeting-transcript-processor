# Meeting Transcript Action Item Extractor

Automatically extract action items from meeting transcripts and create tasks in your project management tool.

## Features

- 🎯 **Smart Action Item Detection**: Identifies explicit and implied commitments
- 👤 **Owner Assignment**: Extracts responsible parties from conversation
- 📅 **Due Date Parsing**: Handles both absolute and relative dates (e.g., "by Friday")
- ⚡ **Priority Classification**: Categorizes tasks as High/Medium/Low based on urgency language
- 🔄 **Automation Ready**: Integrates with Make.com, Zapier, and custom webhooks
- 📧 **Automatic Notifications**: Sends summaries and reminders to team members

## Quick Start

### 1. Installation

```bash
pip install -r requirements.txt
```

### 2. Basic Usage

```python
from transcript_processor import process_transcript

transcript = """
John: Sarah, can you send the report by Friday?
Sarah: Yes, I'll send it by end of week.
Mike: I need to follow up with the client ASAP.
"""

result = process_transcript(transcript, "2026-07-27")
print(result)
```

**Output:**
```json
{
  "meeting_date": "2026-07-27",
  "action_items": [
    {
      "task_description": "Send the report",
      "owner": "Sarah",
      "due_date": "2026-07-31",
      "priority": "Medium",
      "context": "John requested Sarah to send the report by Friday."
    },
    {
      "task_description": "Follow up with the client",
      "owner": "Mike",
      "due_date": null,
      "priority": "High",
      "context": "Mike needs to follow up with the client ASAP."
    }
  ],
  "summary": "The meeting resulted in 2 action items. Tasks were assigned to Sarah, Mike. 1 high-priority tasks require immediate attention."
}
```

### 3. Run Webhook Server

```bash
python webhook_handler.py
```

The server will start on `http://localhost:5000`

### 4. Test the Webhook

```bash
curl -X POST http://localhost:5000/webhook/transcript \
  -H "Content-Type: application/json" \
  -d '{
    "transcript": "John: Sarah, please update the docs by tomorrow. Sarah: Will do!",
    "meeting_date": "2026-07-27",
    "meeting_id": "zoom_12345",
    "attendees": ["john@example.com", "sarah@example.com"]
  }'
```

## Automation Setup

### Option 1: Make.com (Recommended)

1. **Import the Blueprint**
   - Use `make_zapier_integration.json` as reference
   - Create a new scenario in Make.com

2. **Configure Modules**
   - **Trigger**: Zoom/Google Meet webhook → New recording
   - **HTTP Module**: POST transcript to your webhook endpoint
   - **Iterator**: Loop through `action_items` array
   - **Project Manager**: Create task in Asana/ClickUp/Trello
   - **Email Module**: Send summary to attendees
   - **Slack Module**: Send reminders before due dates

3. **Set Up Webhook**
   - Deploy `webhook_handler.py` to Heroku/AWS/DigitalOcean
   - Configure the public URL in Make.com

### Option 2: Zapier

1. **Create Multi-Step Zap** (requires paid plan)
   - Trigger: New transcript from Zoom/Fireflies/Otter.ai
   - Action: Webhook POST to your processor
   - Action: Loop through action items (use Looping by Zapier)
   - Action: Create tasks in project manager
   - Action: Send email summary
   - Action: Delay until 48 hours before due date
   - Action: Send Slack/email reminder

2. **Configure Assignee Mapping**
   - Create a lookup table (Google Sheets or Zapier Storage)
   - Map transcript names to user IDs in your task manager

### Option 3: Custom Integration

```python
import requests

# Process transcript
response = requests.post(
    'https://your-server.com/webhook/transcript',
    json={
        'transcript': transcript_text,
        'meeting_date': '2026-07-27',
        'meeting_id': 'meeting_123',
        'attendees': ['user1@example.com', 'user2@example.com']
    }
)

result = response.json()

# Create tasks in your project manager
for item in result['action_items']:
    create_task(
        title=item['task_description'],
        assignee=item['owner'],
        due_date=item['due_date'],
        priority=item['priority'],
        description=item['context']
    )
```

## Integration with Meeting Platforms

### Zoom
- Enable Cloud Recording
- Set up webhook for "Recording Completed" event
- Extract transcript from recording object

### Google Meet
- Use Google Drive API to detect new transcripts
- Parse .sbv or .vtt transcript files
- Trigger webhook on new file creation

### Fireflies.ai / Otter.ai
- Use their webhook integrations
- Configure to POST transcript data to your endpoint
- These services provide cleaned, formatted transcripts

## Configuration

### Supported Date Formats

- **Absolute**: `07/31/2026`, `2026-07-31`, `July 31`
- **Relative**: `tomorrow`, `by Friday`, `end of week`, `next Monday`, `in 3 days`

### Priority Keywords

- **High**: urgent, asap, critical, immediately, must, crucial
- **Low**: when you get a chance, eventually, nice to have, no rush
- **Medium**: Everything else (default)

### Action Patterns

The processor detects these patterns:
- "I will [action]"
- "[Name] should [action]"
- "Need to [action]"
- "Action item: [action]"
- "Responsible for [action]"
- "By [date] we need to [action]"

## Deployment

### Deploy to Heroku

```bash
# Create Heroku app
heroku create meeting-transcript-processor

# Deploy
git push heroku main

# Set environment variables
heroku config:set FLASK_ENV=production

# View logs
heroku logs --tail
```

### Deploy to AWS Lambda

1. Package the application:
```bash
pip install -r requirements.txt -t ./package
cd package
zip -r ../deployment.zip .
cd ..
zip -g deployment.zip *.py
```

2. Create Lambda function with API Gateway trigger
3. Upload `deployment.zip`
4. Set handler to `webhook_handler.app`

### Deploy to DigitalOcean

```bash
# Use App Platform
# Connect GitHub repo
# Auto-deploy on push
```

## Example Workflows

### Workflow 1: Zoom → Asana → Email
1. Zoom recording completes
2. Webhook triggers transcript processing
3. Action items extracted
4. Tasks created in Asana with proper assignees
5. Email summary sent to all attendees
6. Slack reminders sent 48h before due dates

### Workflow 2: Google Meet → Trello → Slack
1. Google Drive detects new transcript
2. Transcript sent to processor
3. Cards created in Trello board
4. Slack notification posted to team channel
5. DM reminders sent to card owners

## Advanced Customization

### Custom Action Patterns

Edit `transcript_processor.py` to add your own patterns:

```python
action_patterns = [
    r"(will|'ll)\s+(.+)",
    r"(your custom pattern here)",
]
```

### Custom Priority Rules

Modify the `_determine_priority` method:

```python
def _determine_priority(self, line: str, context_lines: List[str]) -> str:
    # Add your custom logic
    if 'revenue' in text or 'customer' in text:
        return "High"
    # ...
```

### Integration with LLM (Optional)

For better accuracy, integrate with OpenAI/Claude API:

```python
import openai

def extract_with_llm(transcript: str) -> List[Dict]:
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{
            "role": "system",
            "content": "Extract action items from this transcript..."
        }, {
            "role": "user",
            "content": transcript
        }]
    )
    return parse_llm_response(response)
```

## Testing

Run the sample processor:

```bash
python transcript_processor.py
```

Test with your own transcript:

```python
from transcript_processor import process_transcript

my_transcript = """
[Your transcript here]
"""

result = process_transcript(my_transcript, "2026-07-27")
print(result)
```

## Troubleshooting

### No action items detected
- Check if transcript contains action verbs (will, should, need to)
- Verify names are capitalized
- Ensure proper sentence structure

### Wrong owner assignment
- Names must be capitalized in transcript
- Add explicit assignment ("Sarah, you'll do X")
- Update assignee mapping in automation tool

### Date parsing issues
- Use standard date formats
- Be explicit: "by Friday July 31" instead of just "Friday"
- Check that meeting_date is correct

## License

MIT License - feel free to use and modify for your needs.

## Support

For issues and questions:
- Check the troubleshooting section
- Review example transcripts in code
- Customize patterns for your team's language

## Roadmap

- [ ] Multi-language support
- [ ] Speaker diarization improvement
- [ ] Integration with Microsoft Teams
- [ ] Mobile app for on-the-go processing
- [ ] AI-powered summary generation
- [ ] Custom field mapping for different PM tools
