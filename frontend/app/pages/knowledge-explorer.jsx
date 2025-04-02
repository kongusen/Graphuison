 // frontend/pages/knowledge-explorer.jsx
 import React, { useState, useEffect } from 'react';
 import Navbar from '@/components/common/Navbar';
 import GraphDisplay from '@/components/graph/GraphDisplay';
 import { getAllGraphData, fuseGraph } from '@/utils/api';

 const KnowledgeExplorer = () => {
     const [graphData, setGraphData] = useState([]);
     const [fusedTriples, setFusedTriples] = useState([]);
     const [loading, setLoading] = useState(true);
     const [error, setError] = useState(null);

     useEffect(() => {
         const fetchGraphData = async () => {
           try {
               setLoading(true);
              // 获取图谱所有数据
              const allData = await getAllGraphData();
              setGraphData(allData);
              // 获取融合后的三元组数据，用于展示列表
             const fusedData = await fuseGraph([], [], 1, 100);
              setFusedTriples(fusedData.fused_triples);
              setLoading(false)
          }  catch (err){
             console.log(err)
               setError(err.message);
               setLoading(false)
           }
         };

         fetchGraphData();
     }, []);

     if (loading) return <div>Loading...</div>;
     if (error) return <div>Error: {error}</div>
     return (
         <div>
             <Navbar />
             <div className="container mx-auto p-4">
                 <h1 className="text-2xl font-bold mb-4">Knowledge Explorer</h1>
                 <div className="flex">
                     <div className="w-3/4">
                      <GraphDisplay data={graphData} />
                      </div>
                         <div className="w-1/4 pl-4">
                             <h2 className="text-xl font-semibold mb-2">Entities</h2>
                             <ul>
                                 {[...new Set(graphData.flatMap(item => [item.source, item.target]))].map((entity, index) => (
                                   <li key={index}>{entity}</li>
                                  ))}
                              </ul>
                           <h2 className="text-xl font-semibold mb-2 mt-4">Triples</h2>
                            <ul>
                              {fusedTriples.map((triple, index) => (
                                     <li key={index}>{`${triple.subject} - ${triple.relation} - ${triple.object}`}</li>
                                  ))}
                             </ul>
                      </div>
                 </div>
              </div>
         </div>
     );
 };

 export default KnowledgeExplorer;