'use client';

import { FC, useState, useEffect, useRef } from 'react';
import { useQuery } from '@tanstack/react-query';
import { APIService } from '@/services/api';
import { Graph } from '@/types';
import Alert from '@/components/common/Alert';
import Button from '@/components/common/Button';
import { MagnifyingGlassIcon, ArrowDownTrayIcon } from '@heroicons/react/24/outline';
import * as d3 from 'd3';

const GraphPage: FC = () => {
  const [error, setError] = useState<string>('');
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedNode, setSelectedNode] = useState<Graph['nodes'][0] | null>(null);
  const svgRef = useRef<SVGSVGElement>(null);

  const { data: graph, isLoading } = useQuery({
    queryKey: ['graph'],
    queryFn: APIService.getGraph,
  });

  useEffect(() => {
    if (!graph || !svgRef.current) return;

    const width = 800;
    const height = 600;
    const margin = { top: 20, right: 20, bottom: 20, left: 20 };

    // 清除现有的SVG内容
    d3.select(svgRef.current).selectAll('*').remove();

    // 创建SVG
    const svg = d3
      .select(svgRef.current)
      .attr('width', width)
      .attr('height', height);

    // 创建力导向图
    const simulation = d3
      .forceSimulation(graph.nodes)
      .force('link', d3.forceLink(graph.links).id((d: any) => d.id))
      .force('charge', d3.forceManyBody().strength(-100))
      .force('center', d3.forceCenter(width / 2, height / 2));

    // 创建箭头标记
    svg
      .append('defs')
      .append('marker')
      .attr('id', 'arrowhead')
      .attr('viewBox', '-0 -5 27 10')
      .attr('refX', 13)
      .attr('refY', 0)
      .attr('orient', 'auto')
      .attr('markerWidth', 6)
      .attr('markerHeight', 6)
      .append('path')
      .attr('d', 'M 0 -5 L 10 0 L 0 5')
      .attr('fill', '#999');

    // 创建连接线
    const link = svg
      .append('g')
      .selectAll('line')
      .data(graph.links)
      .join('line')
      .attr('stroke', '#999')
      .attr('stroke-opacity', 0.6)
      .attr('marker-end', 'url(#arrowhead)');

    // 创建节点
    const node = svg
      .append('g')
      .selectAll('circle')
      .data(graph.nodes)
      .join('circle')
      .attr('r', 5)
      .attr('fill', '#69b3a2')
      .call(drag(simulation) as any);

    // 添加节点标签
    const label = svg
      .append('g')
      .selectAll('text')
      .data(graph.nodes)
      .join('text')
      .text((d: any) => d.name)
      .attr('font-size', 12)
      .attr('dx', 8)
      .attr('dy', 3);

    // 更新力导向图
    simulation.on('tick', () => {
      link
        .attr('x1', (d: any) => d.source.x)
        .attr('y1', (d: any) => d.source.y)
        .attr('x2', (d: any) => d.target.x)
        .attr('y2', (d: any) => d.target.y);

      node
        .attr('cx', (d: any) => d.x)
        .attr('cy', (d: any) => d.y);

      label
        .attr('x', (d: any) => d.x)
        .attr('y', (d: any) => d.y);
    });

    // 添加节点点击事件
    node.on('click', (event, d: any) => {
      setSelectedNode(d);
    });

    // 添加拖拽功能
    function drag(simulation: d3.Simulation<any, undefined>) {
      function dragstarted(event: any) {
        if (!event.active) simulation.alphaTarget(0.3).restart();
        event.subject.fx = event.subject.x;
        event.subject.fy = event.subject.y;
      }

      function dragged(event: any) {
        event.subject.fx = event.x;
        event.subject.fy = event.y;
      }

      function dragended(event: any) {
        if (!event.active) simulation.alphaTarget(0);
        event.subject.fx = null;
        event.subject.fy = null;
      }

      return d3
        .drag()
        .on('start', dragstarted)
        .on('drag', dragged)
        .on('end', dragended);
    }
  }, [graph]);

  const handleExport = () => {
    if (!graph) return;
    const dataStr = JSON.stringify(graph, null, 2);
    const dataUri = 'data:application/json;charset=utf-8,' + encodeURIComponent(dataStr);
    const exportFileDefaultName = 'graph.json';

    const linkElement = document.createElement('a');
    linkElement.setAttribute('href', dataUri);
    linkElement.setAttribute('download', exportFileDefaultName);
    linkElement.click();
  };

  if (isLoading) {
    return <div>加载中...</div>;
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-2xl font-bold text-gray-900">知识图谱</h1>
        <div className="flex items-center gap-4">
          <Button
            onClick={handleExport}
            variant="secondary"
            size="sm"
          >
            <ArrowDownTrayIcon className="h-5 w-5 mr-2" />
            导出图谱
          </Button>
        </div>
      </div>

      {error && (
        <Alert
          type="error"
          message={error}
          onClose={() => setError('')}
        />
      )}

      <div className="bg-white shadow rounded-lg p-4">
        <div className="mb-4">
          <div className="relative">
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="搜索节点..."
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
            />
            <MagnifyingGlassIcon className="h-5 w-5 text-gray-400 absolute left-3 top-2.5" />
          </div>
        </div>

        <div className="relative">
          <svg ref={svgRef} className="w-full h-[600px] border border-gray-200 rounded-lg" />
          
          {selectedNode && (
            <div className="absolute top-4 right-4 bg-white p-4 rounded-lg shadow-lg max-w-sm">
              <h3 className="text-lg font-semibold mb-2">{selectedNode.name}</h3>
              <p className="text-sm text-gray-600">{selectedNode.description}</p>
              <div className="mt-2">
                <h4 className="text-sm font-medium text-gray-900">属性:</h4>
                <ul className="mt-1 text-sm text-gray-600">
                  {Object.entries(selectedNode.properties || {}).map(([key, value]) => (
                    <li key={key}>
                      {key}: {value}
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default GraphPage; 