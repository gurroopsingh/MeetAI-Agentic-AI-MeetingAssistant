import type { Speaker } from '@/lib/types';
import { CheckCircle2, Circle, Clock, Link as LinkIcon } from 'lucide-react';
import { formatTimestamp, getPriorityColor, cn } from '@/lib/utils';

interface ActionItemsProps {
  actionItems: { task: string; assignee?: string; deadline?: string; priority?: string; status?: string; timestamp?: number }[];
  speakers?: Speaker[];
  onSeek: (time: number) => void;
}

export default function ActionItemsPanel({ actionItems, speakers, onSeek }: ActionItemsProps) {
  if (!actionItems || actionItems.length === 0) {
    return (
      <div className="text-center py-10 text-muted-foreground">
        <CheckCircle2 className="w-10 h-10 mx-auto mb-3 opacity-20" />
        <p>No action items were assigned in this meeting.</p>
      </div>
    );
  }

  return (
    <div className="space-y-4 animate-in fade-in duration-500">
      {actionItems.map((item, i) => {
        const isDone = item.status === 'completed';
        return (
          <div key={i} className={cn(
            "glass-card p-4 transition-all",
            isDone ? "opacity-60" : "hover:border-primary/30"
          )}>
            <div className="flex items-start gap-3">
              <button className="mt-0.5 text-muted-foreground hover:text-primary transition-colors flex-none">
                {isDone ? <CheckCircle2 className="w-5 h-5 text-primary" /> : <Circle className="w-5 h-5" />}
              </button>
              
              <div className="flex-1 space-y-3">
                <div>
                  <p className={cn("text-sm font-medium", isDone && "line-through text-muted-foreground")}>
                    {item.task}
                  </p>
                </div>
                
                <div className="flex flex-wrap items-center gap-2 text-xs">
                  {item.assignee && (
                    <span className="px-2.5 py-1 rounded-full bg-primary/10 text-primary font-medium">
                      @ {item.assignee}
                    </span>
                  )}
                  {item.deadline && (
                    <span className="flex items-center gap-1 text-muted-foreground bg-muted px-2 py-1 rounded-full">
                      <Clock className="w-3 h-3" />
                      {item.deadline}
                    </span>
                  )}
                  {item.priority && (
                    <span className={cn(
                      "px-2 py-1 rounded-full font-semibold uppercase text-[10px]",
                      getPriorityColor(item.priority)
                    )}>
                      {item.priority}
                    </span>
                  )}
                  
                  {item.timestamp !== undefined && (
                    <button 
                      onClick={() => onSeek(item.timestamp)}
                      className="ml-auto flex items-center gap-1 text-muted-foreground hover:text-primary transition-colors font-mono"
                    >
                      <LinkIcon className="w-3 h-3" />
                      {formatTimestamp(item.timestamp)}
                    </button>
                  )}
                </div>
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}
