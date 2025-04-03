import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export function middleware(request: NextRequest) {
  const token = request.cookies.get('token')?.value;
  const isAuthPage = request.nextUrl.pathname.startsWith('/login') || 
                    request.nextUrl.pathname.startsWith('/register');

  // 如果用户未登录且访问需要认证的页面，重定向到登录页
  if (!token && !isAuthPage) {
    const loginUrl = new URL('/login', request.url);
    loginUrl.searchParams.set('from', request.nextUrl.pathname);
    return NextResponse.redirect(loginUrl);
  }

  // 如果用户已登录且访问登录/注册页，重定向到首页
  if (token && isAuthPage) {
    return NextResponse.redirect(new URL('/', request.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: [
    /*
     * 匹配所有需要认证的路径
     * - /documents
     * - /graphs
     * - /chat
     * - /settings
     */
    '/documents/:path*',
    '/graphs/:path*',
    '/chat/:path*',
    '/settings/:path*',
    '/login',
    '/register',
  ],
}; 