import { useState, useEffect, useCallback } from 'react';
import type { GraphData, ModelDetail, StatsData, EdgeView } from '../types/graph';

const API_BASE = '/api/v1';

interface UseGraphDataReturn {
  graphData: GraphData | null;
  stats: StatsData | null;
  loading: boolean;
  error: string | null;
  fetchGraph: (view: EdgeView) => Promise<void>;
  fetchModelDetail: (modelId: string) => Promise<ModelDetail | null>;
  searchModels: (query: string, type?: string) => Promise<GraphData | null>;
}

export function useGraphData(): UseGraphDataReturn {
  const [graphData, setGraphData] = useState<GraphData | null>(null);
  const [stats, setStats] = useState<StatsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchGraph = useCallback(async (view: EdgeView) => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_BASE}/graph?view=${view}`);
      if (!response.ok) throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      const data: GraphData = await response.json();
      setGraphData(data);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to fetch graph data';
      setError(message);
      setGraphData(null);
    } finally {
      setLoading(false);
    }
  }, []);

  const fetchStats = useCallback(async () => {
    try {
      const response = await fetch(`${API_BASE}/stats`);
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      const data: StatsData = await response.json();
      setStats(data);
    } catch {
      // Stats are non-critical, silently fail
    }
  }, []);

  const fetchModelDetail = useCallback(async (modelId: string): Promise<ModelDetail | null> => {
    try {
      const response = await fetch(`${API_BASE}/models/${encodeURIComponent(modelId)}`);
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return await response.json();
    } catch {
      return null;
    }
  }, []);

  const searchModels = useCallback(async (query: string, type?: string): Promise<GraphData | null> => {
    try {
      const params = new URLSearchParams({ q: query });
      if (type) params.set('type', type);
      const response = await fetch(`${API_BASE}/search?${params.toString()}`);
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return await response.json();
    } catch {
      return null;
    }
  }, []);

  useEffect(() => {
    fetchGraph('all');
    fetchStats();
  }, [fetchGraph, fetchStats]);

  return { graphData, stats, loading, error, fetchGraph, fetchModelDetail, searchModels };
}
