export default function Stat({ label, value, sub, accent = false }) {
  return (
    <div className="rounded-xl border border-white/10 bg-white/[0.03] p-4">
      <div className="text-[11px] tracking-[0.18em] uppercase text-white/35 font-mono-f1">{label}</div>
      <div className={`mt-2 font-display text-2xl font-bold ${accent ? 'text-emerald-400' : 'text-white'}`}>{value}</div>
      {sub && <div className="mt-1 text-xs text-white/40">{sub}</div>}
    </div>
  );
}
