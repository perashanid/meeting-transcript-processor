"""
Test script for the transcript processor
"""

from transcript_processor import process_transcript
import json


def test_with_example_transcript():
    """Test processor with the example transcript file."""
    
    # Read the example transcript
    with open('example_transcript.txt', 'r', encoding='utf-8') as f:
        transcript = f.read()
    
    # Process it
    print("Processing example transcript...")
    print("=" * 80)
    
    result = process_transcript(transcript, "2026-07-27")
    
    # Parse and display results
    data = json.loads(result)
    
    print(f"\n📅 Meeting Date: {data['meeting_date']}")
    print(f"\n📊 Summary:\n{data['summary']}")
    print(f"\n✅ Total Action Items: {len(data['action_items'])}\n")
    
    # Display each action item
    for i, item in enumerate(data['action_items'], 1):
        print(f"\n{'─' * 80}")
        print(f"Action Item #{i}")
        print(f"{'─' * 80}")
        print(f"📝 Task: {item['task_description']}")
        print(f"👤 Owner: {item['owner']}")
        print(f"📅 Due Date: {item['due_date'] if item['due_date'] else 'Not specified'}")
        print(f"⚡ Priority: {item['priority']}")
        print(f"💬 Context: {item['context']}")
    
    print("\n" + "=" * 80)
    print("\n✨ Full JSON Output:\n")
    print(json.dumps(data, indent=2))
    
    return data


def test_simple_cases():
    """Test with simple, specific cases."""
    
    test_cases = [
        {
            "name": "Explicit assignment with date",
            "transcript": "John: Sarah, please send the quarterly report by Friday.\nSarah: Sure, I'll get it done.",
            "date": "2026-07-27"
        },
        {
            "name": "Urgent task without date",
            "transcript": "Mike: I need to fix the critical bug ASAP.\nJohn: Yes, please prioritize that immediately.",
            "date": "2026-07-27"
        },
        {
            "name": "Unassigned task",
            "transcript": "John: Someone should update the documentation.\nSarah: Good idea, we need that.",
            "date": "2026-07-27"
        },
        {
            "name": "Multiple tasks in one sentence",
            "transcript": "John: Sarah will handle the frontend and Mike will handle the backend by next week.",
            "date": "2026-07-27"
        },
        {
            "name": "Relative date parsing",
            "transcript": "Lisa: I'll complete the design review by end of this week.\nJohn: And I'll schedule the client call by next Monday.",
            "date": "2026-07-27"
        }
    ]
    
    print("\n\n" + "=" * 80)
    print("TESTING SIMPLE CASES")
    print("=" * 80)
    
    for test in test_cases:
        print(f"\n\n📋 Test: {test['name']}")
        print("-" * 80)
        print(f"Transcript: {test['transcript'][:100]}...")
        
        result = process_transcript(test['transcript'], test['date'])
        data = json.loads(result)
        
        print(f"\nFound {len(data['action_items'])} action item(s):")
        for item in data['action_items']:
            print(f"  • {item['task_description']} (Owner: {item['owner']}, Due: {item['due_date']}, Priority: {item['priority']})")


if __name__ == "__main__":
    # Test with full example
    print("\n🚀 Testing with Example Transcript\n")
    test_with_example_transcript()
    
    # Test simple cases
    test_simple_cases()
    
    print("\n\n✅ All tests completed!")
