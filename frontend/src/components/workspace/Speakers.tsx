import type { Speaker } from '@/lib/types';
import { Users, Mic, Type } from 'lucide-react';
import { getInitials, formatDuration } from '@/lib/utils';

export default function Speakers({ speakers }: { speakers: Speaker[] }) {
  if (!speakers || speakers.length === 0) {
    return (
      <div className="text-center py-10 text-muted-foreground">
        <Users className="w-10 h-10 mx-auto mb-3 opacity-20" />
        <p>No speakers identified.</p>
      </div>
    );
  }

  // Calculate total speaking time to show relative progress bars
  const totalTime = speakers.reduce((acc, s) => acc + (s.speaking_time || 0), 0);

  return (
    <div className="space-y-4 animate-in fade-in duration-500">
      {speakers.map((speaker, i) => {
        const percentage = totalTime > 0 ? ((speaker.speaking_time || 0) / totalTime) * 100 : 0;
        
        return (
          <div key={i} className="glass-card p-4 flex flex-col gap-4">
            <div className="flex items-center gap-4">
              <div 
                className="w-12 h-12 rounded-full flex items-center justify-center text-white text-lg font-semibold shadow-md flex-none"
                style={{ backgroundColor: speaker.avatar_color || '#ccc' }}
              >
                {getInitials(speaker.name)}
              </div>
              <div className="flex-1 min-w-0">
                <h4 className="font-semibold text-foreground truncate">{speaker.name}</h4>
                {speaker.role && (
                  <p className="text-xs text-muted-foreground truncate">{speaker.role}</p>
                )}
              </div>
              
              <div className="flex flex-col items-end gap-1 text-xs text-muted-foreground whitespace-nowrap">
                <span className="flex items-center gap-1">
                  <Mic className="w-3 h-3" /> {formatDuration(speaker.speaking_time || 0)}
                </span>
                <span className="flex items-center gap-1">
                  <Type className="w-3 h-3" /> {speaker.word_count || 0} words
                </span>
              </div>
            </div>
            
            <div className="space-y-1">
              <div className="flex justify-between text-[10px] text-muted-foreground">
                <span>Talk Time</span>
                <span>{Math.round(percentage)}%</span>
              </div>
              <div className="w-full h-1.5 bg-muted rounded-full overflow-hidden">
                <div 
                  className="h-full rounded-full transition-all duration-1000"
                  style={{ 
                    width: `${percentage}%`,
                    backgroundColor: speaker.avatar_color || 'var(--primary)' 
                  }}
                />
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}
