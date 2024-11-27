import { useState } from 'react';
import axios from 'axios';

export default function ConceptExtractionForm() {
  const [text, setText] = useState('');
  const [result, setResult] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.post('http://localhost:8000/api/v1/concept/extract/', {
        texts: [text],
        stop_words: ['的', '是'],
        config: { language: 'chinese' }
      });
      setResult(response.data);
    } catch (error) {
      console.error('Error during API call:', error);
    }
  };

  return (
    <div>
      <h1>概念提取工具</h1>
      <form onSubmit={handleSubmit}>
        <textarea
          value={text}
          onChange={(e) => setText(e.target.value)}
          rows="10"
          cols="50"
          placeholder="在此输入文本..."
          required
        />
        <br />
        <button type="submit">提取概念</button>
      </form>
      {result && (
        <pre>{JSON.stringify(result, null, 2)}</pre>
      )}
    </div>
  );
}
