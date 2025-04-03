'use client';

import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { APIService } from '@/services/api';
import { KnowledgeGraph, Granularity } from '@/types';
import { useStore } from '@/store';
import {
  ChartBarIcon,
  MagnifyingGlassIcon,
  ArrowDownTrayIcon,
} from '@heroicons/react/24/outline';

export default function GraphsPage() {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedGranularity, setSelectedGranularity] =
    useState<Granularity>('medium');
  const { graphs, setGraphs, setCurrentGraph } = useStore();

  // 获取图谱列表
  const { data: graphsData, isLoading } = useQuery({
    queryKey: ['graphs'],
    queryFn: APIService.getGraphs,
    onSuccess: (data) => {
      setGraphs(data);
    },
  });

  // 搜索图谱
  const { data: searchResults } = useQuery({
    queryKey: ['search', searchQuery],
    queryFn: () => APIService.searchGraph(searchQuery),
    enabled: searchQuery.length > 0,
  });

  // 导出图谱
  const handleExport = async (graphId: string) => {
    try {
      const blob = await APIService.exportGraph(graphId, {
        format: 'json',
        granularity: selectedGranularity,
        includeMetadata: true,
      });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `graph-${graphId}.json`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (error) {
      console.error('Export error:', error);
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-semibold text-gray-900">知识图谱</h1>
        <div className="flex items-center gap-4">
          <div className="relative">
            <div className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3">
              <MagnifyingGlassIcon
                className="h-5 w-5 text-gray-400"
                aria-hidden="true"
              />
            </div>
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="block w-full rounded-md border-0 py-1.5 pl-10 pr-3 text-gray-900 ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6"
              placeholder="搜索图谱..."
            />
          </div>
          <select
            value={selectedGranularity}
            onChange={(e) => setSelectedGranularity(e.target.value as Granularity)}
            className="block rounded-md border-0 py-1.5 pl-3 pr-10 text-gray-900 ring-1 ring-inset ring-gray-300 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6"
          >
            <option value="fine">细粒度</option>
            <option value="medium">中粒度</option>
            <option value="coarse">粗粒度</option>
          </select>
        </div>
      </div>

      {searchQuery ? (
        <div className="bg-white shadow overflow-hidden sm:rounded-md">
          <ul role="list" className="divide-y divide-gray-200">
            {searchResults?.map((result) => (
              <li key={result.entity}>
                <div className="px-4 py-4 sm:px-6">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center">
                      <ChartBarIcon className="h-5 w-5 text-gray-400" />
                      <p className="ml-2 text-sm font-medium text-indigo-600 truncate">
                        {result.entity}
                      </p>
                    </div>
                  </div>
                  <div className="mt-2">
                    <p className="text-sm text-gray-500">类型: {result.type}</p>
                    <div className="mt-2">
                      <h4 className="text-sm font-medium text-gray-900">
                        关系:
                      </h4>
                      <ul className="mt-1 space-y-1">
                        {result.relationships.map((rel) => (
                          <li
                            key={`${rel.target}-${rel.type}`}
                            className="text-sm text-gray-500"
                          >
                            {rel.target} ({rel.type})
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>
                </div>
              </li>
            ))}
          </ul>
        </div>
      ) : (
        <div className="bg-white shadow overflow-hidden sm:rounded-md">
          <ul role="list" className="divide-y divide-gray-200">
            {graphs.map((graph) => (
              <li key={graph.id}>
                <div className="px-4 py-4 sm:px-6">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center">
                      <ChartBarIcon className="h-5 w-5 text-gray-400" />
                      <p className="ml-2 text-sm font-medium text-indigo-600 truncate">
                        {graph.name}
                      </p>
                    </div>
                    <div className="ml-2 flex-shrink-0 flex">
                      <button
                        onClick={() => handleExport(graph.id)}
                        className="text-gray-400 hover:text-gray-500"
                      >
                        <ArrowDownTrayIcon className="h-5 w-5" />
                      </button>
                    </div>
                  </div>
                  <div className="mt-2 sm:flex sm:justify-between">
                    <div className="sm:flex">
                      <p className="flex items-center text-sm text-gray-500">
                        {graph.description}
                      </p>
                    </div>
                    <div className="mt-2 flex items-center text-sm text-gray-500 sm:mt-0">
                      <p>
                        创建于{' '}
                        {new Date(graph.created_at).toLocaleDateString('zh-CN')}
                      </p>
                    </div>
                  </div>
                  <div className="mt-2">
                    <div className="flex items-center text-sm text-gray-500">
                      <span className="mr-4">
                        节点数: {graph.stats.nodes}
                      </span>
                      <span>关系数: {graph.stats.relationships}</span>
                    </div>
                  </div>
                </div>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
} 