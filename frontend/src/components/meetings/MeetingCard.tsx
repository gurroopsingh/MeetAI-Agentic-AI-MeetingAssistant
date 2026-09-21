'use client';
import { useState } from 'react';
import { motion } from 'framer-motion';
import { Play, Clock, Users, CheckSquare, MoreHorizontal, Trash2, Eye } from 'lucide-react';
import Link from 'next/link';
import type { Meeting } from '@/lib/types';
import { formatDuration, formatRelativeTime, getStatusColor, cn } from '@/lib/utils';

interface Props {
  meeting: Meeting;
  onDelete?: (id: number) => void;
  index?: number;
}

export function MeetingCard({ meeting, onDelete, index = 0 }: Props) {
  const [showMenu, setShowMenu] = useState(false);
  const topics = (() => {
    try { return JSON.parse(meeting.key_topics || '[]') as string[]; }
    catch { return []; }
  })();

  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.05 }}
      whileHover={{ y: -2 }}
      className="glass-card p-5 hover:border-primary/30 transition-all duration-300 group relative"
    >
      {/* Status + menu */}
      <div className="flex items-start justify-between mb-3">
        <span className={cn('text-[10px] font-semibold px-2 py-0.5 rounded-full border capitalize', getStatusColor(meeting.status))}>
          {meeting.status}
        </span>
        <div className="relative">
          <button
            onClick={() => setShowMenu(!showMenu)}
            className="w-7 h-7 rounded-lg opacity-0 group-hover:opacity-100 bg-secondary/80 flex items-center justify-center text-muted-foreground hover:text-foreground transition-all"
          >
            <MoreHorizontal className="w-4 h-4" />
          </button>
          {showMenu && (
            <div className="absolute right-0 top-8 w-40 rounded-lg border border-border bg-popover shadow-xl z-10 py-1">
              <Link href={`/meetings/${meeting.id}`}>
                <button className="w-full text-left px-3 py-2 text-sm hover:bg-secondary/50 flex items-center gap-2 transition-colors">
                  <Eye className="w-3.5 h-3.5" /> View Meeting
                </button>
              </Link>
              {onDelete && (
                <button
                  onClick={() => { onDelete(meeting.id); setShowMenu(false); }}
                  className="w-full text-left px-3 py-2 text-sm hover:bg-secondary/50 text-red-400 flex items-center gap-2 transition-colors"
                >
                  <Trash2 className="w-3.5 h-3.5" /> Delete
                </button>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Title */}
      <Link href={`/meetings/${meeting.id}`}>
        <h3 className="font-semibold text-base mb-1 hover:text-primary transition-colors line-clamp-2 cursor-pointer">
          {meeting.title}
        </h3>
      </Link>

      {/* Meta */}
      <div className="flex items-center gap-3 text-xs text-muted-foreground mb-3">
        <span className="flex items-center gap-1"><Clock className="w-3 h-3" />{formatDuration(meeting.duration)}</span>
        <span>{formatRelativeTime(meeting.created_at)}</span>
        {meeting.meeting_type && <span className="text-primary/70">{meeting.meeting_type}</span>}
      </div>

      {/* Summary */}
      {meeting.summary && (
        <p className="text-xs text-muted-foreground line-clamp-2 mb-3 leading-relaxed">{meeting.summary}</p>
      )}

      {/* Topics */}
      {topics.length > 0 && (
        <div className="flex flex-wrap gap-1">
          {topics.slice(0, 3).map(t => (
            <span key={t} className="text-[10px] px-2 py-0.5 rounded-full bg-primary/10 text-primary/80 border border-primary/20">
              {t}
            </span>
          ))}
          {topics.length > 3 && (
            <span className="text-[10px] px-2 py-0.5 rounded-full bg-secondary text-muted-foreground">+{topics.length - 3}</span>
          )}
        </div>
      )}

      {/* Footer */}
      <div className="flex items-center justify-between mt-4 pt-3 border-t border-border/50">
        <Link href={`/meetings/${meeting.id}`}>
          <button className="flex items-center gap-1.5 text-xs text-primary hover:text-primary/80 font-medium transition-colors">
            <Play className="w-3 h-3" /> Open Workspace
          </button>
        </Link>
        {meeting.sentiment && (
          <span className={`text-[10px] font-medium ${
            meeting.sentiment === 'positive' ? 'text-green-400' :
            meeting.sentiment === 'negative' ? 'text-red-400' : 'text-muted-foreground'
          }`}>
            {meeting.sentiment}
          </span>
        )}
      </div>
    </motion.div>
  );
}
