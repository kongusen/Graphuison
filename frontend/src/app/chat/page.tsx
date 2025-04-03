'use client';

import { FC, useState, useRef, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { APIService } from '@/services/api';
import { ChatMessage } from '@/types';
import Alert from '@/components/common/Alert';
import Button from '@/components/common/Button';
import { PaperAirplaneIcon, ArrowDownTrayIcon } from '@heroicons/react/24/outline';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

const ChatPage: FC = () => {
  const [error, setError] = useState<string>('');
  const [message, setMessage] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const queryClient = useQueryClient();

  const { data: messages, isLoading } = useQuery({
    queryKey: ['chat-messages'],
    queryFn: APIService.getChatHistory,
  });

  const sendMessageMutation = useMutation({
    mutationFn: (content: string) => APIService.sendMessage(content),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['chat-messages'] });
      setMessage('');
    },
    onError: (error) => {
      setError(error.detail);
    },
  });

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!message.trim()) return;

    sendMessageMutation.mutate(message);
  };

  const handleExport = () => {
    if (!messages) return;
    const dataStr = JSON.stringify(messages, null, 2);
    const dataUri = 'data:application/json;charset=utf-8,' + encodeURIComponent(dataStr);
    const exportFileDefaultName = 'chat-history.json';

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
        <h1 className="text-2xl font-bold text-gray-900">智能问答</h1>
        <div className="flex items-center gap-4">
          <Button
            onClick={handleExport}
            variant="secondary"
            size="sm"
          >
            <ArrowDownTrayIcon className="h-5 w-5 mr-2" />
            导出对话
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

      <div className="bg-white shadow rounded-lg h-[600px] flex flex-col">
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages?.map((msg: ChatMessage) => (
            <div
              key={msg.id}
              className={`flex ${
                msg.role === 'user' ? 'justify-end' : 'justify-start'
              }`}
            >
              <div
                className={`max-w-[70%] rounded-lg p-3 ${
                  msg.role === 'user'
                    ? 'bg-indigo-600 text-white'
                    : 'bg-gray-100 text-gray-900'
                }`}
              >
                <div className="prose prose-sm max-w-none dark:prose-invert">
                  <ReactMarkdown
                    remarkPlugins={[remarkGfm]}
                    components={{
                      code({ node, inline, className, children, ...props }) {
                        const match = /language-(\w+)/.exec(className || '');
                        return !inline && match ? (
                          <pre className="bg-gray-800 text-white p-2 rounded-md overflow-x-auto">
                            <code className={className} {...props}>
                              {children}
                            </code>
                          </pre>
                        ) : (
                          <code className="bg-gray-200 dark:bg-gray-800 px-1 rounded" {...props}>
                            {children}
                          </code>
                        );
                      },
                      p({ children }) {
                        return <p className="mb-2">{children}</p>;
                      },
                      ul({ children }) {
                        return <ul className="list-disc pl-4 mb-2">{children}</ul>;
                      },
                      ol({ children }) {
                        return <ol className="list-decimal pl-4 mb-2">{children}</ol>;
                      },
                      li({ children }) {
                        return <li className="mb-1">{children}</li>;
                      },
                      h1({ children }) {
                        return <h1 className="text-xl font-bold mb-2">{children}</h1>;
                      },
                      h2({ children }) {
                        return <h2 className="text-lg font-bold mb-2">{children}</h2>;
                      },
                      h3({ children }) {
                        return <h3 className="text-base font-bold mb-2">{children}</h3>;
                      },
                      blockquote({ children }) {
                        return (
                          <blockquote className="border-l-4 border-gray-300 pl-4 italic mb-2">
                            {children}
                          </blockquote>
                        );
                      },
                      table({ children }) {
                        return (
                          <div className="overflow-x-auto mb-2">
                            <table className="min-w-full divide-y divide-gray-200">
                              {children}
                            </table>
                          </div>
                        );
                      },
                      th({ children }) {
                        return (
                          <th className="px-4 py-2 bg-gray-100 font-semibold text-left">
                            {children}
                          </th>
                        );
                      },
                      td({ children }) {
                        return <td className="px-4 py-2 border-b">{children}</td>;
                      },
                    }}
                  >
                    {msg.content}
                  </ReactMarkdown>
                </div>
                <p className="text-xs mt-1 opacity-70">
                  {new Date(msg.created_at).toLocaleString()}
                </p>
              </div>
            </div>
          ))}
          <div ref={messagesEndRef} />
        </div>

        <form onSubmit={handleSubmit} className="p-4 border-t">
          <div className="flex gap-2">
            <input
              type="text"
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              placeholder="输入您的问题..."
              className="flex-1 rounded-md border border-gray-300 px-4 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              disabled={sendMessageMutation.isPending}
            />
            <Button
              type="submit"
              isLoading={sendMessageMutation.isPending}
              disabled={!message.trim() || sendMessageMutation.isPending}
            >
              <PaperAirplaneIcon className="h-5 w-5" />
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default ChatPage; 