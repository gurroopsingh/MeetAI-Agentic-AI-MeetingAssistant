'use client';
import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { CheckSquare, Plus, Calendar, User, Clock } from 'lucide-react';
import { getTasks, updateTask } from '@/lib/api';
import type { Task } from '@/lib/types';
import { getPriorityColor, getStatusColor, formatDate, getInitials, cn } from '@/lib/utils';
import { toast } from '@/components/ui/Toaster';
import Link from 'next/link';

type TaskStatus = 'todo' | 'in_progress' | 'done';

const COLUMNS: { key: TaskStatus; label: string; color: string }[] = [
  { key: 'todo', label: 'To Do', color: 'text-slate-400' },
  { key: 'in_progress', label: 'In Progress', color: 'text-blue-400' },
  { key: 'done', label: 'Done', color: 'text-green-400' },
];

function TaskCard({ task, onStatusChange }: { task: Task; onStatusChange: (id: number, status: TaskStatus) => void }) {
  return (
    <motion.div
      layout
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 0.95 }}
      whileHover={{ y: -2 }}
      className="glass-card p-4 cursor-pointer hover:border-primary/30 transition-all"
    >
      {/* Priority */}
      <div className="flex items-start justify-between gap-2 mb-2">
        <span className={cn('text-[10px] font-semibold px-2 py-0.5 rounded-full border capitalize', getPriorityColor(task.priority))}>
          {task.priority}
        </span>
        {task.meeting_title && (
          <Link href={task.meeting_id ? `/meetings/${task.meeting_id}` : '#'}>
            <span className="text-[10px] text-primary/70 hover:text-primary truncate max-w-[120px] cursor-pointer">
              {task.meeting_title}
            </span>
          </Link>
        )}
      </div>

      {/* Title */}
      <p className="text-sm font-medium mb-3 leading-snug">{task.title}</p>

      {/* Meta */}
      <div className="space-y-1.5 mb-3">
        {task.assignee && (
          <div className="flex items-center gap-2">
            <div className="w-5 h-5 rounded-full bg-primary/20 flex items-center justify-center text-[9px] font-bold text-primary">
              {getInitials(task.assignee)}
            </div>
            <span className="text-xs text-muted-foreground">{task.assignee}</span>
          </div>
        )}
        {task.deadline && (
          <div className="flex items-center gap-1.5 text-xs text-muted-foreground">
            <Calendar className="w-3 h-3" />
            <span>{task.deadline}</span>
          </div>
        )}
      </div>

      {/* Status selector */}
      <select
        value={task.status}
        onChange={e => onStatusChange(task.id, e.target.value as TaskStatus)}
        className="w-full bg-secondary/50 border border-border/50 rounded-md px-2 py-1 text-xs text-foreground focus:outline-none focus:ring-1 focus:ring-primary/50"
        onClick={e => e.stopPropagation()}
      >
        <option value="todo">To Do</option>
        <option value="in_progress">In Progress</option>
        <option value="done">Done</option>
      </select>
    </motion.div>
  );
}

export default function TasksPage() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<'all' | 'high' | 'medium' | 'low'>('all');

  useEffect(() => {
    getTasks()
      .then(setTasks)
      .catch(() => toast('Failed to load tasks', 'error'))
      .finally(() => setLoading(false));
  }, []);

  const handleStatusChange = async (id: number, status: TaskStatus) => {
    try {
      const updated = await updateTask(id, { status });
      setTasks(prev => prev.map(t => t.id === id ? updated : t));
      toast('Task updated', 'success');
    } catch {
      toast('Failed to update task', 'error');
    }
  };

  const filtered = tasks.filter(t => filter === 'all' || t.priority === filter);

  const byStatus = (status: TaskStatus) => filtered.filter(t => t.status === status);

  if (loading) {
    return (
      <div className="p-8">
        <div className="grid grid-cols-3 gap-6">
          {[...Array(3)].map((_, i) => (
            <div key={i} className="space-y-3">
              <div className="h-8 rounded-lg bg-secondary/20 animate-pulse" />
              {[...Array(3)].map((_, j) => (
                <div key={j} className="glass-card p-4 h-36 animate-pulse bg-secondary/20" />
              ))}
            </div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="p-8 max-w-[1400px] mx-auto">
      {/* Header */}
      <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }} className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-bold">Tasks</h1>
          <p className="text-sm text-muted-foreground mt-0.5">{tasks.length} tasks across all meetings</p>
        </div>
        <div className="flex items-center gap-3">
          <div className="flex rounded-lg border border-border overflow-hidden">
            {(['all', 'high', 'medium', 'low'] as const).map(p => (
              <button
                key={p}
                onClick={() => setFilter(p)}
                className={`px-3 py-1.5 text-xs font-medium capitalize transition-colors ${filter === p ? 'bg-primary text-white' : 'text-muted-foreground hover:text-foreground bg-secondary/50'}`}
              >
                {p}
              </button>
            ))}
          </div>
        </div>
      </motion.div>

      {/* Summary stats */}
      <div className="grid grid-cols-3 gap-4 mb-6">
        {COLUMNS.map(col => (
          <div key={col.key} className="glass-card p-4 flex items-center gap-3">
            <div className={`text-2xl font-bold ${col.color}`}>{byStatus(col.key).length}</div>
            <div>
              <p className="text-sm font-medium">{col.label}</p>
              <p className="text-xs text-muted-foreground">tasks</p>
            </div>
          </div>
        ))}
      </div>

      {/* Kanban */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {COLUMNS.map(col => {
          const columnTasks = byStatus(col.key);
          return (
            <div key={col.key}>
              <div className="flex items-center gap-2 mb-4">
                <div className={`w-2.5 h-2.5 rounded-full ${
                  col.key === 'todo' ? 'bg-slate-500' :
                  col.key === 'in_progress' ? 'bg-blue-500' : 'bg-green-500'
                }`} />
                <h3 className={`font-semibold text-sm ${col.color}`}>{col.label}</h3>
                <span className="ml-auto text-xs font-medium px-2 py-0.5 rounded-full bg-secondary text-muted-foreground">
                  {columnTasks.length}
                </span>
              </div>

              <div className="space-y-3 min-h-[200px]">
                {columnTasks.map(task => (
                  <TaskCard key={task.id} task={task} onStatusChange={handleStatusChange} />
                ))}
                {columnTasks.length === 0 && (
                  <div className="border-2 border-dashed border-border rounded-xl p-6 text-center">
                    <p className="text-xs text-muted-foreground">No {col.label.toLowerCase()} tasks</p>
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
