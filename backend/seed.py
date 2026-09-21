"""
Seed Data — 3 realistic sample meetings with full transcripts, analysis, and tasks.
Run: python seed.py
"""
import json
import sys
from datetime import datetime, timezone
from sqlalchemy.orm import Session
import models
from database import SessionLocal, engine


def seed_database():
    models.Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()

    # Clear existing data
    db.query(models.Task).delete()
    db.query(models.Chapter).delete()
    db.query(models.UnresolvedQuestion).delete()
    db.query(models.ActionItem).delete()
    db.query(models.Decision).delete()
    db.query(models.Speaker).delete()
    db.query(models.TranscriptSegment).delete()
    db.query(models.Meeting).delete()
    db.commit()

    print("Seeding database with sample meetings...")

    # ───────────────────────────────────────────────
    # MEETING 1: AI-103 Project Planning
    # ───────────────────────────────────────────────
    m1 = models.Meeting(
        id=1,
        title="AI-103 Project Planning",
        description="Initial planning session for the AI-103 university project. Discussing scope, tech stack, and task assignments.",
        status="ready",
        duration=2640.0,  # 44 minutes
        file_path="sample/ai103_planning.mp4",
        thumbnail_url=None,
        summary=(
            "The team held the inaugural planning session for the AI-103 Meeting Assistant project. "
            "Key decisions were made around the technology stack, choosing Next.js for frontend and "
            "FastAPI with Python for the backend. The team agreed to use Azure AI Speech and Azure AI Language "
            "for production, with mock providers for initial development. Task assignments were distributed "
            "across the team with clear deadlines aligned to the university submission schedule."
        ),
        key_topics=json.dumps([
            "Azure AI Speech", "FastAPI architecture", "Next.js frontend",
            "mock providers", "university deadline", "team assignments",
            "project scope", "AI-103 requirements"
        ]),
        sentiment="positive",
        meeting_type="Planning",
    )
    db.add(m1)
    db.flush()

    # Speakers
    db.add(models.Speaker(meeting_id=1, name="Dr. Ahmed Hassan", role="Course Supervisor", speaking_time=780.0, word_count=1180, avatar_color="#f59e0b"))
    db.add(models.Speaker(meeting_id=1, name="Sarah Chen", role="Project Lead", speaking_time=650.0, word_count=980, avatar_color="#6366f1"))
    db.add(models.Speaker(meeting_id=1, name="Marcus Johnson", role="Backend Developer", speaking_time=540.0, word_count=820, avatar_color="#8b5cf6"))
    db.add(models.Speaker(meeting_id=1, name="Priya Patel", role="Frontend Developer", speaking_time=420.0, word_count=640, avatar_color="#ec4899"))
    db.add(models.Speaker(meeting_id=1, name="Tom Williams", role="DevOps Engineer", speaking_time=250.0, word_count=380, avatar_color="#10b981"))

    # Transcript
    transcript1 = [
        (1, "Dr. Ahmed Hassan", "Good morning everyone. I'm glad we could all make it. Today we're kicking off the AI-103 project — the Meeting Assistant. This is going to be a significant piece of work, so let's make sure we're all aligned on the scope and deliverables.", 0.0, 14.5),
        (1, "Sarah Chen", "Good morning, Dr. Hassan. Thanks for organizing this. I've put together a project overview — should I walk everyone through it?", 15.0, 22.0),
        (1, "Dr. Ahmed Hassan", "Please go ahead, Sarah.", 22.5, 24.0),
        (1, "Sarah Chen", "Great. So the core idea is to build an AI-powered meeting assistant that can transcribe meetings, extract insights like action items and decisions, and let you ask questions about past meetings. Think of it as an intelligent layer on top of your meetings.", 24.5, 42.0),
        (1, "Marcus Johnson", "I've been thinking about the backend architecture. I'd recommend FastAPI for the API layer — it's fast, supports async natively, and has great automatic documentation. We pair that with SQLAlchemy for the ORM and SQLite for development.", 43.0, 58.5),
        (1, "Priya Patel", "For the frontend I was thinking Next.js with TypeScript and Tailwind CSS. It gives us server-side rendering, great performance, and a really polished developer experience. I also want to use shadcn/ui for the component library.", 59.0, 74.0),
        (1, "Tom Williams", "Makes sense. I can set up the Docker environment and CI pipeline once we have the basic structure in place.", 74.5, 81.0),
        (1, "Dr. Ahmed Hassan", "Excellent choices. Now, regarding the AI capabilities — the project requirement maps to three Azure services: Azure AI Speech for transcription, Azure AI Language for text analysis, and Microsoft Foundry for the generative AI and agent orchestration.", 82.0, 100.0),
        (1, "Sarah Chen", "That's right. But we've decided to build with mock providers first and keep the interfaces clean so we can swap in the Azure services later without touching the frontend.", 100.5, 113.0),
        (1, "Marcus Johnson", "Exactly. I'll define abstract base classes for each provider. The agent layer will only ever talk to those interfaces, never directly to Azure or any specific implementation.", 113.5, 124.0),
        (1, "Dr. Ahmed Hassan", "Very good approach. This is exactly the kind of architectural thinking I want to see in AI-103. What about the timeline?", 124.5, 132.0),
        (1, "Sarah Chen", "We're targeting 4 weeks. Week 1 is architecture and mock setup, week 2 is the core UI, week 3 is Azure integration, week 4 is testing and polish.", 132.5, 144.0),
        (1, "Marcus Johnson", "I'll own the backend. Give me two weeks for the core APIs and agent layer.", 144.5, 150.0),
        (1, "Priya Patel", "I'll handle the frontend — dashboard, meeting workspace, the whole UI system. Two weeks feels tight but doable.", 150.5, 158.0),
        (1, "Tom Williams", "I'll handle the database schema, seed data, and deployment configuration.", 158.5, 163.5),
        (1, "Dr. Ahmed Hassan", "This sounds like a solid plan. One question: how will you handle the responsible AI aspects? Data privacy, bias in speaker identification, that sort of thing?", 164.0, 174.0),
        (1, "Sarah Chen", "Good point. We'll document those in the README. We'll note that the system processes meeting content which may contain personal information, and we'll recommend access controls and data retention policies.", 174.5, 188.0),
        (1, "Dr. Ahmed Hassan", "Very good. Make sure that's in the submission. Anything unresolved before we close?", 188.5, 193.0),
        (1, "Marcus Johnson", "One thing — should we implement real-time transcription or just batch processing?", 193.5, 198.0),
        (1, "Sarah Chen", "Let's do batch for the first version. Real-time can be a future enhancement.", 198.5, 203.0),
        (1, "Dr. Ahmed Hassan", "Agreed. What about multi-language support?", 203.5, 206.0),
        (1, "Tom Williams", "That's probably out of scope for this version given the timeline.", 206.5, 210.0),
        (1, "Dr. Ahmed Hassan", "Fair. Let's keep it English-only for now and note it as future work. Alright, great session everyone. Let's get building!", 210.5, 218.0),
    ]
    for seg in transcript1:
        db.add(models.TranscriptSegment(meeting_id=seg[0], speaker_name=seg[1], text=seg[2], start_time=seg[3], end_time=seg[4], confidence=0.97))

    # Decisions
    db.add(models.Decision(meeting_id=1, text="Use FastAPI + SQLAlchemy + SQLite for backend", timestamp=58.5, speaker_name="Marcus Johnson", importance="high"))
    db.add(models.Decision(meeting_id=1, text="Use Next.js + TypeScript + Tailwind CSS + shadcn/ui for frontend", timestamp=74.0, speaker_name="Priya Patel", importance="high"))
    db.add(models.Decision(meeting_id=1, text="Build with mock providers first, Azure integration in week 3", timestamp=113.0, speaker_name="Sarah Chen", importance="high"))
    db.add(models.Decision(meeting_id=1, text="4-week project timeline with Azure integration in week 3", timestamp=144.0, speaker_name="Sarah Chen", importance="high"))
    db.add(models.Decision(meeting_id=1, text="Batch processing for transcription (not real-time) for v1", timestamp=203.0, speaker_name="Sarah Chen", importance="medium"))
    db.add(models.Decision(meeting_id=1, text="English-only support for first version", timestamp=218.0, speaker_name="Dr. Ahmed Hassan", importance="medium"))

    # Action Items
    db.add(models.ActionItem(meeting_id=1, title="Define provider interfaces and abstract base classes", assignee="Marcus Johnson", deadline="2026-09-20", priority="high", timestamp=124.0, status="done"))
    db.add(models.ActionItem(meeting_id=1, title="Set up Next.js project with Tailwind and shadcn/ui", assignee="Priya Patel", deadline="2026-09-20", priority="high", timestamp=158.0, status="done"))
    db.add(models.ActionItem(meeting_id=1, title="Design SQLite database schema and seed data", assignee="Tom Williams", deadline="2026-09-20", priority="high", timestamp=163.5, status="in_progress"))
    db.add(models.ActionItem(meeting_id=1, title="Write responsible AI section for README", assignee="Sarah Chen", deadline="2026-09-25", priority="medium", timestamp=188.0, status="todo"))
    db.add(models.ActionItem(meeting_id=1, title="Create Docker setup and CI pipeline", assignee="Tom Williams", deadline="2026-09-28", priority="low", timestamp=81.0, status="todo"))

    # Questions
    db.add(models.UnresolvedQuestion(meeting_id=1, text="Should we implement real-time transcription or batch processing for v2?", asked_by="Marcus Johnson", timestamp=198.0))
    db.add(models.UnresolvedQuestion(meeting_id=1, text="What is the budget/quota limit for Azure AI services?", asked_by="Sarah Chen", timestamp=180.0))

    # Chapters
    db.add(models.Chapter(meeting_id=1, title="Welcome & Project Overview", start_time=0.0, end_time=580.0, summary="Dr. Hassan opens the session and Sarah presents the project overview."))
    db.add(models.Chapter(meeting_id=1, title="Technology Stack Decisions", start_time=580.0, end_time=1200.0, summary="Team decides on FastAPI backend, Next.js frontend, and Azure AI services."))
    db.add(models.Chapter(meeting_id=1, title="Architecture & Provider Strategy", start_time=1200.0, end_time=1800.0, summary="Mock providers first approach decided; abstract interfaces defined."))
    db.add(models.Chapter(meeting_id=1, title="Timeline & Task Assignments", start_time=1800.0, end_time=2200.0, summary="4-week timeline agreed; tasks distributed across team members."))
    db.add(models.Chapter(meeting_id=1, title="Responsible AI & Wrap Up", start_time=2200.0, end_time=2640.0, summary="Responsible AI considerations discussed; open questions noted."))

    # ───────────────────────────────────────────────
    # MEETING 2: Sprint Planning
    # ───────────────────────────────────────────────
    m2 = models.Meeting(
        id=2,
        title="Sprint Planning — Week 2",
        description="Sprint 2 planning session to review completed work and plan the upcoming development sprint.",
        status="ready",
        duration=3120.0,  # 52 minutes
        file_path="sample/sprint_planning.mp4",
        thumbnail_url=None,
        summary=(
            "The team reviewed sprint 1 outcomes and planned sprint 2 work items. "
            "Backend APIs are 80% complete with all core endpoints implemented. "
            "The frontend shell is up with navigation and theming. Sprint 2 focuses on "
            "completing the meeting workspace UI, integrating the Ask Meeting feature, "
            "and beginning the Azure migration preparations. Velocity is on track for the deadline."
        ),
        key_topics=json.dumps([
            "sprint velocity", "API completion", "meeting workspace", "Azure migration",
            "frontend integration", "testing strategy", "performance optimization"
        ]),
        sentiment="positive",
        meeting_type="Sprint Planning",
    )
    db.add(m2)
    db.flush()

    db.add(models.Speaker(meeting_id=2, name="Sarah Chen", role="Scrum Master", speaking_time=840.0, word_count=1260, avatar_color="#6366f1"))
    db.add(models.Speaker(meeting_id=2, name="Marcus Johnson", role="Backend Developer", speaking_time=720.0, word_count=1080, avatar_color="#8b5cf6"))
    db.add(models.Speaker(meeting_id=2, name="Priya Patel", role="Frontend Developer", speaking_time=640.0, word_count=960, avatar_color="#ec4899"))
    db.add(models.Speaker(meeting_id=2, name="Tom Williams", role="DevOps Engineer", speaking_time=380.0, word_count=560, avatar_color="#10b981"))

    transcript2 = [
        (2, "Sarah Chen", "Good morning team. Let's kick off sprint 2 planning. First, quick retrospective on sprint 1 — Marcus, how did the backend go?", 0.0, 10.0),
        (2, "Marcus Johnson", "Sprint 1 was solid. I've got all the core API endpoints done — meetings CRUD, the agent layer, transcript storage, all the analysis tools. The mock providers are working end-to-end. I'd say we're at 80% backend completion.", 10.5, 28.0),
        (2, "Priya Patel", "Frontend progress: the Next.js project is set up, navigation is in, theming with dark/light mode is working, the dashboard is rendering with real API data. I'm about 60% done.", 28.5, 42.0),
        (2, "Tom Williams", "The SQLite schema is done and the seed data is in. I've also configured the CORS settings and got both servers running together without issues.", 42.5, 52.0),
        (2, "Sarah Chen", "Great progress. For sprint 2, the big ticket items are: completing the meeting workspace UI with all tabs, getting the Ask Meeting chat working, the task kanban board, and analytics charts. Can we commit to finishing those this week?", 52.5, 68.0),
        (2, "Marcus Johnson", "The Ask Meeting endpoint is already implemented — I just need to connect it on the frontend. Same with catch-up and follow-up email.", 68.5, 76.0),
        (2, "Priya Patel", "The meeting workspace is my priority this sprint. I'll build the video player, transcript viewer, and all the sidebar tabs — summary, decisions, action items. That's a lot but I can do it.", 76.5, 90.0),
        (2, "Sarah Chen", "What about the analytics charts?", 90.5, 92.5),
        (2, "Priya Patel", "I'll use Recharts — it integrates cleanly with Next.js. I'll get the basic charts done but maybe not all the fancy drill-downs in this sprint.", 93.0, 102.0),
        (2, "Tom Williams", "Should we write tests this sprint?", 102.5, 105.0),
        (2, "Sarah Chen", "At minimum, let's make sure the API endpoints are tested manually via the Swagger UI. We can add pytest tests in sprint 3 if time permits.", 105.5, 115.0),
        (2, "Marcus Johnson", "I'll add a few smoke tests at least. The key thing is the agent integration test — making sure the full upload-to-analysis pipeline works end-to-end.", 115.5, 125.0),
        (2, "Sarah Chen", "Good. Let's also start thinking about Azure prep — not implementing yet, but making sure our interfaces are clean enough to swap in.", 125.5, 134.0),
        (2, "Marcus Johnson", "The provider interfaces are solid. Swapping in Azure providers will be a matter of implementing the abstract classes — shouldn't touch any routing or business logic.", 134.5, 144.0),
        (2, "Sarah Chen", "Perfect. Any blockers?", 144.5, 146.0),
        (2, "Priya Patel", "One thing — the video player. If someone uploads a real file, I need a way to serve it. How is the backend handling file storage?", 146.5, 155.0),
        (2, "Marcus Johnson", "Right now files go to the /uploads directory and I serve them as static files via FastAPI. For the mock meetings there's no actual video file, so I'll return a dummy URL for the player.", 155.5, 168.0),
        (2, "Priya Patel", "Works for me. I'll handle the case where the video URL is null and show a placeholder.", 168.5, 175.0),
        (2, "Sarah Chen", "Great. Any other blockers?", 175.5, 177.0),
        (2, "Tom Williams", "Not from my side.", 177.5, 179.0),
        (2, "Sarah Chen", "Perfect. Let's aim to have a demo-ready build by end of week. I'll update the task board after this meeting.", 179.5, 187.0),
    ]
    for seg in transcript2:
        db.add(models.TranscriptSegment(meeting_id=seg[0], speaker_name=seg[1], text=seg[2], start_time=seg[3], end_time=seg[4], confidence=0.96))

    db.add(models.Decision(meeting_id=2, text="Complete meeting workspace UI as sprint 2 top priority", timestamp=90.0, speaker_name="Sarah Chen", importance="high"))
    db.add(models.Decision(meeting_id=2, text="Use Recharts for analytics charts", timestamp=102.0, speaker_name="Priya Patel", importance="medium"))
    db.add(models.Decision(meeting_id=2, text="Manual API testing via Swagger UI for sprint 2; pytest in sprint 3", timestamp=115.0, speaker_name="Sarah Chen", importance="medium"))
    db.add(models.Decision(meeting_id=2, text="Videos served as FastAPI static files; null URL shows placeholder in frontend", timestamp=168.0, speaker_name="Marcus Johnson", importance="medium"))

    db.add(models.ActionItem(meeting_id=2, title="Build meeting workspace UI (video player, transcript, all tabs)", assignee="Priya Patel", deadline="2026-09-21", priority="high", timestamp=90.0, status="in_progress"))
    db.add(models.ActionItem(meeting_id=2, title="Connect Ask Meeting chat to backend endpoint", assignee="Priya Patel", deadline="2026-09-21", priority="high", timestamp=76.0, status="todo"))
    db.add(models.ActionItem(meeting_id=2, title="Build Kanban task board", assignee="Priya Patel", deadline="2026-09-22", priority="high", timestamp=68.0, status="todo"))
    db.add(models.ActionItem(meeting_id=2, title="Implement analytics charts with Recharts", assignee="Priya Patel", deadline="2026-09-22", priority="medium", timestamp=102.0, status="todo"))
    db.add(models.ActionItem(meeting_id=2, title="Add end-to-end agent integration smoke test", assignee="Marcus Johnson", deadline="2026-09-21", priority="medium", timestamp=125.0, status="todo"))
    db.add(models.ActionItem(meeting_id=2, title="Update task board after sprint planning", assignee="Sarah Chen", deadline="2026-09-19", priority="low", timestamp=187.0, status="done"))

    db.add(models.UnresolvedQuestion(meeting_id=2, text="How will we handle real video file serving in production? S3? Azure Blob?", asked_by="Priya Patel", timestamp=155.0))
    db.add(models.UnresolvedQuestion(meeting_id=2, text="Will we have time for pytest coverage in sprint 2?", asked_by="Tom Williams", timestamp=105.0))

    db.add(models.Chapter(meeting_id=2, title="Sprint 1 Retrospective", start_time=0.0, end_time=780.0, summary="Review of sprint 1 completion — backend 80%, frontend 60%."))
    db.add(models.Chapter(meeting_id=2, title="Sprint 2 Planning & Commitments", start_time=780.0, end_time=1680.0, summary="Meeting workspace, Ask Meeting, Kanban, analytics charts."))
    db.add(models.Chapter(meeting_id=2, title="Technical Discussions", start_time=1680.0, end_time=2520.0, summary="Video serving, testing strategy, Azure prep."))
    db.add(models.Chapter(meeting_id=2, title="Blockers & Wrap Up", start_time=2520.0, end_time=3120.0, summary="Blockers cleared; demo target set for end of week."))

    # ───────────────────────────────────────────────
    # MEETING 3: Product Design Discussion
    # ───────────────────────────────────────────────
    m3 = models.Meeting(
        id=3,
        title="Product Design Discussion",
        description="UX and product design review for the MeetAI interface. Focus on the meeting workspace, dashboard, and analytics.",
        status="ready",
        duration=2280.0,  # 38 minutes
        file_path="sample/design_review.mp4",
        thumbnail_url=None,
        summary=(
            "Priya led a comprehensive design review of the MeetAI interface. The team aligned on "
            "a dark-mode-first design system using indigo and violet as the primary palette. "
            "Key decisions included using glassmorphism cards for the dashboard, a tabbed sidebar "
            "layout for the meeting workspace, and a split-panel layout for the transcript. "
            "The Ask Meeting feature will use a chat-bubble UI similar to messaging apps. "
            "Motion design guidelines were established using Framer Motion."
        ),
        key_topics=json.dumps([
            "dark mode design", "glassmorphism", "meeting workspace layout", "Ask Meeting UI",
            "motion design", "color palette", "typography", "accessibility"
        ]),
        sentiment="positive",
        meeting_type="Design Review",
    )
    db.add(m3)
    db.flush()

    db.add(models.Speaker(meeting_id=3, name="Priya Patel", role="UX Lead", speaking_time=920.0, word_count=1380, avatar_color="#ec4899"))
    db.add(models.Speaker(meeting_id=3, name="Sarah Chen", role="Product Manager", speaking_time=680.0, word_count=1020, avatar_color="#6366f1"))
    db.add(models.Speaker(meeting_id=3, name="Marcus Johnson", role="Backend Developer", speaking_time=340.0, word_count=510, avatar_color="#8b5cf6"))
    db.add(models.Speaker(meeting_id=3, name="Tom Williams", role="DevOps Engineer", speaking_time=180.0, word_count=270, avatar_color="#10b981"))

    transcript3 = [
        (3, "Priya Patel", "Alright, let me share my screen. I've been working on the design system and I want to walk you through the key decisions.", 0.0, 10.0),
        (3, "Sarah Chen", "Excited to see this. The UI is really what's going to make this project stand out.", 10.5, 16.0),
        (3, "Priya Patel", "So first — color palette. I went dark-mode-first with indigo and violet as the primary colors. The background is a very dark blue-gray, and we layer glassmorphism cards on top. It gives it that premium SaaS feel.", 16.5, 32.0),
        (3, "Marcus Johnson", "Looks great. Will the light mode use the same palette?", 32.5, 36.0),
        (3, "Priya Patel", "Yes but inverted — light gray backgrounds with the same indigo accents. The component library handles the theming through CSS variables.", 36.5, 45.0),
        (3, "Sarah Chen", "What about typography?", 45.5, 47.0),
        (3, "Priya Patel", "Inter from Google Fonts. It's clean, highly legible, and works great at all sizes. I'm using a 7-step type scale — 12, 14, 16, 18, 20, 24, 32px.", 47.5, 60.0),
        (3, "Sarah Chen", "The dashboard — talk me through the layout.", 60.5, 63.0),
        (3, "Priya Patel", "Dashboard has a stats row at the top — total meetings, action items, decisions, unresolved questions, total meeting time. Then below that a two-column layout: left is a meetings-over-time chart and recent meetings, right is task overview and recent activity. There's also a big Upload Meeting button in the top right of the header.", 63.5, 86.0),
        (3, "Sarah Chen", "I love it. What about the meeting workspace?", 86.5, 89.0),
        (3, "Priya Patel", "The workspace has a left panel for the video player and below it the transcript with clickable timestamps. The right side is a tabbed panel — Summary, Topics, Decisions, Action Items, Unresolved, Chapters, Speakers. At the bottom of the right panel are three action buttons: Ask Meeting, Catch Me Up, Generate Email.", 89.5, 112.0),
        (3, "Marcus Johnson", "The transcript timestamps — clicking them seeks the video?", 112.5, 116.0),
        (3, "Priya Patel", "Exactly. I'll use a ref on the video player element and update its currentTime. Works cleanly without any state management overhead.", 116.5, 125.0),
        (3, "Sarah Chen", "Ask Meeting — how does the UI work?", 125.5, 128.0),
        (3, "Priya Patel", "It slides up as a panel below the transcript — think messaging app. User types a question, it shows a loading indicator, then the AI answer appears with source citations showing speaker name and timestamp. Clicking a citation seeks the video.", 128.5, 147.0),
        (3, "Sarah Chen", "That's really nice. And animations?", 147.5, 150.0),
        (3, "Priya Patel", "Framer Motion throughout. Page transitions with a subtle fade-slide, card hover effects with a slight lift, the upload modal fades in with a scale-up. Nothing too flashy — just enough to feel alive and premium.", 150.5, 165.0),
        (3, "Tom Williams", "What about mobile responsiveness?", 165.5, 168.0),
        (3, "Priya Patel", "The sidebar collapses to a bottom tab bar on mobile. The workspace goes single-column. The dashboard stats stack vertically. All built with CSS Grid and Tailwind responsive prefixes.", 168.5, 181.0),
        (3, "Sarah Chen", "Accessibility?", 181.5, 183.0),
        (3, "Priya Patel", "ARIA labels on all interactive elements, keyboard navigation for the main flows, sufficient color contrast in both themes — WCAG AA at minimum. shadcn/ui handles a lot of this for free.", 183.5, 196.0),
        (3, "Sarah Chen", "This is excellent work, Priya. Any open design questions?", 196.5, 200.0),
        (3, "Priya Patel", "One thing I'm not sure about — should the Ask Meeting panel be a modal overlay or an inline panel? I went inline but a modal might feel more focused.", 200.5, 211.0),
        (3, "Sarah Chen", "Let's go inline for now. We can always change it based on user feedback.", 211.5, 216.0),
        (3, "Marcus Johnson", "Agreed. Inline is less disruptive to the workflow.", 216.5, 220.0),
        (3, "Priya Patel", "Great. I'll finalize the implementation today.", 220.5, 223.5),
    ]
    for seg in transcript3:
        db.add(models.TranscriptSegment(meeting_id=seg[0], speaker_name=seg[1], text=seg[2], start_time=seg[3], end_time=seg[4], confidence=0.98))

    db.add(models.Decision(meeting_id=3, text="Dark-mode-first design with indigo/violet primary palette and glassmorphism cards", timestamp=32.0, speaker_name="Priya Patel", importance="high"))
    db.add(models.Decision(meeting_id=3, text="Inter font from Google Fonts as the primary typeface", timestamp=60.0, speaker_name="Priya Patel", importance="medium"))
    db.add(models.Decision(meeting_id=3, text="Meeting workspace: left panel (video + transcript) + right tabbed panel", timestamp=112.0, speaker_name="Priya Patel", importance="high"))
    db.add(models.Decision(meeting_id=3, text="Transcript timestamps seek the video player via ref.currentTime", timestamp=125.0, speaker_name="Priya Patel", importance="high"))
    db.add(models.Decision(meeting_id=3, text="Ask Meeting as inline panel (not modal) below the transcript", timestamp=216.0, speaker_name="Sarah Chen", importance="medium"))
    db.add(models.Decision(meeting_id=3, text="Framer Motion for all animations — subtle fade-slide and lift effects", timestamp=165.0, speaker_name="Priya Patel", importance="medium"))

    db.add(models.ActionItem(meeting_id=3, title="Finalize design system CSS variables and tokens", assignee="Priya Patel", deadline="2026-09-20", priority="high", timestamp=45.0, status="done"))
    db.add(models.ActionItem(meeting_id=3, title="Implement video player with timestamp-seek functionality", assignee="Priya Patel", deadline="2026-09-21", priority="high", timestamp=125.0, status="in_progress"))
    db.add(models.ActionItem(meeting_id=3, title="Build Ask Meeting inline chat panel", assignee="Priya Patel", deadline="2026-09-22", priority="high", timestamp=147.0, status="todo"))
    db.add(models.ActionItem(meeting_id=3, title="Implement mobile responsive layout", assignee="Priya Patel", deadline="2026-09-23", priority="medium", timestamp=181.0, status="todo"))
    db.add(models.ActionItem(meeting_id=3, title="WCAG AA accessibility audit", assignee="Tom Williams", deadline="2026-09-25", priority="medium", timestamp=196.0, status="todo"))

    db.add(models.UnresolvedQuestion(meeting_id=3, text="Should Ask Meeting be a modal overlay or inline panel in the final version?", asked_by="Priya Patel", timestamp=211.0))
    db.add(models.UnresolvedQuestion(meeting_id=3, text="Do we need a full WCAG audit or just spot checks?", asked_by="Tom Williams", timestamp=168.0))

    db.add(models.Chapter(meeting_id=3, title="Design System Overview", start_time=0.0, end_time=570.0, summary="Color palette, dark mode, typography decisions."))
    db.add(models.Chapter(meeting_id=3, title="Dashboard Layout", start_time=570.0, end_time=1050.0, summary="Stats cards, chart layout, upload button placement."))
    db.add(models.Chapter(meeting_id=3, title="Meeting Workspace Design", start_time=1050.0, end_time=1620.0, summary="Video + transcript panel, tabbed sidebar design."))
    db.add(models.Chapter(meeting_id=3, title="Ask Meeting & Animations", start_time=1620.0, end_time=2000.0, summary="Chat UI design, Framer Motion guidelines."))
    db.add(models.Chapter(meeting_id=3, title="Accessibility & Open Questions", start_time=2000.0, end_time=2280.0, summary="WCAG AA target, Ask Meeting panel placement decision."))

    db.commit()

    # ───────────────────────────────────────────────
    # Standalone Tasks
    # ───────────────────────────────────────────────
    standalone_tasks = [
        {"title": "Write README with Azure integration guide", "assignee": "Sarah Chen", "deadline": "2026-09-28", "priority": "high", "status": "todo"},
        {"title": "Create .env.example with all Azure service variables", "assignee": "Marcus Johnson", "deadline": "2026-09-25", "priority": "medium", "status": "todo"},
        {"title": "Review and finalize responsible AI documentation", "assignee": "Dr. Ahmed Hassan", "deadline": "2026-10-01", "priority": "high", "status": "todo"},
        {"title": "Configure Azure AI Speech resource in Azure portal", "assignee": "Tom Williams", "deadline": "2026-09-30", "priority": "high", "status": "todo"},
        {"title": "Implement AzureSpeechProvider class", "assignee": "Marcus Johnson", "deadline": "2026-09-30", "priority": "high", "status": "todo"},
        {"title": "Set up final presentation slides", "assignee": "Sarah Chen", "deadline": "2026-10-05", "priority": "medium", "status": "todo"},
    ]

    for t in standalone_tasks:
        db.add(models.Task(**t))

    # Action items from meetings as tasks
    action_items_as_tasks = [
        {"title": "Draft API refactor technical specification", "assignee": "Marcus Johnson", "deadline": "2026-09-25", "priority": "high", "status": "todo", "meeting_id": 1, "meeting_title": "AI-103 Project Planning", "source_timestamp": 145.0},
        {"title": "Design SQLite database schema and seed data", "assignee": "Tom Williams", "deadline": "2026-09-20", "priority": "high", "status": "in_progress", "meeting_id": 1, "meeting_title": "AI-103 Project Planning", "source_timestamp": 163.5},
        {"title": "Build meeting workspace UI", "assignee": "Priya Patel", "deadline": "2026-09-21", "priority": "high", "status": "in_progress", "meeting_id": 2, "meeting_title": "Sprint Planning — Week 2", "source_timestamp": 90.0},
        {"title": "Implement video player with timestamp-seek", "assignee": "Priya Patel", "deadline": "2026-09-21", "priority": "high", "status": "in_progress", "meeting_id": 3, "meeting_title": "Product Design Discussion", "source_timestamp": 125.0},
        {"title": "Define provider interfaces (SpeechProvider, GenAIProvider)", "assignee": "Marcus Johnson", "deadline": "2026-09-20", "priority": "high", "status": "done", "meeting_id": 1, "meeting_title": "AI-103 Project Planning", "source_timestamp": 124.0},
        {"title": "Set up Next.js with Tailwind and shadcn/ui", "assignee": "Priya Patel", "deadline": "2026-09-20", "priority": "high", "status": "done", "meeting_id": 1, "meeting_title": "AI-103 Project Planning", "source_timestamp": 158.0},
    ]

    for t in action_items_as_tasks:
        db.add(models.Task(**t))

    db.commit()
    print("Database seeded successfully!")
    print(f"  - 3 meetings created")
    print(f"  - Transcripts, speakers, decisions, action items, chapters seeded")
    print(f"  - Tasks created")


if __name__ == "__main__":
    seed_database()
