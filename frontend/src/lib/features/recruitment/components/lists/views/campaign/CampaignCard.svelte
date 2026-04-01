<script lang="ts">
  import type { RecruitmentCampaign } from '../../../../types/types';
  import AppIcon from '@/components/layout/elements/AppIcon.svelte';
  import { Badge } from "@/components/ui/badge";
  import { cn } from "@/utilities/common/css";
  import * as DropdownMenu from "@/components/ui/dropdown-menu";
  import { Button } from "@/components/ui/button";
  import { goto } from '$app/navigation';

  let { campaign, onEdit, onDelete } = $props<{ 
    campaign: RecruitmentCampaign,
    onEdit?: (c: RecruitmentCampaign) => void,
    onDelete?: (c: RecruitmentCampaign) => void
  }>();

  const statusConfig: Record<string, { label: string, color: string, bg: string, border: string, dot: string }> = {
    'OPEN':   { label: 'Ouverte', color: 'text-blue-700', bg: 'bg-blue-50', border: 'border-blue-100', dot: 'bg-blue-500' },
    'PAUSED': { label: 'En pause', color: 'text-amber-700', bg: 'bg-amber-50', border: 'border-amber-100', dot: 'bg-amber-500' },
    'DRAFT':  { label: 'Brouillon', color: 'text-slate-600', bg: 'bg-slate-50', border: 'border-slate-200', dot: 'bg-slate-400' },
    'CLOSED': { label: 'Fermée', color: 'text-emerald-700', bg: 'bg-emerald-50', border: 'border-emerald-100', dot: 'bg-emerald-500' }
  };

  const config = $derived(statusConfig[campaign.status] || statusConfig.DRAFT);

  function handleView(e: MouseEvent) {
    e.preventDefault();
    e.stopPropagation();
    goto(`/recruitment/${campaign.id}`);
  }

  function handleEdit(e: MouseEvent) {
    e.preventDefault();
    e.stopPropagation();
    onEdit?.(campaign);
  }

  function handleDelete(e: MouseEvent) {
    e.preventDefault();
    e.stopPropagation();
    onDelete?.(campaign);
  }
</script>


<a 
  href={`/recruitment/${campaign.id}`}
  class="group relative flex flex-col bg-white border border-slate-200/80 rounded-2xl overflow-hidden hover:shadow-fine hover:shadow-slate-200/50 transition-all duration-300 hover:border-slate-300 shadow-fine"
>
  <!-- Background subtle gradient -->
  <div class="absolute inset-x-0 top-0 h-32 pointer-events-none"></div>

  <div class="p-5 flex flex-col h-full relative z-10">
    {@render Header()}

    {@render Body()}
    
    {@render Footer()}
  </div>

  <!-- Decorative blur on hover -->
  <div class="absolute -bottom-12 -right-12 h-24 w-24 bg-primary/10 rounded-full blur-3xl opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
</a>


{#snippet Header()}
  <div class="flex justify-between items-start mb-5">
    <div class="space-y-1.5 min-w-0 flex-1">
      <h3 class="text-[0.9rem] font-bold text-slate-900 group-hover:text-primary transition-colors truncate pr-2">
        {campaign.title}
      </h3>
      <div class="flex items-center gap-2">
          <div class="h-6.5 w-6.5 rounded-full bg-slate-100 flex items-center justify-center shrink-0">
            <AppIcon name="briefcase" size={17} class="text-indigo-500" />
          </div>
          <span class="text-[0.8rem] font-medium text-slate-500 truncate">{campaign.jobName}</span>
      </div>
    </div>
    
    <div class="flex items-center gap-2 shrink-0">
      <Badge variant="outline" class={cn(
        "px-2 py-0.5 rounded-lg border text-[0.62rem] font-bold uppercase tracking-wider shadow-none transition-all flex items-center gap-1.5",
        config.bg, config.color, config.border
      )}>
        <span class={cn("h-1 w-1 rounded-full", config.dot, campaign.status === 'OPEN' ? "animate-pulse" : "")}></span>
        {config.label}
      </Badge>

      {@render Actions()}
    </div>
  </div>
{/snippet}


{#snippet Body()}
  <div class="space-y-3 mb-6">
    <div class="flex items-center text-slate-600 hover:text-slate-900 transition-colors">
      <div class="h-6.5 w-6.5 rounded-full bg-slate-50 flex items-center justify-center mr-2.5 shrink-0 border border-slate-100">
        <AppIcon name="map-pin" size={17} class="text-slate-400" />
      </div>
      <span class="truncate text-[0.81rem]">{campaign.location}</span>
    </div>
    
    <div class="flex items-center text-slate-600">
      <div class="h-6.5 w-6.5 rounded-full bg-slate-50 flex items-center justify-center mr-2.5 shrink-0 border border-slate-100">
        <AppIcon name="user" size={17} class="text-slate-400" />
      </div>
      <span class="truncate font-medium text-slate-700 text-[0.81rem]">
        {campaign.hiringManagerName}
      </span>
    </div>
  </div>
{/snippet}


{#snippet Footer()}
  <div class="mt-auto">
    <!-- Progress Bar -->
    <div class="space-y-1.5 mb-4">
      <div class="flex justify-between font-medium text-slate-900">
        <span class="text-[0.78rem]">Progression</span>
        <span class="text-emerald-700 text-[0.78rem]">{campaign.metrics.offersSent} / {campaign.targetHires} embauches</span>
      </div>
      <div class="h-1.5 w-full bg-slate-100 rounded-full overflow-hidden">
        <div 
          class="h-full bg-emerald-500 rounded-full transition-all duration-500" 
          style={`width: ${Math.min(100, (campaign.metrics.offersSent / campaign.targetHires) * 100)}%`}
        ></div>
      </div>
    </div>

    <div class="grid grid-cols-2 gap-3 pt-4 border-t border-slate-100">
      <div class="p-2.5 rounded-xl bg-slate-50 border border-slate-100 flex flex-col gap-1 hover:bg-white hover:shadow-sm transition-all duration-300">
        <span class="text-[0.62rem] font-bold text-slate-500 uppercase tracking-widest">Candidats</span>
        <div class="flex items-center gap-2">
          <span class="text-[0.95rem] font-medium text-slate-900">{campaign.metrics.totalCandidates}</span>
          <span class="text-[0.7rem] font-bold text-emerald-600 bg-emerald-50 px-1 rounded">+{Math.floor(Math.random() * 5)}</span>
        </div>
      </div>
      <div class="p-2.5 rounded-xl bg-slate-50 border border-slate-100 flex flex-col gap-1 hover:bg-white hover:shadow-sm transition-all duration-300">
        <span class="text-[0.62rem] font-bold text-slate-500 uppercase tracking-widest">En cours</span>
        <div class="flex items-center gap-2">
          <span class="text-[0.95rem] font-medium text-amber-600">{campaign.metrics.inPipeline}</span>
          <AppIcon name="kanban" size={17} class="text-amber-400" />
        </div>
      </div>
    </div>
  </div>
{/snippet}


{#snippet Actions()} 
  <DropdownMenu.Root>
    <DropdownMenu.Trigger>
      {#snippet child({ props })}
        <Button 
          {...props}
          variant="ghost" 
          size="icon" 
          class="h-7 w-7 rounded-lg text-slate-400 hover:text-slate-900 hover:bg-slate-100"
          onclick={(e) => e.stopPropagation()}
        >
          <AppIcon name="more-horizontal" size={17} />
        </Button>
      {/snippet}
    </DropdownMenu.Trigger>
    <DropdownMenu.Content align="end" class="w-48 p-1.5 rounded-lg shadow-fine border-slate-100 bg-white">
      <DropdownMenu.Item onclick={handleView} class="rounded-lg gap-2.5 py-1.5 cursor-pointer text-[0.845rem]">
        <AppIcon name="eye" size={16} class="text-slate-500" />
        Voir les détails
      </DropdownMenu.Item>
      <DropdownMenu.Item onclick={handleEdit} class="rounded-lg gap-2.5 py-1.5 cursor-pointer text-[0.845rem]">
        <AppIcon name="edit" size={16} class="text-slate-500" />
        Modifier
      </DropdownMenu.Item>
      <DropdownMenu.Separator class="my-1 bg-slate-100" />
      <DropdownMenu.Item 
        onclick={handleDelete}
        class="rounded-lg gap-2.5 py-1.5 cursor-pointer text-red-600 hover:text-red-600! hover:bg-red-50! text-[0.845rem]"
      >
        <AppIcon name="trash" size={16} class="text-red-600" />
        Supprimer
      </DropdownMenu.Item>
    </DropdownMenu.Content>
  </DropdownMenu.Root>
{/snippet}

