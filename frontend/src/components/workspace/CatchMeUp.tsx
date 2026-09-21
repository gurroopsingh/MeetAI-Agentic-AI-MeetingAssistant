'use client';

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Clock, Loader2, Sparkles, CheckCircle } from 'lucide-react';
import { catchMeUp } from '@/lib/api';
import { formatTimestamp } from '@/lib/utils';

interface CatchMeUpProps {
  meetingId: number;
  onClose: () => void;
}

export default function CatchMeUp({ meetingId, onClose }: CatchMeUpProps) {
  const [joinedAt, setJoinedAt] = useState(0);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<{ summary: string; key_points?: string[]; missed_decisions?: string[] } | null>(null);

  const handleCatchUp = async () => {
    setLoading(true);
    try {
      const data = await catchMeUp(meetingId, joinedAt);
      setResult(data);
    } catch (error) {
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <AnimatePresence>
      <motion.div 
        initial={{ x: '100%', opacity: 0.5 }}
        animate={{ x: 0, opacity: 1 }}
        exit={{ x: '100%', opacity: 0 }}
        transition={{ type: 'spring', damping: 25, stiffness: 200 }}
        className="absolute inset-y-0 right-0 w-full max-w-sm bg-background border-l border-border shadow-2xl flex flex-col z-20"
      >
        <div className="flex items-center justify-between p-4 border-b border-border bg-card/50 backdrop-blur-sm">
          <h2 className="font-semibold text-lg flex items-center gap-2">
            Catch Me Up <Sparkles className="w-4 h-4 text-primary" />
          </h2>
          <button onClick={onClose} className="p-2 hover:bg-muted rounded-full transition-colors text-muted-foreground">
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="flex-1 overflow-y-auto p-4">
          {!result ? (
            <div className="space-y-6 mt-4">
              <div className="p-4 bg-muted/50 rounded-xl border border-border space-y-4">
                <label className="text-sm font-medium flex justify-between">
                  <span>I joined the meeting at:</span>
                  <span className="text-primary font-mono bg-primary/10 px-2 py-0.5 rounded">{formatTimestamp(joinedAt)}</span>
                </label>
                <input 
                  type="range" 
                  min="0" 
                  max="3600" // Should ideally be meeting duration, mocked for now
                  step="30"
                  value={joinedAt}
                  onChange={(e) => setJoinedAt(Number(e.target.value))}
                  className="w-full accent-primary"
                />
                <p className="text-xs text-muted-foreground">Adjust the slider to the time you joined to get a summary of what you missed.</p>
              </div>
              
              <button 
                onClick={handleCatchUp}
                disabled={loading}
                className="w-full flex items-center justify-center gap-2 bg-primary text-primary-foreground py-3 rounded-lg font-medium hover:bg-primary/90 transition-colors disabled:opacity-70"
              >
                {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : <Clock className="w-5 h-5" />}
                Generate Catch-Up Summary
              </button>
            </div>
          ) : (
            <motion.div 
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className="space-y-6"
            >
              <div className="bg-primary/5 border border-primary/20 rounded-xl p-4">
                <h3 className="font-semibold text-primary mb-2 flex items-center gap-2">
                  <Sparkles className="w-4 h-4" /> 
                  Summary of what you missed
                </h3>
                <p className="text-sm leading-relaxed text-foreground/90">{result.summary}</p>
              </div>

              {result.key_points && result.key_points.length > 0 && (
                <div>
                  <h4 className="font-medium text-sm text-muted-foreground mb-3 uppercase tracking-wider">Key Points Discussed</h4>
                  <ul className="space-y-2">
                    {result.key_points.map((pt: string, i: number) => (
                      <li key={i} className="flex gap-2 text-sm bg-card border border-border p-3 rounded-lg shadow-sm">
                        <span className="text-primary mt-0.5">•</span>
                        <span>{pt}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {result.missed_decisions && result.missed_decisions.length > 0 && (
                <div>
                  <h4 className="font-medium text-sm text-muted-foreground mb-3 uppercase tracking-wider">Decisions Made</h4>
                  <ul className="space-y-2">
                    {result.missed_decisions.map((dec: string, i: number) => (
                      <li key={i} className="flex gap-2 text-sm bg-green-500/10 border border-green-500/20 text-green-700 dark:text-green-400 p-3 rounded-lg">
                        <CheckCircle className="w-4 h-4 mt-0.5 flex-none" />
                        <span>{dec}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
              
              <button 
                onClick={() => setResult(null)}
                className="w-full py-2 text-sm text-muted-foreground hover:text-foreground hover:bg-muted rounded-lg transition-colors"
              >
                Start Over
              </button>
            </motion.div>
          )}
        </div>
      </motion.div>
    </AnimatePresence>
  );
}
