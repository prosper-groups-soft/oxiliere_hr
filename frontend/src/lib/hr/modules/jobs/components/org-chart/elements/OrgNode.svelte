<script lang="ts">
  import AppIcon from "@/hr/components/layout/elements/AppIcon.svelte";
  import { cn } from "@/hr/utilities/common/css";
  import * as Avatar from "@/components/ui/avatar";
  import AvatarGallery from "@/hr/components/shared/media/AvatarGallery.svelte";
  import { Skeleton } from "@/components/ui/skeleton";
  import type { NodeType } from "../../../types/types";
  import type { OrgUnit } from "../../../types/org.types";
  import { formatEmployeeName } from "@/hr/utilities/common/employee.utils";
  import { getInitials } from "@/hr/utilities/common/string";
  import { getAvatarPalette } from "@/hr/utilities/common/func";
  import { slide, fade } from "svelte/transition";
  import { jobsStore } from "../../../stores/jobs.svelte";
  import { notification } from "@/hr/stores/notification.svelte";

  let {
    orgUnit,
    isSelected = false,
    onClick,
    onAddChild,
    onEdit
  } = $props<{
    orgUnit: OrgUnit,
    isSelected?: boolean,
    onClick?: (unit: OrgUnit) => void,
    onAddChild?: (parent: OrgUnit) => void,
    onEdit?: (unit: OrgUnit) => void
  }>();

  // Lire les données fraîches depuis le store pour garantir la réactivité
  const freshOrgUnit = $derived.by(() => {
    // Dépendance explicite au store
    const _units = jobsStore.orgUnits;
    return jobsStore.getOrgUnitById(orgUnit.id) ?? orgUnit;
  });

  const memberCount = $derived(freshOrgUnit.employeeCount ?? 0);

  // Manager inclus directement dans l'objet orgUnit (backend)
  const managerName = $derived.by(() => {
    const m = freshOrgUnit.manager;
    if (!m) return '';
    return formatEmployeeName(m);
  });

  const managerAvatarUrl = $derived.by(() => freshOrgUnit.manager?.photo || '');

  const managerExists = $derived.by(() => !!freshOrgUnit.manager);

  // Adjoint (affoint) inclus directement dans l'objet orgUnit
  const affointName = $derived.by(() => {
    const a = freshOrgUnit.affoint;
    if (!a) return '';
    return formatEmployeeName(a);
  });

  const affointAvatarUrl = $derived.by(() => freshOrgUnit.affoint?.photo || '');

  const affointExists = $derived.by(() => !!freshOrgUnit.affoint);

  const nodeTypeConfig = $derived.by(() => {
    const type = (freshOrgUnit.type as NodeType) || 'DEPARTMENT';
    const config: Record<NodeType, { label: string; icon: string; colors: { border: string; badge: string; badgeText: string; badgeBorder: string; icon: string; iconBg: string } }> = {
      'DEPARTMENT': {
        label: 'Département',
        icon: 'business',
        colors: { border: 'border-indigo-200', badge: 'bg-indigo-50', badgeText: 'text-indigo-700', badgeBorder: 'border-indigo-200', icon: 'text-indigo-500', iconBg: 'bg-indigo-100' }
      },
      'DIVISION': {
        label: 'Division',
        icon: 'corporate_fare',
        colors: { border: 'border-violet-200', badge: 'bg-violet-50', badgeText: 'text-violet-700', badgeBorder: 'border-violet-200', icon: 'text-violet-500', iconBg: 'bg-violet-100' }
      },
      'TEAM': {
        label: 'Equipe',
        icon: 'team',
        colors: { border: 'border-emerald-200', badge: 'bg-emerald-50', badgeText: 'text-emerald-700', badgeBorder: 'border-emerald-200', icon: 'text-emerald-500', iconBg: 'bg-emerald-100' }
      },
      'FUNCTION': {
        label: 'Fonction',
        icon: 'settings',
        colors: { border: 'border-amber-200', badge: 'bg-amber-50', badgeText: 'text-amber-700', badgeBorder: 'border-amber-200', icon: 'text-amber-500', iconBg: 'bg-amber-100' }
      },
      'BRANCH': {
        label: 'Succursale',
        icon: 'store',
        colors: { border: 'border-sky-200', badge: 'bg-sky-50', badgeText: 'text-sky-700', badgeBorder: 'border-sky-200', icon: 'text-sky-500', iconBg: 'bg-sky-100' }
      },
      'PROJECT': {
        label: 'Projet',
        icon: 'folder',
        colors: { border: 'border-rose-200', badge: 'bg-rose-50', badgeText: 'text-rose-700', badgeBorder: 'border-rose-200', icon: 'text-rose-500', iconBg: 'bg-rose-100' }
      }
    };
    return config[type] || config['DEPARTMENT'];
  });

  function handleDelete() {
    const guardMessage = jobsStore.getDeleteOrgUnitGuard(orgUnit);
    if (guardMessage) {
      notification.toast.error(guardMessage);
      return;
    }

    notification.confirm({
      title: 'Supprimer l\'unite ?',
      message: `Voulez-vous vraiment supprimer l'unite "${orgUnit.name}" ? Cette action est reservee aux unites feuilles sans affectation active et reste irreversible.`,
      type: 'danger',
      yesText: 'Supprimer',
      onYes: async () => {
        try {
          await jobsStore.deleteOrgUnit(orgUnit.id);
          notification.toast.success(`L'unite "${orgUnit.name}" a ete supprimee.`);
        } catch {
          // Error toast is handled by the service.
        }
      }
    });
  }
</script>


<div
  role="button"
  tabindex="0"
  onclick={() => onClick?.(orgUnit)}
  onkeydown={(e) => e.key === 'Enter' && onClick?.(orgUnit)}
  class={cn(
    "relative flex flex-col w-75 bg-white border rounded-xl p-4 pt-5 transition-all duration-200 cursor-pointer select-none",
    "hover:border-slate-300 hover:bg-slate-50 group shadow-soft",
    nodeTypeConfig.colors.border,
    isSelected && "border-primary ring-2 ring-primary/10"
  )}
>
  <!-- Quick Action -->
  <div class="flex gap-1.5 absolute -top-4 -right-2">
    <button
      onclick={(e) => { e.stopPropagation(); handleDelete(); }}
      class="w-8.5 h-8.5 rounded-full bg-red-50 border border-red-200 text-red-800 shadow-fine flex items-center justify-center opacity-0 group-hover:opacity-100 transition-all hover:scale-105 active:scale-95 z-20 cursor-pointer"
      title="Supprimer l'unité"
    >
      <AppIcon name="trash-2" size={19} />
    </button>
    <button
      onclick={(e) => { e.stopPropagation(); onEdit?.(orgUnit); }}
      class="w-8.5 h-8.5 rounded-full bg-blue-50 border border-blue-200 text-blue-700 shadow-fine flex items-center justify-center opacity-0 group-hover:opacity-100 transition-all hover:scale-105 active:scale-95 z-20 cursor-pointer"
      title="Modifier l'unité"
    >
      <AppIcon name="edit" size={18} />
    </button>
    <button
      onclick={(e) => { e.stopPropagation(); onAddChild?.(orgUnit); }}
      class="w-8.5 h-8.5 rounded-full bg-primary text-white shadow-fine flex items-center justify-center opacity-0 group-hover:opacity-100 transition-all hover:scale-105 active:scale-95 z-20 cursor-pointer"
      title="Ajouter un enfant"
    >
      <AppIcon name="plus" size={19} />
    </button>
  </div>


  <!-- Type Badge -->
  <div class={cn(
    "absolute -top-2.5 left-3 px-2 py-0.5 rounded-full shadow-fine flex items-center gap-1 z-10 border",
    nodeTypeConfig.colors.badge,
    nodeTypeConfig.colors.badgeBorder
  )}>
    <AppIcon name={nodeTypeConfig.icon} size={18} class={nodeTypeConfig.colors.icon} />
    <span class={cn("text-[0.8rem] font-medium", nodeTypeConfig.colors.badgeText)}>{nodeTypeConfig.label}</span>
  </div>
  <div class="flex items-center justify-between mb-3 pt-2">
    <div class={cn(
      "p-1.5 rounded-lg transition-colors group-hover:text-white group-hover:bg-primary!",
      nodeTypeConfig.colors.iconBg,
      nodeTypeConfig.colors.icon,
      isSelected && "bg-primary/10 text-primary"
    )}>
      <AppIcon name="network" size={22} />
    </div>
    <div class="space-y-1 text-right text-[0.7rem] font-bold text-slate-500 uppercase tracking-tighter">
      <div class="px-2 py-0.5 rounded-full bg-slate-50 border border-slate-100 flex items-center gap-1 whitespace-nowrap">
        <span>{memberCount}</span>
        <span class="text-[0.77rem]">/ {freshOrgUnit.authorizedHeadcount}</span>
      </div>
    </div>
  </div>

  <div class="space-y-1">
    <div class="flex items-start justify-between gap-2">
      <h3 class="text-[0.87rem] font-bold text-slate-900 leading-tight flex-1 truncate" title={freshOrgUnit.name}>
        {freshOrgUnit.name}
      </h3>
    </div>
    {#if managerExists}
      {@const palette = getAvatarPalette(managerName)}
      <div class="flex items-center gap-2" in:fade={{ duration: 200 }}>
        <AvatarGallery
          name={managerName}
          src={managerAvatarUrl}
          onUpload={() => {}}
          iconSize={12}
          iconStroke={2}
          disableUploadHover={true}
          class="h-7 w-7 rounded-full"
        >
          <Avatar.Root class="h-full w-full border border-slate-200">
            <Avatar.Image src={managerAvatarUrl} alt={managerName} />
            <Avatar.Fallback class={cn("text-[0.86rem] font-medium", palette.bg, palette.text)}>
              {getInitials(...managerName.split(' '))}
            </Avatar.Fallback>
          </Avatar.Root>
        </AvatarGallery>
        <div class="flex flex-col min-w-0">
          <span class="text-[0.9rem] font-medium text-slate-900 truncate">{managerName}</span>
          <span class="text-[0.89rem] text-slate-500 truncate">Responsable</span>
        </div>
      </div>
    {:else if freshOrgUnit.manager === undefined}
      <!-- Skeleton loading state -->
      <div class="flex items-center gap-2">
        <Skeleton class="h-7 w-7 rounded-full" />
        <div class="flex flex-col gap-1">
          <Skeleton class="h-4 w-24" />
          <Skeleton class="h-3 w-16" />
        </div>
      </div>
    {:else}
      <div class="flex items-center gap-1.5 text-slate-400" in:fade={{ duration: 200 }}>
        <AppIcon name="circle-x" size={24} />
        <span class="text-[0.92rem]">Non assigné</span>
      </div>
    {/if}

    {#if affointExists}
      {@const affointPalette = getAvatarPalette(affointName)}
      <div class="flex items-center gap-2 mt-1.5 pt-1.5 border-t border-slate-100" in:fade={{ duration: 200 }}>
        <AvatarGallery
          name={affointName}
          src={affointAvatarUrl}
          onUpload={() => {}}
          iconSize={12}
          iconStroke={2}
          disableUploadHover={true}
          class="h-7 w-7 rounded-full"
        >
          <Avatar.Root class="h-full w-full border border-slate-200">
            <Avatar.Image src={affointAvatarUrl} alt={affointName} />
            <Avatar.Fallback class={cn("text-[0.86rem] font-medium", affointPalette.bg, affointPalette.text)}>
              {getInitials(...affointName.split(' '))}
            </Avatar.Fallback>
          </Avatar.Root>
        </AvatarGallery>
        <div class="flex flex-col min-w-0">
          <span class="text-[0.9rem] font-medium text-slate-900 truncate">{affointName}</span>
          <span class="text-[0.89rem] text-slate-500 truncate">Adjoint</span>
        </div>
      </div>
    {:else if freshOrgUnit.affoint === undefined}
      <!-- Skeleton loading state -->
      <div class="flex items-center gap-2 mt-1.5 pt-1.5 border-t border-slate-100">
        <Skeleton class="h-7 w-7 rounded-full" />
        <div class="flex flex-col gap-1">
          <Skeleton class="h-4 w-24" />
          <Skeleton class="h-3 w-16" />
        </div>
      </div>
    {/if}
  </div>

  {#if isSelected}
    <div transition:slide={{ duration: 250 }} class="overflow-hidden">
      <div class="mt-1 pt-2 border-t border-slate-100 flex justify-between items-center text-primary group-hover:text-primary">
        <span class="text-[0.87rem] font-bold uppercase tracking-wider">Voir détails</span>
        <AppIcon name="arrow-right" size={17} />
      </div>
    </div>
  {/if}
</div>

