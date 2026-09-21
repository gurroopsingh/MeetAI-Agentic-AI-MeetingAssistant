'use client';

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Send, Loader2, Link as LinkIcon } from 'lucide-react';
import { askMeeting } from '@/lib/api';
import { formatTimestamp, cn } from '@/lib/utils';

interface AskMeetingProps {
  meetingId: number;
  onClose: () => void;
  onSeek: (time: number) => void;
}

interface Message {
  id: string;
  role: 'user' | 'ai';
  content: string;
  citations?: { speaker: string; time: number }[];
}

export default function AskMeeting({ meetingId, onClose, onSeek }: AskMeetingProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const SUGGESTIONS = [
    "What were the main decisions made?",
    "What is my action items?",
    "Did they discuss the Q3 budget?"
  ];

  const handleSend = async (text: string) => {
    if (!text.trim() || isLoading) return;
    
    const userMsg: Message = { id: crypto.randomUUID(), role: 'user', content: text };
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await askMeeting(meetingId, text);
      const aiMsg: Message = {
        id: crypto.randomUUID(),
        role: 'ai',
        content: response.answer,
        citations: response.citations
      };
      setMessages(prev => [...prev, aiMsg]);
    } catch {
      const errorMsg: Message = { id: crypto.randomUUID(), role: 'ai', content: "Sorry, I couldn't get an answer. Please try again." };
      setMessages(prev => [...prev, errorMsg]);
    } finally {
      setIsLoading(false);
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
            Ask Meeting <span className="px-2 py-0.5 rounded-full bg-primary/20 text-primary text-xs font-bold">AI</span>
          </h2>
          <button onClick={onClose} className="p-2 hover:bg-muted rounded-full transition-colors text-muted-foreground">
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.length === 0 ? (
            <div className="h-full flex flex-col items-center justify-center text-center space-y-6 text-muted-foreground mt-8">
              <div className="p-4 bg-muted rounded-full">
                <Send className="w-8 h-8 text-primary" />
              </div>
              <p className="text-sm px-4">Ask anything about the meeting. I&apos;ll search the transcript and find answers.</p>
              <div className="w-full space-y-2">
                {SUGGESTIONS.map((s, i) => (
                  <button 
                    key={i}
                    onClick={() => handleSend(s)}
                    className="w-full text-left p-3 rounded-lg border border-border bg-card hover:bg-muted hover:border-primary/30 transition-all text-sm"
                  >
                    {s}
                  </button>
                ))}
              </div>
            </div>
          ) : (
            messages.map((msg) => (
              <div key={msg.id} className={cn("flex flex-col max-w-[85%]", msg.role === 'user' ? "ml-auto items-end" : "mr-auto items-start")}>
                <div className={cn(
                  "p-3 rounded-2xl shadow-sm text-sm",
                  msg.role === 'user' 
                    ? "bg-primary text-primary-foreground rounded-br-none" 
                    : "bg-card border border-border rounded-bl-none text-foreground"
                )}>
                  {msg.content}
                </div>
                {msg.citations && msg.citations.length > 0 && (
                  <div className="flex flex-wrap gap-1 mt-1.5 px-1">
                    {msg.citations.map((cite, i) => (
                      <button
                        key={i}
                        onClick={() => onSeek(cite.time)}
                        className="flex items-center gap-1 text-[10px] bg-muted hover:bg-primary/10 text-muted-foreground hover:text-primary px-2 py-0.5 rounded-full transition-colors font-mono"
                      >
                        <LinkIcon className="w-3 h-3" />
                        {cite.speaker} &bull; {formatTimestamp(cite.time)}
                      </button>
                    ))}
                  </div>
                )}
              </div>
            ))
          )}
          {isLoading && (
            <div className="flex items-center gap-2 text-muted-foreground text-sm p-2">
              <Loader2 className="w-4 h-4 animate-spin text-primary" />
              Thinking...
            </div>
          )}
        </div>

        <div className="p-4 border-t border-border bg-card/50 backdrop-blur-sm">
          <form 
            onSubmit={(e) => { e.preventDefault(); handleSend(input); }}
            className="relative flex items-center"
          >
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask a question..."
              className="w-full bg-background border border-border rounded-full pl-4 pr-12 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-primary/50 transition-shadow"
            />
            <button 
              type="submit"
              disabled={!input.trim() || isLoading}
              className="absolute right-2 p-2 bg-primary text-primary-foreground rounded-full hover:bg-primary/90 disabled:opacity-50 disabled:hover:bg-primary transition-colors"
            >
              <Send className="w-4 h-4" />
            </button>
          </form>
        </div>
      </motion.div>
    </AnimatePresence>
  );
}
