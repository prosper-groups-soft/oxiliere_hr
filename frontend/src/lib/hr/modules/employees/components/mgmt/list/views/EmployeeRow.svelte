<script lang="ts">
  import AppIcon from "@/hr/components/layout/elements/AppIcon.svelte";
  import { Badge } from "@/components/ui/badge";
  import { cn } from "@/hr/utilities/common/css";
  import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
  import * as DropdownMenu from "@/components/ui/dropdown-menu";
  import { getInitials } from "@/hr/utilities/common/string";
  import { getAvatarPalette } from "@/hr/utilities/common/func";
  import { goto } from '$app/navigation';
  import { hr } from '@/hr/constants/navigation/navigation';
  import AvatarGallery from "@/hr/components/shared/media/AvatarGallery.svelte";
  import { getOrgUnitIcon } from "@/hr/modules/jobs/constants/orgUnit.constants";
  import { getEmployeeStatusConfig, getEmployeeStatusDotConfig } from "@/hr/modules/employees/constants/employeeStatus";
  import { fade } from "svelte/transition";
  import { buildFullName } from "@/hr/utilities/common/employee.utils";
  import { getMediaUrl } from "@/hr/utilities/common/media";
  import { get_api_base_origin } from "@/hr/utilities/http/urls";
  import { useUploadProfilePhotoMutation } from "@/hr/modules/employees/queries/employeeQueries";

  
  let { employee } = $props();

  const uploadPhotoMutation = useUploadProfilePhotoMutation();

  // --- LOGIQUE DÉRIVÉE ---
  const fullName = $derived(buildFullName(employee));

  const profilePhoto = $derived(
    getMediaUrl(employee.profile_photo || employee.avatarUrl || employee.user?.photo)
  );

  const currentStatus = $derived(employee.current_status?.status);
  const cfg = $derived(getEmployeeStatusConfig(currentStatus));
  const statusDotConfig = $derived(getEmployeeStatusDotConfig(currentStatus));

  const palette = $derived(getAvatarPalette(fullName || ''));

  // Formatage de la date d'embauche
  const hireDateDisplay = $derived(
    employee.joinDate 
      ? new Date(employee.joinDate).toLocaleDateString('fr-FR', { 
          day: 'numeric', 
          month: 'short', 
          year: 'numeric' 
        })
      : 'Non renseignée'
  );

  //  même helpers que EmployeeCard — extraire en utils/employeeDisplay.ts quand 3e usage
  function seniorityLabel(dateStr: string | undefined): string {
    if (!dateStr) return '';
    const start = new Date(dateStr);
    if (isNaN(start.getTime())) return '';
    const now = new Date();
    let months = (now.getFullYear() - start.getFullYear()) * 12 + (now.getMonth() - start.getMonth());
    if (now.getDate() < start.getDate()) months -= 1;
    if (months < 0) months = 0;
    if (months < 1) {
      const days = Math.floor((now.getTime() - start.getTime()) / 86400000);
      return days <= 1 ? "1 jour" : `${days} jours`;
    }
    const years = Math.floor(months / 12);
    const rem = months % 12;
    if (years === 0) return rem === 1 ? "1 mois" : `${rem} mois`;
    if (rem === 0) return years === 1 ? "1 an" : `${years} ans`;
    return `${years} ${years === 1 ? 'an' : 'ans'} ${rem} mois`;
  }
  
  const seniority = $derived(seniorityLabel(employee.joinDate || employee.hire_date));
  
  const isProbation = $derived.by(() => {
    const d = employee.joinDate || employee.hire_date;
    if (!d) return false;
    const start = new Date(d);
    if (isNaN(start.getTime())) return false;
    const diff = (Date.now() - start.getTime()) / 86400000;
    return diff >= 0 && diff < 90;
  });

  const contractEnriched = $derived.by(() => {
    const c = employee.currentContract;
    if (c) {
      const type = c.contract_type || employee.contractType || '';
      const regime = c.remuneration_type === 'HOURLY' ? 'Horaire' : c.remuneration_type === 'FIXED' ? 'Fixe' : c.remuneration_type || '';
      const cur = c.currency || '';
      return [type, regime, cur].filter(Boolean).join(' · ') || type || employee.contractType || '';
    }
    return employee.contractType || '';
  });

  const contractSalary = $derived.by(() => {
    const c = employee.currentContract;
    if (!c) return '';
    const cur = c.currency ? ` ${c.currency}` : '';
    if (c.remuneration_type === 'HOURLY' && c.hourly_rate != null) return `${Number(c.hourly_rate).toLocaleString('fr-FR')}${cur}/h`;
    if (c.base_salary != null && c.base_salary !== 0) return `${Number(c.base_salary).toLocaleString('fr-FR')}${cur}`;
    return '';
  });

  const contractEnd = $derived(employee.currentContract?.end_date ?? null);
  
  const daysUntilEnd = $derived.by(() => {
    if (!contractEnd) return null;
    const end = new Date(contractEnd);
    if (isNaN(end.getTime())) return null;
    return Math.ceil((end.getTime() - Date.now()) / 86400000);
  });
  
  const isExpiringSoon = $derived(daysUntilEnd != null && daysUntilEnd >= 0 && daysUntilEnd <= 30);
  
  const expiryLabel = $derived.by(() => {
    if (!contractEnd || !isExpiringSoon) return '';
    return new Date(contractEnd).toLocaleDateString('fr-FR', { day: '2-digit', month: '2-digit' });
  });

  function toEmployeeDetails() {
    goto(hr(`/employees/${employee.id}`));
  }

  function handleAvatarUpload(file: File) {
    $uploadPhotoMutation.mutate({ employeeId: employee.id, file });
  }
</script>


<div 
  in:fade={{ duration: 300 }}
  role="link"
  tabindex="0"
  onclick={toEmployeeDetails}
  onkeydown={(e) => e.key === 'Enter' && toEmployeeDetails()}
  class="group/row flex items-center py-3 px-6 border-b border-slate-50 hover:bg-indigo-50/30 cursor-pointer transition-colors"
>
  <!-- Avatar & Identity -->
  <div class="w-[28%] flex items-center gap-3">
    <div role="none" onclick={(e) => e.stopPropagation()} class="relative">
      <AvatarGallery 
        name={fullName || ''}
        src={profilePhoto}
        onUpload={handleAvatarUpload}
        iconSize={16}
        iconStroke={2}
        class="h-13 w-13 rounded-full shadow-fine"
      >
        <Avatar class="h-full w-full border border-slate-200">
          <AvatarImage src={profilePhoto} alt={fullName} class="object-cover" />
          <AvatarFallback class={cn("font-bold text-[0.8rem]", palette.bg, palette.text)}>
            {getInitials(employee.last_name, employee.middle_name, employee.first_name)}
          </AvatarFallback>
        </Avatar>
      </AvatarGallery>
      <div class={cn('z-1000 absolute bottom-0 right-0.5 h-3 w-3 rounded-full border border-white shadow-fine transition-colors duration-300', statusDotConfig.color)} title={statusDotConfig.title}></div>
    </div>
    <div class="flex flex-col min-w-0">
      <span class="font-semibold text-[0.85rem] text-slate-800 truncate leading-tight group-hover/row:text-indigo-600 transition-colors">
        {fullName}
      </span>
      <span class="text-[0.86rem] truncate flex items-center gap-1">
        {#if employee.jobTitle}
          <span class="text-slate-500 truncate text-[0.86rem]">{employee.jobTitle}</span>
        {:else}
          <AppIcon name="briefcase" size={15} class="text-slate-300 shrink-0" />
          <span class="text-slate-400 text-[0.86rem]">Fonction non affectée</span>
        {/if}
      </span>
    </div>
  </div>

  <!-- Unité Organisationnelle -->
  <div class="w-[18%] flex flex-col justify-center gap-0.5">
    {#if employee.orgUnit}
      <div class="flex items-center gap-1.5">
        <AppIcon name={getOrgUnitIcon(employee.orgUnitType)} size={17} class="text-slate-400" />
        <span class="text-[0.83rem] font-medium text-slate-700 truncate">
          {employee.orgUnit}
        </span>
      </div>
    {:else}
      <span class="text-[0.83rem] text-slate-400">Aucune unité</span>
    {/if}
  </div>

  <!-- Type de contrat (enrichi) -->
  <div class="w-[14%] flex flex-col justify-center gap-1">
    {#if contractEnriched}
      <Badge 
        variant="outline"
        class="w-fit bg-blue-50 text-blue-600 border-blue-200 text-[0.78rem] font-medium px-2 py-0.5 rounded-full"
      >
        {contractEnriched}
      </Badge>
      {#if contractSalary}
        <span class="text-[0.82rem] font-medium text-slate-600">{contractSalary}</span>
      {/if}
      {#if isExpiringSoon}
        <span class="w-fit inline-flex items-center gap-1 px-1.5 py-0 rounded-full bg-amber-50 text-amber-700 border border-amber-200 text-[0.68rem] font-semibold">
          <AppIcon name="alert-triangle" size={10} />
          Expire le {expiryLabel}
        </span>
      {/if}
    {:else}
      <span class="text-[0.82rem] text-slate-400">Contrat non défini</span>
    {/if}
  </div>

  <!-- Ancienneté -->
  <div class="w-[14%] flex flex-col justify-center gap-0.5">
    <div class="flex items-center gap-1.5">
      <AppIcon name="calendar" size={17} class="text-slate-400 shrink-0" />
      <span class="text-[0.82rem] text-slate-600">{hireDateDisplay}</span>
    </div>
    {#if seniority}
      <span class="text-[0.82rem] text-slate-400">
        · {seniority} d'ancienneté
        {#if isProbation}
          <span class="ml-1 px-1 py-0 rounded-full bg-violet-50 text-violet-600 border border-violet-200 text-[0.7rem] font-semibold align-middle">Essai</span>
        {/if}
      </span>
    {/if}
  </div>

  <!-- Localisation -->
  <div class="w-[14%] flex items-center gap-1.5 min-w-0">
    <AppIcon name="map-pin" size={17} class="text-slate-400 shrink-0" />
    <span class="text-[0.82rem] text-slate-600 truncate">
      {employee.location || employee.workSite || 'Site non renseigné'}
    </span>
  </div>

  <!-- Statut -->
  <div class="w-[12%] flex items-center justify-end pr-4">
    <Badge 
      variant="outline"
      class="{cfg.bg} {cfg.color} border-0 text-[0.78rem] font-semibold px-2.5 py-1 shadow-none rounded-full whitespace-nowrap flex items-center gap-1.5"
    >
      <span class={cn("h-1.5 w-1.5 rounded-full", cfg.dot)}></span>
      {cfg.label}
    </Badge>
  </div>

  {@render RowActions()}
</div>


{#snippet RowActions()}
  <div class="w-[5%] flex items-center px-2" onclick={(e) => e.stopPropagation()} role="none">
    <DropdownMenu.Root>
      <DropdownMenu.Trigger asChild>
        {#snippet child({ props })}
          <button 
            {...props}
            class="p-1.5 hover:bg-slate-200/50 rounded-md transition-colors text-slate-800 z-10 cursor-pointer outline-none"
          >
            <AppIcon name="more-vertical" size={21} />
          </button>
        {/snippet}
      </DropdownMenu.Trigger>

      <DropdownMenu.Content align="end" class="p-1 rounded-lg shadow-fine bg-white border-slate-100">
        <DropdownMenu.Item onclick={toEmployeeDetails} class="cursor-pointer gap-2 py-2 text-[0.85rem]!">
          <AppIcon name="user" size={19} class="text-slate-500" />
          Détails du profil
        </DropdownMenu.Item>

        <DropdownMenu.Item 
          onclick={() => window.open(`${get_api_base_origin()}/api/employees/${employee.id}/export/`, '_blank')}
          class="cursor-pointer gap-2 py-2 text-[0.85rem]!"
        >
          <AppIcon name="download" size={19} class="text-slate-500" />
          Exporter profil
        </DropdownMenu.Item>
      </DropdownMenu.Content>
    </DropdownMenu.Root>
  </div>
{/snippet}
