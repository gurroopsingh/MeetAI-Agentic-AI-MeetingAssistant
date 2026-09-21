'use client';

import { forwardRef, useImperativeHandle, useRef, useState } from 'react';
import { Video } from 'lucide-react';
import { formatTimestamp } from '@/lib/utils';

interface VideoPlayerProps {
  videoUrl?: string;
  onTimeUpdate?: (currentTime: number) => void;
}

export interface VideoPlayerRef {
  seekTo: (time: number) => void;
}

const VideoPlayer = forwardRef<VideoPlayerRef, VideoPlayerProps>(({ videoUrl, onTimeUpdate }, ref) => {
  const videoRef = useRef<HTMLVideoElement>(null);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);

  useImperativeHandle(ref, () => ({
    seekTo: (time: number) => {
      if (videoRef.current) {
        videoRef.current.currentTime = time;
        videoRef.current.play().catch(() => {
          // Ignore auto-play restriction errors if any
        });
      }
    }
  }));

  const handleTimeUpdate = () => {
    if (videoRef.current) {
      const time = videoRef.current.currentTime;
      setCurrentTime(time);
      if (onTimeUpdate) {
        onTimeUpdate(time);
      }
    }
  };

  const handleLoadedMetadata = () => {
    if (videoRef.current) {
      setDuration(videoRef.current.duration);
    }
  };

  if (!videoUrl) {
    return (
      <div className="w-full aspect-video bg-black/90 rounded-xl flex flex-col items-center justify-center text-muted-foreground border border-border shadow-inner">
        <Video className="w-12 h-12 mb-4 opacity-50" />
        <p className="font-medium">No video file available</p>
        <p className="text-sm opacity-70">This meeting was audio-only or video is still processing.</p>
      </div>
    );
  }

  return (
    <div className="relative w-full aspect-video bg-black rounded-xl overflow-hidden group shadow-md border border-border/50">
      <video
        ref={videoRef}
        src={videoUrl}
        className="w-full h-full object-contain"
        controls
        onTimeUpdate={handleTimeUpdate}
        onLoadedMetadata={handleLoadedMetadata}
      />
      <div className="absolute top-4 left-4 bg-black/60 backdrop-blur-md px-3 py-1.5 rounded-full text-white text-sm font-mono opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none border border-white/10">
        {formatTimestamp(currentTime)} / {formatTimestamp(duration)}
      </div>
    </div>
  );
});

VideoPlayer.displayName = 'VideoPlayer';

export default VideoPlayer;
