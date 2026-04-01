<script lang="ts">
  import { recruitmentStore } from '@/features/recruitment/stores/recruitment.svelte';
  import AppIcon from '@/components/layout/elements/AppIcon.svelte';
  import { 
    Card, 
    CardContent, 
    CardHeader, 
    CardTitle 
  } from "@/components/ui/card";
  import { cn } from "@/utilities/common/css";
  import { Separator } from "@/components/ui/separator";
  import type { RecruitmentCampaign } from '@/features/recruitment/types/types';

  const campaign = $derived(recruitmentStore.activeCampaign);

  const typeLabels: Record<string, string> = {
    'FULL_TIME': 'Temps plein',
    'PART_TIME': 'Temps partiel',
    'CONTRACT': 'Contractuel',
    'INTERNSHIP': 'Stage'
  };
</script>


<div class="animate-in fade-in duration-500 overflow-hidden mt-2 mr-4">
  {#if campaign}
    <div class="grid grid-cols-1 lg:grid-cols-12 gap-3 pb-2">
      {@render MainInfoArea(campaign)}
      {@render StatsStatusArea(campaign)}
    </div>
  {/if}
</div>


{#snippet MainInfoArea(campaign: RecruitmentCampaign)}
  <div class="lg:col-span-7 space-y-5">
    <Card class="shadow-none border-slate-200 py-4 gap-2">
      <CardHeader class="p-0 px-5 m-0 pb-2.5! border-b border-slate-50 flex items-center justify-between">
        <CardTitle class="flex items-center gap-2 text-[0.95rem] font-bold text-slate-900">
          <AppIcon name="info" size={20} strokeWidth={1.2} class="text-slate-500" />
          Informations générales
        </CardTitle>
      </CardHeader>
      <CardContent class="px-5 py-0 pt-3 space-y-5">
        <div class="grid grid-cols-2 gap-y-4 gap-x-8">
          {@render InfoItem("Titre du poste", campaign.title, "briefcase")}
          {@render InfoItem("Localisation", campaign.location || 'N/A', "map-pin")}
          {@render InfoItem("Hiring Manager", campaign.hiringManagerName, "user")}
          {@render InfoItem("Type de contrat", typeLabels[campaign.type] || campaign.type, "file-text")}
        </div>
        
        <Separator class="bg-slate-100" />
        
        <div class="grid grid-cols-2 gap-x-8">
          {@render InfoItem("Poste (Interne)", campaign.jobName, "layers")}
          {@render InfoItem("Date d'ouverture", campaign.openDate ? new Date(campaign.openDate).toLocaleDateString() : 'En attente', "calendar")}
        </div>
      </CardContent>
    </Card>

    <Card class="shadow-none border-slate-200 py-4 gap-2">
      <CardHeader class="p-0 px-5 m-0 pb-2.5! border-b border-slate-50">
        <CardTitle class="flex items-center gap-2 text-[0.95rem] font-bold text-slate-900">
          <AppIcon name="align-left" size={20} strokeWidth={1.2} class="text-slate-500" />
          Description
        </CardTitle>
      </CardHeader>
      <CardContent class="px-5 py-0">
        <p class="text-sm text-slate-600 leading-relaxed line-clamp-4 hover:line-clamp-none transition-all duration-300">
          {campaign.description || "Aucune description fournie."}
        </p>
      </CardContent>
    </Card>
  </div>
{/snippet}


{#snippet StatsStatusArea(campaign: RecruitmentCampaign)}
  <div class="lg:col-span-5 space-y-3">
    <Card class="shadow-none border-slate-200 py-4 gap-2">
      <CardHeader class="p-0 px-5 m-0 pb-2.5! border-b border-slate-50">
        <CardTitle class="flex items-center gap-2 text-[0.95rem] font-bold text-slate-900">
          <AppIcon name="chart-area" size={20} strokeWidth={1.2} class="text-slate-500" />
          Performances
        </CardTitle>
      </CardHeader>
      <CardContent class="px-3 py-0 pt-3 space-y-5">
        <div class="grid grid-cols-2 gap-3">
          {@render MetricItem("Candidats", campaign.metrics.totalCandidates, "users", "text-blue-600", "bg-blue-50/50")}
          {@render MetricItem("Pipeline", campaign.metrics.inPipeline, "layers", "text-amber-600", "bg-amber-50/50")}
          {@render MetricItem("Entretiens", campaign.metrics.interviews, "calendar", "text-purple-600", "bg-purple-50/50")}
          {@render MetricItem("Objectif", `${campaign.metrics.offersSent}/${campaign.targetHires}`, "target", "text-emerald-600", "bg-emerald-50/50")}
        </div>

        <div class="space-y-2 border-t border-slate-50 mt-2 pt-4">
          <div class="flex justify-between items-center">
            <span class="text-xs font-medium text-slate-500 uppercase tracking-wider">Avancement global</span>
            <span class="text-[0.84rem] font-bold text-slate-900">
              {Math.round((campaign.metrics.offersSent / campaign.targetHires) * 100)}%
            </span>
          </div>
          <div class="h-2 w-full bg-slate-100 rounded-full overflow-hidden">
            <div 
              class="h-full bg-emerald-500 transition-all duration-500 rounded-full shadow-fine" 
              style={`width: ${(campaign.metrics.offersSent / campaign.targetHires) * 100}%`}
            ></div>
          </div>
        </div>
      </CardContent>
    </Card>

    <Card class="shadow-none border-slate-200 p-0">
      <CardContent class="p-4">
         <div class="flex items-center justify-between gap-3">
           <div class="flex items-center gap-3">
             <div class={cn(
               "h-2.5 w-2.5 rounded-full",
               campaign.status === 'OPEN' ? "bg-emerald-500 animate-pulse shadow-[0_0_8px_rgba(16,185,129,0.5)]" : 
               campaign.status === 'PAUSED' ? "bg-amber-500" : "bg-slate-300"
             )}></div>
             <div class="space-y-0.5">
               <p class="text-[0.84rem]! font-bold text-slate-900">
                 {campaign.status === 'OPEN' ? 'Campagne Ouverte' : 
                  campaign.status === 'PAUSED' ? 'Mise en pause' : 
                  campaign.status === 'CLOSED' ? 'Clôturée' : 'Brouillon'}
               </p>
               <p class="text-[0.78rem] text-slate-500 font-medium leading-none">Visibilité active sur le portail</p>
             </div>
           </div>
           <div class="h-8 w-8 rounded-lg bg-slate-50 border border-slate-100 flex items-center justify-center">
             <AppIcon name="activity" size={17} class="text-slate-500" />
           </div>
         </div>
      </CardContent>
    </Card>
  </div>
{/snippet}


{#snippet InfoItem(label: string, value: string | number | undefined, icon: string)}
  <div class="flex flex-col gap-1 min-w-0">
    <div class="text-sm font-medium text-slate-500">{label}</div>
    <div class="flex items-center gap-2">
      <AppIcon name={icon} size={18} strokeWidth={1.3} class="text-slate-400 shrink-0" />
      <p class="text-sm text-slate-900 truncate font-medium">{value || 'N/A'}</p>
    </div>
  </div>
{/snippet}


{#snippet MetricItem(label: string, value: string | number, icon: string, color: string, bg: string)}
  <div class={cn("p-3 rounded-xl border border-slate-100 flex items-center justify-between group transition-all", bg)}>
    <div class="space-y-0.5 min-w-0">
      <p class="text-[0.7rem] font-medium text-slate-500 uppercase tracking-widest truncate">{label}</p>
      <p class={cn("text-[0.9rem] font-bold", color)}>{value}</p>
    </div>
    <div class="h-8 w-8 rounded-lg bg-white border border-slate-200/50 flex items-center justify-center shadow-fine group-hover:scale-110 transition-transform shrink-0">
      <AppIcon name={icon} size={17} strokeWidth={1.4} class={color} />
    </div>
  </div>
{/snippet}
