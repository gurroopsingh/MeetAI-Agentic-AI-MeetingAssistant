import type { MeetingAnalysis } from '@/lib/types';
import { AlignLeft, Tag, Activity } from 'lucide-react';

export default function Summary({ analysis }: { analysis: MeetingAnalysis }) {
  if (!analysis) return null;

  return (
    <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
      <section>
        <h3 className="text-lg font-semibold flex items-center gap-2 mb-4">
          <AlignLeft className="w-5 h-5 text-primary" />
          Executive Summary
        </h3>
        <div className="glass-card p-5 text-sm leading-relaxed text-foreground/90 whitespace-pre-wrap">
          {analysis.summary}
        </div>
      </section>

      <div className="grid grid-cols-2 gap-4">
        <div className="glass-card p-4 space-y-2">
          <h4 className="text-sm font-medium text-muted-foreground flex items-center gap-2">
            <Activity className="w-4 h-4" /> Sentiment
          </h4>
          <div className="flex items-center gap-2">
            <span className="capitalize font-semibold text-lg">{analysis.sentiment}</span>
            <div className="flex-1 h-2 bg-muted rounded-full overflow-hidden">
              <div 
                className={`h-full ${
                  analysis.sentiment === 'positive' ? 'bg-green-500' :
                  analysis.sentiment === 'negative' ? 'bg-red-500' : 'bg-yellow-500'
                }`}
                style={{ width: '100%' }}
              />
            </div>
          </div>
        </div>
        
        <div className="glass-card p-4 space-y-2">
          <h4 className="text-sm font-medium text-muted-foreground flex items-center gap-2">
            <Tag className="w-4 h-4" /> Meeting Type
          </h4>
          <p className="font-semibold text-lg capitalize">{analysis.meeting_type?.replace('_', ' ')}</p>
        </div>
      </div>
    </div>
  );
}
