import { useQuery } from '@tanstack/react-query';
import { runMonteCarloSimulation } from '@/lib/api-client';
import Panel from '@/components/ui-f1/Panel';
import Stat from '@/components/ui-f1/Stat';

export default function Predictor() {
  const { data, isLoading, error } = useQuery({
    queryKey: ['monte-carlo-preview'],
    queryFn: () => runMonteCarloSimulation({ runs: 10, current_lap: 42, circuit: { lap_count: 44 } }),
  });

  const leader = data?.probabilities?.[0];

  return (
    <div className="space-y-6">
      <Panel className="p-8">
        <div className="text-[11px] tracking-[0.25em] uppercase text-white/35 font-mono-f1">Simulation workspace</div>
        <h1 className="font-display text-4xl font-extrabold mt-3">Race Predictor</h1>
        <p className="text-white/45 mt-3 max-w-3xl">Winner probability, expected finishing position and confidence intervals from the FastAPI Monte Carlo endpoint.</p>
      </Panel>

      {isLoading && <Panel className="p-6 text-white/50">Loading simulation preview from backend...</Panel>}
      {error && <Panel className="p-6 text-red-300">Backend unavailable. Start FastAPI with uvicorn backend.app.main:app --reload.</Panel>}

      {data && (
        <>
          <div className="grid md:grid-cols-4 gap-4">
            <Stat label="Runs" value={data.runs} sub="Monte Carlo samples" />
            <Stat label="Leader" value={leader?.driver_id || 'N/A'} sub="highest win probability" accent />
            <Stat label="Win probability" value={leader ? `${Math.round(leader.win_probability * 100)}%` : 'N/A'} sub="simulation estimate" />
            <Stat label="Expected finish" value={leader?.expected_finish_position ?? 'N/A'} sub="mean position" />
          </div>

          <Panel className="p-6">
            <h2 className="font-display font-semibold text-xl mb-4">Probability table</h2>
            <div className="space-y-3">
              {data.probabilities.map((row) => (
                <div key={row.driver_id} className="rounded-xl border border-white/10 bg-white/[0.03] p-4">
                  <div className="flex items-center justify-between gap-4">
                    <div className="font-display font-semibold">{row.driver_id}</div>
                    <div className="font-mono-f1 text-sm text-white/70">{Math.round(row.win_probability * 100)}%</div>
                  </div>
                  <div className="mt-3 h-2 rounded-full bg-white/10 overflow-hidden">
                    <div className="h-full bg-[var(--f1-red)]" style={{ width: `${Math.round(row.win_probability * 100)}%` }} />
                  </div>
                  <div className="mt-2 text-xs text-white/40">CI {Math.round(row.win_ci_lower * 100)}% - {Math.round(row.win_ci_upper * 100)}% · Expected finish {row.expected_finish_position}</div>
                </div>
              ))}
            </div>
          </Panel>

          <Panel className="p-6">
            <h2 className="font-display font-semibold text-xl mb-3">Assumptions</h2>
            <ul className="space-y-2 text-sm text-white/45">
              {data.assumptions.map((item) => <li key={item}>{item}</li>)}
            </ul>
          </Panel>
        </>
      )}
    </div>
  );
}
