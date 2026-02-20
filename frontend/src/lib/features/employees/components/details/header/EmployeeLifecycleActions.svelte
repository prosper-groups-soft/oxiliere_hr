<script lang="ts">
  import * as DropdownMenu from "@/components/ui/dropdown-menu";
  import { buttonVariants } from "@/components/ui/button";
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import type { Employee } from '../../../types/types';
  import { cn } from "@/utilities/common/css";

  let { employee } = $props<{ employee: Employee }>();

  function handleAction(action: string) {
    console.log(`Action: ${action} for employee ${employee.id}`);
    // Future: implement lifecycle transitions here
  }
</script>


<DropdownMenu.Root>
  <DropdownMenu.Trigger class={cn(buttonVariants({ size: "sm" }), "text-[0.85rem] h-7.5 px-3")}>
    <AppIcon name="more-vertical" size={18} />
    Actions
  </DropdownMenu.Trigger>
  <DropdownMenu.Content align="end">
    <DropdownMenu.Label class="uppercase tracking-wider text-muted-foreground text-[0.78rem]!">
      Cycle de Vie
    </DropdownMenu.Label>
    <DropdownMenu.Separator />
    <DropdownMenu.Group>
      <DropdownMenu.Item onclick={() => handleAction('transition')} class="cursor-pointer">
        <AppIcon name="refresh-cw" size={20} />
        <span>Mettre en transition</span>
      </DropdownMenu.Item>
      <DropdownMenu.Item onclick={() => handleAction('suspend')} class="cursor-pointer">
        <AppIcon name="circle-pause" size={20} />
        <span>Suspendre le contrat</span>
      </DropdownMenu.Item>
      <DropdownMenu.Separator />
      <DropdownMenu.Item 
        onclick={() => handleAction('offboard')} 
        class="cursor-pointer text-orange-600 hover:text-orange-700! hover:bg-orange-100! dark:focus:bg-red-950/20"
      >
        <AppIcon name="user-minus" size={20} class="text-red-600 hover:text-orange-700!" />
        <span>Lancer l'offboarding</span>
      </DropdownMenu.Item>
    </DropdownMenu.Group>
  </DropdownMenu.Content>
</DropdownMenu.Root>

