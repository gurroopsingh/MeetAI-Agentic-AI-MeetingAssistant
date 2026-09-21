import type { Speaker } from '@/lib/types';
import { CheckSquare, Link as LinkIcon } from 'lucide-react';
import { formatTimestamp, getInitials, cn } from '@/lib/utils';

interface DecisionsProps {
  decisions: { text: string; importance?: string; speaker_id?: string; timestamp?: number }[];
  speakers: Speaker[];
  onSeek: (time: number) => void;
}

export default function Decisions({ decisions, speakers, onSeek }: DecisionsProps) {
  if (!decisions || decisions.length === 0) {
    return (
      <div className="text-center py-10 text-muted-foreground">
        <CheckSquare className="w-10 h-10 mx-auto mb-3 opacity-20" />
        <p>No decisions were recorded in this meeting.</p>
      </div>
    );
  }

  return (
    <div className="space-y-4 animate-in fade-in duration-500">
      {decisions.map((decision, i) => {
        const speaker = speakers?.find(s => s.id === decision.speaker_id);
        return (
          <div key={i} className="glass-card p-4 hover:border-primary/30 transition-colors">
            <div className="flex items-start justify-between gap-4">
              <p className="text-sm font-medium leading-relaxed flex-1">
                {decision.text}
              </p>
              {decision.importance && (
                <span className={cn(
                  "px-2 py-1 text-[10px] font-bold uppercase rounded-full whitespace-nowrap",
                  decision.importance === 'high' ? "bg-red-500/10 text-red-500" :
                  decision.importance === 'medium' ? "bg-yellow-500/10 text-yellow-600 dark:text-yellow-400" :
                  "bg-blue-500/10 text-blue-500"
                )}>
                  {decision.importance}
                </span>
              )}
            </div>
            
            <div className="mt-4 flex items-center justify-between text-xs text-muted-foreground">
              <div className="flex items-center gap-2">
                {speaker && (
                  <div className="flex items-center gap-1.5 bg-muted px-2 py-1 rounded-full">
                    <div 
                      className="w-4 h-4 rounded-full flex items-center justify-center text-white text-[8px]"
                      style={{ backgroundColor: speaker.avatar_color }}
                    >
                      {getInitials(speaker.name)}
                    </div>
                    <span className="font-medium text-foreground">{speaker.name}</span>
                  </div>
                )}
              </div>
              {decision.timestamp !== undefined && (
                <button 
                  onClick={() => onSeek(decision.timestamp)}
                  className="flex items-center gap-1 hover:text-primary transition-colors font-mono"
                >
                  <LinkIcon className="w-3 h-3" />
                  {formatTimestamp(decision.timestamp)}
                </button>
              )}
            </div>
          </div>
        );
      })}
    </div>
  );
}
