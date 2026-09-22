<script lang="ts">
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import { Badge } from "@/components/ui/badge";
  import { cn } from "@/utilities/common/css";
  import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
  import * as DropdownMenu from "@/components/ui/dropdown-menu";
  import { getInitials } from "@/utilities/common/string";
  import { getAvatarPalette } from "@/utilities/common/func";
  import { goto } from '$app/navigation';
  import { hr } from '@/constants/features/navigation';
  import AvatarGallery from "@/components/shared/media/AvatarGallery.svelte";
  import { getOrgUnitIcon } from "@/hr/jobs/constants/orgUnit.constants";
  import { getEmployeeStatusConfig, getEmployeeStatusDotConfig } from "@/hr/employees/constants/employeeStatus";
  import { fade } from "svelte/transition";
  import { buildFullName } from "@/utilities/common/employee.utils";
  import { getMediaUrl } from "@/utilities/common/media";
  import { get_api_base_origin } from "@/utilities/http/urls";
  import { useUploadProfilePhotoMutation } from "@/hr/employees/queries/employeeQueries";

  
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
      : '-'
  );

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
      <div class={cn('z-10000 absolute bottom-0 right-0.5 h-3 w-3 rounded-full border border-white shadow-fine transition-colors duration-300', statusDotConfig.color)} title={statusDotConfig.title}></div>
    </div>
    <div class="flex flex-col min-w-0">
      <span class="font-semibold text-[0.85rem] text-slate-800 truncate leading-tight group-hover/row:text-indigo-600 transition-colors">
        {fullName}
      </span>
      <span class="text-[0.82rem] text-slate-500 truncate">
        {employee.jobTitle || 'Poste non défini'}
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
      <span class="text-[0.83rem] text-slate-400">-</span>
    {/if}
  </div>

  <!-- Type de contrat -->
  <div class="w-[14%] flex flex-col justify-center gap-0.5">
    {#if employee.contractType}
      <Badge 
        variant="outline"
        class="w-fit bg-blue-50 text-blue-600 border-blue-200 text-[0.78rem] font-medium px-2 py-0.5 rounded-full"
      >
        {employee.contractType}
      </Badge>
    {:else}
      <span class="text-[0.83rem] text-slate-400">-</span>
    {/if}
  </div>

  <!-- Date d'embauche -->
  <div class="w-[14%] flex items-center gap-1.5">
    <AppIcon name="calendar" size={17} class="text-slate-400 shrink-0" />
    <span class="text-[0.82rem] text-slate-600">{hireDateDisplay}</span>
  </div>

  <!-- Localisation -->
  <div class="w-[14%] flex items-center gap-1.5 min-w-0">
    <AppIcon name="map-pin" size={17} class="text-slate-400 shrink-0" />
    <span class="text-[0.82rem] text-slate-600 truncate">
      {employee.location || employee.workSite || '-'}
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

