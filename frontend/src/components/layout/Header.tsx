'use client';
import { useState, useCallback, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Search, Bell, Moon, Sun, User, Upload } from 'lucide-react';
import { useTheme } from 'next-themes';
import { motion, AnimatePresence } from 'framer-motion';
import { search } from '@/lib/api';
import type { SearchResult } from '@/lib/types';
import { formatTimestamp } from '@/lib/utils';
import { UploadModal } from '@/components/meetings/UploadModal';

export function Header() {
  const { theme, setTheme } = useTheme();
  const router = useRouter();
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<SearchResult[]>([]);
  const [searching, setSearching] = useState(false);
  const [showUpload, setShowUpload] = useState(false);
  const [showSearch, setShowSearch] = useState(false);
  // Prevent hydration mismatch: only render theme-dependent icon after mount
  const [mounted, setMounted] = useState(false);
  useEffect(() => { setMounted(true); }, []);

  const handleSearch = useCallback(async (q: string) => {
    setQuery(q);
    if (q.length < 2) { setResults([]); setShowSearch(false); return; }
    setSearching(true);
    setShowSearch(true);
    try {
      const data = await search(q);
      setResults(data.results);
    } catch { setResults([]); }
    finally { setSearching(false); }
  }, []);

  const handleResultClick = (r: SearchResult) => {
    setShowSearch(false);
    setQuery('');
    if (r.meeting_id) router.push(`/meetings/${r.meeting_id}`);
    else if (r.type === 'task') router.push('/tasks');
  };

  return (
    <>
      <header className="h-16 flex items-center justify-between px-6 border-b border-border/50 bg-card/30 backdrop-blur-sm shrink-0">
        {/* Search */}
        <div className="relative w-96 max-w-full">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
          <input
            value={query}
            onChange={e => handleSearch(e.target.value)}
            onBlur={() => setTimeout(() => setShowSearch(false), 200)}
            placeholder="Search meetings, transcripts, tasks..."
            className="w-full bg-secondary/50 border border-border/50 rounded-lg pl-9 pr-4 py-2 text-sm placeholder:text-muted-foreground focus:outline-none focus:ring-1 focus:ring-primary/50 focus:border-primary/50 transition-all"
          />
          <AnimatePresence>
            {showSearch && (
              <motion.div
                initial={{ opacity: 0, y: -8 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -8 }}
                className="absolute top-full mt-2 w-full rounded-lg border border-border bg-popover shadow-xl z-50 max-h-80 overflow-y-auto"
              >
                {searching ? (
                  <div className="p-4 text-sm text-muted-foreground">Searching...</div>
                ) : results.length === 0 ? (
                  <div className="p-4 text-sm text-muted-foreground">No results found</div>
                ) : results.map((r, i) => (
                  <button
                    key={i}
                    onMouseDown={() => handleResultClick(r)}
                    className="w-full text-left px-4 py-3 hover:bg-secondary/50 transition-colors border-b border-border/30 last:border-0"
                  >
                    <div className="flex items-center gap-2">
                      <span className={`text-[10px] font-medium px-1.5 py-0.5 rounded-full ${
                        r.type === 'meeting' ? 'bg-indigo-500/20 text-indigo-400' :
                        r.type === 'transcript' ? 'bg-violet-500/20 text-violet-400' :
                        r.type === 'task' ? 'bg-emerald-500/20 text-emerald-400' :
                        'bg-amber-500/20 text-amber-400'
                      }`}>{r.type}</span>
                      <span className="text-sm font-medium truncate">{r.title}</span>
                      {r.timestamp && <span className="text-xs text-muted-foreground ml-auto">{formatTimestamp(r.timestamp)}</span>}
                    </div>
                    <p className="text-xs text-muted-foreground mt-1 truncate">{r.excerpt}</p>
                  </button>
                ))}
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        {/* Right actions */}
        <div className="flex items-center gap-2">
          <button
            onClick={() => setShowUpload(true)}
            className="flex items-center gap-2 px-4 py-2 rounded-lg gradient-primary text-white text-sm font-medium hover:opacity-90 transition-all shadow-lg shadow-indigo-500/20"
          >
            <Upload className="w-4 h-4" />
            Upload Meeting
          </button>

          <button
            onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
            className="w-9 h-9 rounded-lg bg-secondary/50 border border-border/50 flex items-center justify-center text-muted-foreground hover:text-foreground hover:bg-secondary transition-all"
          >
            {mounted ? (
              theme === 'dark' ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />
            ) : (
              <Moon className="w-4 h-4" />
            )}
          </button>
        </div>
      </header>

      <UploadModal open={showUpload} onClose={() => setShowUpload(false)} />
    </>
  );
}
