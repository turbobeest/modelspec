import { useEffect, useState } from 'react';
import type { GraphNode, ModelDetail } from '../types/graph';

interface DetailPanelProps {
  node: GraphNode | null;
  onClose: () => void;
  fetchModelDetail: (modelId: string) => Promise<ModelDetail | null>;
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

function formatParams(params: number | null | undefined): string {
  if (params == null) return 'N/A';
  if (params >= 1e12) return `${(params / 1e12).toFixed(1)}T`;
  if (params >= 1e9) return `${(params / 1e9).toFixed(1)}B`;
  if (params >= 1e6) return `${(params / 1e6).toFixed(1)}M`;
  if (params >= 1e3) return `${(params / 1e3).toFixed(1)}K`;
  return String(params);
}

function formatCost(cost: number | null | undefined): string {
  if (cost == null) return 'N/A';
  return `$${cost.toFixed(2)}/M`;
}

function formatContext(ctx: number | null | undefined): string {
  if (ctx == null) return 'N/A';
  if (ctx >= 1e6) return `${(ctx / 1e6).toFixed(1)}M`;
  if (ctx >= 1e3) return `${(ctx / 1e3).toFixed(0)}K`;
  return String(ctx);
}

export default function DetailPanel({ node, onClose, fetchModelDetail }: DetailPanelProps) {
  const [detail, setDetail] = useState<ModelDetail | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!node) {
      setDetail(null);
      return;
    }
    setLoading(true);
    fetchModelDetail(node.id).then((d) => {
      setDetail(d);
      setLoading(false);
    });
  }, [node, fetchModelDetail]);

  const isOpen = node !== null;
  const displayData = detail ?? node;
  const nodeType = node?.node_type;
  const modelType = displayData?.model_type ?? nodeType ?? 'unknown';
  const typeColor = MODEL_TYPE_COLORS[modelType] ?? '#6b7280';
  const displayLabel = node?.label ?? displayData?.id ?? '';

  return (
    <>
      {/* Backdrop */}
      {isOpen && (
        <div
          className="fixed inset-0 z-30 bg-black/20 transition-opacity"
          onClick={onClose}
        />
      )}

      {/* Panel */}
      <div
        className={`fixed top-0 right-0 h-full w-96 max-w-[90vw] z-40 bg-slate-800/95 backdrop-blur-md border-l border-slate-700/50 shadow-2xl transform transition-transform duration-300 ease-in-out ${
          isOpen ? 'translate-x-0' : 'translate-x-full'
        }`}
      >
        {displayData && (
          <div className="h-full flex flex-col">
            {/* Header */}
            <div className="flex items-start justify-between p-6 border-b border-slate-700/50">
              <div className="flex-1 min-w-0">
                <h2 className="text-lg font-bold text-white truncate">
                  {displayLabel}
                </h2>
                {'provider' in displayData && displayData.provider && (
                  <p className="text-sm text-slate-400 mt-0.5">{displayData.provider}</p>
                )}
                <span
                  className="inline-block mt-2 px-2.5 py-0.5 rounded-full text-xs font-medium"
                  style={{
                    backgroundColor: `${typeColor}20`,
                    color: typeColor,
                    border: `1px solid ${typeColor}40`,
                  }}
                >
                  {modelType}
                </span>
              </div>
              <button
                onClick={onClose}
                className="ml-4 p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-700/50 transition-all"
              >
                <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            {/* Content */}
            <div className="flex-1 overflow-y-auto p-6">
              {loading ? (
                <div className="flex items-center justify-center py-12">
                  <div className="animate-spin rounded-full h-8 w-8 border-2 border-slate-600 border-t-blue-400" />
                </div>
              ) : (
                <div className="space-y-6">
                  {/* Key Stats */}
                  <div>
                    <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-3">
                      Key Stats
                    </h3>
                    <div className="grid grid-cols-2 gap-3">
                      <StatCard
                        label="Parameters"
                        value={formatParams(displayData.parameter_count)}
                      />
                      <StatCard
                        label="Context Window"
                        value={formatContext(displayData.context_window)}
                      />
                      <StatCard
                        label="Arena ELO"
                        value={displayData.arena_elo?.toString() ?? 'N/A'}
                      />
                      <StatCard
                        label="Release Date"
                        value={displayData.release_date ?? 'N/A'}
                      />
                    </div>
                  </div>

                  {/* Cost */}
                  {(displayData.cost_input != null || displayData.cost_output != null) && (
                    <div>
                      <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-3">
                        Pricing
                      </h3>
                      <div className="grid grid-cols-2 gap-3">
                        <StatCard
                          label="Input Cost"
                          value={formatCost(displayData.cost_input)}
                        />
                        <StatCard
                          label="Output Cost"
                          value={formatCost(displayData.cost_output)}
                        />
                      </div>
                    </div>
                  )}

                  {/* Description */}
                  {detail?.description && (
                    <div>
                      <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">
                        Description
                      </h3>
                      <p className="text-sm text-slate-300 leading-relaxed">
                        {detail.description}
                      </p>
                    </div>
                  )}

                  {/* License */}
                  {detail?.license && (
                    <div>
                      <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">
                        License
                      </h3>
                      <p className="text-sm text-slate-300">{detail.license}</p>
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </>
  );
}

function StatCard({ label, value }: { label: string; value: string }) {
  return (
    <div className="bg-slate-700/30 rounded-lg p-3 border border-slate-600/20">
      <div className="text-xs text-slate-500 mb-1">{label}</div>
      <div className="text-sm font-semibold text-slate-200">{value}</div>
    </div>
  );
}
