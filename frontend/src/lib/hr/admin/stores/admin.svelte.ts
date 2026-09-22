import { hr } from '@/constants/features/navigation';


class AdminStore {
  lastRoute = $state<string | null>(null);

  setLastRoute(route: string) {
    if (route.startsWith(hr('/admin/'))) {
      this.lastRoute = route;
    }
  }
}

export const adminStore = new AdminStore();
