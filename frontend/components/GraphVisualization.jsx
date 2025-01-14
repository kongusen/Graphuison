// components/GraphVisualization.js
import React, { useEffect, useRef, useState } from 'react';
import cytoscape from 'cytoscape';
import { Modal } from 'antd'; // 引入 Modal 组件

const GraphVisualization = ({ graphData }) => {
  const containerRef = useRef(null);
  const [selectedNode, setSelectedNode] = useState(null); // 存储选中的节点

  useEffect(() => {
    if (containerRef.current && graphData && graphData.nodes && graphData.edges) {
        const cy = cytoscape({
            container: containerRef.current,
            elements: {
                nodes: graphData.nodes.map(node => ({ data: node })),
                edges: graphData.edges.map(edge => ({ data: edge })),
            },
             style: [
                {
                  selector: 'node',
                  style: {
                    'background-color': '#666',
                    'label': 'data(label)',
                    'width': '50px',
                    'height': '50px'
                  }
                },
                {
                  selector: 'edge',
                  style: {
                    'width': 3,
                    'line-color': '#ccc',
                    'label': 'data(relation)',
                    'target-arrow-color': '#ccc',
                    'target-arrow-shape': 'triangle'
                  }
                }
              ],
             layout: {
              name: 'cose'
             }
        });
        cy.on('tap', 'node', (evt) => {
            const tappedNode = evt.target;
            setSelectedNode(tappedNode.data());  // 获取点击节点的 data
        });
            //  节点取消选中时，将 selectedNode 设置为 null
        cy.on('tap', (evt) => {
           if (evt.target === cy) {
              setSelectedNode(null);
           }
        })
    }
  }, [graphData]);

    const handleCloseModal = () => {
        setSelectedNode(null);
     }


  return (
       <>
          <div ref={containerRef} style={{ height: '800px', border: '1px solid #ccc' }} />
          {selectedNode && (
             <Modal
              title={`Node Details for ${selectedNode.label}`}
                visible={selectedNode !== null}
               onCancel={handleCloseModal}
               footer={null}
             >
                 {Object.entries(selectedNode).map(([key, value]) => (
                   <div key={key}>
                    <strong>{key}:</strong> {JSON.stringify(value)}
                    </div>
                ))}
            </Modal>
         )}
        </>
    );
};

export default GraphVisualization;