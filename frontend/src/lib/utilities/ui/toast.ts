import { toast as sonnerToast } from 'svelte-sonner';
import RichToast from '@/components/ui/sonner/RichToast.svelte';

interface ToastOptions {
  duration?: number;
  [key: string]: any;
}

function show(message: string, type: 'success' | 'error' | 'info' = 'success', options: ToastOptions = {}) {
  const duration = options.duration || 5000;
  
  const id = options.id || Math.random().toString(36).substring(2, 9);

  return sonnerToast.custom(RichToast, {
    id,
    componentProps: {
      id,
      message,
      type,
      duration
    },
    duration: duration,
    ...options
  });
}

export const toast = {
  success: (message: string, options?: ToastOptions) => show(message, 'success', options),
  error:   (message: string, options?: ToastOptions) => show(message, 'error', options),
  info:    (message: string, options?: ToastOptions) => show(message, 'info', options),
  dismiss: (id?: string | number) => sonnerToast.dismiss(id),
  loading: (message: string, options?: ToastOptions) => sonnerToast.loading(message, options),
};
