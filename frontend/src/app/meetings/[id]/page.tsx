'use client';

import { useEffect, useState, useRef } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { getMeeting, getMeetingAnalysis, getMeetingTranscript } from '@/lib/api';
import type { MeetingDetail, MeetingAnalysis, TranscriptSegment } from '@/lib/types';
import { formatDuration, formatDate, cn } from '@/lib/utils';
import { ChevronLeft, MessageSquare, Clock, Mail, Loader2 } from 'lucide-react';

import VideoPlayer from '@/components/workspace/VideoPlayer';
import type { VideoPlayerRef } from '@/components/workspace/VideoPlayer';
import Transcript from '@/components/workspace/Transcript';
import Summary from '@/components/workspace/Summary';
import Decisions from '@/components/workspace/Decisions';
import ActionItemsPanel from '@/components/workspace/ActionItemsPanel';
import Chapters from '@/components/workspace/Chapters';
import Speakers from '@/components/workspace/Speakers';
import AskMeeting from '@/components/workspace/AskMeeting';
import CatchMeUp from '@/components/workspace/CatchMeUp';
import FollowUpEmail from '@/components/workspace/FollowUpEmail';

type Tab = 'summary' | 'topics' | 'decisions' | 'action-items' | 'questions' | 'chapters' | 'speakers';

const TABS: { id: Tab; label: string }[] = [
  { id: 'summary', label: 'Summary' },
  { id: 'topics', label: 'Topics' },
  { id: 'decisions', label: 'Decisions' },
  { id: 'action-items', label: 'Action Items' },
  { id: 'questions', label: 'Questions' },
  { id: 'chapters', label: 'Chapters' },
  { id: 'speakers', label: 'Speakers' },
];

export default function MeetingWorkspace() {
  const params = useParams();
  const router = useRouter();
  const id = Number(params.id);

  const [meeting, setMeeting] = useState<MeetingDetail | null>(null);
  const [analysis, setAnalysis] = useState<MeetingAnalysis | null>(null);
  const [transcript, setTranscript] = useState<TranscriptSegment[]>([]);
  const [loading, setLoading] = useState(true);

  const [activeTab, setActiveTab] = useState<Tab>('summary');
  const [currentTime, setCurrentTime] = useState(0);
  const [isTranscriptExpanded, setIsTranscriptExpanded] = useState(false);

  const [activePanel, setActivePanel] = useState<'ask' | 'catchup' | 'email' | null>(null);

  const videoPlayerRef = useRef<VideoPlayerRef>(null);

  useEffect(() => {
    async function loadData() {
      try {
        setLoading(true);
        const [meetingData, analysisData, transcriptData] = await Promise.all([
          getMeeting(id),
          getMeetingAnalysis(id),
          getMeetingTranscript(id),
        ]);
        setMeeting(meetingData);
        setAnalysis(analysisData);
        setTranscript(Array.isArray(transcriptData) ? transcriptData : []);
      } catch (error) {
        console.error('Error loading meeting workspace:', error);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, [id]);

  const handleSeek = (time: number) => {
    if (videoPlayerRef.current) {
      videoPlayerRef.current.seekTo(time);
    }
  };

  if (loading) {
    return (
      <div className="flex h-screen items-center justify-center bg-background">
        <Loader2 className="w-8 h-8 animate-spin text-primary" />
      </div>
    );
  }

  if (!meeting || !analysis) {
    return (
      <div className="flex h-screen items-center justify-center bg-background">
        <p className="text-muted-foreground">Failed to load meeting.</p>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-screen bg-background overflow-hidden">
      {/* Header */}
      <header className="flex-none h-16 border-b border-border bg-card/50 backdrop-blur-md flex items-center px-4 justify-between">
        <div className="flex items-center gap-4">
          <button 
            onClick={() => router.push('/meetings')}
            className="p-2 rounded-full hover:bg-muted text-muted-foreground transition-colors"
          >
            <ChevronLeft className="w-5 h-5" />
          </button>
          <div>
            <h1 className="font-semibold text-foreground text-lg">{meeting.title}</h1>
            <div className="text-sm text-muted-foreground flex items-center gap-2">
              <span>{formatDate(meeting.created_at)}</span>
              <span>&bull;</span>
              <span>{formatDuration(meeting.duration)}</span>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 flex overflow-hidden relative">
        {/* Left Column - Video & Transcript */}
        <div className="w-[60%] flex flex-col border-r border-border h-full">
          {!isTranscriptExpanded && (
            <div className="p-4 bg-muted/20 shrink-0">
              <VideoPlayer 
                ref={videoPlayerRef}
                videoUrl={meeting.file_path ? `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/meetings/${meeting.id}/video` : undefined} 
                onTimeUpdate={setCurrentTime} 
              />
            </div>
          )}
          <div className="flex-1 flex flex-col overflow-hidden">
            <div className="flex items-center justify-between px-4 py-2 border-b border-border bg-card/50 shrink-0">
              <h3 className="text-sm font-semibold text-muted-foreground">Transcript</h3>
              <button
                onClick={() => setIsTranscriptExpanded(!isTranscriptExpanded)}
                className="text-xs font-medium text-primary hover:text-primary/80 transition-colors"
              >
                {isTranscriptExpanded ? "Show Video" : "Expand Transcript"}
              </button>
            </div>
            <div className="flex-1 overflow-hidden">
              <Transcript 
                segments={transcript} 
                speakers={analysis.speakers || meeting.speakers || []} 
                onSeek={handleSeek}
                currentTime={currentTime}
              />
            </div>
          </div>
        </div>

        {/* Right Column - Tabs & Analysis */}
        <div className="w-[40%] flex flex-col h-full bg-card/30">
          <div className="flex-none overflow-x-auto border-b border-border hide-scrollbar">
            <div className="flex p-2 gap-1">
              {TABS.map(tab => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={cn(
                    "px-3 py-1.5 text-sm font-medium rounded-md whitespace-nowrap transition-colors",
                    activeTab === tab.id 
                      ? "bg-primary text-primary-foreground shadow-sm" 
                      : "text-muted-foreground hover:text-foreground hover:bg-muted"
                  )}
                >
                  {tab.label}
                </button>
              ))}
            </div>
          </div>

          <div className="flex-1 overflow-y-auto p-4 hide-scrollbar">
            {activeTab === 'summary' && <Summary analysis={analysis} />}
            {activeTab === 'topics' && (
              <div className="space-y-4">
                <h3 className="font-semibold text-lg">Key Topics</h3>
                <div className="flex flex-wrap gap-2">
                  {analysis.key_topics?.map((topic, i) => (
                    <span key={i} className="px-3 py-1 bg-primary/10 text-primary rounded-full text-sm">
                      {topic}
                    </span>
                  ))}
                </div>
              </div>
            )}
            {activeTab === 'decisions' && <Decisions decisions={analysis.decisions} speakers={analysis.speakers} onSeek={handleSeek} />}
            {activeTab === 'action-items' && <ActionItemsPanel actionItems={analysis.action_items} speakers={analysis.speakers} onSeek={handleSeek} />}
            {activeTab === 'chapters' && <Chapters chapters={analysis.chapters} onSeek={handleSeek} />}
            {activeTab === 'speakers' && <Speakers speakers={analysis.speakers || meeting.speakers || []} />}
            {activeTab === 'questions' && (
              <div className="p-4 text-center text-muted-foreground mt-10">
                <MessageSquare className="w-12 h-12 mx-auto mb-4 opacity-20" />
                <p>Click "Ask Meeting" below to ask questions about this session.</p>
              </div>
            )}
          </div>

          {/* Bottom Actions */}
          <div className="flex-none p-4 border-t border-border bg-card/50 backdrop-blur-sm grid grid-cols-3 gap-3">
            <button 
              onClick={() => setActivePanel('ask')}
              className="flex flex-col items-center justify-center p-3 rounded-lg bg-muted hover:bg-primary/10 text-foreground hover:text-primary transition-colors border border-transparent hover:border-primary/20"
            >
              <MessageSquare className="w-5 h-5 mb-1" />
              <span className="text-xs font-medium">Ask Meeting</span>
            </button>
            <button 
              onClick={() => setActivePanel('catchup')}
              className="flex flex-col items-center justify-center p-3 rounded-lg bg-muted hover:bg-primary/10 text-foreground hover:text-primary transition-colors border border-transparent hover:border-primary/20"
            >
              <Clock className="w-5 h-5 mb-1" />
              <span className="text-xs font-medium">Catch Me Up</span>
            </button>
            <button 
              onClick={() => setActivePanel('email')}
              className="flex flex-col items-center justify-center p-3 rounded-lg bg-muted hover:bg-primary/10 text-foreground hover:text-primary transition-colors border border-transparent hover:border-primary/20"
            >
              <Mail className="w-5 h-5 mb-1" />
              <span className="text-xs font-medium">Generate Email</span>
            </button>
          </div>
        </div>

        {/* Sliding Panels */}
        {activePanel === 'ask' && <AskMeeting meetingId={id} onClose={() => setActivePanel(null)} onSeek={handleSeek} />}
        {activePanel === 'catchup' && <CatchMeUp meetingId={id} onClose={() => setActivePanel(null)} />}
        {activePanel === 'email' && <FollowUpEmail meetingId={id} onClose={() => setActivePanel(null)} />}
      </main>
    </div>
  );
}
