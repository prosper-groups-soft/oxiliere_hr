<script lang="ts">
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import { Badge } from "@/components/ui/badge";
  import { cn } from "@/utilities/common/css";
  import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
  import { getInitials } from "@/utilities/common/string";
  import { getAvatarPalette } from "@/utilities/common/func";
  import { getOrgUnitIcon } from "@/features/jobs/constants/orgUnit.constants";
  import { getEmployeeStatusConfig, getEmployeeStatusDotConfig } from "@/features/employees/constants/employeeStatus";
  import { fade } from "svelte/transition";
  import { buildFullName } from "@/utilities/common/employee.utils";
  import { getMediaUrl } from "@/utilities/common/media";
  import { get_api_base_origin } from "@/utilities/http/urls";
  import { useUploadProfilePhotoMutation } from "@/features/employees/queries/employeeQueries";
  import AvatarGallery from "@/components/shared/media/AvatarGallery.svelte";
  import { goto } from "$app/navigation";
  import * as DropdownMenu from "@/components/ui/dropdown-menu";

  
  let { employee } = $props();

  const uploadPhotoMutation = useUploadProfilePhotoMutation();

  // --- LOGIQUE DÉRIVÉE ---
  const fullName = $derived(buildFullName(employee));

  const profilePhoto = $derived(
    getMediaUrl(employee.profile_photo || employee.avatarUrl || employee.user?.photo)
  );

  const palette = $derived(getAvatarPalette(fullName || ''));

  const currentStatus = $derived(employee.current_status?.status);
  const cfg = $derived(getEmployeeStatusConfig(currentStatus));
  const statusDotConfig = $derived(getEmployeeStatusDotConfig(currentStatus));

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
    goto(`/employees/${employee.id}`);
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
  <!-- Actions & Status -->
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

  <!-- Header: Avatar & Identity -->
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
      <p class="text-[0.85rem] text-slate-500 truncate">
        {employee.jobTitle || 'Poste non défini'}
      </p>
    </div>
  </div>

  <!-- Info Grid -->
  <div class="space-y-3">
    <!-- Unité Organisationnelle -->
    {#if employee.orgUnit}
      <div class="flex items-center gap-2">
        <AppIcon name={getOrgUnitIcon(employee.orgUnitType)} size={16} class="text-slate-400 shrink-0" />
        <span class="text-[0.82rem] text-slate-600 truncate">
          {employee.orgUnit}
        </span>
      </div>
    {/if}

    <!-- Type de contrat -->
    <div class="flex items-center gap-2">
      <AppIcon name="file-text" size={16} class="text-slate-400 shrink-0" />
      {#if employee.contractType}
        <Badge 
          variant="outline"
          class="bg-blue-50 text-blue-600 border-blue-200 text-[0.75rem] font-medium px-2 py-0.5 rounded-full"
        >
          {employee.contractType}
        </Badge>
      {:else}
        <span class="text-[0.82rem] text-slate-400">-</span>
      {/if}
    </div>

    <!-- Localisation -->
    <div class="flex items-center gap-2">
      <AppIcon name="map-pin" size={16} class="text-slate-400 shrink-0" />
      <span class="text-[0.82rem] text-slate-600 truncate">
        {employee.location || employee.workSite || '-'}
      </span>
    </div>
  </div>

  <!-- Footer: Date d'embauche -->
  <div class="mt-4 pt-4 border-t border-slate-100 flex items-center justify-between">
    <div class="flex items-center gap-1.5">
      <AppIcon name="calendar" size={14} class="text-slate-400" />
      <span class="text-[0.78rem] text-slate-500">Embauché le</span>
    </div>
    <span class="text-[0.82rem] font-medium text-slate-700">
      {hireDateDisplay}
    </span>
  </div>
</div>

