<script lang="ts">
  import { slide } from "svelte/transition";
  import { Checkbox } from "@/components/ui/checkbox";
  import { Label } from "@/components/ui/label";
  import { Separator } from "@/components/ui/separator";
  import { Button } from "@/components/ui/button";
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import { cn } from "@/utils";

  let { filters = $bindable() } = $props();

  // State for collapsible groups
  let expandedGroups = $state(new Set(["department", "status", "location"]));

  const departments = [
    "Ingénierie", 
    "Produit", 
    "Vente", 
    "Marketing", 
    "Ressources Humaines", 
    "Finance"
  ];
  
  const status = [
    "Actif", 
    "En intégration", 
    "Suspendu", 
    "Terminé"
  ];
  
  const locations = [
    "Siège Paris", 
    "Télétravail", 
    "Agence Lyon", 
    "Hub Bordeaux"
  ];

  function toggleGroup(category: string) {
    if (expandedGroups.has(category)) {
      expandedGroups.delete(category);
    } else {
      expandedGroups.add(category);
    }
    // Trigger Svelte state update for Set
    expandedGroups = new Set(expandedGroups);
  }

  function handleFilterChange(category: string, value: string, checked: boolean) {
    if (checked) {
      filters[category] = [...(filters[category] || []), value];
    } else {
      filters[category] = (filters[category] || []).filter((v: string) => v !== value);
    }
  }

  function clearFilters() {
    filters = {
      department: [],
      status: [],
      location: []
    }
  }
</script>


<div class="flex flex-col gap-6 py-2 relative">
  <div class="sticky top-0 bg-white/98 backdrop-blur-sm z-20 flex items-center justify-between px-2 py-4 -mt-2 border-b border-slate-200 transition-all">
    <div class="flex items-center gap-2">
      <div class="bg-primary/10 p-1.5 rounded-lg">
        <AppIcon name="filter" size={14} class="text-primary" />
      </div>
      <h3 class="font-bold text-xs text-slate-800 tracking-tight uppercase">Filtres</h3>
    </div>
    <Button 
      variant="outline" 
      size="sm" 
      class="h-auto py-0.5 px-3.5 text-[11px] font-bold bg-white border-slate-200 hover:text-primary hover:bg-primary/5 rounded-lg transition-all shadow-none" 
      onclick={clearFilters}
    >
      Effacer
    </Button>
  </div>

  <div class="space-y-2">
    {@render FilterGroup("Département", "department", departments, "team")}
    <Separator class="bg-slate-100 mx-2" />
    {@render FilterGroup("Statut", "status", status, "monitoring")}
    <Separator class="bg-slate-100 mx-2" />
    {@render FilterGroup("Lieu", "location", locations, "location")}
  </div>
</div>


{#snippet FilterGroup(title: string, category: string, options: string[], icon: string)}
  {@const isExpanded = expandedGroups.has(category)}
  <div class="flex flex-col px-2">
    <button 
      class="flex w-full items-center justify-between text-slate-800 hover:text-primary transition-all group/header py-1 cursor-pointer"
      onclick={() => toggleGroup(category)}
    >
      <div class="flex items-center gap-2">
        <AppIcon name={icon} size={13} class="text-slate-400 group-hover/header:text-primary transition-all" />
        <h4 class="text-[10.5px] font-extrabold uppercase tracking-[0.15em]">{title}</h4>
      </div>
      <div class={cn("transition-transform duration-300", isExpanded ? "rotate-0" : "-rotate-90")}>
        <AppIcon name="chevron" size={13} class="text-slate-500 group-hover/header:text-primary transition-all" />
      </div>
    </button>
    
    {#if isExpanded}
      <div transition:slide={{ duration: 300 }}>
        <div class="flex flex-col gap-1.5 pt-3 pb-1 px-2">
          {#each options as option}
            {@const id = `${category}-${option.replace(/\s+/g, '-').toLowerCase()}`}
            {@const isChecked = filters[category]?.includes(option)}
            <div class={cn(
              "flex items-center space-x-3 p-1.5 -ml-1 rounded-xl transition-all duration-300 cursor-pointer group",
              isChecked ? "bg-primary/[0.04]" : "hover:bg-slate-50/60"
            )}>
              <div class="flex size-4.5 items-center justify-center rounded-md border border-slate-300 bg-white shadow-none transition-colors group-hover:border-primary/40">
                <Checkbox 
                  {id} 
                  checked={isChecked}
                  onCheckedChange={(v) => handleFilterChange(category, option, v as boolean)}
                  class="size-4.5 border-none bg-transparent shadow-none data-[state=checked]:bg-transparent data-[state=checked]:text-primary"
                />
              </div>
              <Label 
                for={id} 
                class={cn(
                  "text-[12px] font-normal cursor-pointer leading-none transition-all",
                  isChecked ? "text-primary font-bold" : "text-slate-800 group-hover:text-slate-800"
                )}
              >
                {option}
              </Label>
            </div>
          {/each}
        </div>
      </div>
    {/if}
  </div>
{/snippet}

