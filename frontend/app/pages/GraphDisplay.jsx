import React, { useEffect, useRef, useMemo } from 'react';
import cytoscape from 'cytoscape';

const GraphDisplay = ({ data }) => {
  const containerRef = useRef(null);

  // 定义节点和边的样式
  const nodeStyle = {
    'background-color': '#666',
    'label': 'data(label)',
  };

  const edgeStyle = {
    'width': 3,
    'line-color': '#ccc',
    'target-arrow-color': '#ccc',
    'target-arrow-shape': 'triangle',
    'label': 'data(label)',
  };

  // 使用 useMemo 缓存生成的元素
  const elements = useMemo(() => {
    if (!data) return [];
    return data.flatMap(item => [
      { data: { id: item.source, label: item.source } },
      { data: { id: item.target, label: item.target } },
      { 
        data: { 
          id: `${item.source}-${item.target}`, 
          source: item.source, 
          target: item.target, 
          label: item.relation 
        } 
      },
    ]);
  }, [data]);

  useEffect(() => {
    if (!containerRef.current || !elements.length) return;

    // 初始化 Cytoscape 实例
    const cy = cytoscape({
      container: containerRef.current,
      elements,
      style: [
        { selector: 'node', style: nodeStyle },
        { selector: 'edge', style: edgeStyle },
      ],
      layout: {
        name: 'cose',
        nodeOverlap: 20,
        padding: 20,
      },
    });

    // 清理函数
    return () => {
      if (cy) {
        cy.destroy();
      }
    };
  }, [elements]);

  return (
    <div
      ref={containerRef}
      style={{ height: '500px', border: '1px solid #eee' }}
      aria-label="Graph Display"
    ></div>
  );
};

export default GraphDisplay;