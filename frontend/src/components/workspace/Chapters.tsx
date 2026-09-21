import { List, Play } from 'lucide-react';
import { formatTimestamp } from '@/lib/utils';

interface ChaptersProps {
  chapters: { title: string; start_time: number; summary?: string }[];
  onSeek: (time: number) => void;
}

export default function Chapters({ chapters, onSeek }: ChaptersProps) {
  if (!chapters || chapters.length === 0) {
    return (
      <div className="text-center py-10 text-muted-foreground">
        <List className="w-10 h-10 mx-auto mb-3 opacity-20" />
        <p>No chapters generated for this meeting.</p>
      </div>
    );
  }

  return (
    <div className="relative pl-6 space-y-8 before:absolute before:inset-y-0 before:left-[11px] before:w-px before:bg-border animate-in fade-in duration-500">
      {chapters.map((chapter, i) => (
        <div key={i} className="relative">
          {/* Timeline dot */}
          <div className="absolute -left-[30px] w-5 h-5 rounded-full bg-background border-2 border-primary flex items-center justify-center z-10">
            <div className="w-1.5 h-1.5 rounded-full bg-primary" />
          </div>
          
          <div className="glass-card p-4 hover:border-primary/30 transition-colors group">
            <div className="flex justify-between items-start mb-2">
              <h4 className="font-semibold text-foreground text-sm group-hover:text-primary transition-colors">
                {chapter.title}
              </h4>
              <button 
                onClick={() => onSeek(chapter.start_time)}
                className="flex items-center gap-1 text-xs font-mono bg-muted text-muted-foreground hover:bg-primary hover:text-primary-foreground px-2 py-1 rounded transition-colors"
              >
                <Play className="w-3 h-3" />
                {formatTimestamp(chapter.start_time)}
              </button>
            </div>
            {chapter.summary && (
              <p className="text-xs text-muted-foreground leading-relaxed mt-2">
                {chapter.summary}
              </p>
            )}
          </div>
        </div>
      ))}
    </div>
  );
}
