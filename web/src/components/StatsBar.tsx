import type { EdgeView } from '../types/graph';

interface StatsBarProps {
  nodeCount: number;
  edgeCount: number;
  currentView: EdgeView;
}

const VIEW_LABELS: Record<EdgeView, string> = {
  all: 'All',
  providers: 'Providers',
  lineage: 'Lineage',
  hardware: 'Hardware',
  platforms: 'Platforms',
  benchmarks: 'Benchmarks',
};

function formatNumber(n: number): string {
  if (n >= 1000) {
    return n.toLocaleString();
  }
  return String(n);
}

export default function StatsBar({ nodeCount, edgeCount, currentView }: StatsBarProps) {
  return (
    <div className="absolute bottom-0 left-0 right-0 z-20 bg-slate-900/90 backdrop-blur-sm border-t border-slate-700/50 px-4 py-2">
      <div className="flex items-center justify-center gap-6 text-xs text-slate-400">
        <span>
          Nodes: <span className="text-slate-200 font-medium">{formatNumber(nodeCount)}</span>
        </span>
        <span className="text-slate-600">|</span>
        <span>
          Edges: <span className="text-slate-200 font-medium">{formatNumber(edgeCount)}</span>
        </span>
        <span className="text-slate-600">|</span>
        <span>
          View: <span className="text-blue-400 font-medium">{VIEW_LABELS[currentView]}</span>
        </span>
      </div>
    </div>
  );
}
