'use client';
import { useState, useEffect, createContext, useContext, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, CheckCircle, AlertCircle, Info } from 'lucide-react';

type ToastType = 'success' | 'error' | 'info';
interface Toast { id: string; message: string; type: ToastType; }
interface ToastContextType { toast: (message: string, type?: ToastType) => void; }

const ToastContext = createContext<ToastContextType>({ toast: () => {} });
export const useToast = () => useContext(ToastContext);

let externalToast: ((msg: string, type?: ToastType) => void) | null = null;
export const toast = (msg: string, type: ToastType = 'info') => externalToast?.(msg, type);

export function Toaster() {
  const [toasts, setToasts] = useState<Toast[]>([]);

  const addToast = useCallback((message: string, type: ToastType = 'info') => {
    const id = Math.random().toString(36).slice(2);
    setToasts(t => [...t, { id, message, type }]);
    setTimeout(() => setToasts(t => t.filter(x => x.id !== id)), 4000);
  }, []);

  useEffect(() => { externalToast = addToast; return () => { externalToast = null; }; }, [addToast]);

  return (
    <div className="fixed bottom-6 right-6 z-[100] space-y-2 pointer-events-none">
      <AnimatePresence>
        {toasts.map(t => (
          <motion.div
            key={t.id}
            initial={{ opacity: 0, x: 60 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: 60 }}
            className="pointer-events-auto flex items-center gap-3 px-4 py-3 rounded-lg shadow-xl border max-w-sm bg-card border-border"
          >
            {t.type === 'success' && <CheckCircle className="w-4 h-4 text-green-400 shrink-0" />}
            {t.type === 'error' && <AlertCircle className="w-4 h-4 text-red-400 shrink-0" />}
            {t.type === 'info' && <Info className="w-4 h-4 text-blue-400 shrink-0" />}
            <p className="text-sm flex-1">{t.message}</p>
            <button
              onClick={() => setToasts(prev => prev.filter(x => x.id !== t.id))}
              className="text-muted-foreground hover:text-foreground"
            >
              <X className="w-3.5 h-3.5" />
            </button>
          </motion.div>
        ))}
      </AnimatePresence>
    </div>
  );
}
