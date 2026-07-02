import { useQuery } from '@tanstack/react-query';
import { previewStrategy } from '@/lib/api-client';
import Panel from '@/components/ui-f1/Panel';
import Stat from '@/components/ui-f1/Stat';

export default function Strategy() {
  const { data, isLoading, error } = useQuery({
    queryKey: ['strategy-preview'],
    queryFn: () => previewStrategy({ current_lap: 14, tyre_compound: 'medium', tyre_age_laps: 12 }),
  });

  return (
    <div className="space-y-6">
      <Panel className="p-8">
        <div className="text-[11px] tracking-[0.25em] uppercase text-white/35 font-mono-f1">Strategy workspace</div>
        <h1 className="font-display text-4xl font-extrabold mt-3">Strategy Lab</h1>
        <p className="text-white/45 mt-3 max-w-3xl">Pit-window recommendation and risk explanation from the FastAPI strategy preview endpoint.</p>
      </Panel>

      {isLoading && <Panel className="p-6 text-white/50">Loading strategy preview from backend...</Panel>}
      {error && <Panel className="p-6 text-red-300">Backend unavailable. Start FastAPI with uvicorn backend.app.main:app --reload.</Panel>}

      {data && (
        <>
          <div className="grid md:grid-cols-3 gap-4">
            <Stat label="Window start" value={`Lap ${data.recommended_window_start}`} sub="recommended review" accent />
            <Stat label="Window end" value={`Lap ${data.recommended_window_end}`} sub="pit decision range" />
            <Stat label="Risk" value={data.risk_label.toUpperCase()} sub="tyre/weather/circuit" />
          </div>
          <Panel className="p-6">
            <h2 className="font-display font-semibold text-xl mb-3">Engineering explanation</h2>
            <p className="text-sm text-white/50 leading-relaxed">{data.explanation}</p>
          </Panel>
        </>
      )}
    </div>
  );
}
