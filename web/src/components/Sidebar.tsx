import type { EdgeView, LayoutMode } from '../types/graph';

interface SidebarProps {
  currentView: EdgeView;
  onViewChange: (view: EdgeView) => void;
  layoutMode: LayoutMode;
  onLayoutChange: (mode: LayoutMode) => void;
}

const VIEW_OPTIONS: { key: EdgeView; label: string; description: string }[] = [
  { key: 'all', label: 'All', description: 'All connections' },
  { key: 'providers', label: 'Providers', description: 'MADE_BY edges' },
  { key: 'lineage', label: 'Lineage', description: 'DERIVED_FROM edges' },
  { key: 'hardware', label: 'Hardware', description: 'FITS_ON edges' },
  { key: 'platforms', label: 'Platforms', description: 'AVAILABLE_ON edges' },
  { key: 'benchmarks', label: 'Benchmarks', description: 'SCORED_ON edges' },
];

const VIEW_ICONS: Record<EdgeView, string> = {
  all: 'M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zm10 0a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zm10 0a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z',
  providers: 'M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4',
  lineage: 'M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2',
  hardware: 'M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM9 9h6v6H9V9z',
  platforms: 'M3 15a4 4 0 004 4h9a5 5 0 10-.1-9.999 5.002 5.002 0 10-9.78 2.096A4.001 4.001 0 003 15z',
  benchmarks: 'M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z',
};

export default function Sidebar({
  currentView,
  onViewChange,
  layoutMode,
  onLayoutChange,
}: SidebarProps) {
  return (
    <div className="absolute top-16 left-4 z-20 flex flex-col gap-2">
      {/* Edge View Toggles */}
      <div className="bg-slate-800/90 backdrop-blur-sm rounded-xl border border-slate-700/50 p-3 shadow-xl">
        <div className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2 px-1">
          Edge View
        </div>
        <div className="flex flex-col gap-1">
          {VIEW_OPTIONS.map(({ key, label }) => (
            <button
              key={key}
              onClick={() => onViewChange(key)}
              className={`flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium transition-all ${
                currentView === key
                  ? 'bg-blue-500/20 text-blue-400 border border-blue-500/30'
                  : 'text-slate-300 hover:bg-slate-700/50 hover:text-white border border-transparent'
              }`}
              title={label}
            >
              <svg className="h-4 w-4 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d={VIEW_ICONS[key]} />
              </svg>
              <span>{label}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Layout Toggle */}
      <div className="bg-slate-800/90 backdrop-blur-sm rounded-xl border border-slate-700/50 p-3 shadow-xl">
        <div className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2 px-1">
          Layout
        </div>
        <div className="flex flex-col gap-1">
          <button
            onClick={() => onLayoutChange('force')}
            className={`flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium transition-all ${
              layoutMode === 'force'
                ? 'bg-blue-500/20 text-blue-400 border border-blue-500/30'
                : 'text-slate-300 hover:bg-slate-700/50 hover:text-white border border-transparent'
            }`}
          >
            <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
            Force
          </button>
          <button
            onClick={() => onLayoutChange('hierarchical')}
            className={`flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium transition-all ${
              layoutMode === 'hierarchical'
                ? 'bg-blue-500/20 text-blue-400 border border-blue-500/30'
                : 'text-slate-300 hover:bg-slate-700/50 hover:text-white border border-transparent'
            }`}
          >
            <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M4 5a1 1 0 011-1h14a1 1 0 011 1v2a1 1 0 01-1 1H5a1 1 0 01-1-1V5zM4 13a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H5a1 1 0 01-1-1v-6zM16 13a1 1 0 011-1h2a1 1 0 011 1v6a1 1 0 01-1 1h-2a1 1 0 01-1-1v-6z" />
            </svg>
            Hierarchical
          </button>
        </div>
      </div>
    </div>
  );
}
