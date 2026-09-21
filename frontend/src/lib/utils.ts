import { type ClassValue, clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatDuration(seconds: number): string {
  if (!seconds) return '0:00';
  const h = Math.floor(seconds / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  const s = Math.floor(seconds % 60);
  if (h > 0) return `${h}:${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
  return `${m}:${s.toString().padStart(2, '0')}`;
}

export function formatTimestamp(seconds: number): string {
  return formatDuration(seconds);
}

export function formatDate(dateString?: string): string {
  if (!dateString) return 'Unknown date';
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  });
}

export function formatRelativeTime(dateString?: string): string {
  if (!dateString) return '';
  const date = new Date(dateString);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));
  
  if (diffHours < 1) return 'Just now';
  if (diffHours < 24) return `${diffHours}h ago`;
  if (diffDays < 7) return `${diffDays}d ago`;
  return formatDate(dateString);
}

export function getInitials(name: string): string {
  return name
    .split(' ')
    .map((n) => n[0])
    .join('')
    .toUpperCase()
    .slice(0, 2);
}

export function getPriorityColor(priority: string): string {
  switch (priority) {
    case 'high': return 'text-red-400 bg-red-500/10 border-red-500/20';
    case 'medium': return 'text-amber-400 bg-amber-500/10 border-amber-500/20';
    case 'low': return 'text-green-400 bg-green-500/10 border-green-500/20';
    default: return 'text-muted-foreground';
  }
}

export function getStatusColor(status: string): string {
  switch (status) {
    case 'todo': return 'text-slate-400 bg-slate-500/10 border-slate-500/20';
    case 'in_progress': return 'text-blue-400 bg-blue-500/10 border-blue-500/20';
    case 'done': return 'text-green-400 bg-green-500/10 border-green-500/20';
    case 'ready': return 'text-green-400 bg-green-500/10';
    case 'processing': return 'text-amber-400 bg-amber-500/10';
    case 'failed': return 'text-red-400 bg-red-500/10';
    default: return '';
  }
}
