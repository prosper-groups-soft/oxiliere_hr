import { redirect, type Handle } from '@sveltejs/kit';
import { create_url_with_next } from '@/utilities/http/urls';


const PUBLIC_URLS = [
  '/auth/login',
  '/auth/2fa',
  '/auth/register',
  '/auth/forgot-password',
  '/auth/reset-password',
  '/auth/r' // Route of redirection for non authenticated users
];


const STATIC_PATHS = [
  '/_app',
  '/favicon.ico',
  '/robots.txt',
  '/sitemap.xml'
];


function isPublicRoute(pathname: string): boolean {
  // Allow all routes starting with /auth/
  if (pathname.startsWith('/auth/')) {
    return true;
  }
    
  return PUBLIC_URLS.some(url => pathname.startsWith(url)) ||
         STATIC_PATHS.some(path => pathname.startsWith(path));
}


function isAuthenticated(event: any): boolean {
  // Verify the artificial cookie defined on the client side
  //const isAuth = event.cookies.get('is_authenticated');
  //return isAuth === 'true';
  return true;
}


export const handle: Handle = async ({ event, resolve }) => {
  const { pathname } = event.url;
    
  // Skip authentication for public routes and static assets
  if (isPublicRoute(pathname)) {
    return await resolve(event);
  }
    
  // Check authentication
  if (!isAuthenticated(event)) {
    throw redirect(302, create_url_with_next('/auth/r', undefined, event.url));
  }
    
  const response = await resolve(event);
  return response;
};

