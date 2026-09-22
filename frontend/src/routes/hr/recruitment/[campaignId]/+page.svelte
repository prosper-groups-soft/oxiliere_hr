<script lang="ts">
  import { recruitmentStore } from '@/hr/recruitment/stores/recruitment.svelte';
  import AppIcon from '@/components/layout/elements/AppIcon.svelte';
  import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
  import type { RecruitmentCampaign } from '@/hr/recruitment/types/types';


  const campaign = $derived(recruitmentStore.activeCampaign);
</script>


<div class="overflow-hidden mt-2 mr-4">
  {#if campaign}
    <div class="grid grid-cols-1 lg:grid-cols-12 gap-4 pb-2">
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
      <CardContent class="px-4 py-3 space-y-4">
        <div class="grid grid-cols-2 gap-y-3 gap-x-6">
          {@render InfoItem("Campagne", campaign.title)}
          {@render InfoItem("Localisation", campaign.location || 'N/A')}
          {@render InfoItem("Responsable", campaign.hiringManagerName || 'Non assigné')}
          {@render InfoItem("Ouverture", campaign.openDate ? new Date(campaign.openDate).toLocaleDateString() : 'En attente')}
          {@render InfoItem("Clôture", campaign.closeDate ? new Date(campaign.closeDate).toLocaleDateString() : 'Non définie')}
          {@render InfoItem("Poste(s)", campaign.jobNames?.join(', ') || 'Non spécifié')}
          {@render InfoItem("Max candidatures", campaign.maxApplications ? String(campaign.maxApplications) : 'Illimité')}
          {@render InfoItem("Postes ouverts", campaign.targetHires ? String(campaign.targetHires) : 'Non défini')}
          {@render InfoItem("Publiée", campaign.isPublished ? 'Oui' : 'Non')}
          {@render InfoItem("Active", campaign.isActive !== undefined ? (campaign.isActive ? 'Oui' : 'Non') : 'N/A')}
        </div>

        {#if campaign.positionSlots && Object.keys(campaign.positionSlots).length > 0}
          <hr class="border-slate-200" />
          <div>
            <p class="text-sm font-medium text-slate-500 mb-1.5">Répartition des postes</p>
            <div class="space-y-1">
              {#each Object.entries(campaign.positionSlots) as [positionId, slots]}
                <div class="flex items-center justify-between text-sm py-0.5">
                  <span class="text-slate-700 text-sm">{campaign.positionNameMap?.[positionId] || positionId}</span>
                  <span class="font-medium text-slate-900 text-sm">{slots} poste{slots > 1 ? 's' : ''} à pourvoir</span>
                </div>
              {/each}
            </div>
          </div>
        {/if}
      </CardContent>
    </Card>

    {#if campaign.positions && campaign.positions.length > 0}
      <Card class="borderr border-slate-200 border-0 shadow-none">
        <CardHeader class="px-4 py-1.5! border-b border-slate-100">
          <CardTitle class="text-sm font-semibold text-slate-900">Prérequis et Compétences</CardTitle>
        </CardHeader>
        <CardContent class="px-4! py-0! space-y-3!">
          {#each campaign.positions as position (position.id)}
            <div class="pb-2 border-b border-slate-100 last:pb-0 last:border-0">
              <div class="flex items-center gap-2 mb-2">
                <span class="font-medium text-slate-900 text-sm">{position.name}</span>
                {#if campaign.positionSlots?.[position.id]}
                  <span class="text-sm text-slate-500">
                    ({campaign.positionSlots[position.id]} poste{campaign.positionSlots[position.id] > 1 ? 's' : ''} à pourvoir)
                  </span>
                {/if}
              </div>
              <div class="mb-1.5">
                <p class="text-[0.82rem] font-medium text-indigo-500 mb-1">Compétences</p>
                <div class="flex flex-wrap items-center gap-1.5 pl-2.5">
                  {#if position.skills && position.skills.length > 0}
                    {#each position.skills as skill}
                      <span class="text-[0.82rem] bg-indigo-50 text-indigo-600 px-2 py-0.5 rounded-full font-medium flex items-center gap-1.5 whitespace-nowrap">
                        <AppIcon name="tag" size={14} />
                        {skill.name}
                      </span>
                    {/each}
                  {:else}
                    <span class="text-sm text-slate-400 flex gap-1">
                      <AppIcon name="circle-x" size={14} />
                      Aucune compétence
                    </span>
                  {/if}
                </div>
              </div>
              <div>
                <p class="text-[0.82rem] font-medium text-emerald-500 mb-1">Prérequis</p>
                <div class="flex flex-wrap items-center gap-1.5 pl-2.5">
                  {#if position.requirements && position.requirements.length > 0}
                    {#each position.requirements as req}
                      <span class="text-[0.82rem] bg-emerald-50 text-emerald-600 px-2 py-0.5 rounded-full font-medium flex items-center gap-1.5 whitespace-nowrap">
                        <AppIcon name="circle-check" size={14} class="text-emerald-500" strokeWidth={1.7} />
                        {req}
                      </span>
                    {/each}
                  {:else}
                    <span class="text-sm text-slate-400 flex gap-1">
                      <AppIcon name="circle-x" size={14} />
                      Aucune exigence
                    </span>
                  {/if}
                </div>
              </div>
            </div>
          {/each}
        </CardContent>
      </Card>
    {:else if campaign.requirements && campaign.requirements.length > 0}
      <Card class="border border-slate-200 shadow-none">
        <CardHeader class="px-4 py-3 border-b border-slate-200">
          <CardTitle class="text-sm font-semibold text-slate-900">Prérequis généraux</CardTitle>
        </CardHeader>
        <CardContent class="px-4 py-3">
          <div class="flex flex-wrap items-center gap-1.5">
            {#each campaign.requirements as req}
              <span class="text-[0.82rem] bg-emerald-50 text-emerald-600 px-2 py-0.5 rounded-full font-medium flex items-center gap-1.5 whitespace-nowrap">
                <AppIcon name="circle-check" size={14} class="text-emerald-500" strokeWidth={1.7} />
                {req}
              </span>
            {/each}
          </div>
        </CardContent>
      </Card>
    {/if}
  </div>
{/snippet}


{#snippet StatsStatusArea(campaign: RecruitmentCampaign)}
  <div class="lg:col-span-5 space-y-3">
    <!-- Metriques -->
    <Card class="border border-slate-200">
      <CardHeader class="px-4 py-3 border-b border-slate-200">
        <CardTitle class="text-sm font-semibold text-slate-900">Performances</CardTitle>
      </CardHeader>
      <CardContent class="px-4 py-3 space-y-3">
        <div class="grid grid-cols-2 gap-2">
          <div class="p-3 bg-slate-50 rounded">
            <p class="text-xs text-slate-500 uppercase font-medium">Candidats</p>
            <p class="text-lg font-bold text-slate-900 tabular-nums">{campaign.metrics.totalCandidates}</p>
          </div>
          <div class="p-3 bg-slate-50 rounded">
            <p class="text-xs text-slate-500 uppercase font-medium">Pipeline</p>
            <p class="text-lg font-bold text-amber-700 tabular-nums">{campaign.metrics.inPipeline}</p>
          </div>
          <div class="p-3 bg-slate-50 rounded">
            <p class="text-xs text-slate-500 uppercase font-medium">Entretiens</p>
            <p class="text-lg font-bold text-purple-700 tabular-nums">{campaign.metrics.interviews}</p>
          </div>
          <div class="p-3 bg-slate-50 rounded">
            <p class="text-xs text-slate-500 uppercase font-medium">Embauches</p>
            <p class="text-lg font-bold text-emerald-700 tabular-nums">{campaign.metrics.offersSent} / {campaign.targetHires}</p>
          </div>
        </div>

        {#if campaign.targetHires > 0}
          <div class="pt-2 border-t border-slate-200">
            <div class="flex justify-between text-sm mb-1">
              <span class="text-slate-500 text-sm">Avancement</span>
              <span class="font-semibold text-slate-900 tabular-nums">{Math.round((campaign.metrics.offersSent / campaign.targetHires) * 100)}%</span>
            </div>
            <div class="h-2 bg-slate-100 rounded overflow-hidden">
              <div class="h-full bg-emerald-500 rounded transition-all" style={`width: ${(campaign.metrics.offersSent / campaign.targetHires) * 100}%`}></div>
            </div>
          </div>
        {/if}

        <div class="text-sm text-slate-500">
          Offres envoyées : <span class="font-semibold text-slate-700 tabular-nums text-sm">{campaign.metrics.offersMade}</span>
        </div>
      </CardContent>
    </Card>

    <!-- Statut compact -->
    <Card class="border border-slate-200">
      <CardContent class="px-4 py-3 space-y-1">
        <div class="flex items-center justify-between">
          <span class="text-sm font-medium text-slate-900">
            {campaign.status === 'OPEN' ? 'Campagne Ouverte' : 
             campaign.status === 'PAUSED' ? 'Mise en pause' : 
             campaign.status === 'CLOSED' ? 'Clôturée' : 'Brouillon'}
          </span>
          <span class="text-xs {campaign.isPublished ? 'text-green-600' : 'text-slate-400'}">
            {campaign.isPublished ? 'Publiée' : 'Non publiée'}
          </span>
        </div>
        <div class="flex gap-3 text-xs text-slate-500">
          {#if campaign.openDate}
            <span class="text-xs">Ouverte : {new Date(campaign.openDate).toLocaleDateString('fr-FR')}</span>
          {/if}
          {#if campaign.closeDate}
            <span class="text-xs">Clôture : {new Date(campaign.closeDate).toLocaleDateString('fr-FR')}</span>
          {/if}
        </div>
        {#if campaign.isActive !== undefined}
          <div class="text-xs {campaign.isActive ? 'text-green-600' : 'text-red-500'}">
            {campaign.isActive ? 'Active' : 'Inactive'}
          </div>
        {/if}
      </CardContent>
    </Card>

    <!-- Description -->
    {#if campaign.description}
      <Card class="border border-slate-200">
        <CardContent class="px-4 py-3">
          <p class="text-sm text-slate-700 leading-relaxed whitespace-pre-line">{campaign.description}</p>
        </CardContent>
      </Card>
    {/if}

    <!-- Postes & Vacancies factorisé -->
    <Card class="border border-slate-200">
      <CardHeader class="px-4 py-3 border-b border-slate-200">
        <CardTitle class="text-sm font-semibold text-slate-900">Postes & Vacancies</CardTitle>
      </CardHeader>
      <CardContent class="px-4 py-3">
        {#if campaign.vacancies && campaign.vacancies.length > 0}
          <div class="space-y-2">
            {#each campaign.vacancies as vacancy (vacancy.id)}
              <div class="flex items-center justify-between p-2 bg-slate-50 rounded text-sm">
                <div>
                  <span class="font-medium text-slate-900 text-sm">{vacancy.positionName || 'Poste non défini'}</span>
                  <span class="text-slate-500 ml-2 text-sm">{vacancy.slots} poste{vacancy.slots > 1 ? 's' : ''} à pourvoir</span>
                </div>
                <div class="flex items-center gap-2 text-xs">
                  {#if vacancy.status}
                    <span class="text-sm px-1.5 py-0.5 rounded {vacancy.status === 'OPEN' ? 'text-green-700 bg-green-50' : vacancy.status === 'FILLED' ? 'text-blue-700 bg-blue-50' : 'text-red-600 bg-red-50'}">
                      {vacancy.status === 'OPEN' ? 'Ouverte' : vacancy.status === 'FILLED' ? 'Pourvue' : 'Annulée'}
                    </span>
                  {/if}
                  {#if vacancy.filledDate}
                    <span class="text-sm text-slate-500">{new Date(vacancy.filledDate).toLocaleDateString('fr-FR')}</span>
                  {/if}
                </div>
              </div>
            {/each}
          </div>
        {:else if campaign.positionSlots && Object.keys(campaign.positionSlots).length > 0}
          <div class="space-y-1 text-sm">
            {#each Object.entries(campaign.positionSlots) as [positionId, slots]}
              <div class="flex justify-between py-1">
                <span class="text-slate-700 text-sm">{campaign.positionNameMap?.[positionId] || positionId}</span>
                <span class="font-medium text-slate-900 text-sm">{slots} poste{slots > 1 ? 's' : ''} à pourvoir</span>
              </div>
            {/each}
          </div>
        {:else if campaign.positions && campaign.positions.length > 0}
          <div class="space-y-1 text-sm">
            {#each campaign.positions as pos}
              <div class="text-slate-700 text-sm">{pos.name}</div>
            {/each}
          </div>
        {:else}
          <p class="text-sm text-slate-400 flex gap-1">
            <AppIcon name="circle-x" size={14} />
            Aucune vacancy associée
          </p>
        {/if}
      </CardContent>
    </Card>
  </div>
{/snippet}


{#snippet InfoItem(label: string, value: string | number | undefined)}
  <div class="flex flex-col gap-0 min-w-0">
    <p class="text-xs text-slate-500">{label}</p>
    <p class="text-sm text-slate-900 truncate font-medium">{value || 'N/A'}</p>
  </div>
{/snippet}


