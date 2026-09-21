'use client';
import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { Video, Search, Filter, Grid, List } from 'lucide-react';
import { getMeetings, deleteMeeting } from '@/lib/api';
import type { Meeting } from '@/lib/types';
import { MeetingCard } from '@/components/meetings/MeetingCard';
import { UploadModal } from '@/components/meetings/UploadModal';
import { toast } from '@/components/ui/Toaster';

type SortKey = 'date' | 'duration' | 'title';
type Filter = 'all' | 'ready' | 'processing';

export default function MeetingsPage() {
  const [meetings, setMeetings] = useState<Meeting[]>([]);
  const [loading, setLoading] = useState(true);
  const [showUpload, setShowUpload] = useState(false);
  const [search, setSearch] = useState('');
  const [sortBy, setSortBy] = useState<SortKey>('date');
  const [filter, setFilter] = useState<Filter>('all');

  const loadMeetings = async () => {
    try {
      const data = await getMeetings();
      setMeetings(data);
    } catch {
      toast('Failed to load meetings', 'error');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { loadMeetings(); }, []);

  const handleDelete = async (id: number) => {
    try {
      await deleteMeeting(id);
      setMeetings(prev => prev.filter(m => m.id !== id));
      toast('Meeting deleted', 'success');
    } catch {
      toast('Failed to delete meeting', 'error');
    }
  };

  const filtered = meetings
    .filter(m => filter === 'all' || m.status === filter)
    .filter(m => !search || m.title.toLowerCase().includes(search.toLowerCase()) || m.summary?.toLowerCase().includes(search.toLowerCase()))
    .sort((a, b) => {
      if (sortBy === 'title') return a.title.localeCompare(b.title);
      if (sortBy === 'duration') return b.duration - a.duration;
      return new Date(b.created_at || 0).getTime() - new Date(a.created_at || 0).getTime();
    });

  return (
    <div className="p-8 max-w-[1400px] mx-auto">
      {/* Header */}
      <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }} className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-bold">Meetings</h1>
          <p className="text-sm text-muted-foreground mt-0.5">{meetings.length} meetings total</p>
        </div>
        <button
          onClick={() => setShowUpload(true)}
          className="flex items-center gap-2 px-4 py-2 rounded-xl gradient-primary text-white text-sm font-medium hover:opacity-90 transition-all shadow-lg shadow-indigo-500/20"
        >
          <Video className="w-4 h-4" /> Upload Meeting
        </button>
      </motion.div>

      {/* Filters */}
      <div className="flex flex-wrap items-center gap-3 mb-6">
        <div className="relative flex-1 min-w-[200px] max-w-xs">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
          <input
            value={search}
            onChange={e => setSearch(e.target.value)}
            placeholder="Search meetings..."
            className="w-full bg-secondary/50 border border-border/50 rounded-lg pl-9 pr-4 py-2 text-sm placeholder:text-muted-foreground focus:outline-none focus:ring-1 focus:ring-primary/50"
          />
        </div>

        <div className="flex rounded-lg border border-border overflow-hidden">
          {(['all', 'ready', 'processing'] as Filter[]).map(f => (
            <button
              key={f}
              onClick={() => setFilter(f)}
              className={`px-3 py-1.5 text-xs font-medium capitalize transition-colors ${filter === f ? 'bg-primary text-white' : 'text-muted-foreground hover:text-foreground bg-secondary/50'}`}
            >
              {f}
            </button>
          ))}
        </div>

        <select
          value={sortBy}
          onChange={e => setSortBy(e.target.value as SortKey)}
          className="bg-secondary/50 border border-border/50 rounded-lg px-3 py-2 text-sm text-foreground focus:outline-none focus:ring-1 focus:ring-primary/50"
        >
          <option value="date">Sort by Date</option>
          <option value="duration">Sort by Duration</option>
          <option value="title">Sort by Title</option>
        </select>
      </div>

      {/* Grid */}
      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-5">
          {[...Array(6)].map((_, i) => (
            <div key={i} className="glass-card p-5 h-52 animate-pulse bg-secondary/20" />
          ))}
        </div>
      ) : filtered.length === 0 ? (
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="text-center py-24">
          <Video className="w-16 h-16 text-muted-foreground/30 mx-auto mb-4" />
          <p className="text-lg font-medium text-muted-foreground mb-2">
            {search || filter !== 'all' ? 'No meetings match your filters' : 'No meetings yet'}
          </p>
          <p className="text-sm text-muted-foreground mb-6">
            {search || filter !== 'all' ? 'Try adjusting your search or filters' : 'Upload your first meeting to get started'}
          </p>
          {!search && filter === 'all' && (
            <button
              onClick={() => setShowUpload(true)}
              className="px-4 py-2 rounded-xl gradient-primary text-white text-sm font-medium hover:opacity-90 transition-all"
            >
              Upload Meeting
            </button>
          )}
        </motion.div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-5">
          {filtered.map((m, i) => (
            <MeetingCard key={m.id} meeting={m} onDelete={handleDelete} index={i} />
          ))}
        </div>
      )}

      <UploadModal open={showUpload} onClose={() => { setShowUpload(false); loadMeetings(); }} />
    </div>
  );
}
