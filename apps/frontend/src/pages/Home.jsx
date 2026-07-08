import React from 'react';
import { Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { TrendingUp, FlaskConical, Activity, Bot, ChevronRight, Cpu, Target, GaugeCircle } from 'lucide-react';
import Panel from '@/components/ui-f1/Panel';
import Stat from '@/components/ui-f1/Stat';
import { getHealth } from '@/lib/api-client';

const QUICK = [
  { to: '/predictor', label: 'Race Predictor', icon: TrendingUp, desc: 'Winner and podium probabilities' },
  { to: '/strategy', label: 'Strategy Lab', icon: FlaskConical, desc: 'Pit windows and tyre model' },
  { to: '/telemetry', label: 'Telemetry Lab', icon: Activity, desc: 'Speed, throttle, brake and gear' },
  { to: '/engineer', label: 'AI Race Engineer', icon: Bot, desc: 'Explain the why and evidence' },
];

export default function Home() {
  const { data: health, isLoading, error } = useQuery({
    queryKey: ['backend-health'],
    queryFn: getHealth,
    retry: 1,
  });
  const backendStatus = isLoading
    ? 'CHECKING'
    : error
      ? 'DEMO'
      : health?.status?.toUpperCase() || 'DEMO';
  const serviceLabel = health?.demo ? 'Frontend demo fallback' : health?.service || 'FastAPI service';

  return (
    <div className="space-y-6">
      <Panel className="relative overflow-hidden p-8 md:p-10">
        <div className="absolute inset-0 grid-lines opacity-40" />
        <div className="relative">
          <div className="text-[11px] font-semibold tracking-[0.28em] uppercase text-white/45 font-mono-f1">Executive Overview</div>
          <h1 className="font-display text-4xl md:text-5xl font-extrabold tracking-tight mt-3">APEX Race Engineering</h1>
          <p className="text-white/45 mt-3 max-w-3xl">Professional Formula 1 race strategy, telemetry, simulation and probability intelligence. The frontend now renders in demo mode even before the FastAPI backend is connected.</p>
          <div className="grid md:grid-cols-4 gap-4 mt-8">
            <Stat label="Backend" value={backendStatus} sub={serviceLabel} accent={!isLoading} />
            <Stat label="Race confidence" value="87%" sub="demo model status" accent />
            <Stat label="Simulations" value="2,500" sub="Monte Carlo baseline" />
            <Stat label="Predicted winner" value="LEC" sub="demo display pending full API wiring" />
          </div>
        </div>
      </Panel>

      <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {QUICK.map((q) => (
          <Link key={q.to} to={q.to} className="glass glass-hover rounded-2xl p-5 block">
            <div className="h-11 w-11 rounded-xl bg-white/[0.05] flex items-center justify-center mb-4"><q.icon className="h-5 w-5 text-white/80" /></div>
            <div className="flex items-center justify-between"><div className="font-display font-semibold">{q.label}</div><ChevronRight className="h-4 w-4 text-white/30" /></div>
            <div className="text-xs text-white/40 mt-1">{q.desc}</div>
          </Link>
        ))}
      </div>

      <div className="grid sm:grid-cols-3 gap-4">
        {[{ icon: Cpu, t: 'Deterministic Engine', d: 'Reproducible seeded race simulations' }, { icon: Target, t: 'Explicit Assumptions', d: 'No black-box presentation' }, { icon: GaugeCircle, t: 'Scientific Transparency', d: 'Confidence intervals and diagnostics' }].map((c) => (
          <div key={c.t} className="glass rounded-2xl p-5"><c.icon className="h-5 w-5 text-[var(--f1-red)]" /><div className="font-display font-semibold mt-3">{c.t}</div><div className="text-xs text-white/40 mt-1">{c.d}</div></div>
        ))}
      </div>
    </div>
  );
}
