'use client';
import { motion } from 'framer-motion';
import { useTheme } from 'next-themes';
import { Moon, Sun, Bot, Shield, Database, Zap, ExternalLink } from 'lucide-react';

function SettingSection({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} className="glass-card p-6">
      <h2 className="font-semibold mb-4 flex items-center gap-2">{title}</h2>
      {children}
    </motion.div>
  );
}

function SettingRow({ label, description, children }: { label: string; description?: string; children: React.ReactNode }) {
  return (
    <div className="flex items-center justify-between py-3 border-b border-border/30 last:border-0">
      <div>
        <p className="text-sm font-medium">{label}</p>
        {description && <p className="text-xs text-muted-foreground mt-0.5">{description}</p>}
      </div>
      <div className="shrink-0 ml-4">{children}</div>
    </div>
  );
}

export default function SettingsPage() {
  const { theme, setTheme } = useTheme();

  return (
    <div className="p-8 max-w-[800px] mx-auto space-y-6">
      <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }}>
        <h1 className="text-2xl font-bold">Settings</h1>
        <p className="text-sm text-muted-foreground mt-0.5">Configure your MeetAI experience</p>
      </motion.div>

      <SettingSection title="Appearance">
        <SettingRow label="Theme" description="Choose between dark and light mode">
          <div className="flex rounded-lg border border-border overflow-hidden">
            <button
              onClick={() => setTheme('dark')}
              className={`flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium transition-colors ${theme === 'dark' ? 'bg-primary text-white' : 'text-muted-foreground hover:text-foreground bg-secondary/50'}`}
            >
              <Moon className="w-3.5 h-3.5" /> Dark
            </button>
            <button
              onClick={() => setTheme('light')}
              className={`flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium transition-colors ${theme === 'light' ? 'bg-primary text-white' : 'text-muted-foreground hover:text-foreground bg-secondary/50'}`}
            >
              <Sun className="w-3.5 h-3.5" /> Light
            </button>
          </div>
        </SettingRow>
      </SettingSection>

      <SettingSection title="AI Provider">
        <SettingRow label="Current Provider" description="The AI provider powering meeting analysis">
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-emerald-500/10 border border-emerald-500/20">
            <Zap className="w-3.5 h-3.5 text-emerald-500" />
            <span className="text-xs font-semibold text-emerald-500">Azure</span>
          </div>
        </SettingRow>
        <SettingRow label="Azure AI Speech" description="Connect for real transcription with speaker diarization">
          <span className="text-xs text-emerald-500 px-3 py-1.5 rounded-lg bg-emerald-500/10 border border-emerald-500/20">Connected</span>
        </SettingRow>
        <SettingRow label="Azure AI Language" description="Connect for production NLP analysis">
          <span className="text-xs text-emerald-500 px-3 py-1.5 rounded-lg bg-emerald-500/10 border border-emerald-500/20">Connected</span>
        </SettingRow>
        <SettingRow label="Microsoft Foundry" description="Connect for generative AI and agent orchestration">
          <span className="text-xs text-emerald-500 px-3 py-1.5 rounded-lg bg-emerald-500/10 border border-emerald-500/20">Connected</span>
        </SettingRow>
        <div className="mt-4 p-4 rounded-lg bg-secondary/30 border border-border/50">
          <p className="text-xs text-muted-foreground leading-relaxed">
            To connect Azure services, set <code className="text-primary/80 bg-primary/10 px-1 rounded">AI_PROVIDER=azure</code> in your <code className="text-primary/80 bg-primary/10 px-1 rounded">.env</code> file and provide your Azure credentials. See the README for detailed setup instructions.
          </p>
        </div>
      </SettingSection>

      <SettingSection title="Database">
        <SettingRow label="Database Type" description="Current storage backend">
          <div className="flex items-center gap-2">
            <Database className="w-4 h-4 text-muted-foreground" />
            <span className="text-xs text-muted-foreground">SQLite (Local)</span>
          </div>
        </SettingRow>
        <SettingRow label="Data Location" description="Where your meeting data is stored">
          <code className="text-[10px] text-muted-foreground bg-secondary/50 px-2 py-1 rounded">backend/meetai.db</code>
        </SettingRow>
      </SettingSection>

      <SettingSection title="Responsible AI">
        <div className="space-y-3">
          {[
            { title: 'Data Privacy', desc: 'Meeting transcripts may contain personal information. Ensure appropriate access controls before sharing.' },
            { title: 'AI Accuracy', desc: 'Always verify AI-extracted decisions and action items with meeting participants.' },
            { title: 'Participant Consent', desc: 'Ensure all participants consent to AI transcription before recording meetings.' },
            { title: 'Speaker Identification Bias', desc: 'AI speaker diarization may vary in accuracy across accents and recording quality.' },
          ].map(item => (
            <div key={item.title} className="flex items-start gap-3 p-3 rounded-lg bg-secondary/30 border border-border/50">
              <Shield className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
              <div>
                <p className="text-sm font-medium">{item.title}</p>
                <p className="text-xs text-muted-foreground mt-0.5 leading-relaxed">{item.desc}</p>
              </div>
            </div>
          ))}
        </div>
      </SettingSection>

      <SettingSection title="About">
        <SettingRow label="Version" description="MeetAI application version">
          <span className="text-xs text-muted-foreground">v1.0.0</span>
        </SettingRow>
        <SettingRow label="AI-103 Project" description="University course project mapping">
          <a href="#" className="flex items-center gap-1 text-xs text-primary hover:underline">
            View README <ExternalLink className="w-3 h-3" />
          </a>
        </SettingRow>
        <div className="mt-4 p-4 rounded-lg bg-primary/5 border border-primary/20">
          <div className="flex items-center gap-2 mb-2">
            <Bot className="w-4 h-4 text-primary" />
            <span className="text-sm font-semibold gradient-text">MeetAI</span>
          </div>
          <p className="text-xs text-muted-foreground leading-relaxed">
            Built with Next.js, FastAPI, and the Microsoft Azure AI ecosystem. Architecture is designed for Azure AI Speech, Azure AI Language, and Microsoft Foundry integration.
          </p>
        </div>
      </SettingSection>
    </div>
  );
}
