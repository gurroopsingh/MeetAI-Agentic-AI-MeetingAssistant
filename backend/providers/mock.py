"""
Mock Provider Implementations
These return realistic fake data for local development.
Replace with Azure providers when ready:
  - MockSpeechProvider → AzureSpeechProvider
  - MockLanguageProvider → AzureLanguageProvider
  - MockGenAIProvider → MicrosoftFoundryProvider
"""
import asyncio
import random
import os
import subprocess
import hashlib
from typing import List, Dict, Optional
from providers.base import SpeechProvider, LanguageProvider, GenAIProvider, MeetingAnalysisProvider


MOCK_SPEAKERS = [
    {"name": "Sarah Chen", "role": "Product Manager", "avatar_color": "#6366f1"},
    {"name": "Marcus Johnson", "role": "Tech Lead", "avatar_color": "#8b5cf6"},
    {"name": "Priya Patel", "role": "UX Designer", "avatar_color": "#ec4899"},
    {"name": "Tom Williams", "role": "Backend Engineer", "avatar_color": "#10b981"},
    {"name": "Dr. Ahmed Hassan", "role": "AI Researcher", "avatar_color": "#f59e0b"},
]


class MockSpeechProvider(SpeechProvider):
    """Mock speech provider — simulates Azure AI Speech."""

    async def extract_audio(self, video_path: str) -> str:
        audio_path = video_path.rsplit(".", 1)[0] + ".wav"
        try:
            def run_ffmpeg():
                return subprocess.run(
                    ['ffmpeg', '-i', video_path, '-q:a', '0', '-map', 'a', audio_path, '-y'],
                    capture_output=True, text=True
                )
            process = await asyncio.to_thread(run_ffmpeg)
            if process.returncode != 0:
                print(f"FFmpeg failed with code {process.returncode}, returning original path")
                return video_path
            return audio_path
        except FileNotFoundError:
            print("FFmpeg not found. Skipping audio extraction (mock mode).")
            return video_path

    async def transcribe(self, audio_path: str) -> List[Dict]:
        await asyncio.sleep(1.0)
        size_bytes = os.path.getsize(audio_path) if os.path.exists(audio_path) else 1000000
        # Approximate 1MB to 10 seconds for mock purposes, max 1 hour
        duration = min(max(size_bytes / 100000, 10.0), 3600.0)
        
        seed_val = int(hashlib.md5(audio_path.encode()).hexdigest(), 16) % (2**32)
        random.seed(seed_val)
        
        topics = ["API architecture", "database migration", "UX redesign", "marketing launch", "server costs", "customer feedback", "security audit"]
        chosen_topic = random.choice(topics)
        
        segments = []
        current_time = 0.0
        
        while current_time < duration:
            speaker = random.choice(MOCK_SPEAKERS)["name"]
            length = random.uniform(3.0, 15.0)
            end_time = min(current_time + length, duration)
            text = f"We really need to focus on the {chosen_topic} during this sprint. Let's look at the file {os.path.basename(audio_path)}. We should definitely proceed with option {random.randint(1, 5)}."
            if current_time == 0.0:
                text = f"Welcome everyone. Today we are discussing {chosen_topic}."
            
            segments.append({
                "speaker": speaker,
                "text": text,
                "start_time": current_time,
                "end_time": end_time,
                "confidence": random.uniform(0.85, 0.99),
            })
            current_time = end_time + random.uniform(0.5, 2.0)
            
        random.seed()
        return segments

    async def identify_speakers(self, audio_path: str) -> List[Dict]:
        await asyncio.sleep(0.1)
        seed_val = int(hashlib.md5(audio_path.encode()).hexdigest(), 16) % (2**32)
        random.seed(seed_val)
        
        speakers = random.sample(MOCK_SPEAKERS, random.randint(2, len(MOCK_SPEAKERS)))
        result = []
        for s in speakers:
            result.append({
                "name": s["name"],
                "speaking_time": random.uniform(20.0, 500.0),
                "word_count": random.randint(50, 1000)
            })
        random.seed()
        return result


class MockLanguageProvider(LanguageProvider):
    """Mock language provider — simulates Azure AI Language."""

    async def extract_key_phrases(self, text: str) -> List[str]:
        await asyncio.sleep(0.05)
        phrases = [
            "API architecture", "Q4 roadmap", "technical debt", "user experience",
            "sprint planning", "database optimization", "onboarding flow",
            "machine learning model", "deployment pipeline", "security audit",
        ]
        return random.sample(phrases, min(6, len(phrases)))

    async def analyze_sentiment(self, text: str) -> Dict:
        await asyncio.sleep(0.05)
        return {
            "sentiment": "positive",
            "confidence": 0.87,
            "scores": {"positive": 0.87, "neutral": 0.10, "negative": 0.03},
        }

    async def extract_entities(self, text: str) -> List[Dict]:
        await asyncio.sleep(0.05)
        return [
            {"text": "Q4", "category": "DateTime", "confidence": 0.99},
            {"text": "Azure", "category": "Organization", "confidence": 0.95},
            {"text": "FastAPI", "category": "Product", "confidence": 0.93},
        ]

    async def classify_meeting_type(self, text: str) -> str:
        await asyncio.sleep(0.05)
        types = ["Planning", "Sprint Planning", "Design Review", "Retrospective", "Standup"]
        return random.choice(types)


class MockGenAIProvider(GenAIProvider):
    """Mock generative AI provider — simulates Microsoft Foundry."""

    async def summarize(self, text: str, context: Optional[Dict] = None) -> str:
        await asyncio.sleep(0.1)
        seed_val = int(hashlib.md5(text.encode()).hexdigest(), 16) % (2**32)
        random.seed(seed_val)
        topics = ["API architecture improvements", "UX redesign", "database optimization", "server scaling", "marketing outreach"]
        topic = random.choice(topics)
        random.seed()
        
        return (
            f"The team held a productive session covering {topic}. "
            "Key discussions included reviewing the latest files and making decisions on the path forward. "
            "The team agreed on priorities and assigned clear action items with deadlines. "
            "Overall sentiment was positive with strong alignment."
        )

    async def extract_decisions(self, text: str) -> List[Dict]:
        await asyncio.sleep(0.1)
        seed_val = int(hashlib.md5(text.encode()).hexdigest(), 16) % (2**32)
        random.seed(seed_val)
        
        num_decisions = random.randint(1, 4)
        decisions = []
        for i in range(num_decisions):
            decisions.append({
                "text": f"Decision {i+1} regarding the current topic was approved.",
                "timestamp": random.uniform(10.0, 200.0),
                "speaker_name": random.choice(MOCK_SPEAKERS)["name"],
                "importance": random.choice(["high", "medium", "low"]),
            })
        random.seed()
        return decisions

    async def extract_action_items(self, text: str) -> List[Dict]:
        await asyncio.sleep(0.1)
        seed_val = int(hashlib.md5(text.encode()).hexdigest(), 16) % (2**32)
        random.seed(seed_val)
        
        num_actions = random.randint(2, 5)
        actions = []
        for i in range(num_actions):
            actions.append({
                "title": f"Follow up on task {i+1} discussed in the meeting",
                "assignee": random.choice(MOCK_SPEAKERS)["name"],
                "deadline": "2026-10-01",
                "priority": random.choice(["high", "medium", "low"]),
                "timestamp": random.uniform(20.0, 300.0),
            })
        random.seed()
        return actions

    async def extract_unresolved_questions(self, text: str) -> List[Dict]:
        await asyncio.sleep(0.05)
        return [
            {
                "text": "Should we migrate the entire database or do a phased migration?",
                "asked_by": "Tom Williams",
                "timestamp": 210.0,
            },
            {
                "text": "What is the budget allocation for Q4 tooling upgrades?",
                "asked_by": "Sarah Chen",
                "timestamp": 480.0,
            },
        ]

    async def generate_chapters(self, segments: List[Dict]) -> List[Dict]:
        await asyncio.sleep(0.1)
        if not segments:
            return []
            
        total_duration = segments[-1].get("end_time", 0.0)
        chapters = [
            {
                "title": "Introduction",
                "start_time": 0.0,
                "end_time": min(60.0, total_duration / 3),
                "summary": "Meeting kickoff.",
            },
            {
                "title": "Main Discussion",
                "start_time": min(60.0, total_duration / 3),
                "end_time": max(min(60.0, total_duration / 3), total_duration * 0.8),
                "summary": "Deep dive into the core topics.",
            },
            {
                "title": "Wrap Up",
                "start_time": max(min(60.0, total_duration / 3), total_duration * 0.8),
                "end_time": total_duration,
                "summary": "Summary and action items.",
            },
        ]
        return chapters

    async def answer_question(self, question: str, context: str, segments: List[Dict]) -> Dict:
        await asyncio.sleep(0.15)
        q_lower = question.lower()

        if "database" in q_lower or "postgresql" in q_lower or "sql" in q_lower:
            return {
                "answer": "The team decided to switch to PostgreSQL for production. Tom Williams was assigned to set up the staging environment by September 30th. There was an unresolved question about whether to do a full migration or phased approach.",
                "sources": [
                    {"speaker": "Marcus Johnson", "timestamp": 185.0, "text": "I recommend we move to PostgreSQL — it gives us better performance at scale."},
                    {"speaker": "Tom Williams", "timestamp": 210.0, "text": "Should we do a full migration or phased approach?"},
                ],
            }
        elif "onboarding" in q_lower or "ux" in q_lower or "design" in q_lower:
            return {
                "answer": "Priya Patel committed to delivering new onboarding flow wireframes by end of week. The UX team will focus on reducing friction in the sign-up process.",
                "sources": [
                    {"speaker": "Priya Patel", "timestamp": 325.0, "text": "I'll have the wireframes ready by Friday."},
                ],
            }
        elif "api" in q_lower or "refactor" in q_lower:
            return {
                "answer": "The API refactor was prioritized as the top Q4 initiative. Marcus Johnson was tasked with drafting the technical specification by September 25th.",
                "sources": [
                    {"speaker": "Marcus Johnson", "timestamp": 145.0, "text": "I'll draft the API refactor spec and share it with the team."},
                    {"speaker": "Sarah Chen", "timestamp": 14.5, "text": "API refactor will be our sprint 1 priority."},
                ],
            }
        else:
            return {
                "answer": "I couldn't find specific information about that in this meeting. The meeting primarily covered Q4 roadmap planning, API architecture, database migration, and UX redesign.",
                "sources": [],
            }

    async def generate_catch_up(self, segments: List[Dict], from_timestamp: Optional[float]) -> Dict:
        await asyncio.sleep(0.1)
        ts = from_timestamp or 0.0
        return {
            "summary": f"Here's what you missed from {int(ts // 60)}:{int(ts % 60):02d} onwards: The team finalized the Q4 roadmap with API refactor as top priority. A decision was made to migrate to PostgreSQL. Priya committed to wireframes by Friday.",
            "key_points": [
                "API refactor is Q4 Sprint 1 priority",
                "Database migration to PostgreSQL approved",
                "UX wireframes due by end of week",
                "Security audit scheduled for October",
            ],
            "missed_decisions": [
                "API refactor prioritized for Q4 Sprint 1",
                "PostgreSQL migration approved",
            ],
            "action_items_for_you": [
                "Review the API refactor spec when Marcus shares it",
                "Provide feedback on UX wireframes",
            ],
        }

    async def generate_follow_up_email(self, meeting_data: Dict) -> Dict:
        await asyncio.sleep(0.1)
        title = meeting_data.get("title", "Meeting")
        decisions = meeting_data.get("decisions", [])
        action_items = meeting_data.get("action_items", [])

        decisions_text = "\n".join([f"• {d['text']}" for d in decisions[:3]])
        actions_text = "\n".join([f"• {a['title']} — {a.get('assignee', 'TBD')} (by {a.get('deadline', 'TBD')})" for a in action_items[:4]])

        body = f"""Hi Team,

Thank you for joining today's {title}. Here's a summary of our key outcomes:

**Decisions Made:**
{decisions_text}

**Action Items:**
{actions_text}

Please review your assigned tasks and reach out if you have any questions or blockers.

Looking forward to our progress!

Best regards,
[Your Name]

---
This email was generated by MeetAI.
"""
        return {
            "subject": f"Follow-up: {title} — Key Decisions & Action Items",
            "body": body,
        }


class MockMeetingAnalysisProvider(MeetingAnalysisProvider):
    """Orchestrates all mock providers for full meeting analysis."""

    def __init__(self):
        self.language = MockLanguageProvider()
        self.genai = MockGenAIProvider()

    async def analyze(self, transcript_segments: List[Dict], metadata: Dict) -> Dict:
        full_text = " ".join([s.get("text", "") for s in transcript_segments])

        summary, key_phrases, sentiment, meeting_type, decisions, actions, questions, chapters = await asyncio.gather(
            self.genai.summarize(full_text),
            self.language.extract_key_phrases(full_text),
            self.language.analyze_sentiment(full_text),
            self.language.classify_meeting_type(full_text),
            self.genai.extract_decisions(full_text),
            self.genai.extract_action_items(full_text),
            self.genai.extract_unresolved_questions(full_text),
            self.genai.generate_chapters(transcript_segments),
        )

        return {
            "summary": summary,
            "key_topics": key_phrases,
            "sentiment": sentiment["sentiment"],
            "meeting_type": meeting_type,
            "decisions": decisions,
            "action_items": actions,
            "unresolved_questions": questions,
            "chapters": chapters,
        }
