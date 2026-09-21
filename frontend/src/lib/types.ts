// TypeScript types for MeetAI — mirrors backend Pydantic schemas

export interface Speaker {
  id: number;
  meeting_id: number;
  name: string;
  role?: string;
  speaking_time: number;
  word_count: number;
  avatar_color?: string;
}

export interface TranscriptSegment {
  id: number;
  meeting_id: number;
  speaker_name?: string;
  text: string;
  start_time: number;
  end_time: number;
  confidence: number;
}

export interface Decision {
  id: number;
  meeting_id: number;
  text: string;
  timestamp?: number;
  speaker_name?: string;
  importance: 'low' | 'medium' | 'high';
}

export interface ActionItem {
  id: number;
  meeting_id: number;
  title: string;
  assignee?: string;
  deadline?: string;
  status: 'todo' | 'in_progress' | 'done';
  priority: 'low' | 'medium' | 'high';
  timestamp?: number;
}

export interface UnresolvedQuestion {
  id: number;
  meeting_id: number;
  text: string;
  asked_by?: string;
  timestamp?: number;
}

export interface Chapter {
  id: number;
  meeting_id: number;
  title: string;
  start_time: number;
  end_time: number;
  summary?: string;
}

export interface Meeting {
  id: number;
  title: string;
  description?: string;
  status: 'uploading' | 'processing' | 'ready' | 'failed';
  duration: number;
  file_path?: string;
  thumbnail_url?: string;
  created_at?: string;
  updated_at?: string;
  summary?: string;
  key_topics?: string;
  sentiment?: string;
  meeting_type?: string;
}

export interface MeetingDetail extends Meeting {
  speakers: Speaker[];
  decisions: Decision[];
  action_items: ActionItem[];
  unresolved_questions: UnresolvedQuestion[];
  chapters: Chapter[];
}

export interface MeetingAnalysis {
  summary: string;
  key_topics: string[];
  sentiment: string;
  meeting_type: string;
  decisions: Decision[];
  action_items: ActionItem[];
  unresolved_questions: UnresolvedQuestion[];
  chapters: Chapter[];
  speakers: Speaker[];
}

export interface Task {
  id: number;
  title: string;
  description?: string;
  assignee?: string;
  deadline?: string;
  status: 'todo' | 'in_progress' | 'done';
  priority: 'low' | 'medium' | 'high';
  meeting_id?: number;
  meeting_title?: string;
  source_timestamp?: number;
  created_at?: string;
  updated_at?: string;
}

export interface AskResponse {
  answer: string;
  sources: Array<{
    speaker?: string;
    timestamp?: number;
    text?: string;
  }>;
}

export interface CatchMeUpResponse {
  summary: string;
  key_points: string[];
  missed_decisions: string[];
  action_items_for_you: string[];
}

export interface FollowUpEmailResponse {
  subject: string;
  body: string;
}

export interface SearchResult {
  type: 'meeting' | 'transcript' | 'task' | 'decision';
  id: number;
  title: string;
  excerpt: string;
  meeting_id?: number;
  timestamp?: number;
}

export interface AnalyticsData {
  total_meetings: number;
  total_duration: number;
  total_action_items: number;
  total_decisions: number;
  total_unresolved_questions: number;
  meetings_over_time: Array<{ week: string; count: number }>;
  duration_by_meeting: Array<{ name: string; duration: number }>;
  action_items_by_meeting: Array<{ name: string; count: number }>;
  speaker_participation: Array<{ name: string; speaking_time: number; avatar_color?: string }>;
  decisions_over_time: Array<{ week: string; decisions: number; questions: number }>;
}
