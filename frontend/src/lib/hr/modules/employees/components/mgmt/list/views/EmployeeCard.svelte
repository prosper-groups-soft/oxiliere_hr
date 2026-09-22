<script lang="ts">
  import AppIcon from "@/hr/components/layout/elements/AppIcon.svelte";
  import { Badge } from "@/components/ui/badge";
  import { cn } from "@/hr/utilities/common/css";
  import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
  import { getInitials } from "@/hr/utilities/common/string";
  import { getAvatarPalette } from "@/hr/utilities/common/func";
  import { getOrgUnitIcon } from "@/hr/modules/jobs/constants/orgUnit.constants";
  import { getEmployeeStatusConfig, getEmployeeStatusDotConfig } from "@/hr/modules/employees/constants/employeeStatus";
  import { fade } from "svelte/transition";
  import { buildFullName } from "@/hr/utilities/common/employee.utils";
  import { getMediaUrl } from "@/hr/utilities/common/media";
  import { get_api_base_origin } from "@/hr/utilities/http/urls";
  import { useUploadProfilePhotoMutation } from "@/hr/modules/employees/queries/employeeQueries";
  import AvatarGallery from "@/hr/components/shared/media/AvatarGallery.svelte";
  import { goto } from "$app/navigation";
  import * as DropdownMenu from "@/components/ui/dropdown-menu";
  import { hr } from '@/hr/constants/navigation/navigation';

  let { employee } = $props();

  const uploadPhotoMutation = useUploadProfilePhotoMutation();

  const fullName = $derived(buildFullName(employee));
  const profilePhoto = $derived(getMediaUrl(employee.profile_photo || employee.avatarUrl || employee.user?.photo));
  const palette = $derived(getAvatarPalette(fullName || ''));
  const currentStatus = $derived(employee.current_status?.status);
  const cfg = $derived(getEmployeeStatusConfig(currentStatus));
  const statusDotConfig = $derived(getEmployeeStatusDotConfig(currentStatus));

  const hireDateDisplay = $derived(
    employee.joinDate 
      ? new Date(employee.joinDate).toLocaleDateString('fr-FR', { day: 'numeric', month: 'short', year: 'numeric' })
      : 'Non renseignée'
  );

  //  calcul local — évite un champ backend seniority_label
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

  function handlePhotoUpload(file: File) {
    $uploadPhotoMutation.mutate({ employeeId: employee.id, file });
  }
</script>


<div
  in:fade={{ duration: 300 }}
  onclick={toEmployeeDetails}
  role="link"
  tabindex="0"
  onkeydown={(e) => e.key === 'Enter' && toEmployeeDetails()}
  class="group block bg-white border border-slate-200 rounded-xl p-6 hover:shadow-md hover:border-indigo-200 transition-all cursor-pointer relative overflow-hidden outline-none focus-visible:ring-2 focus-visible:ring-indigo-500 w-full"
>
  <div class="absolute top-2 right-3 flex items-center gap-2">
    <Badge 
      variant="outline"
      class="{cfg.bg} {cfg.color} border-0 text-[0.75rem] font-semibold px-2 py-0.5 shadow-none rounded-full whitespace-nowrap flex items-center gap-1"
    >
      <span class={cn("h-1.5 w-1.5 rounded-full", cfg.dot)}></span>
      {cfg.label}
    </Badge>

    <div onclick={(e) => e.stopPropagation()} role="none">
      <DropdownMenu.Root>
        <DropdownMenu.Trigger asChild>
          {#snippet child({ props })}
            <button 
              {...props}
              class="p-1.5 hover:bg-slate-100 rounded-md transition-colors text-slate-400 hover:text-slate-600 outline-none cursor-pointer"
            >
              <AppIcon name="more-vertical" size={18} />
            </button>
          {/snippet}
        </DropdownMenu.Trigger>
  
        <DropdownMenu.Content align="end" class="p-1 rounded-lg shadow-fine bg-white border-slate-100">
          <DropdownMenu.Item onclick={toEmployeeDetails} class="cursor-pointer gap-2 py-2 text-[0.85rem]!">
            <AppIcon name="user" size={18} class="text-slate-500" />
            Détails du profil
          </DropdownMenu.Item>
  
          <DropdownMenu.Item 
            onclick={() => window.open(`${get_api_base_origin()}/api/employees/${employee.id}/export/`, '_blank')}
            class="cursor-pointer gap-2 py-2 text-[0.85rem]!"
          >
            <AppIcon name="download" size={18} class="text-slate-500" />
            Exporter profil
          </DropdownMenu.Item>
        </DropdownMenu.Content>
      </DropdownMenu.Root>
    </div>
  </div>

  <div class="flex items-center gap-4 mb-4 pr-8">
    <div class="relative" onclick={(e) => e.stopPropagation()} role="none">
      <AvatarGallery
        name={fullName || ''}
        src={profilePhoto}
        onUpload={handlePhotoUpload}
        iconSize={16}
        iconStroke={2}
        class="h-16 w-16 rounded-full shadow-none"
      >
        <Avatar class="h-full w-full ring-1 ring-slate-100 group-hover:ring-indigo-100 transition-all border shadow-none overflow-hidden">
          <AvatarImage src={profilePhoto} alt={fullName} class="object-cover" />
          <AvatarFallback class={cn("text-lg font-bold", palette.bg, palette.text)}>
            {getInitials(employee.last_name, employee.middle_name, employee.first_name)}
          </AvatarFallback>
        </Avatar>
      </AvatarGallery>
      <div class={cn('absolute bottom-0 right-1.5 h-3 w-3 rounded-full border border-white shadow-fine transition-colors duration-300', statusDotConfig.color)} title={statusDotConfig.title}></div>
    </div>
    
    <div class="flex-1 min-w-0">
      <h3 class="font-semibold text-slate-900 group-hover:text-indigo-600 transition-colors text-[0.95rem] truncate">
        {fullName}
      </h3>
      <p class="truncate flex items-center gap-1.5 mt-0.5">
        {#if employee.jobTitle}
          <span class="text-slate-500 text-sm">{employee.jobTitle}</span>
        {:else}
          <AppIcon name="briefcase" size={14} class="text-slate-300 shrink-0" />
          <span class="text-slate-400 text-sm">Fonction non affectée</span>
        {/if}
      </p>
    </div>
  </div>

  <div class="space-y-3">
    {#if employee.orgUnit}
      <div class="flex items-center gap-2">
        <AppIcon name={getOrgUnitIcon(employee.orgUnitType)} size={16} class="text-slate-400 shrink-0" />
        <span class="text-[0.82rem] text-slate-600 truncate">
          {employee.orgUnit}
        </span>
      </div>
    {/if}

    <div class="flex items-center gap-2 flex-wrap">
      <AppIcon name="file-text" size={16} class="text-slate-400 shrink-0" />
      {#if contractEnriched}
        <Badge 
          variant="outline"
          class="bg-blue-50 text-blue-600 border-blue-200 text-[0.75rem] font-medium px-2 py-0.5 rounded-full"
        >
          {contractEnriched}
        </Badge>
        {#if contractSalary}
          <span class="text-[0.82rem] font-medium text-slate-600">{contractSalary}</span>
        {/if}
      {:else}
        <span class="text-[0.84rem] text-slate-400">Contrat non défini</span>
      {/if}
      {#if isExpiringSoon}
        <span class="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-amber-50 text-amber-700 border border-amber-200 text-[0.8rem] font-semibold">
          <AppIcon name="alert-triangle" size={14} />
          Expire le {expiryLabel}
        </span>
      {/if}
    </div>

    <div class="flex items-center gap-2">
      <AppIcon name="map-pin" size={16} class="text-slate-400 shrink-0" />
      <span class="text-[0.82rem] text-slate-600 truncate">
        {employee.location || employee.workSite || 'Site non renseigné'}
      </span>
    </div>
  </div>

  <div class="mt-4 pt-4 border-t border-slate-100 flex items-center justify-between">
    <div class="flex items-center gap-1.5">
      <AppIcon name="calendar" size={15} class="text-slate-400" />
      <span class="text-[0.82rem] text-slate-500">Embauché le</span>
    </div>
    <span class="font-medium text-slate-700 inline-flex items-center gap-1.5 text-[0.86rem]">
      {hireDateDisplay}
      {#if seniority}
        <span class="text-slate-400 font-normal text-[0.86rem]">· {seniority} d'ancienneté</span>
      {/if}
      {#if isProbation}
        <span class="px-1.5 py-0 rounded-full bg-violet-50 text-violet-600 border border-violet-200 text-[0.7rem] font-semibold">Essai</span>
      {/if}
    </span>
  </div>
</div>
