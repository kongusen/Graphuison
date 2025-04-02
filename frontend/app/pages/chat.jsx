// frontend/pages/chat.jsx
import React, { useState } from 'react';
import Navbar from '@/components/common/Navbar';
import { sendMessage } from '@/utils/api';
import GraphDisplay from '@/components/graph/GraphDisplay';

const Chat = () => {
  const [message, setMessage] = useState('');
  const [chatHistory, setChatHistory] = useState([]);
  const [graphData, setGraphData] = useState([]);
   const handleSendMessage = async () => {
        if (message.trim() === '') return;
        try {
             const result = await sendMessage(message);
             setChatHistory([...chatHistory,{ query: message, response:result.response }]);
             setGraphData(result.triples);
             setMessage('');
        } catch (error) {
         console.error('Error sending message:', error);
        }
    };

    return (
        <div>
            <Navbar />
            <div className="container mx-auto p-4">
              <h1 className="text-2xl font-bold mb-4">Chat</h1>
              <div className="mb-4">
                <div className="flex">
                  <input
                    type="text"
                    value={message}
                     onChange={(e) => setMessage(e.target.value)}
                       placeholder="Type your message..."
                     className="border p-2 w-3/4"
                  />
                  <button
                    onClick={handleSendMessage}
                     className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded w-1/4"
                 >Send</button>
               </div>
              </div>
               <div className="mb-4">
                  {chatHistory.map((item, index) => (
                   <div key={index} className="mb-2">
                     <p className="font-bold">User:</p>
                      <p>{item.query}</p>
                       <p className="font-bold">Assistant:</p>
                     <p>{item.response}</p>
                   </div>
                  ))}
                </div>
                 {graphData.length > 0 && (
                    <div className="mb-4">
                     <h2 className="text-xl font-semibold mb-2">Graph</h2>
                    <GraphDisplay data={graphData} />
                   </div>
                 )}
            </div>
        </div>
      );
    };

export default Chat;