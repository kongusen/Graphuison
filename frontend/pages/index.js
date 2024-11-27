import Head from 'next/head';
import ConceptExtractionForm from '../components/ConceptExtractionForm';

export default function Home() {
  return (
    <div>
      <Head>
        <title>概念提取应用</title>
        <meta name="description" content="使用FastAPI后端的概念提取应用" />
        <link rel="icon" href="/favicon.ico" />
      </Head>
      <main>
        <ConceptExtractionForm />
      </main>
    </div>
  );
}
