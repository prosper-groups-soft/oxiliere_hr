<script lang="ts">
  import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
  import { formatDate } from '@/hr/utilities/common/date';
  import type { TimelineEvent } from '@/hr/modules/employees/types/types';
  import AppIcon from '@/hr/components/layout/elements/AppIcon.svelte';
  import { Badge } from '@/components/ui/badge';
  import { TRANSITION_TYPE_CONFIG } from '@/hr/modules/jobs/constants/transition.constants';
  import { getOrgUnitIcon } from '@/hr/modules/jobs/constants/orgUnit.constants';


  let { events = [] } = $props<{ events: TimelineEvent[] }>();

  /**
   * Get styling for an event based on its type and metadata
   */
  function getEventStyle(event: TimelineEvent) {
    if (event.type === 'transition' && event.metadata?.transition_type) {
      const config = TRANSITION_TYPE_CONFIG[event.metadata.transition_type as keyof typeof TRANSITION_TYPE_CONFIG];
      if (config) {
        return {
          icon: config.icon,
          iconClass: config.color,
          bgClass: config.bg,
          borderClass: config.border
        };
      }
    }
    
    // Default/Status style (Sober)
    return {
      icon: 'user-check',
      iconClass: 'text-slate-500',
      bgClass: 'bg-slate-50',
      borderClass: 'border-slate-200'
    };
  }

  function getHumanNarrative(event: TimelineEvent): string | null {
    const m = event.metadata;
    const label = (event.label ?? '').trim();
    const status = (event.status ?? '').trim();

    // Transition explicite avec from → to
    if (m?.from && m?.to) {
      if (m.org_unit) return `Passage de ${m.from} à ${m.to} au sein de ${m.org_unit}.`;
      return `Évolution : ${m.from} → ${m.to}.`;
    }

    if (label === 'Mouvement de carrière') {
      if (m?.seniority && m?.org_unit) return `Prise de poste en tant que ${status} — ${m.seniority}, au sein de ${m.org_unit}.`;
      if (m?.seniority) return `Prise de poste en tant que ${status} — ${m.seniority}.`;
      if (m?.org_unit) return `Affectation en tant que ${status} au sein de ${m.org_unit}.`;
      return `Nouvelle affectation : ${status}.`;
    }

    if (label === 'Transfert') {
      if (m?.org_unit) return `Transfert en tant que ${status} vers ${m.org_unit}.`;
      return `Transfert enregistré en tant que ${status}.`;
    }

    if (label === 'Embauche') {
      if (m?.seniority && m?.org_unit) return `Bienvenue ! Embauche en tant que ${status} — ${m.seniority} au sein de ${m.org_unit}.`;
      if (m?.org_unit) return `Bienvenue ! Embauche en tant que ${status} au sein de ${m.org_unit}.`;
      return `Bienvenue ! Embauche en tant que ${status}.`;
    }

    if (label === 'Départ') {
      return `Départ acté — fin de collaboration.`;
    }

    if (label === 'Statut administratif') {
      switch (status) {
        case 'Actif':
          return `L'employé est de nouveau actif et pleinement opérationnel.`;
        case 'Suspendu':
          return `Activité temporairement suspendue.`;
        case 'Licencié':
          return `Contrat rompu — l'employé quitte l'effectif.`;
        case 'Période d\'essai':
          return `En période d'essai — intégration et évaluation en cours.`;
        default:
          return `Statut administratif : ${status}.`;
      }
    }

    return null;
  }
</script>


<Card class="rounded-xl border-slate-200 bg-white overflow-hidden flex flex-col border shadow-fine">
  <CardHeader class="pb-3 border-b border-slate-50 shrink-0">
    <div class="flex items-center gap-2.5">
      <span class="h-8 w-8 rounded-lg bg-sky-50 border border-sky-100 flex items-center justify-center shrink-0">
        <AppIcon name="clock" size={18} class="text-sky-600" />
      </span>
      <div class="flex flex-col">
        <div class="flex items-center gap-2">
          <span class="text-[0.92rem] font-bold tracking-tight text-slate-900">Historique de carrière</span>
          {#if events.length > 0}
            <Badge variant="secondary" class="bg-slate-100 text-slate-600 border-0 rounded-full font-bold text-[0.85rem] px-2.5 py-0 h-5">
              {events.length}
            </Badge>
          {/if}
        </div>
        <p class="text-[0.85rem] text-slate-500 leading-snug">Retracez chaque étape du parcours, de l'embauche à aujourd'hui.</p>
      </div>
    </div>
  </CardHeader>
  <CardContent class="pt-5 pb-6">
    {#if events.length === 0}
      <div class="text-center py-10 border-2 border-dashed border-slate-200 rounded-xl bg-slate-50/50">
        <span class="h-11 w-11 rounded-xl bg-white border border-slate-200 shadow-fine flex items-center justify-center mx-auto mb-3">
          <AppIcon name="calendar" size={20} class="text-slate-400" />
        </span>
        <p class="text-[0.86rem] font-semibold text-slate-700">Aucun événement enregistré</p>
        <p class="text-[0.85rem] text-slate-500 mt-1 max-w-sm mx-auto leading-relaxed">L'historique apparaîtra ici dès la première embauche ou transition. Chaque mouvement y sera raconté simplement.</p>
      </div>
    {:else}
      <div class="relative ml-4 border-l border-slate-200 pl-8 space-y-6">
        {#each events as event (event.id)}
          {@const style = getEventStyle(event)}
          {@const narrative = getHumanNarrative(event)}
          <div class="relative group">
            <!-- Timeline dot/icon -->
            <span class="absolute -left-[45px] top-0 h-8 w-8 rounded-full border-2 flex items-center justify-center shadow-fine bg-white {style.bgClass} {style.borderClass}">
              <AppIcon name={style.icon} size={18} class={style.iconClass} />
            </span>

            <div class="rounded-xl border border-slate-200 bg-white shadow-fine group-hover:border-sky-200 group-hover:shadow-sm p-4 transition-all">
              <div class="flex items-center justify-between gap-2">
                <div class="text-[0.85rem] font-bold uppercase tracking-widest text-slate-400">
                  {formatDate(event.date, false, false)}
                </div>
                <Badge variant="outline" class="font-semibold text-[0.85rem] text-slate-600 border-slate-200 bg-slate-50 rounded-full px-2.5 py-0 h-5">
                  {event.label}
                </Badge>
              </div>

              <div class="text-[0.90rem] font-bold text-slate-900 tracking-tight mt-2 leading-tight">
                {event.status}
              </div>

              {#if narrative}
                <p class="text-[0.85rem] text-slate-600 leading-relaxed mt-1.5">
                  {narrative}
                </p>
              {/if}

              {#if event.metadata?.from && event.metadata?.to}
                <div class="inline-flex items-center gap-1.5 mt-3 text-[0.85rem] bg-slate-50 border border-slate-100 rounded-full pl-1 pr-2.5 py-1">
                  <span class="line-through opacity-60 text-slate-500">{event.metadata.from}</span>
                  <AppIcon name="arrow-right" size={16} class="text-slate-400" />
                  <span class="font-semibold text-slate-700">{event.metadata.to}</span>
                </div>
              {:else if event.metadata?.seniority || event.metadata?.org_unit}
                <div class="flex flex-wrap items-center gap-1.5 mt-3">
                  {#if event.metadata.seniority}
                    <span class="inline-flex items-center gap-1.5 text-[0.85rem] font-medium text-slate-600 bg-slate-50 border border-slate-100 rounded-full px-2.5 py-1">
                      <AppIcon name="trending-up" size={16} class="text-slate-400" />
                      {event.metadata.seniority}
                    </span>
                  {/if}
                  {#if event.metadata.org_unit}
                    <span class="inline-flex items-center gap-1.5 text-[0.85rem] font-medium text-slate-600 bg-slate-50 border border-slate-100 rounded-full px-2.5 py-1">
                      <AppIcon name={getOrgUnitIcon(event.metadata.org_unit_type ?? '')} size={16} class="text-slate-400" />
                      {event.metadata.org_unit}
                    </span>
                  {/if}
                </div>
              {/if}

              <!-- Commentaire / raison — l'interface parle -->
              {#if event.description && event.description.trim().length > 0}
                <div class="flex gap-2.5 bg-sky-50/60 border border-sky-100 p-3 rounded-xl mt-3.5 leading-relaxed">
                  <AppIcon name="message-circle" size={16} class="text-sky-500 shrink-0 mt-0.5" />
                  <p class="text-[0.85rem] text-slate-700">« {event.description} »</p>
                </div>
              {:else}
                <div class="flex gap-2 bg-slate-50/70 border border-dashed border-slate-200 p-2.5 rounded-xl mt-3.5">
                  <AppIcon name="message-circle" size={16} class="text-slate-400 shrink-0 mt-0.5" />
                  <p class="text-[0.85rem] text-slate-400">Aucun commentaire.</p>
                </div>
              {/if}
            </div>
          </div>
        {/each}
      </div>
    {/if}
  </CardContent>
</Card>

