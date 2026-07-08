const modules = [
  "Race simulation engine",
  "Tyre degradation",
  "Fuel effect",
  "Weather uncertainty",
  "Safety car / VSC",
  "Monte Carlo strategy risk",
  "Telemetry-driven pace modelling",
  "Interactive dashboards",
];

export default function Page() {
  return (
    <main className="min-h-screen bg-neutral-950 text-white">
      <section className="mx-auto max-w-6xl px-6 py-24">
        <p className="text-sm uppercase tracking-[0.4em] text-red-400">F1Sim Engineering Platform</p>
        <h1 className="mt-6 text-5xl font-black tracking-tight md:text-7xl">
          Open race strategy simulation for tyre, weather and safety-car uncertainty.
        </h1>
        <p className="mt-6 max-w-3xl text-lg text-neutral-300">
          A reproducible Formula 1 race simulation platform for students, analysts, data scientists and motorsport engineering research.
        </p>
        <div className="mt-10 flex gap-4">
          <a className="rounded-full bg-red-500 px-6 py-3 font-semibold" href="https://github.com/panagiotagrosdouli/formula1-race-simulation">GitHub</a>
          <a className="rounded-full border border-neutral-700 px-6 py-3 font-semibold" href="/docs">Documentation</a>
        </div>
      </section>
      <section className="mx-auto grid max-w-6xl gap-4 px-6 pb-24 md:grid-cols-4">
        {modules.map((module) => (
          <div key={module} className="rounded-2xl border border-neutral-800 bg-neutral-900 p-5">
            <h2 className="font-bold">{module}</h2>
            <p className="mt-2 text-sm text-neutral-400">Implemented/prototype status is documented transparently in the repository README.</p>
          </div>
        ))}
      </section>
    </main>
  );
}
