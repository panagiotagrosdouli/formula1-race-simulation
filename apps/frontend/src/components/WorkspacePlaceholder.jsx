import Panel from '@/components/ui-f1/Panel';

export default function WorkspacePlaceholder({ title, description }) {
  return (
    <div className="space-y-6">
      <Panel className="p-8">
        <div className="text-[11px] tracking-[0.25em] uppercase text-white/35 font-mono-f1">APEX Workspace</div>
        <h1 className="font-display text-4xl font-extrabold mt-3">{title}</h1>
        <p className="text-white/45 mt-3 max-w-3xl">{description}</p>
      </Panel>
      <Panel className="p-6">
        <div className="font-display font-semibold">Backend integration pending</div>
        <p className="text-sm text-white/45 mt-2">This page is reserved for the corresponding FastAPI and analytics modules. Existing Streamlit functionality remains untouched while the new frontend is developed.</p>
      </Panel>
    </div>
  );
}
