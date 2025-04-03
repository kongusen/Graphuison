'use client';

import { FC, useState } from 'react';
import { useRouter } from 'next/navigation';
import { Form, FormGroup, Input } from '@/components/common/Form';
import Button from '@/components/common/Button';
import { useMutation } from '@tanstack/react-query';
import { APIService } from '@/services/api';
import Alert from '@/components/common/Alert';
import Link from 'next/link';

const RegisterPage: FC = () => {
  const router = useRouter();
  const [error, setError] = useState<string>('');

  const registerMutation = useMutation({
    mutationFn: (data: { username: string; email: string; password: string }) =>
      APIService.register(data),
    onSuccess: () => {
      router.push('/login');
    },
    onError: (error) => {
      setError(error.detail);
    },
  });

  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const formData = new FormData(e.currentTarget);
    const username = formData.get('username') as string;
    const email = formData.get('email') as string;
    const password = formData.get('password') as string;

    registerMutation.mutate({ username, email, password });
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
            注册新账户
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
          <FormGroup label="邮箱" required>
            <Input
              name="email"
              type="email"
              required
              autoComplete="email"
            />
          </FormGroup>
          <FormGroup label="密码" required>
            <Input
              name="password"
              type="password"
              required
              autoComplete="new-password"
            />
          </FormGroup>
          <Button
            type="submit"
            isLoading={registerMutation.isPending}
            className="w-full"
          >
            注册
          </Button>
        </Form>
        <div className="text-center">
          <Link
            href="/login"
            className="font-medium text-indigo-600 hover:text-indigo-500"
          >
            已有账户？立即登录
          </Link>
        </div>
      </div>
    </div>
  );
};

export default RegisterPage; 