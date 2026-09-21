'use client';
import { useState, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { motion, AnimatePresence } from 'framer-motion';
import { Upload, X, FileVideo, CheckCircle, Loader2, AlertCircle } from 'lucide-react';
import { uploadMeeting } from '@/lib/api';

interface Props {
  open: boolean;
  onClose: () => void;
}

const STAGES = [
  'Uploading',
  'Extracting Audio',
  'Transcribing',
  'Identifying Speakers',
  'Analyzing',
  'Generating Insights',
  'Complete',
];

export function UploadModal({ open, onClose }: Props) {
  const router = useRouter();
  const [dragging, setDragging] = useState(false);
  const [file, setFile] = useState<File | null>(null);
  const [stage, setStage] = useState(-1);
  const [error, setError] = useState<string | null>(null);
  const [meetingId, setMeetingId] = useState<number | null>(null);

  const handleFile = useCallback((f: File) => {
    setFile(f);
    setError(null);
    setStage(-1);
    setMeetingId(null);
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setDragging(false);
    const f = e.dataTransfer.files[0];
    if (f) handleFile(f);
  }, [handleFile]);

  const handleUpload = async () => {
    if (!file) return;
    setStage(0);
    setError(null);

    try {
      // 1. Upload the file
      const meeting = await uploadMeeting(file);
      setMeetingId(meeting.id);
      
      // 2. Poll for status
      let currentMeeting = meeting;
      let mockStageIndex = 1;
      
      while (currentMeeting.status !== 'ready' && currentMeeting.status !== 'failed') {
        // Advance fake stages every few seconds while polling, just for visual feedback
        if (mockStageIndex < STAGES.length - 2) {
           setStage(mockStageIndex);
           mockStageIndex++;
        }
        
        await new Promise(r => setTimeout(r, 2000));
        
        const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/meetings/${meeting.id}`);
        if (res.ok) {
           currentMeeting = await res.json();
        }
      }

      if (currentMeeting.status === 'failed') {
         throw new Error("Processing failed on the server.");
      }

      setStage(STAGES.length - 1);
    } catch (e: any) {
      setError(e.message || 'Upload failed');
      setStage(-1);
    }
  };

  const handleClose = () => {
    if (meetingId) {
      router.push(`/meetings/${meetingId}`);
    }
    setFile(null);
    setStage(-1);
    setError(null);
    setMeetingId(null);
    onClose();
  };

  const isProcessing = stage >= 0 && stage < STAGES.length - 1;
  const isDone = stage === STAGES.length - 1;

  if (!open) return null;

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm"
        onClick={e => { if (e.target === e.currentTarget && !isProcessing) handleClose(); }}
      >
        <motion.div
          initial={{ scale: 0.95, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          exit={{ scale: 0.95, opacity: 0 }}
          className="w-full max-w-lg glass-card p-6 shadow-2xl"
        >
          <div className="flex items-center justify-between mb-6">
            <div>
              <h2 className="text-lg font-semibold">Upload Meeting</h2>
              <p className="text-sm text-muted-foreground">MP4, MOV, or WEBM supported</p>
            </div>
            {!isProcessing && (
              <button onClick={handleClose} className="text-muted-foreground hover:text-foreground transition-colors">
                <X className="w-5 h-5" />
              </button>
            )}
          </div>

          {!file && !isProcessing && !isDone && (
            <div
              onDragOver={e => { e.preventDefault(); setDragging(true); }}
              onDragLeave={() => setDragging(false)}
              onDrop={handleDrop}
              className={`border-2 border-dashed rounded-xl p-10 text-center transition-all cursor-pointer ${
                dragging ? 'border-primary bg-primary/5' : 'border-border hover:border-primary/50 hover:bg-primary/5'
              }`}
              onClick={() => document.getElementById('meeting-file-input')?.click()}
            >
              <Upload className="w-10 h-10 text-muted-foreground mx-auto mb-3" />
              <p className="text-sm font-medium mb-1">Drop your meeting file here</p>
              <p className="text-xs text-muted-foreground">or click to browse</p>
              <input
                id="meeting-file-input"
                type="file"
                className="hidden"
                accept="video/mp4,video/quicktime,video/webm"
                onChange={e => e.target.files?.[0] && handleFile(e.target.files[0])}
              />
            </div>
          )}

          {file && !isProcessing && !isDone && (
            <div className="space-y-4">
              <div className="flex items-center gap-3 p-4 rounded-lg bg-secondary/50 border border-border">
                <FileVideo className="w-8 h-8 text-primary shrink-0" />
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium truncate">{file.name}</p>
                  <p className="text-xs text-muted-foreground">{(file.size / 1024 / 1024).toFixed(1)} MB</p>
                </div>
                <button onClick={() => setFile(null)} className="text-muted-foreground hover:text-foreground">
                  <X className="w-4 h-4" />
                </button>
              </div>
              {error && (
                <div className="flex items-center gap-2 p-3 rounded-lg bg-red-500/10 border border-red-500/20 text-red-400 text-sm">
                  <AlertCircle className="w-4 h-4 shrink-0" />
                  {error}
                </div>
              )}
              <button
                onClick={handleUpload}
                className="w-full py-2.5 rounded-lg gradient-primary text-white text-sm font-medium hover:opacity-90 transition-all"
              >
                Start Processing
              </button>
            </div>
          )}

          {(isProcessing || isDone) && (
            <div className="space-y-3">
              {STAGES.map((s, i) => {
                const done = i < stage || isDone;
                const active = i === stage && !isDone;
                return (
                  <div key={s} className={`flex items-center gap-3 p-3 rounded-lg transition-all ${
                    active ? 'bg-primary/10 border border-primary/20' :
                    done ? 'opacity-60' : 'opacity-30'
                  }`}>
                    {active ? (
                      <Loader2 className="w-4 h-4 text-primary animate-spin shrink-0" />
                    ) : done ? (
                      <CheckCircle className="w-4 h-4 text-green-400 shrink-0" />
                    ) : (
                      <div className="w-4 h-4 rounded-full border border-border shrink-0" />
                    )}
                    <span className={`text-sm ${active ? 'text-primary font-medium' : done ? 'text-foreground' : 'text-muted-foreground'}`}>
                      {s}
                    </span>
                    {active && <span className="text-xs text-primary/70 ml-auto animate-pulse">Processing...</span>}
                    {done && !isDone && <CheckCircle className="w-3 h-3 text-green-400 ml-auto" />}
                  </div>
                );
              })}

              {isDone && (
                <motion.div
                  initial={{ opacity: 0, y: 8 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="mt-4"
                >
                  <button
                    onClick={handleClose}
                    className="w-full py-2.5 rounded-lg gradient-primary text-white text-sm font-medium hover:opacity-90 transition-all"
                  >
                    View Meeting →
                  </button>
                </motion.div>
              )}
            </div>
          )}
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
}
