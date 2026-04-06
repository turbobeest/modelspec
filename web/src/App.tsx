import { useState, useCallback } from 'react';
import GraphExplorer from './components/GraphExplorer';
import Sidebar from './components/Sidebar';
import DetailPanel from './components/DetailPanel';
import SearchBar from './components/SearchBar';
import Legend from './components/Legend';
import StatsBar from './components/StatsBar';
import { useGraphData } from './hooks/useGraphData';
import type { GraphNode, EdgeView, LayoutMode } from './types/graph';

export default function App() {
  const { graphData, loading, error, fetchGraph, fetchModelDetail } = useGraphData();
  const [currentView, setCurrentView] = useState<EdgeView>('all');
  const [layoutMode, setLayoutMode] = useState<LayoutMode>('force');
  const [selectedNode, setSelectedNode] = useState<GraphNode | null>(null);
  const [searchQuery, setSearchQuery] = useState('');

  const handleViewChange = useCallback(
    (view: EdgeView) => {
      setCurrentView(view);
      fetchGraph(view);
    },
    [fetchGraph],
  );

  const handleNodeClick = useCallback((node: GraphNode) => {
    setSelectedNode(node);
  }, []);

  const handleCloseDetail = useCallback(() => {
    setSelectedNode(null);
  }, []);

  const handleSearch = useCallback((query: string) => {
    setSearchQuery(query);
  }, []);

  const nodes = graphData?.nodes ?? [];
  const edges = graphData?.edges ?? [];

  return (
    <div className="w-full h-full relative" style={{ backgroundColor: '#0a0e17' }}>
      {/* Search Bar */}
      <SearchBar onSearch={handleSearch} />

      {/* Left Sidebar */}
      <Sidebar
        currentView={currentView}
        onViewChange={handleViewChange}
        layoutMode={layoutMode}
        onLayoutChange={setLayoutMode}
      />

      {/* Main Graph Area */}
      <div className="w-full h-full">
        {loading && nodes.length === 0 ? (
          <div className="w-full h-full flex items-center justify-center">
            <div className="text-center">
              <div className="animate-spin rounded-full h-12 w-12 border-2 border-slate-600 border-t-blue-400 mx-auto mb-4" />
              <p className="text-slate-400 text-sm">Loading graph data...</p>
            </div>
          </div>
        ) : error ? (
          <div className="w-full h-full flex items-center justify-center">
            <div className="text-center max-w-md px-4">
              <div className="w-16 h-16 rounded-full bg-red-500/10 flex items-center justify-center mx-auto mb-4">
                <svg
                  className="h-8 w-8 text-red-400"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z"
                  />
                </svg>
              </div>
              <h2 className="text-lg font-semibold text-white mb-2">
                Unable to Load Graph
              </h2>
              <p className="text-slate-400 text-sm mb-4">{error}</p>
              <p className="text-slate-500 text-xs">
                Make sure the API server is running at http://localhost:8000
              </p>
              <button
                onClick={() => fetchGraph(currentView)}
                className="mt-4 px-4 py-2 bg-blue-500/20 text-blue-400 rounded-lg border border-blue-500/30 text-sm hover:bg-blue-500/30 transition-colors"
              >
                Retry
              </button>
            </div>
          </div>
        ) : nodes.length === 0 ? (
          <div className="w-full h-full flex items-center justify-center">
            <div className="text-center">
              <p className="text-slate-400 text-sm">No data to display</p>
            </div>
          </div>
        ) : (
          <GraphExplorer
            nodes={nodes}
            edges={edges}
            layoutMode={layoutMode}
            searchQuery={searchQuery}
            onNodeClick={handleNodeClick}
          />
        )}
      </div>

      {/* Legend */}
      {nodes.length > 0 && <Legend nodes={nodes} />}

      {/* Stats Bar */}
      <StatsBar nodeCount={nodes.length} edgeCount={edges.length} currentView={currentView} />

      {/* Detail Panel */}
      <DetailPanel
        node={selectedNode}
        onClose={handleCloseDetail}
        fetchModelDetail={fetchModelDetail}
      />
    </div>
  );
}
