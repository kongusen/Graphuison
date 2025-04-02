import React, { useState, useEffect } from 'react';
import Navbar from '@/components/common/Navbar';
import { getStats, getHistory } from '@/utils/api';

const Home = () => {
  const [stats, setStats] = useState({
    entities_count: 0,
    triples_count: 0,
  });

  const [history, setHistory] = useState([]);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const data = await getStats();
        setStats(data);
      } catch (error) {
        console.error('Error fetching stats:', error);
      }
    };

    const fetchHistory = async () => {
      try {
        const data = await getHistory();
        setHistory(data.history);
      } catch (error) {
        console.error('Error fetching history:', error);
      }
    };

    fetchStats();
    fetchHistory();
  }, []);

  return (
    <div>
      <Navbar />
      <div className="container mx-auto p-4">
        <h1 className="text-2xl font-bold mb-4">Home</h1>
        <div className="grid grid-cols-3 gap-4">
          <div className="bg-gray-100 p-4 rounded">
            <h2 className="text-lg font-semibold">Entities</h2>
            <p className="text-gray-600">{stats.entities_count}</p>
          </div>
          <div className="bg-gray-100 p-4 rounded">
            <h2 className="text-lg font-semibold">Triples</h2>
            <p className="text-gray-600">{stats.triples_count}</p>
          </div>
          <div className="bg-gray-100 p-4 rounded">
            <h2 className="text-lg font-semibold">Chunks</h2>
            <p className="text-gray-600">0</p>
          </div>
        </div>
        <div className="bg-white p-6 rounded-lg shadow-md mt-5">
          <h2 className="text-2xl font-semibold mb-4">Recent Queries</h2>
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Query</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Response</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Confidence</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {history.map((item, index) => (
                <tr key={index}>
                  <td className="px-6 py-4 whitespace-nowrap">{item.query}</td>
                  <td className="px-6 py-4 whitespace-nowrap">{item.response}</td>
                  <td className="px-6 py-4 whitespace-nowrap">{item.confidence}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default Home;