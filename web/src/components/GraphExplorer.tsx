import { useEffect, useRef, useCallback, useMemo } from 'react';
import * as d3 from 'd3';
import type { GraphNode, GraphEdge, SimulationNode, SimulationEdge, LayoutMode } from '../types/graph';

interface GraphExplorerProps {
  nodes: GraphNode[];
  edges: GraphEdge[];
  layoutMode: LayoutMode;
  searchQuery: string;
  onNodeClick: (node: GraphNode) => void;
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

const EDGE_TYPE_COLORS: Record<string, string> = {
  MADE_BY: '#64748b',
  DERIVED_FROM: '#8b5cf6',
  FITS_ON: '#22c55e',
  AVAILABLE_ON: '#3b82f6',
  SCORED_ON: '#f59e0b',
};

const DEFAULT_NODE_COLOR = '#6b7280';
const DEFAULT_EDGE_COLOR = '#334155';

function getNodeColor(node: GraphNode): string {
  if (node.node_type === 'provider') return MODEL_TYPE_COLORS.provider;
  return MODEL_TYPE_COLORS[node.model_type ?? ''] ?? DEFAULT_NODE_COLOR;
}

function getNodeRadius(node: GraphNode): number {
  const params = node.parameter_count;
  if (params == null || params <= 0) return 4;
  // Log scale: 1M = 4, 1B = 6, 100B = 8, 1T = 10
  const logVal = Math.log10(params);
  const radius = Math.max(3, Math.min(14, 1.5 + logVal * 0.8));
  return radius;
}

function getEdgeColor(edge: GraphEdge): string {
  return EDGE_TYPE_COLORS[edge.edge_type] ?? DEFAULT_EDGE_COLOR;
}

export default function GraphExplorer({
  nodes,
  edges,
  layoutMode,
  searchQuery,
  onNodeClick,
}: GraphExplorerProps) {
  const svgRef = useRef<SVGSVGElement>(null);
  const simulationRef = useRef<d3.Simulation<SimulationNode, SimulationEdge> | null>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  // Build lookup for search highlighting
  const highlightedNodeIds = useMemo(() => {
    if (!searchQuery.trim()) return null;
    const q = searchQuery.toLowerCase();
    const matched = new Set<string>();
    for (const node of nodes) {
      if (
        node.label?.toLowerCase().includes(q) ||
        node.id.toLowerCase().includes(q) ||
        node.model_type?.toLowerCase().includes(q) ||
        node.provider?.toLowerCase().includes(q) ||
        node.node_type?.toLowerCase().includes(q)
      ) {
        matched.add(node.id);
      }
    }
    return matched.size > 0 ? matched : null;
  }, [nodes, searchQuery]);

  const handleNodeClick = useCallback(
    (_event: MouseEvent, d: SimulationNode) => {
      onNodeClick(d as GraphNode);
    },
    [onNodeClick],
  );

  useEffect(() => {
    if (!svgRef.current || !containerRef.current) return;
    if (nodes.length === 0) return;

    const svg = d3.select(svgRef.current);
    const container = containerRef.current;
    const width = container.clientWidth;
    const height = container.clientHeight;

    // Clear previous
    svg.selectAll('*').remove();
    if (simulationRef.current) {
      simulationRef.current.stop();
    }

    svg.attr('width', width).attr('height', height);

    // Defs for glow filter
    const defs = svg.append('defs');
    const filter = defs.append('filter').attr('id', 'glow');
    filter
      .append('feGaussianBlur')
      .attr('stdDeviation', '3')
      .attr('result', 'coloredBlur');
    const feMerge = filter.append('feMerge');
    feMerge.append('feMergeNode').attr('in', 'coloredBlur');
    feMerge.append('feMergeNode').attr('in', 'SourceGraphic');

    // Container group for zoom
    const g = svg.append('g');

    // Zoom behavior
    const zoom = d3
      .zoom<SVGSVGElement, unknown>()
      .scaleExtent([0.1, 8])
      .on('zoom', (event: d3.D3ZoomEvent<SVGSVGElement, unknown>) => {
        g.attr('transform', event.transform.toString());
      });
    svg.call(zoom);

    // Prepare data
    const simNodes: SimulationNode[] = nodes.map((n) => ({ ...n }));
    const nodeMap = new Map(simNodes.map((n) => [n.id, n]));

    const simEdges: SimulationEdge[] = edges
      .filter((e) => nodeMap.has(e.source) && nodeMap.has(e.target))
      .map((e) => ({
        source: e.source,
        target: e.target,
        edge_type: e.edge_type,
        weight: e.weight,
        label: e.label,
      }));

    // Draw edges
    const linkGroup = g.append('g').attr('class', 'edges');
    const link = linkGroup
      .selectAll<SVGLineElement, SimulationEdge>('line')
      .data(simEdges)
      .join('line')
      .attr('stroke', (d) => getEdgeColor(d as unknown as GraphEdge))
      .attr('stroke-opacity', 0.15)
      .attr('stroke-width', 0.5);

    // Draw nodes
    const nodeGroup = g.append('g').attr('class', 'nodes');
    const nodeSelection = nodeGroup
      .selectAll<SVGCircleElement, SimulationNode>('circle')
      .data(simNodes)
      .join('circle')
      .attr('r', (d) => getNodeRadius(d))
      .attr('fill', (d) => getNodeColor(d))
      .attr('stroke', (d) => getNodeColor(d))
      .attr('stroke-width', 1)
      .attr('stroke-opacity', 0.5)
      .style('filter', 'url(#glow)')
      .style('cursor', 'pointer')
      .on('click', handleNodeClick as unknown as (this: SVGCircleElement, event: MouseEvent, d: SimulationNode) => void);

    // Drag behavior
    const drag = d3
      .drag<SVGCircleElement, SimulationNode>()
      .on('start', (event: d3.D3DragEvent<SVGCircleElement, SimulationNode, SimulationNode>, d) => {
        if (!event.active) simulationRef.current?.alphaTarget(0.3).restart();
        d.fx = d.x;
        d.fy = d.y;
      })
      .on('drag', (event: d3.D3DragEvent<SVGCircleElement, SimulationNode, SimulationNode>, d) => {
        d.fx = event.x;
        d.fy = event.y;
      })
      .on('end', (event: d3.D3DragEvent<SVGCircleElement, SimulationNode, SimulationNode>, d) => {
        if (!event.active) simulationRef.current?.alphaTarget(0);
        d.fx = null;
        d.fy = null;
      });
    nodeSelection.call(drag);

    // Tooltip
    const tooltip = d3
      .select(container)
      .selectAll<HTMLDivElement, unknown>('.graph-tooltip')
      .data([null])
      .join('div')
      .attr(
        'class',
        'graph-tooltip absolute pointer-events-none z-50 bg-slate-800/95 backdrop-blur-sm border border-slate-600/50 rounded-lg px-3 py-2 text-xs shadow-xl transition-opacity duration-150',
      )
      .style('opacity', '0');

    nodeSelection
      .on('mouseenter', (event: MouseEvent, d) => {
        const params = d.parameter_count;
        let paramsStr = 'N/A';
        if (params != null) {
          if (params >= 1e9) paramsStr = `${(params / 1e9).toFixed(1)}B`;
          else if (params >= 1e6) paramsStr = `${(params / 1e6).toFixed(1)}M`;
          else paramsStr = String(params);
        }

        tooltip
          .html(
            `<div class="font-semibold text-white mb-1">${d.label ?? d.id}</div>` +
              `<div class="text-slate-400">Type: <span class="text-slate-200">${d.model_type ?? d.node_type}</span></div>` +
              `<div class="text-slate-400">Params: <span class="text-slate-200">${paramsStr}</span></div>` +
              (d.arena_elo != null
                ? `<div class="text-slate-400">Arena ELO: <span class="text-slate-200">${d.arena_elo}</span></div>`
                : ''),
          )
          .style('opacity', '1')
          .style('left', `${event.offsetX + 12}px`)
          .style('top', `${event.offsetY - 10}px`);

        // Highlight connected edges
        link.attr('stroke-opacity', (l) => {
          const src = typeof l.source === 'object' ? (l.source as SimulationNode).id : l.source;
          const tgt = typeof l.target === 'object' ? (l.target as SimulationNode).id : l.target;
          return src === d.id || tgt === d.id ? 0.6 : 0.05;
        }).attr('stroke-width', (l) => {
          const src = typeof l.source === 'object' ? (l.source as SimulationNode).id : l.source;
          const tgt = typeof l.target === 'object' ? (l.target as SimulationNode).id : l.target;
          return src === d.id || tgt === d.id ? 1.5 : 0.5;
        });
      })
      .on('mousemove', (event: MouseEvent) => {
        tooltip
          .style('left', `${event.offsetX + 12}px`)
          .style('top', `${event.offsetY - 10}px`);
      })
      .on('mouseleave', () => {
        tooltip.style('opacity', '0');
        link.attr('stroke-opacity', 0.15).attr('stroke-width', 0.5);
      });

    // Force simulation
    const simulation = d3
      .forceSimulation<SimulationNode>(simNodes)
      .force(
        'link',
        d3
          .forceLink<SimulationNode, SimulationEdge>(simEdges)
          .id((d) => d.id)
          .distance(layoutMode === 'hierarchical' ? 80 : 50)
          .strength(0.3),
      )
      .force('charge', d3.forceManyBody().strength(layoutMode === 'hierarchical' ? -120 : -80))
      .force('center', d3.forceCenter(width / 2, height / 2))
      .force('collision', d3.forceCollide<SimulationNode>().radius((d) => getNodeRadius(d) + 2));

    if (layoutMode === 'hierarchical') {
      // Add Y force to separate by node type
      const typeOrder: Record<string, number> = {
        provider: 0,
        'llm-reasoning': 1,
        'llm-chat': 2,
        'llm-code': 3,
        vlm: 4,
        'embedding-text': 5,
        'image-generation': 6,
      };
      simulation.force(
        'y',
        d3
          .forceY<SimulationNode>()
          .y((d) => {
            const type = d.node_type === 'provider' ? 'provider' : (d.model_type ?? '');
            const order = typeOrder[type] ?? 3;
            return (height * (order + 1)) / 8;
          })
          .strength(0.3),
      );
      simulation.force(
        'x',
        d3.forceX<SimulationNode>().x(width / 2).strength(0.05),
      );
    }

    simulation.on('tick', () => {
      link
        .attr('x1', (d) => (d.source as SimulationNode).x ?? 0)
        .attr('y1', (d) => (d.source as SimulationNode).y ?? 0)
        .attr('x2', (d) => (d.target as SimulationNode).x ?? 0)
        .attr('y2', (d) => (d.target as SimulationNode).y ?? 0);

      nodeSelection.attr('cx', (d) => d.x ?? 0).attr('cy', (d) => d.y ?? 0);
    });

    simulationRef.current = simulation;

    // Initial zoom to fit
    const initialTransform = d3.zoomIdentity
      .translate(width / 2, height / 2)
      .scale(0.8)
      .translate(-width / 2, -height / 2);
    svg.call(zoom.transform, initialTransform);

    return () => {
      simulation.stop();
      tooltip.remove();
    };
  }, [nodes, edges, layoutMode, handleNodeClick]);

  // Update search highlighting without re-creating the simulation
  useEffect(() => {
    if (!svgRef.current) return;
    const svg = d3.select(svgRef.current);

    if (highlightedNodeIds === null) {
      // Reset all nodes to full opacity
      svg.selectAll<SVGCircleElement, SimulationNode>('.nodes circle')
        .attr('opacity', 1)
        .attr('r', (d) => getNodeRadius(d));
      svg.selectAll('.edges line').attr('stroke-opacity', 0.15);
    } else {
      // Dim non-matching nodes
      svg.selectAll<SVGCircleElement, SimulationNode>('.nodes circle')
        .attr('opacity', (d) => (highlightedNodeIds.has(d.id) ? 1 : 0.15))
        .attr('r', (d) =>
          highlightedNodeIds.has(d.id) ? getNodeRadius(d) * 1.5 : getNodeRadius(d) * 0.7,
        );
      svg.selectAll<SVGLineElement, SimulationEdge>('.edges line').attr('stroke-opacity', (d) => {
        const src = typeof d.source === 'object' ? (d.source as SimulationNode).id : String(d.source);
        const tgt = typeof d.target === 'object' ? (d.target as SimulationNode).id : String(d.target);
        return highlightedNodeIds.has(src) || highlightedNodeIds.has(tgt) ? 0.4 : 0.03;
      });
    }
  }, [highlightedNodeIds]);

  return (
    <div ref={containerRef} className="w-full h-full relative overflow-hidden">
      <svg ref={svgRef} className="w-full h-full" />
    </div>
  );
}
