<script lang="ts">
  import * as Sheet from "@/components/ui/sheet";
  import { Button } from "@/components/ui/button";
  import type { Role } from "../../types/access.types";
  import RolePermissionMatrix from "../RolePermissionMatrix.svelte";
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";

  interface Props {
    open: boolean;
    role: Role | null;
  }

  let { open = $bindable(false), role }: Props = $props();
</script>


<Sheet.Root bind:open>
  <Sheet.Content side="right" class="sm:max-w-xl flex flex-col h-full overflow-hidden p-0">
    <Sheet.Header class="px-6 py-4 border-b bg-slate-50/50">
      <Sheet.Title class="text-[1rem] font-bold">
        Permissions : {role?.name || ''}
      </Sheet.Title>
    </Sheet.Header>

    <div class="flex-1 overflow-y-auto px-6 py-6 custom-scrollbar">
      {#if role}
        <div class="rounded-xl border border-slate-200 bg-white shadow-fine overflow-hidden">
          <RolePermissionMatrix {role} />
        </div>
      {/if}
    </div>

    <Sheet.Footer class="px-6 py-5 border-t flex flex-row gap-3">
      <div class="flex-1 flex items-start gap-3 text-[0.78rem] text-amber-700 bg-amber-50/50 border border-amber-100 p-3 rounded-lg shadow-fine">
        <div class="mt-0.5 text-amber-500">
          <AppIcon name="info" size={16} />
        </div>
        <p class="leading-relaxed">
          Une synchronisation des groupes est nécessaire pour propager ces modifications aux membres.
        </p>
      </div>
      <Sheet.Close class="flex-1">
        <Button variant="outline" class="w-full h-10">Fermer</Button>
      </Sheet.Close>
    </Sheet.Footer>
  </Sheet.Content>
</Sheet.Root>


<style>
  .custom-scrollbar::-webkit-scrollbar { width: 4px; }
  .custom-scrollbar::-webkit-scrollbar-thumb { background: #e2e8f0; border-radius: 10px; }
</style>

