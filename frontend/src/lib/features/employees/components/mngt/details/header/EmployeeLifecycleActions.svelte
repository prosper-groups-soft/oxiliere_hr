<script lang="ts">
  import * as DropdownMenu from "@/components/ui/dropdown-menu";
  import { buttonVariants } from "@/components/ui/button";
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import type { Employee } from '@/features/employees/types/types';
  import { cn } from "@/utilities/common/css";

  let { employee } = $props<{ employee: Employee }>();

  function handleAction(action: string) {
    console.log(`Action: ${action} for employee ${employee.id}`);
    // Future: implement lifecycle transitions here
  }
</script>


<DropdownMenu.Root>
  <DropdownMenu.Trigger class={cn(buttonVariants({ size: "sm" }), "text-[0.85rem] h-7.5 px-3 rounded-lg!")}>
    <AppIcon name="more-vertical" size={16} />
    Actions
  </DropdownMenu.Trigger>
  <DropdownMenu.Content align="end" class="p-1 rounded-lg shadow-fine bg-white border-slate-100">
    <DropdownMenu.Label class="uppercase tracking-wider text-muted-foreground text-[0.75rem]!">
      Cycle de vie
    </DropdownMenu.Label>
    <DropdownMenu.Separator class="my-1 bg-slate-50" />
    <DropdownMenu.Group>
      <DropdownMenu.Item onclick={() => handleAction('transition')} class="cursor-pointer text-[0.85rem]!">
        <AppIcon name="refresh-cw" size={20} />
        Mettre en transition
      </DropdownMenu.Item>
      <DropdownMenu.Item onclick={() => handleAction('suspend')} class="cursor-pointer text-[0.85rem]!">
        <AppIcon name="circle-pause" size={20} />
        Suspendre le contrat
      </DropdownMenu.Item>
      <DropdownMenu.Separator />
      <DropdownMenu.Item 
        onclick={() => handleAction('offboard')} 
        class="cursor-pointer text-red-600 hover:text-red-700! hover:bg-red-100! dark:focus:bg-red-950/20 text-[0.85rem]!"
      >
        <AppIcon name="user-minus" size={20} class="text-red-600 hover:text-red-700!" />
        Lancer l'offboarding
      </DropdownMenu.Item>
    </DropdownMenu.Group>
  </DropdownMenu.Content>
</DropdownMenu.Root>

