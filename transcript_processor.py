"""
Meeting Transcript Processor
Extracts action items from meeting transcripts and outputs structured JSON
"""

import json
import re
from datetime import datetime, timedelta
from typing import List, Dict, Optional


class TranscriptProcessor:
    def __init__(self, transcript: str, meeting_date: str):
        """
        Initialize the processor with transcript text and meeting date.
        
        Args:
            transcript: Raw meeting transcript text
            meeting_date: Meeting date in YYYY-MM-DD format
        """
        self.transcript = transcript
        self.meeting_date = datetime.strptime(meeting_date, "%Y-%m-%d")
        self.action_items = []
        
    def process(self) -> Dict:
        """
        Main processing method that extracts action items and generates output.
        
        Returns:
            Dictionary with meeting_date, action_items, and summary
        """
        self._extract_action_items()
        summary = self._generate_summary()
        
        return {
            "meeting_date": self.meeting_date.strftime("%Y-%m-%d"),
            "action_items": self.action_items,
            "summary": summary
        }
    
    def _extract_action_items(self):
        """Extract action items from transcript using pattern matching."""
        lines = self.transcript.split('\n')
        
        # Action verb patterns
        action_patterns = [
            r"(will|'ll)\s+(.+)",
            r"(should|must|need to)\s+(.+)",
            r"(going to|gonna)\s+(.+)",
            r"(action item|task|todo|to-do):\s*(.+)",
            r"(responsible for|in charge of|owning)\s+(.+)",
            r"(by\s+\w+day|by\s+\w+|deadline|due)\s+(.+)",
        ]
        
        for i, line in enumerate(lines):
            line_lower = line.lower()
            
            # Skip greetings and small talk
            if any(phrase in line_lower for phrase in ['hello', 'hi everyone', 'good morning', 'thanks for joining', 'bye', 'see you']):
                continue
            
            # Check for action patterns
            for pattern in action_patterns:
                if re.search(pattern, line_lower):
                    action_item = self._parse_action_item(line, lines[max(0, i-1):min(len(lines), i+3)])
                    if action_item and action_item not in self.action_items:
                        self.action_items.append(action_item)
                    break
    
    def _parse_action_item(self, line: str, context_lines: List[str]) -> Optional[Dict]:
        """
        Parse a single action item from a line and its context.
        
        Args:
            line: The line containing the action item
            context_lines: Surrounding lines for context
            
        Returns:
            Dictionary with task details or None
        """
        # Extract owner
        owner = self._extract_owner(line, context_lines)
        
        # Extract due date
        due_date = self._extract_due_date(line, context_lines)
        
        # Determine priority
        priority = self._determine_priority(line, context_lines)
        
        # Extract task description
        task_description = self._extract_task_description(line)
        
        # Extract context
        context = self._extract_context(context_lines)
        
        if not task_description:
            return None
        
        return {
            "task_description": task_description,
            "owner": owner,
            "due_date": due_date,
            "priority": priority,
            "context": context
        }
    
    def _extract_owner(self, line: str, context_lines: List[str]) -> str:
        """Extract the person responsible for the task."""
        # Common name patterns
        text = " ".join(context_lines)
        
        # Look for explicit assignment patterns
        assignment_patterns = [
            r"([A-Z][a-z]+),?\s+(will|'ll|should|can|please)",
            r"([A-Z][a-z]+),?\s+you('re| are)?\s+(responsible|take|in charge)",
            r"(assign|assigned to|owner:?)\s+([A-Z][a-z]+)",
            r"([A-Z][a-z]+),?\s+can you",
            r"([A-Z][a-z]+):\s+.*(I'll|I will|I can|I should)",
        ]
        
        for pattern in assignment_patterns:
            match = re.search(pattern, text)
            if match:
                # Extract the name from the match groups
                for group in match.groups():
                    if group and len(group) > 2 and group[0].isupper() and group.lower() not in ['will', 'can', 'should', 'please', 'owner', 'assign', 'assigned']:
                        return group
        
        return "UNASSIGNED"
    
    def _extract_due_date(self, line: str, context_lines: List[str]) -> Optional[str]:
        """Extract and calculate due date from relative or absolute references."""
        text = " ".join(context_lines).lower()
        
        # Absolute dates
        date_patterns = [
            r"(\d{1,2}/\d{1,2}/\d{2,4})",
            r"(\d{4}-\d{2}-\d{2})",
            r"(january|february|march|april|may|june|july|august|september|october|november|december)\s+(\d{1,2})",
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, text)
            if match:
                try:
                    date_str = match.group(0)
                    # Try multiple date formats
                    for fmt in ["%m/%d/%Y", "%Y-%m-%d", "%B %d"]:
                        try:
                            parsed_date = datetime.strptime(date_str, fmt)
                            if fmt == "%B %d":
                                parsed_date = parsed_date.replace(year=self.meeting_date.year)
                            return parsed_date.strftime("%Y-%m-%d")
                        except ValueError:
                            continue
                except Exception:
                    pass
        
        # Relative dates
        relative_patterns = {
            r"by (tomorrow|tmrw)": 1,
            r"by (monday|mon)": self._days_until_weekday(0),
            r"by (tuesday|tue)": self._days_until_weekday(1),
            r"by (wednesday|wed)": self._days_until_weekday(2),
            r"by (thursday|thu)": self._days_until_weekday(3),
            r"by (friday|fri)": self._days_until_weekday(4),
            r"by end of (week|this week)": self._days_until_weekday(4),
            r"by next week": 7,
            r"in (\d+) days?": None,  # Special handling
            r"by end of month": None,  # Special handling
        }
        
        for pattern, days_offset in relative_patterns.items():
            match = re.search(pattern, text)
            if match:
                if r"in (\d+) days?" in pattern:
                    days_offset = int(match.group(1))
                elif "end of month" in pattern:
                    # Calculate last day of current month
                    next_month = self.meeting_date.replace(day=28) + timedelta(days=4)
                    last_day = next_month - timedelta(days=next_month.day)
                    return last_day.strftime("%Y-%m-%d")
                
                if days_offset is not None:
                    due_date = self.meeting_date + timedelta(days=days_offset)
                    return due_date.strftime("%Y-%m-%d")
        
        return None
    
    def _days_until_weekday(self, target_weekday: int) -> int:
        """Calculate days until a specific weekday from meeting date."""
        current_weekday = self.meeting_date.weekday()
        days_ahead = target_weekday - current_weekday
        if days_ahead <= 0:  # Target day already happened this week
            days_ahead += 7
        return days_ahead
    
    def _determine_priority(self, line: str, context_lines: List[str]) -> str:
        """Determine priority based on urgency language."""
        text = " ".join(context_lines).lower()
        
        # High priority indicators
        high_priority_keywords = [
            'urgent', 'asap', 'critical', 'immediately', 'high priority',
            'must', 'crucial', 'emergency', 'today', 'now'
        ]
        
        # Low priority indicators
        low_priority_keywords = [
            'when you get a chance', 'eventually', 'low priority',
            'nice to have', 'if possible', 'no rush'
        ]
        
        if any(keyword in text for keyword in high_priority_keywords):
            return "High"
        elif any(keyword in text for keyword in low_priority_keywords):
            return "Low"
        else:
            return "Medium"
    
    def _extract_task_description(self, line: str) -> str:
        """Extract concise task description from line."""
        # Remove speaker labels (e.g., "John: ")
        line = re.sub(r'^[A-Z][a-z]+:\s*', '', line)
        
        # Remove filler words
        line = re.sub(r'\b(um|uh|like|you know|basically)\b', '', line, flags=re.IGNORECASE)
        
        # Clean up whitespace
        line = ' '.join(line.split())
        
        # Extract the core action
        action_match = re.search(r"(will|'ll|should|need to|going to)\s+(.+?)(?:\.|,|and|$)", line, re.IGNORECASE)
        if action_match:
            task = action_match.group(2).strip()
        else:
            task = line.strip()
        
        # Limit to 15 words
        words = task.split()
        if len(words) > 15:
            task = ' '.join(words[:15])
        
        return task.capitalize() if task else ""
    
    def _extract_context(self, context_lines: List[str]) -> str:
        """Extract one-sentence context for why the task exists."""
        text = ' '.join(context_lines)
        
        # Look for explanation patterns
        context_patterns = [
            r"(because|since|as|so that)\s+(.+?)(?:\.|$)",
            r"(to|in order to)\s+(.+?)(?:\.|$)",
            r"(this will|this is)\s+(.+?)(?:\.|$)",
        ]
        
        for pattern in context_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                context = match.group(0).strip()
                # Limit to one sentence
                if '.' in context:
                    context = context.split('.')[0] + '.'
                return context
        
        # Fallback: use first complete sentence
        sentences = re.split(r'[.!?]', text)
        if sentences:
            return sentences[0].strip() + '.'
        
        return "Action item from meeting discussion."
    
    def _generate_summary(self) -> str:
        """Generate 3-4 sentence summary of the meeting."""
        # This is a simplified version - in production, you might use
        # more sophisticated NLP or AI summarization
        
        num_items = len(self.action_items)
        owners = set(item['owner'] for item in self.action_items if item['owner'] != 'UNASSIGNED')
        
        summary_parts = []
        summary_parts.append(f"The meeting resulted in {num_items} action items.")
        
        if owners:
            summary_parts.append(f"Tasks were assigned to {', '.join(owners)}.")
        
        high_priority = sum(1 for item in self.action_items if item['priority'] == 'High')
        if high_priority > 0:
            summary_parts.append(f"{high_priority} high-priority tasks require immediate attention.")
        
        with_deadlines = sum(1 for item in self.action_items if item['due_date'])
        if with_deadlines > 0:
            summary_parts.append(f"{with_deadlines} tasks have specific deadlines.")
        
        return ' '.join(summary_parts[:4])


def process_transcript(transcript: str, meeting_date: str) -> str:
    """
    Main function to process transcript and return JSON output.
    
    Args:
        transcript: Raw meeting transcript text
        meeting_date: Meeting date in YYYY-MM-DD format
        
    Returns:
        JSON string with structured action items
    """
    processor = TranscriptProcessor(transcript, meeting_date)
    result = processor.process()
    return json.dumps(result, indent=2)


if __name__ == "__main__":
    # Example usage
    sample_transcript = """
    John: Hi everyone, thanks for joining today's product meeting.
    
    Sarah: We need to finalize the Q4 roadmap by Friday.
    
    John: Agreed. Sarah, can you take the lead on that?
    
    Sarah: Yes, I'll send the draft by end of week.
    
    Mike: I should follow up with the client about the API integration. It's urgent.
    
    John: Good idea. Mike, can you do that by tomorrow?
    
    Mike: Sure, I'll reach out today.
    
    Sarah: Someone should also update the documentation.
    
    John: Let's assign that next meeting. For now, let's focus on the roadmap and client follow-up.
    
    Everyone: Sounds good. Thanks!
    """
    
    result = process_transcript(sample_transcript, "2026-07-27")
    print(result)
