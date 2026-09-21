'use client';
import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import {
  Video, CheckSquare, Lightbulb, HelpCircle, Clock,
  TrendingUp, Plus, ArrowRight
} from 'lucide-react';
import Link from 'next/link';
import { getMeetings, getTasks, getAnalytics } from '@/lib/api';
import type { Meeting, Task, AnalyticsData } from '@/lib/types';
import { formatDuration, formatRelativeTime, formatDate, getStatusColor, getPriorityColor, cn } from '@/lib/utils';
import { MeetingCard } from '@/components/meetings/MeetingCard';
import { UploadModal } from '@/components/meetings/UploadModal';
import {
  AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid
} from 'recharts';

function StatCard({ icon: Icon, label, value, color, delay = 0 }: {
  icon: React.ElementType; label: string; value: string | number; color: string; delay?: number;
}) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay }}
      className="glass-card p-5 flex items-center gap-4 hover:border-primary/20 transition-all"
    >
      <div className={`w-10 h-10 rounded-xl flex items-center justify-center shrink-0 ${color}`}>
        <Icon className="w-5 h-5" />
      </div>
      <div>
        <p className="text-2xl font-bold">{value}</p>
        <p className="text-xs text-muted-foreground">{label}</p>
      </div>
    </motion.div>
  );
}

export default function DashboardPage() {
  const [meetings, setMeetings] = useState<Meeting[]>([]);
  const [tasks, setTasks] = useState<Task[]>([]);
  const [analytics, setAnalytics] = useState<AnalyticsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [showUpload, setShowUpload] = useState(false);

  useEffect(() => {
    Promise.all([getMeetings(), getTasks(), getAnalytics()])
      .then(([m, t, a]) => { setMeetings(m); setTasks(t); setAnalytics(a); })
      .finally(() => setLoading(false));
  }, []);

  const totalTime = meetings.reduce((s, m) => s + m.duration, 0);
  const todoTasks = tasks.filter(t => t.status === 'todo').length;
  const inProgressTasks = tasks.filter(t => t.status === 'in_progress').length;
  const doneTasks = tasks.filter(t => t.status === 'done').length;

  const recentMeetings = meetings.slice(0, 3);
  const urgentTasks = tasks.filter(t => t.priority === 'high' && t.status !== 'done').slice(0, 4);

  if (loading) {
    return (
      <div className="p-8">
        <div className="grid grid-cols-5 gap-4 mb-8">
          {[...Array(5)].map((_, i) => (
            <div key={i} className="glass-card p-5 h-24 animate-pulse bg-secondary/20" />
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="p-8 max-w-[1400px] mx-auto space-y-8">
      {/* Page Header */}
      <motion.div
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex items-center justify-between"
      >
        <div>
          <h1 className="text-2xl font-bold">Dashboard</h1>
          <p className="text-sm text-muted-foreground mt-0.5">Welcome back — here's your meeting intelligence overview</p>
        </div>
        <button
          onClick={() => setShowUpload(true)}
          className="flex items-center gap-2 px-4 py-2 rounded-xl gradient-primary text-white text-sm font-medium hover:opacity-90 transition-all shadow-lg shadow-indigo-500/20"
        >
          <Plus className="w-4 h-4" /> New Meeting
        </button>
      </motion.div>

      {/* Stats Row */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
        <StatCard icon={Video} label="Total Meetings" value={meetings.length} color="bg-indigo-500/15 text-indigo-400" delay={0} />
        <StatCard icon={CheckSquare} label="Action Items" value={analytics?.total_action_items ?? 0} color="bg-violet-500/15 text-violet-400" delay={0.05} />
        <StatCard icon={Lightbulb} label="Decisions" value={analytics?.total_decisions ?? 0} color="bg-amber-500/15 text-amber-400" delay={0.1} />
        <StatCard icon={HelpCircle} label="Open Questions" value={analytics?.total_unresolved_questions ?? 0} color="bg-pink-500/15 text-pink-400" delay={0.15} />
        <StatCard icon={Clock} label="Meeting Time" value={formatDuration(totalTime)} color="bg-emerald-500/15 text-emerald-400" delay={0.2} />
      </div>

      {/* Main content */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left: Chart + Recent Meetings */}
        <div className="lg:col-span-2 space-y-6">
          {/* Chart */}
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.25 }} className="glass-card p-5">
            <div className="flex items-center justify-between mb-4">
              <h2 className="font-semibold">Meetings Over Time</h2>
              <div className="flex items-center gap-1 text-xs text-emerald-400">
                <TrendingUp className="w-3.5 h-3.5" /> On track
              </div>
            </div>
            <ResponsiveContainer width="100%" height={180}>
              <AreaChart data={analytics?.meetings_over_time ?? []}>
                <defs>
                  <linearGradient id="grad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#6366f1" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#6366f1" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                <XAxis dataKey="week" tick={{ fontSize: 11, fill: '#6b7280' }} axisLine={false} tickLine={false} />
                <YAxis tick={{ fontSize: 11, fill: '#6b7280' }} axisLine={false} tickLine={false} />
                <Tooltip
                  contentStyle={{ background: 'hsl(222 47% 14%)', border: '1px solid hsl(222 47% 22%)', borderRadius: '8px', fontSize: '12px' }}
                  labelStyle={{ color: '#e2e8f0' }}
                />
                <Area type="monotone" dataKey="count" stroke="#6366f1" strokeWidth={2} fill="url(#grad)" dot={{ fill: '#6366f1', r: 3 }} />
              </AreaChart>
            </ResponsiveContainer>
          </motion.div>

          {/* Recent Meetings */}
          <div>
            <div className="flex items-center justify-between mb-4">
              <h2 className="font-semibold">Recent Meetings</h2>
              <Link href="/meetings">
                <button className="text-xs text-primary hover:text-primary/80 flex items-center gap-1 transition-colors">
                  View all <ArrowRight className="w-3 h-3" />
                </button>
              </Link>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {recentMeetings.length === 0 ? (
                <div className="col-span-2 glass-card p-8 text-center">
                  <Video className="w-10 h-10 text-muted-foreground mx-auto mb-3" />
                  <p className="text-sm text-muted-foreground">No meetings yet</p>
                  <button onClick={() => setShowUpload(true)} className="mt-3 text-xs text-primary hover:underline">Upload your first meeting</button>
                </div>
              ) : recentMeetings.map((m, i) => (
                <MeetingCard key={m.id} meeting={m} index={i} />
              ))}
            </div>
          </div>
        </div>

        {/* Right: Tasks + Activity */}
        <div className="space-y-6">
          {/* Task Overview */}
          <motion.div initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.3 }} className="glass-card p-5">
            <div className="flex items-center justify-between mb-4">
              <h2 className="font-semibold">Task Overview</h2>
              <Link href="/tasks">
                <button className="text-xs text-primary hover:text-primary/80 flex items-center gap-1">
                  View Tasks <ArrowRight className="w-3 h-3" />
                </button>
              </Link>
            </div>
            <div className="space-y-2 mb-4">
              {[
                { label: 'To Do', count: todoTasks, color: 'bg-slate-500' },
                { label: 'In Progress', count: inProgressTasks, color: 'bg-blue-500' },
                { label: 'Done', count: doneTasks, color: 'bg-green-500' },
              ].map(({ label, count, color }) => (
                <div key={label} className="flex items-center gap-3">
                  <div className={`w-2.5 h-2.5 rounded-full ${color}`} />
                  <span className="text-sm flex-1">{label}</span>
                  <span className="text-sm font-semibold">{count}</span>
                </div>
              ))}
            </div>
            {/* Progress bar */}
            {tasks.length > 0 && (
              <div className="h-2 rounded-full bg-secondary overflow-hidden flex">
                <div style={{ width: `${(doneTasks / tasks.length) * 100}%` }} className="bg-green-500 transition-all" />
                <div style={{ width: `${(inProgressTasks / tasks.length) * 100}%` }} className="bg-blue-500 transition-all" />
              </div>
            )}
          </motion.div>

          {/* Urgent Tasks */}
          <motion.div initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.35 }} className="glass-card p-5">
            <h2 className="font-semibold mb-4">Priority Tasks</h2>
            <div className="space-y-2">
              {urgentTasks.length === 0 ? (
                <p className="text-sm text-muted-foreground">No urgent tasks 🎉</p>
              ) : urgentTasks.map(t => (
                <div key={t.id} className="p-3 rounded-lg bg-secondary/30 border border-border/50 hover:border-primary/20 transition-all">
                  <p className="text-xs font-medium line-clamp-1 mb-1">{t.title}</p>
                  <div className="flex items-center gap-2">
                    <span className={cn('text-[10px] px-1.5 py-0.5 rounded-full border', getPriorityColor(t.priority))}>
                      {t.priority}
                    </span>
                    {t.assignee && <span className="text-[10px] text-muted-foreground">{t.assignee}</span>}
                    {t.deadline && <span className="text-[10px] text-muted-foreground ml-auto">{t.deadline}</span>}
                  </div>
                </div>
              ))}
            </div>
          </motion.div>

          {/* Recent Activity */}
          <motion.div initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.4 }} className="glass-card p-5">
            <h2 className="font-semibold mb-4">Recent Activity</h2>
            <div className="space-y-3">
              {meetings.slice(0, 4).map((m) => (
                <div key={m.id} className="flex items-center gap-3">
                  <div className="w-8 h-8 rounded-lg bg-indigo-500/15 flex items-center justify-center shrink-0">
                    <Video className="w-4 h-4 text-indigo-400" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-xs font-medium truncate">{m.title}</p>
                    <p className="text-[10px] text-muted-foreground">{formatRelativeTime(m.created_at)}</p>
                  </div>
                  <span className={cn('text-[10px] px-1.5 py-0.5 rounded-full', getStatusColor(m.status))}>
                    {m.status}
                  </span>
                </div>
              ))}
              {meetings.length === 0 && <p className="text-sm text-muted-foreground">No recent activity</p>}
            </div>
          </motion.div>
        </div>
      </div>

      <UploadModal open={showUpload} onClose={() => setShowUpload(false)} />
    </div>
  );
}
