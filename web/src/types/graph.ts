export interface GraphNode {
  id: string;
  label: string;
  node_type: string;
  model_type?: string;
  provider?: string;
  parameter_count?: number | null;
  context_window?: number | null;
  arena_elo?: number | null;
  cost_input?: number | null;
  cost_output?: number | null;
  release_date?: string | null;
}

export interface GraphEdge {
  source: string;
  target: string;
  edge_type: string;
  weight?: number;
  label?: string;
}

export interface GraphData {
  nodes: GraphNode[];
  edges: GraphEdge[];
}

export interface ModelDetail {
  id: string;
  name: string;
  provider: string;
  model_type: string;
  parameter_count?: number | null;
  context_window?: number | null;
  arena_elo?: number | null;
  cost_input?: number | null;
  cost_output?: number | null;
  release_date?: string | null;
  description?: string | null;
  license?: string | null;
}

export interface StatsData {
  total_nodes: number;
  total_edges: number;
  model_count: number;
  provider_count: number;
  model_types: Record<string, number>;
}

export type EdgeView = 'all' | 'providers' | 'lineage' | 'hardware' | 'platforms' | 'benchmarks';

export type LayoutMode = 'force' | 'hierarchical';

export interface SimulationNode extends GraphNode, d3.SimulationNodeDatum {
  x?: number;
  y?: number;
  fx?: number | null;
  fy?: number | null;
}

export interface SimulationEdge extends d3.SimulationLinkDatum<SimulationNode> {
  edge_type: string;
  weight?: number;
  label?: string;
}

import type * as d3 from 'd3';
export type D3Module = typeof d3;
