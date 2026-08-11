<script lang="ts">
  import { Avatar, AvatarImage, AvatarFallback } from '@/components/ui/avatar';
  import { Badge } from '@/components/ui/badge';
  import { Button } from '@/components/ui/button';
  import AppIcon from '@/components/layout/elements/AppIcon.svelte';
  import { getInitials } from '@/utilities/common/string';
  import { getAvatarPalette } from '@/utilities/common/func';
  import { cn } from '@/utilities/common/css';
  import { buildFullName } from '@/utilities/common/employee.utils';
  import { getMediaUrl } from '@/utilities/common/media';
  import AvatarGallery from '@/components/shared/media/AvatarGallery.svelte';
  import EmployeeLifecycleActions from './EmployeeLifecycleActions.svelte';
  import EmployeeProfileTabs from './EmployeeProfileTabs.svelte';
  import EmployeeEditSheet from './EmployeeEditSheet.svelte';
  import { useUploadProfilePhotoMutation } from '../../../../queries/employeeQueries';
  import { getEmployeeStatusDotConfig } from '@/features/employees/constants/employeeStatus';
  import type { EmployeeFullProfile } from '@/features/employees/types/types';

  /**
   * EmployeeProfileHeader — En-tête du profil employé (avatar, infos, statut, onglets).
   * SRP : pur affichage. La navigation est déléguée à EmployeeProfileTabs,
   * l'édition à EmployeeEditSheet, les actions de cycle de vie à EmployeeLifecycleActions.
   */

  let {
    employee,
    activeTabId,
  }: {
    employee: EmployeeFullProfile;
    activeTabId: string;
  } = $props();

  // --- LOGIQUE DÉRIVÉE ---
  const fullName = $derived(buildFullName(employee));

  /**
   * Récupère la photo de profil directement depuis employee.profile_photo,
   * sinon se rabat sur la photo du compte utilisateur.
   */
  const profilePhoto = $derived(
    getMediaUrl(employee.profile_photo || employee.user?.photo || '')
  );

  const palette = $derived(getAvatarPalette(fullName || ''));

  const status = $derived(employee.current_status?.status);
  const statusDotConfig = $derived(getEmployeeStatusDotConfig(status));

  const uploadPhotoMutation = useUploadProfilePhotoMutation();

  function handlePhotoUpload(file: File) {
    $uploadPhotoMutation.mutate({ employeeId: employee.id, file });
  }

  let isEditDialogOpen = $state(false);
</script>


{#snippet InfoItem(icon: string, label: string)}
  <div class="flex items-center gap-2 text-[0.8rem] font-medium text-slate-500 bg-slate-50 px-3 py-0.5 rounded-full border border-slate-300/50">
    <AppIcon name={icon} size={16} class="text-slate-500" />
    {label}
  </div>
{/snippet}


<div class="bg-white border-b border-slate-100 sticky top-0 z-11 mb-0">
  <div class="container">
    <div class="flex flex-col md:flex-row md:items-end gap-6 py-3.5 px-4 pr-6">
      <div class="relative group">
        <div class="h-17 w-17 rounded-2xl bg-white shadow-none border border-slate-200 overflow-hidden group-hover:shadow-md transition-all duration-300">
          <AvatarGallery
            name={fullName || ''}
            src={profilePhoto}
            class="h-full w-full rounded-2xl"
            onUpload={handlePhotoUpload}
          >
            <Avatar class="h-full w-full rounded-2xl">
              <AvatarImage src={profilePhoto} alt={fullName} class="object-cover" />
              <AvatarFallback class={cn("font-bold text-[1.3rem] rounded-2xl", palette.bg, palette.text)}>
                {getInitials(employee.last_name || '', employee.middle_name || '', employee.first_name || '')}
              </AvatarFallback>
            </Avatar>
          </AvatarGallery>
        </div>
        <div class={cn('absolute -bottom-0.5 -right-1 h-3.5 w-3.5 rounded-full border border-white shadow-fine transition-colors duration-300', statusDotConfig.color)} title={statusDotConfig.title}></div>
      </div>

      <div class="flex-1 space-y-1">
        <div>
          <div class="flex items-center gap-3">
            <h2 class="text-[1.05rem] font-bold text-slate-900">{fullName}</h2>
            <Badge variant="outline" class="bg-slate-50 text-slate-500 border-slate-200 font-bold text-[0.65rem] uppercase tracking-widest hidden">
              ID: {employee?.id ? String(employee.id).split('-')[0] : '...'}
            </Badge>
          </div>
          <p class="text-slate-500 text-[0.84rem]">
            {employee.job_title || 'Poste non défini'}
            {#if employee.seniority_level}
              <span class="text-slate-400">•</span> {employee.seniority_level}
            {/if}
          </p>
        </div>

        <div class="flex flex-wrap gap-2">
          {@render InfoItem("circle-user", employee.matricule || 'N/A')}
          {@render InfoItem("mail", employee.email)}
        </div>
      </div>

      <div class="flex items-center gap-3 pb-1">
        <Button variant="outline" class="h-7.5" onclick={() => isEditDialogOpen = true}>
          <AppIcon name="edit" size={16} class="text-slate-700" />
          Modifier
        </Button>
        <EmployeeLifecycleActions {employee} />
      </div>
    </div>

    <div class="mt-0.5 px-3.5">
      <EmployeeProfileTabs
        employeeId={employee.id}
        activeTabId={activeTabId}
        counts={{
          education: employee.educations?.length || 0,
          documents: employee.documents?.length || 0,
        }}
      />
    </div>
  </div>
</div>


<EmployeeEditSheet
  {employee}
  bind:open={isEditDialogOpen}
  activeTabId={activeTabId}
  onOpenChange={(open) => isEditDialogOpen = open}
/>
