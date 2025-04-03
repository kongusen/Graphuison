import { FC } from 'react';
import Link from 'next/link';
import {
  DocumentIcon,
  ChartBarIcon,
  ChatBubbleLeftRightIcon,
} from '@heroicons/react/24/outline';

const features = [
  {
    name: '文档管理',
    description: '上传、管理和组织您的文档，支持多种格式。',
    icon: DocumentIcon,
    href: '/documents',
  },
  {
    name: '知识图谱',
    description: '自动构建和可视化知识图谱，发现文档间的关联。',
    icon: ChartBarIcon,
    href: '/graph',
  },
  {
    name: '智能问答',
    description: '基于知识图谱的智能问答系统，快速获取信息。',
    icon: ChatBubbleLeftRightIcon,
    href: '/chat',
  },
];

const HomePage: FC = () => {
  return (
    <div className="bg-white">
      <div className="relative isolate px-6 pt-14 lg:px-8">
        <div className="mx-auto max-w-2xl py-32 sm:py-48 lg:py-56">
          <div className="text-center">
            <h1 className="text-4xl font-bold tracking-tight text-gray-900 sm:text-6xl">
              Graphuison
            </h1>
            <p className="mt-6 text-lg leading-8 text-gray-600">
              智能知识图谱平台，帮助您更好地管理和利用文档知识。
            </p>
          </div>
          <div className="mt-16">
            <div className="grid grid-cols-1 gap-8 sm:grid-cols-2 lg:grid-cols-3">
              {features.map((feature) => (
                <Link
                  key={feature.name}
                  href={feature.href}
                  className="relative rounded-2xl border border-gray-200 p-8 hover:border-indigo-500 hover:shadow-lg transition-all"
                >
                  <div className="flex items-center gap-x-4">
                    <feature.icon
                      className="h-8 w-8 text-indigo-600"
                      aria-hidden="true"
                    />
                    <h3 className="text-lg font-semibold leading-8 text-gray-900">
                      {feature.name}
                    </h3>
                  </div>
                  <p className="mt-4 text-base leading-7 text-gray-600">
                    {feature.description}
                  </p>
                </Link>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default HomePage;
