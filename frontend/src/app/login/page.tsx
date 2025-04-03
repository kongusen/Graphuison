'use client';

import { useState, FC } from 'react';
import { useRouter } from 'next/navigation';
import { Form, FormGroup, Input } from '@/components/common/Form';
import Button from '@/components/common/Button';
import { useMutation } from '@tanstack/react-query';
import { APIService } from '@/services/api';
import Alert from '@/components/common/Alert';
import Link from 'next/link';
import { APIError } from '@/types/api';

const LoginPage: FC = () => {
  const router = useRouter();
  const [error, setError] = useState<string>('');

  const loginMutation = useMutation({
    mutationFn: (data: { username: string; password: string }) =>
      APIService.login(data),
    onSuccess: () => {
      router.push('/');
    },
    onError: (error: APIError) => {
      setError(error.detail || '登录失败，请重试');
    },
  });

  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const formData = new FormData(e.currentTarget);
    const username = formData.get('username') as string;
    const password = formData.get('password') as string;

    loginMutation.mutate({ username, password });
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
            登录您的账户
          </h2>
        </div>
        <Form onSubmit={handleSubmit}>
          {error && (
            <Alert
              type="error"
              message={error}
              onClose={() => setError('')}
            />
          )}
          <FormGroup label="用户名" required>
            <Input
              name="username"
              type="text"
              required
              autoComplete="username"
            />
          </FormGroup>
          <FormGroup label="密码" required>
            <Input
              name="password"
              type="password"
              required
              autoComplete="current-password"
            />
          </FormGroup>
          <Button
            type="submit"
            isLoading={loginMutation.isPending}
            className="w-full"
          >
            登录
          </Button>
        </Form>
        <div className="text-center">
          <Link
            href="/register"
            className="font-medium text-indigo-600 hover:text-indigo-500"
          >
            还没有账户？立即注册
          </Link>
        </div>
      </div>
    </div>
  );
};

export default LoginPage; 