'use client';
import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { getAnalytics } from '@/lib/api';
import type { AnalyticsData } from '@/lib/types';
import { formatDuration } from '@/lib/utils';
import {
  AreaChart, Area, BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer,
  CartesianGrid, PieChart, Pie, Cell, LineChart, Line, Legend
} from 'recharts';

const COLORS = ['#6366f1', '#8b5cf6', '#ec4899', '#10b981', '#f59e0b', '#3b82f6'];

const CustomTooltip = ({ active, payload, label }: any) => {
  if (!active || !payload?.length) return null;
  return (
    <div className="bg-card border border-border rounded-lg px-3 py-2 shadow-xl text-xs">
      <p className="text-muted-foreground mb-1">{label}</p>
      {payload.map((p: any, i: number) => (
        <p key={i} style={{ color: p.color }}>{p.name}: <span className="font-semibold">{p.value}</span></p>
      ))}
    </div>
  );
};

function ChartCard({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="glass-card p-5">
      <h2 className="font-semibold mb-4 text-sm">{title}</h2>
      {children}
    </motion.div>
  );
}

export default function AnalyticsPage() {
  const [data, setData] = useState<AnalyticsData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getAnalytics().then(setData).finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="p-8 grid grid-cols-2 gap-6">
        {[...Array(6)].map((_, i) => (
          <div key={i} className="glass-card p-5 h-60 animate-pulse bg-secondary/20" />
        ))}
      </div>
    );
  }

  if (!data) return null;

  const speakerPieData = data.speaker_participation.map(s => ({ name: s.name, value: s.speaking_time }));

  return (
    <div className="p-8 max-w-[1400px] mx-auto space-y-6">
      {/* Header */}
      <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }}>
        <h1 className="text-2xl font-bold">Analytics</h1>
        <p className="text-sm text-muted-foreground mt-0.5">Insights across all your meetings</p>
      </motion.div>

      {/* Top Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {[
          { label: 'Total Meetings', value: data.total_meetings, color: '#6366f1' },
          { label: 'Total Duration', value: formatDuration(data.total_duration), color: '#8b5cf6' },
          { label: 'Action Items', value: data.total_action_items, color: '#10b981' },
          { label: 'Decisions Made', value: data.total_decisions, color: '#f59e0b' },
        ].map((s, i) => (
          <motion.div
            key={s.label}
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: i * 0.05 }}
            className="glass-card p-5"
          >
            <p className="text-2xl font-bold" style={{ color: s.color }}>{s.value}</p>
            <p className="text-xs text-muted-foreground mt-1">{s.label}</p>
          </motion.div>
        ))}
      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Meetings Over Time */}
        <ChartCard title="Meetings Over Time">
          <ResponsiveContainer width="100%" height={200}>
            <AreaChart data={data.meetings_over_time}>
              <defs>
                <linearGradient id="meetingsGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#6366f1" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="#6366f1" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
              <XAxis dataKey="week" tick={{ fontSize: 10, fill: '#6b7280' }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fontSize: 10, fill: '#6b7280' }} axisLine={false} tickLine={false} />
              <Tooltip content={<CustomTooltip />} />
              <Area type="monotone" dataKey="count" name="Meetings" stroke="#6366f1" strokeWidth={2} fill="url(#meetingsGrad)" dot={{ fill: '#6366f1', r: 3 }} />
            </AreaChart>
          </ResponsiveContainer>
        </ChartCard>

        {/* Decisions & Questions Over Time */}
        <ChartCard title="Decisions & Open Questions Over Time">
          <ResponsiveContainer width="100%" height={200}>
            <LineChart data={data.decisions_over_time}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
              <XAxis dataKey="week" tick={{ fontSize: 10, fill: '#6b7280' }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fontSize: 10, fill: '#6b7280' }} axisLine={false} tickLine={false} />
              <Tooltip content={<CustomTooltip />} />
              <Legend wrapperStyle={{ fontSize: '10px', paddingTop: '8px' }} />
              <Line type="monotone" dataKey="decisions" name="Decisions" stroke="#6366f1" strokeWidth={2} dot={{ fill: '#6366f1', r: 3 }} />
              <Line type="monotone" dataKey="questions" name="Open Questions" stroke="#ec4899" strokeWidth={2} dot={{ fill: '#ec4899', r: 3 }} strokeDasharray="4 2" />
            </LineChart>
          </ResponsiveContainer>
        </ChartCard>

        {/* Meeting Duration */}
        <ChartCard title="Meeting Duration by Meeting (minutes)">
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={data.duration_by_meeting} layout="vertical">
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" horizontal={false} />
              <XAxis type="number" tick={{ fontSize: 10, fill: '#6b7280' }} axisLine={false} tickLine={false} />
              <YAxis type="category" dataKey="name" tick={{ fontSize: 10, fill: '#6b7280' }} axisLine={false} tickLine={false} width={90} />
              <Tooltip content={<CustomTooltip />} />
              <Bar dataKey="duration" name="Minutes" radius={[0, 4, 4, 0]}>
                {data.duration_by_meeting.map((_, i) => (
                  <Cell key={i} fill={COLORS[i % COLORS.length]} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>

        {/* Action Items */}
        <ChartCard title="Action Items by Meeting">
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={data.action_items_by_meeting}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
              <XAxis dataKey="name" tick={{ fontSize: 10, fill: '#6b7280' }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fontSize: 10, fill: '#6b7280' }} axisLine={false} tickLine={false} />
              <Tooltip content={<CustomTooltip />} />
              <Bar dataKey="count" name="Action Items" radius={[4, 4, 0, 0]}>
                {data.action_items_by_meeting.map((_, i) => (
                  <Cell key={i} fill={COLORS[i % COLORS.length]} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>

        {/* Speaker Participation Pie */}
        <ChartCard title="Speaker Participation (minutes)">
          <div className="flex items-center gap-6">
            <ResponsiveContainer width="50%" height={180}>
              <PieChart>
                <Pie
                  data={speakerPieData}
                  cx="50%"
                  cy="50%"
                  innerRadius={40}
                  outerRadius={75}
                  paddingAngle={3}
                  dataKey="value"
                >
                  {speakerPieData.map((_, i) => (
                    <Cell key={i} fill={data.speaker_participation[i]?.avatar_color || COLORS[i % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip content={<CustomTooltip />} />
              </PieChart>
            </ResponsiveContainer>
            <div className="space-y-2 flex-1">
              {data.speaker_participation.slice(0, 5).map((s, i) => (
                <div key={s.name} className="flex items-center gap-2">
                  <div className="w-2.5 h-2.5 rounded-full shrink-0" style={{ background: s.avatar_color || COLORS[i % COLORS.length] }} />
                  <span className="text-xs truncate flex-1">{s.name}</span>
                  <span className="text-xs font-semibold text-muted-foreground">{s.speaking_time}m</span>
                </div>
              ))}
            </div>
          </div>
        </ChartCard>

        {/* Speaker Bar */}
        <ChartCard title="Speaking Time by Participant">
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={data.speaker_participation}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
              <XAxis dataKey="name" tick={{ fontSize: 9, fill: '#6b7280' }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fontSize: 10, fill: '#6b7280' }} axisLine={false} tickLine={false} unit="m" />
              <Tooltip content={<CustomTooltip />} />
              <Bar dataKey="speaking_time" name="Minutes" radius={[4, 4, 0, 0]}>
                {data.speaker_participation.map((s, i) => (
                  <Cell key={i} fill={s.avatar_color || COLORS[i % COLORS.length]} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>
      </div>
    </div>
  );
}
