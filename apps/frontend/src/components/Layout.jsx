import React from 'react';
import { Outlet, NavLink } from 'react-router-dom';
import { LayoutDashboard, TrendingUp, FlaskConical, Activity, Radio, Trophy, Bot, FileText, Sparkles, Wrench, Flag } from 'lucide-react';
import { useMode } from '@/lib/ModeContext';

const NAV = [
  { to: '/', label: 'Home', icon: LayoutDashboard },
  { to: '/predictor', label: 'Race Predictor', icon: TrendingUp },
  { to: '/strategy', label: 'Strategy Lab', icon: FlaskConical },
  { to: '/telemetry', label: 'Telemetry Lab', icon: Activity },
  { to: '/live', label: 'Live Race Control', icon: Radio },
  { to: '/championship', label: 'Championship', icon: Trophy },
  { to: '/engineer', label: 'AI Race Engineer', icon: Bot },
  { to: '/reports', label: 'Reports', icon: FileText },
];

function ModeSwitch() {
  const { mode, setMode } = useMode();
  return (
    <div className="glass rounded-xl p-1 flex text-xs font-semibold">
      <button onClick={() => setMode('fan')} className={`flex items-center gap-1.5 px-3 py-2 rounded-lg ${mode === 'fan' ? 'bg-white/10 text-white' : 'text-white/40'}`}>
        <Sparkles className="h-3.5 w-3.5" /> Fan
      </button>
      <button onClick={() => setMode('engineer')} className={`flex items-center gap-1.5 px-3 py-2 rounded-lg ${mode === 'engineer' ? 'bg-white/10 text-white' : 'text-white/40'}`}>
        <Wrench className="h-3.5 w-3.5" /> Engineer
      </button>
    </div>
  );
}

export default function Layout() {
  return (
    <div className="min-h-screen flex">
      <aside className="hidden lg:flex w-[264px] shrink-0 flex-col fixed inset-y-0 glass-strong border-r border-white/10 z-30">
        <div className="px-6 py-6 flex items-center gap-3 border-b border-white/10">
          <div className="h-10 w-10 rounded-xl bg-[var(--f1-red)] flex items-center justify-center"><Flag className="h-5 w-5 text-white" /></div>
          <div><div className="font-display font-bold text-[15px]">APEX</div><div className="text-[10px] tracking-[0.25em] uppercase text-white/35 font-mono-f1">Race Engineering</div></div>
        </div>
        <nav className="flex-1 px-3 py-5 space-y-1 overflow-y-auto">
          {NAV.map((item) => (
            <NavLink key={item.to} to={item.to} end={item.to === '/'} className={({ isActive }) => `flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm ${isActive ? 'bg-white/[0.07] text-white border border-white/10' : 'text-white/45 hover:text-white/80 hover:bg-white/[0.03] border border-transparent'}`}>
              <item.icon className="h-[18px] w-[18px]" /><span className="font-medium">{item.label}</span>
            </NavLink>
          ))}
        </nav>
      </aside>
      <div className="flex-1 lg:ml-[264px] min-w-0">
        <header className="sticky top-0 z-20 glass border-b border-white/10 px-4 md:px-8 h-16 flex items-center justify-between">
          <div className="hidden md:flex items-center gap-2 text-sm text-white/40"><span className="h-2 w-2 rounded-full bg-emerald-400 pulse-dot" /><span className="font-mono-f1 text-xs tracking-wide">SYSTEMS NOMINAL · MODELS SYNCED</span></div>
          <ModeSwitch />
        </header>
        <main className="px-4 md:px-8 py-8 max-w-[1400px] mx-auto"><Outlet /></main>
      </div>
    </div>
  );
}
