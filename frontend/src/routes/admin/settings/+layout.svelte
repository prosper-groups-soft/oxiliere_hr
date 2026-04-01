<script lang="ts">
  import { page } from "$app/state";
  import { browser } from "$app/environment";
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import { cn } from "@/utilities/common/css";
  import { adminStore } from "$lib/features/admin/stores/admin.svelte";

  $effect(() => {
    if (browser) {
      adminStore.setLastRoute(page.url.pathname);
    }
  });

  const tabs = [
    { id: "users", label: "Utilisateurs", icon: "users", path: "/admin/settings/users" },
    { id: "access", label: "Sécurité & Accès", icon: "shield-check", path: "/admin/settings/access" },
    { id: "leaves", label: "Congés", icon: "calendar-days", path: "/admin/settings/leaves" },
    { id: "tax", label: "Fiscalité", icon: "calculator", path: "/admin/settings/tax" },
    { id: "currency", label: "Devises", icon: "banknote", path: "/admin/settings/currency" }
  ];

  const currentTab = $derived(
    tabs.find(t => page.url.pathname.startsWith(t.path)) || tabs[0]
  );

  let { children } = $props();
</script>


<div class="flex h-full min-h-0">
  <!-- Sidebar Navigation -->
  <aside class="w-53 bg-white border-r border-slate-200 flex flex-col shrink-0">
    <div class="p-4 py-2 border-b border-slate-100">
      <h2 class="text-[0.91rem] font-semibold text-slate-900 flex items-center gap-2">
        <AppIcon name="settings" size={20} class="text-slate-500" />
        Paramètres
      </h2>
    </div>

    <nav class="flex-1 overflow-y-auto p-2 space-y-1">
      {#each tabs as tab}
        <a
          href={tab.path}
          class={cn(
            "flex items-center gap-3 px-3 py-1.5 rounded-lg text-[0.86rem] transition-colors",
            currentTab.id === tab.id
              ? "bg-indigo-50 text-indigo-700 font-medium"
              : "text-slate-800 hover:bg-slate-50 hover:text-slate-900"
          )}
        >
          <AppIcon name={tab.icon} size={19} class={currentTab.id === tab.id ? "text-blue-600" : "text-slate-500"} />
          {tab.label}
        </a>
      {/each}
    </nav>

    <!-- Help Section -->
    <div class="p-1 py-2 border-t border-slate-100 bg-slate-50/50">
      <div class="flex items-start gap-1.5 text-[0.76rem] text-slate-500">
        <AppIcon name="info" size={15} class="shrink-0 mt-0.5" />
        <p class="text-[0.8rem]">
          Les modifications sont sauvegardées manuellement.
        </p>
      </div>
    </div>
  </aside>

  <!-- Main Content -->
  <main class="flex-1 overflow-hidden flex flex-col min-h-0 bg-white">
    <div class="flex-1 overflow-y-auto">
      {@render children()}
    </div>
  </main>
</div>

