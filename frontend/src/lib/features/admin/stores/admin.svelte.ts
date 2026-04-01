class AdminStore {
  lastRoute = $state<string | null>(null);

  setLastRoute(route: string) {
    if (route.startsWith('/admin/')) {
      this.lastRoute = route;
    }
  }
}

export const adminStore = new AdminStore();
