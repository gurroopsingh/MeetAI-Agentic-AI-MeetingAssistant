// API Client — typed fetch wrapper for MeetAI backend
import type {
  Meeting, MeetingDetail, MeetingAnalysis, TranscriptSegment,
  Task, TaskUpdate, AskResponse, CatchMeUpResponse,
  FollowUpEmailResponse, SearchResult, AnalyticsData,
} from './types';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

async function apiFetch<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { 'Content-Type': 'application/json', ...options?.headers },
    ...options,
  });
  if (!res.ok) {
    const error = await res.text();
    throw new Error(`API Error ${res.status}: ${error}`);
  }
  return res.json();
}

// ── Meetings ──────────────────────────────────────────────────────────────

export async function getMeetings(): Promise<Meeting[]> {
  return apiFetch<Meeting[]>('/api/meetings');
}

export async function getMeeting(id: number): Promise<MeetingDetail> {
  return apiFetch<MeetingDetail>(`/api/meetings/${id}`);
}

export async function getMeetingTranscript(id: number): Promise<TranscriptSegment[]> {
  return apiFetch<TranscriptSegment[]>(`/api/meetings/${id}/transcript`);
}

export async function getMeetingAnalysis(id: number): Promise<MeetingAnalysis> {
  return apiFetch<MeetingAnalysis>(`/api/meetings/${id}/analysis`);
}

export async function uploadMeeting(file: File): Promise<Meeting> {
  const formData = new FormData();
  formData.append('file', file);
  const res = await fetch(`${API_BASE}/api/meetings/upload`, {
    method: 'POST',
    body: formData,
  });
  if (!res.ok) throw new Error(`Upload failed: ${res.statusText}`);
  return res.json();
}

export async function deleteMeeting(id: number): Promise<void> {
  await apiFetch(`/api/meetings/${id}`, { method: 'DELETE' });
}

export async function askMeeting(id: number, question: string): Promise<AskResponse> {
  return apiFetch<AskResponse>(`/api/meetings/${id}/ask`, {
    method: 'POST',
    body: JSON.stringify({ question }),
  });
}

export async function catchMeUp(id: number, fromTimestamp?: number): Promise<CatchMeUpResponse> {
  return apiFetch<CatchMeUpResponse>(`/api/meetings/${id}/catch-up`, {
    method: 'POST',
    body: JSON.stringify({ from_timestamp: fromTimestamp }),
  });
}

export async function generateFollowUp(
  id: number,
  recipientName?: string,
  additionalNotes?: string,
): Promise<FollowUpEmailResponse> {
  return apiFetch<FollowUpEmailResponse>(`/api/meetings/${id}/follow-up`, {
    method: 'POST',
    body: JSON.stringify({ recipient_name: recipientName, additional_notes: additionalNotes }),
  });
}

// ── Tasks ────────────────────────────────────────────────────────────────

export async function getTasks(params?: { status?: string; meeting_id?: number }): Promise<Task[]> {
  const qs = new URLSearchParams();
  if (params?.status) qs.set('status', params.status);
  if (params?.meeting_id) qs.set('meeting_id', String(params.meeting_id));
  return apiFetch<Task[]>(`/api/tasks${qs.toString() ? `?${qs}` : ''}`);
}

export async function updateTask(id: number, update: Partial<Pick<Task, 'status' | 'priority' | 'assignee' | 'deadline'>>): Promise<Task> {
  return apiFetch<Task>(`/api/tasks/${id}`, {
    method: 'PATCH',
    body: JSON.stringify(update),
  });
}

// ── Search ────────────────────────────────────────────────────────────────

export async function search(q: string): Promise<{ results: SearchResult[]; total: number }> {
  return apiFetch<{ results: SearchResult[]; total: number }>(`/api/search?q=${encodeURIComponent(q)}`);
}

// ── Analytics ─────────────────────────────────────────────────────────────

export async function getAnalytics(): Promise<AnalyticsData> {
  return apiFetch<AnalyticsData>('/api/analytics');
}
