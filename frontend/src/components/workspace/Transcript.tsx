'use client';

import { useState, useMemo, useRef } from 'react';
import { Search, User } from 'lucide-react';
import type { TranscriptSegment, Speaker } from '@/lib/types';
import { formatTimestamp, getInitials, cn } from '@/lib/utils';

interface TranscriptProps {
  segments: TranscriptSegment[];
  speakers: Speaker[];
  onSeek: (time: number) => void;
  currentTime?: number;
}

export default function Transcript({ segments, speakers, onSeek, currentTime = 0 }: TranscriptProps) {
  const [searchQuery, setSearchQuery] = useState('');
  const scrollRef = useRef<HTMLDivElement>(null);
  
  const speakerMap = useMemo(() => {
    const map = new Map<string, Speaker>();
    speakers?.forEach(s => map.set(s.id, s));
    return map;
  }, [speakers]);

  const groupedSegments = useMemo(() => {
    if (!segments) return [];
    
    let filtered = segments;
    if (searchQuery) {
      const q = searchQuery.toLowerCase();
      filtered = segments.filter(s => s.text.toLowerCase().includes(q));
    }

    const groups: (TranscriptSegment & { segments: TranscriptSegment[] })[] = [];
    let currentGroup: (TranscriptSegment & { segments: TranscriptSegment[] }) | null = null;

    filtered.forEach(segment => {
      if (searchQuery) {
        // If searching, don't group, just show individual hits
        groups.push({ ...segment, segments: [segment] });
        return;
      }

      if (!currentGroup || currentGroup.speaker_id !== segment.speaker_id || segment.start_time - currentGroup.end_time > 30) {
        currentGroup = { ...segment, segments: [segment] };
        groups.push(currentGroup);
      } else {
        currentGroup.segments.push(segment);
        currentGroup.end_time = segment.end_time;
      }
    });

    return groups;
  }, [segments, searchQuery]);

  return (
    <div className="flex flex-col h-full bg-card">
      <div className="p-4 border-b border-border">
        <div className="relative">
          <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" />
          <input
            type="text"
            placeholder="Search transcript..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full bg-muted/50 border border-border rounded-lg pl-9 pr-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary/50 transition-shadow"
          />
        </div>
      </div>
      
      <div className="flex-1 overflow-y-auto p-4 space-y-6" ref={scrollRef}>
        {groupedSegments.map((group, i) => {
          const speaker = speakerMap.get(group.speaker_id);
          const isActive = currentTime >= group.start_time && currentTime <= group.end_time;
          
          return (
            <div key={i} className={cn("flex gap-4 transition-opacity", !isActive && !searchQuery && "opacity-70 hover:opacity-100")}>
              <div className="flex-none mt-1">
                <div 
                  className="w-8 h-8 rounded-full flex items-center justify-center text-white text-xs font-medium shadow-sm"
                  style={{ backgroundColor: speaker?.avatar_color || '#ccc' }}
                >
                  {speaker ? getInitials(speaker.name) : <User className="w-4 h-4" />}
                </div>
              </div>
              <div className="flex-1 space-y-1">
                <div className="flex items-baseline gap-2">
                  <span className="font-semibold text-sm">{speaker?.name || 'Unknown Speaker'}</span>
                  <button 
                    onClick={() => onSeek(group.start_time)}
                    className="text-xs text-primary/70 hover:text-primary font-mono transition-colors"
                  >
                    {formatTimestamp(group.start_time)}
                  </button>
                </div>
                <div className="space-y-1">
                  {group.segments.map((seg, j) => {
                    const isSegActive = currentTime >= seg.start_time && currentTime <= seg.end_time;
                    return (
                      <p 
                        key={j} 
                        className={cn(
                          "text-sm leading-relaxed cursor-text rounded-md px-1 -mx-1 transition-colors", 
                          isSegActive ? "bg-primary/10 text-foreground" : "text-foreground/90"
                        )}
                        onClick={() => onSeek(seg.start_time)}
                      >
                        {seg.text}
                      </p>
                    );
                  })}
                </div>
              </div>
            </div>
          );
        })}
        {groupedSegments.length === 0 && (
          <div className="text-center py-10 text-muted-foreground">
            No transcript found for your search.
          </div>
        )}
      </div>
    </div>
  );
}
