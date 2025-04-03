'use client';

import { FC, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useMutation } from '@tanstack/react-query';
import { APIService } from '@/services/api';
import Alert from '@/components/common/Alert';
import Button from '@/components/common/Button';
import { Form, FormGroup, Input } from '@/components/common/Form';
import { useStore } from '@/store';

const SettingsPage: FC = () => {
  const router = useRouter();
  const { user, logout } = useStore();
  const [error, setError] = useState<string>('');
  const [success, setSuccess] = useState<string>('');

  const updateProfileMutation = useMutation({
    mutationFn: (data: { username: string; email: string }) =>
      APIService.updateProfile(data),
    onSuccess: () => {
      setSuccess('个人信息更新成功');
      setTimeout(() => setSuccess(''), 3000);
    },
    onError: (error) => {
      setError(error.detail);
    },
  });

  const changePasswordMutation = useMutation({
    mutationFn: (data: { current_password: string; new_password: string }) =>
      APIService.changePassword(data),
    onSuccess: () => {
      setSuccess('密码修改成功');
      setTimeout(() => setSuccess(''), 3000);
    },
    onError: (error) => {
      setError(error.detail);
    },
  });

  const handleUpdateProfile = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const formData = new FormData(e.currentTarget);
    const username = formData.get('username') as string;
    const email = formData.get('email') as string;

    updateProfileMutation.mutate({ username, email });
  };

  const handleChangePassword = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const formData = new FormData(e.currentTarget);
    const current_password = formData.get('current_password') as string;
    const new_password = formData.get('new_password') as string;

    changePasswordMutation.mutate({ current_password, new_password });
  };

  const handleLogout = () => {
    logout();
    router.push('/login');
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold text-gray-900 mb-8">设置</h1>

      {error && (
        <Alert
          type="error"
          message={error}
          onClose={() => setError('')}
        />
      )}

      {success && (
        <Alert
          type="success"
          message={success}
          onClose={() => setSuccess('')}
        />
      )}

      <div className="space-y-8">
        {/* 个人信息设置 */}
        <div className="bg-white shadow rounded-lg p-6">
          <h2 className="text-lg font-medium text-gray-900 mb-4">个人信息</h2>
          <Form onSubmit={handleUpdateProfile}>
            <FormGroup label="用户名" required>
              <Input
                name="username"
                type="text"
                defaultValue={user?.username}
                required
              />
            </FormGroup>
            <FormGroup label="邮箱" required>
              <Input
                name="email"
                type="email"
                defaultValue={user?.email}
                required
              />
            </FormGroup>
            <Button
              type="submit"
              isLoading={updateProfileMutation.isPending}
            >
              更新个人信息
            </Button>
          </Form>
        </div>

        {/* 密码修改 */}
        <div className="bg-white shadow rounded-lg p-6">
          <h2 className="text-lg font-medium text-gray-900 mb-4">修改密码</h2>
          <Form onSubmit={handleChangePassword}>
            <FormGroup label="当前密码" required>
              <Input
                name="current_password"
                type="password"
                required
              />
            </FormGroup>
            <FormGroup label="新密码" required>
              <Input
                name="new_password"
                type="password"
                required
              />
            </FormGroup>
            <Button
              type="submit"
              isLoading={changePasswordMutation.isPending}
            >
              修改密码
            </Button>
          </Form>
        </div>

        {/* 通知设置 */}
        <div className="bg-white shadow rounded-lg p-6">
          <h2 className="text-lg font-medium text-gray-900 mb-4">通知设置</h2>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-sm font-medium text-gray-900">邮件通知</h3>
                <p className="text-sm text-gray-500">
                  接收系统更新和重要通知
                </p>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input type="checkbox" className="sr-only peer" />
                <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-indigo-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-indigo-600"></div>
              </label>
            </div>
          </div>
        </div>

        {/* 语言设置 */}
        <div className="bg-white shadow rounded-lg p-6">
          <h2 className="text-lg font-medium text-gray-900 mb-4">语言设置</h2>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-sm font-medium text-gray-900">界面语言</h3>
                <p className="text-sm text-gray-500">
                  选择您偏好的界面语言
                </p>
              </div>
              <select className="rounded-md border-gray-300 text-sm focus:border-indigo-500 focus:ring-indigo-500">
                <option value="zh">简体中文</option>
                <option value="en">English</option>
              </select>
            </div>
          </div>
        </div>

        {/* 退出登录 */}
        <div className="bg-white shadow rounded-lg p-6">
          <h2 className="text-lg font-medium text-gray-900 mb-4">退出登录</h2>
          <p className="text-sm text-gray-500 mb-4">
            退出登录后，您需要重新登录才能访问系统。
          </p>
          <Button
            onClick={handleLogout}
            variant="danger"
          >
            退出登录
          </Button>
        </div>
      </div>
    </div>
  );
};

export default SettingsPage; 