'use client';

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Mail, Loader2, Copy, Check } from 'lucide-react';
import { generateFollowUp } from '@/lib/api';

interface FollowUpEmailProps {
  meetingId: number;
  onClose: () => void;
}

export default function FollowUpEmail({ meetingId, onClose }: FollowUpEmailProps) {
  const [recipient, setRecipient] = useState('');
  const [loading, setLoading] = useState(false);
  const [emailData, setEmailData] = useState<{ subject: string; body: string } | null>(null);
  const [copied, setCopied] = useState(false);

  const handleGenerate = async () => {
    setLoading(true);
    try {
      const data = await generateFollowUp(meetingId, recipient || undefined);
      setEmailData(data);
      setCopied(false);
    } catch (error) {
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const handleCopy = () => {
    if (!emailData) return;
    const text = `Subject: ${emailData.subject}\n\n${emailData.body}`;
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <AnimatePresence>
      <motion.div 
        initial={{ x: '100%', opacity: 0.5 }}
        animate={{ x: 0, opacity: 1 }}
        exit={{ x: '100%', opacity: 0 }}
        transition={{ type: 'spring', damping: 25, stiffness: 200 }}
        className="absolute inset-y-0 right-0 w-full max-w-lg bg-background border-l border-border shadow-2xl flex flex-col z-20"
      >
        <div className="flex items-center justify-between p-4 border-b border-border bg-card/50 backdrop-blur-sm">
          <h2 className="font-semibold text-lg flex items-center gap-2">
            Follow-Up Email
          </h2>
          <button onClick={onClose} className="p-2 hover:bg-muted rounded-full transition-colors text-muted-foreground">
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="flex-1 overflow-y-auto p-4 flex flex-col">
          {!emailData ? (
            <div className="space-y-6 mt-4 flex-1">
              <div className="space-y-2">
                <label className="text-sm font-medium">Recipient Name (Optional)</label>
                <input 
                  type="text" 
                  placeholder="e.g. Team, John, Clients"
                  value={recipient}
                  onChange={(e) => setRecipient(e.target.value)}
                  className="w-full bg-card border border-border rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-primary/50 transition-shadow"
                />
              </div>
              
              <button 
                onClick={handleGenerate}
                disabled={loading}
                className="w-full flex items-center justify-center gap-2 bg-primary text-primary-foreground py-3 rounded-lg font-medium hover:bg-primary/90 transition-colors disabled:opacity-70"
              >
                {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : <Mail className="w-5 h-5" />}
                Generate Draft
              </button>
            </div>
          ) : (
            <motion.div 
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className="flex flex-col h-full space-y-4"
            >
              <div className="space-y-1">
                <label className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">Subject</label>
                <div className="p-3 bg-muted/50 rounded-lg border border-border text-sm font-medium">
                  {emailData.subject}
                </div>
              </div>
              <div className="space-y-1 flex-1 flex flex-col">
                <label className="text-xs font-semibold text-muted-foreground uppercase tracking-wider flex justify-between items-center">
                  <span>Body</span>
                  <button 
                    onClick={handleCopy}
                    className="flex items-center gap-1 text-primary hover:text-primary/80 transition-colors px-2 py-1 rounded bg-primary/10"
                  >
                    {copied ? <Check className="w-3 h-3" /> : <Copy className="w-3 h-3" />}
                    {copied ? 'Copied!' : 'Copy All'}
                  </button>
                </label>
                <textarea 
                  readOnly
                  value={emailData.body}
                  className="flex-1 w-full bg-card border border-border rounded-lg p-4 text-sm font-mono leading-relaxed focus:outline-none resize-none"
                />
              </div>
              <button 
                onClick={() => setEmailData(null)}
                className="w-full py-2 text-sm text-muted-foreground hover:text-foreground hover:bg-muted rounded-lg transition-colors"
              >
                Discard & Regenerate
              </button>
            </motion.div>
          )}
        </div>
      </motion.div>
    </AnimatePresence>
  );
}
