import type { GraphNode } from '../types/graph';

interface LegendProps {
  nodes: GraphNode[];
}

const MODEL_TYPE_COLORS: Record<string, string> = {
  'llm-chat': '#3b82f6',
  'llm-reasoning': '#8b5cf6',
  'llm-code': '#22c55e',
  vlm: '#14b8a6',
  'embedding-text': '#f59e0b',
  'image-generation': '#ec4899',
  provider: '#64748b',
};

const MODEL_TYPE_LABELS: Record<string, string> = {
  'llm-chat': 'LLM Chat',
  'llm-reasoning': 'LLM Reasoning',
  'llm-code': 'LLM Code',
  vlm: 'Vision LM',
  'embedding-text': 'Text Embedding',
  'image-generation': 'Image Gen',
  provider: 'Provider',
};

const DEFAULT_COLOR = '#6b7280';

export default function Legend({ nodes }: LegendProps) {
  // Count nodes by type
  const typeCounts = new Map<string, number>();
  for (const node of nodes) {
    const type = node.node_type === 'provider' ? 'provider' : (node.model_type ?? 'other');
    typeCounts.set(type, (typeCounts.get(type) ?? 0) + 1);
  }

  // Sort by count descending
  const entries = [...typeCounts.entries()].sort((a, b) => b[1] - a[1]);

  return (
    <div className="absolute bottom-14 left-4 z-20 bg-slate-800/90 backdrop-blur-sm rounded-xl border border-slate-700/50 p-3 shadow-xl max-w-xs">
      <div className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">
        Model Types
      </div>
      <div className="grid grid-cols-2 gap-x-4 gap-y-1">
        {entries.map(([type, count]) => (
          <div key={type} className="flex items-center gap-2 text-xs">
            <span
              className="w-2.5 h-2.5 rounded-full flex-shrink-0"
              style={{
                backgroundColor: MODEL_TYPE_COLORS[type] ?? DEFAULT_COLOR,
                boxShadow: `0 0 6px ${MODEL_TYPE_COLORS[type] ?? DEFAULT_COLOR}60`,
              }}
            />
            <span className="text-slate-300 truncate">
              {MODEL_TYPE_LABELS[type] ?? type}
            </span>
            <span className="text-slate-500 ml-auto">{count}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
