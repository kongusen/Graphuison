// pages/index.js
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import GraphVisualization from '../components/GraphVisualization';
import Controls from '../components/Controls';
import { Layout, Pagination } from 'antd';
import LoadingIndicator from '@/components/LoadingIndicator';
import ErrorDisplay from '@/components/ErrorDisplay';

const { Header, Content, Footer } = Layout;
const App = () => {
    const [graphData, setGraphData] = useState({ nodes: [], edges: [] });
    const [currentPage, setCurrentPage] = useState(1);
    const [total, setTotal] = useState(0);
    const [pageSize, setPageSize] = useState(10);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [text, setText] = useState('')


    const handleProcessText = async (inputText) => {
        setText(inputText);
        setLoading(true);
        setError('');
        try {
        // Step 1: Send text to backend for processing (text -> sentences -> concepts -> triples)
        const textResponse = await axios.post('/api/text/process', { text:inputText });
        if(textResponse.data.sentences){
           const conceptsResponse = await axios.post('/api/concepts/extract', {sentences:textResponse.data.sentences});
            if(conceptsResponse.data.concepts){
                const relationResponse = await axios.post('/api/relations/extract', {text:inputText, concepts:conceptsResponse.data.concepts});
                if(relationResponse.data.triples){
                const fusionResponse = await axios.post(`/api/graph/fuse?page=${currentPage}&page_size=${pageSize}`, { triples: relationResponse.data.triples, annotated_triples:[] });
                 if(fusionResponse.data.fused_triples){
                            // Step 3: Format data for visualization
                       const nodes = [];
                       const edges = [];
                       const processedNodes = [];
                       for(let item of fusionResponse.data.fused_triples){
                          if(item.subject && processedNodes.indexOf(item.subject) == -1){
                               nodes.push({id:item.subject,label:item.subject});
                               processedNodes.push(item.subject)
                           }
                           if(item.object && processedNodes.indexOf(item.object) == -1){
                                nodes.push({id:item.object,label:item.object});
                               processedNodes.push(item.object)
                            }
                           edges.push({source:item.subject,target:item.object,relation:item.relation})
                        }
                        setTotal(fusionResponse.data.total_count);
                         setGraphData({ nodes: nodes, edges: edges });
                   }
               }
            }
          }
        } catch (err) {
            console.error("Error:", err);
             setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    const handlePageChange = (page, pageSize) => {
      setCurrentPage(page);
      setPageSize(pageSize);
    };

     useEffect(()=>{
        if(text){
           handleProcessText(text);
       }
     },[currentPage, pageSize])



    return (
        <Layout>
            <Header>
                <h1>知识图谱构建应用</h1>
            </Header>
            <Content style={{ padding: '24px 50px' }}>
               <Controls onProcessText={handleProcessText} />
               {loading && <LoadingIndicator />}
               {error && <ErrorDisplay message={error} />}
               {!loading && !error && <GraphVisualization graphData={graphData} />}
               {!loading && !error &&  <Pagination
                    current={currentPage}
                    pageSize={pageSize}
                     total={total}
                     onChange={handlePageChange}
               />}
            </Content>
            <Footer style={{ textAlign: 'center' }}>Knowledge Graph App ©2024 Created by You</Footer>
        </Layout>
    );
};

export default App;