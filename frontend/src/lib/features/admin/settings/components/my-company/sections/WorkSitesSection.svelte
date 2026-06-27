<script lang="ts">
  import { Button } from "@/components/ui/button";
  import { Input } from "@/components/ui/input";
  import { Label } from "@/components/ui/label";
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import AnimateSpin from "@/components/layout/elements/AnimateSpin.svelte";
  import ValidationError from "@/components/ui/validation-error";
  import { preventNonNumeric } from "@/utilities/common/number";
  import DataPagination from "@/components/layout/elements/DataPagination.svelte";
  import { fade, slide } from 'svelte/transition';
  import { cubicOut } from 'svelte/easing';
  import { workSitesStore } from "../../../stores/workSitesStore.svelte";
  import { 
    useWorkSitesQuery, 
    useCreateWorkSiteMutation, 
    useUpdateWorkSiteMutation,
    useDeleteWorkSiteMutation 
  } from "../../../queries/workSitesQueries";
  import type { 
    WorkSite, 
    WorkSiteUpdate 
  } from "../../../types/workSites.types";
  import { notification } from '@/stores/notification.svelte';

  // TanStack Query hooks
  const query = useWorkSitesQuery(
    () => workSitesStore.currentPage, 
    () => workSitesStore.perPage
  );
  const createMutation = useCreateWorkSiteMutation();
  const updateMutation = useUpdateWorkSiteMutation();
  const deleteMutation = useDeleteWorkSiteMutation();

  // Connect store refresh to query refetch
  workSitesStore.setRefreshCallback(() => {
    $query.refetch();
  });

  // Store sync effects
  $effect(() => {
    if ($query.data) {
      workSitesStore.setWorkSites($query.data.results, $query.data.count);
    }
  });

  $effect(() => {
    workSitesStore.setLoading($query.isLoading);
  });

  $effect(() => {
    workSitesStore.setSaving($createMutation.isPending || $updateMutation.isPending || $deleteMutation.isPending);
  });

  // Derived state
  const workSites = $derived(workSitesStore.workSites);
  const isLoading = $derived(workSitesStore.isLoading);
  const isSaving = $derived(workSitesStore.isSaving);
  const showAddForm = $derived(workSitesStore.showAddForm);
  const currentPage = $derived(workSitesStore.currentPage);
  const perPage = $derived(workSitesStore.perPage);
  const totalCount = $derived(workSitesStore.totalCount);
  const totalPages = $derived(workSitesStore.totalPages);
  const currentCount = $derived(workSites.length);
  const formState = $derived(workSitesStore.formState);
  const validationErrors = $derived(workSitesStore.validationErrors);

  // Add form
  function toggleAddForm() {
    workSitesStore.toggleAddForm();
  }

  async function createWorkSite() {
    if (!workSitesStore.isFormValid()) {
      notification.toast.error('Veuillez corriger les erreurs du formulaire');
      return;
    }
    const data = workSitesStore.getFormData();
    $createMutation.mutate(data);
  }

  // Edit form state
  let editingSiteId = $state<string | null>(null);
  let editForm = $state<WorkSiteUpdate & { name: string }>({ name: '', latitude: undefined, longitude: undefined, allowed_radius: 100 });
  let editValidationErrors = $state<Record<string, string>>({});

  function validateEditForm(): boolean {
    const errors: Record<string, string> = {};
    if (!editForm.name?.trim()) errors.name = 'Le nom du site est requis';
    if (editForm.latitude === undefined || editForm.latitude === null) errors.latitude = 'La latitude est requise';
    if (editForm.longitude === undefined || editForm.longitude === null) errors.longitude = 'La longitude est requise';
    if (editForm.allowed_radius === undefined || editForm.allowed_radius < 10 || editForm.allowed_radius > 1000) {
      errors.allowed_radius = 'Le rayon doit être entre 10 et 1000 mètres';
    }
    editValidationErrors = errors;
    return Object.keys(errors).length === 0;
  }

  function startEdit(site: WorkSite) {
    editingSiteId = site.id;
    editForm = {
      name: site.name,
      latitude: site.latitude,
      longitude: site.longitude,
      allowed_radius: site.allowed_radius
    };
  }

  function cancelEdit() {
    editingSiteId = null;
    editForm = { name: '', latitude: undefined, longitude: undefined, allowed_radius: 100 };
  }

  async function saveEdit(siteId: string) {
    if (!validateEditForm()) return;
    $updateMutation.mutate({ siteId, data: editForm });
    editingSiteId = null;
    editValidationErrors = {};
  }

  // Delete
  async function deleteWorkSite(siteId: string) {
    notification.confirm({
      title: 'Supprimer le site ?',
      message: 'Cette action est irréversible. Les employés associés ne seront plus liés à ce site.',
      type: 'warning',
      yesText: 'Supprimer',
      noText: 'Annuler',
      onYes: () => $deleteMutation.mutate(siteId)
    });
  }

  // Pagination using store methods (with built-in refetch)
  function handlePageChange(page: number) {
    workSitesStore.goToPage(page);
  }

  function handlePerPageChange(size: number) {
    workSitesStore.changePerPage(size);
  }

  function handleNext() {
    workSitesStore.nextPage();
  }

  function handlePrev() {
    workSitesStore.prevPage();
  }

  // Geolocation
  let isGettingLocation = $state(false);

  function getCurrentLocation() {
    if (!navigator.geolocation) {
      notification.toast.error('La géolocalisation n\'est pas supportée par ce navigateur');
      return;
    }
    isGettingLocation = true;
    navigator.geolocation.getCurrentPosition(
      (position) => {
        workSitesStore.updateFormField('latitude', position.coords.latitude);
        workSitesStore.updateFormField('longitude', position.coords.longitude);
        notification.toast.success('Position détectée avec succès');
        isGettingLocation = false;
      },
      (error) => {
        isGettingLocation = false;
        const messages: Record<number, string> = {
          [error.PERMISSION_DENIED]: 'Accès à la localisation refusé.',
          [error.POSITION_UNAVAILABLE]: 'Position indisponible. Vérifiez votre GPS.',
          [error.TIMEOUT]: 'Délai dépassé pour obtenir la position.'
        };
        notification.toast.error(messages[error.code] || 'Erreur lors de la récupération de la position');
      },
      { enableHighAccuracy: true, timeout: 10000, maximumAge: 0 }
    );
  }
</script>


<div class="p-4 bg-white rounded-xl border border-slate-200 mx-6 mr-8">
  <div class="flex items-start gap-4">
    <div class="w-12 h-12 rounded-xl bg-emerald-50 flex items-center justify-center text-emerald-600 shrink-0">
      <AppIcon name="map-pin" size={24} />
    </div>
    <div class="flex-1">
      <!-- Header Snippet -->
      {@render Header()}
      
      <!-- Description -->
      <p class="text-[0.875rem] text-slate-500 mb-4">
        Gérez les emplacements physiques où vos employés travaillent. 
        Chaque site peut être configuré avec des coordonnées GPS pour la géolocalisation des pointages.
      </p>

      <!-- Add Form Snippet -->
      {#if showAddForm}
        {@render AddForm()}
      {/if}

      <!-- Sites List -->
      <div class="space-y-3">
        {#if isLoading}
          <div class="text-slate-400 h-90 flex items-center justify-center">
            <AnimateSpin text="" />
          </div>
        {:else if workSites.length === 0}
          <div class="text-center bg-slate-50 rounded-lg h-90 flex flex-col items-center justify-center">
            <AppIcon name="map-pin" size={32} class="text-slate-300 mx-auto mb-2" />
            <p class="text-[0.88rem] text-slate-500">Aucun site de travail configuré</p>
            <p class="text-[0.85rem] text-slate-400 mt-1">Ajoutez votre premier site pour permettre la géolocalisation</p>
          </div>
        {:else}
          <div class="space-y-3 h-90 overflow-y-auto">
            {#each workSites as site (site.id)}
              <div 
                class="p-3 bg-slate-50 rounded-lg"
                transition:fade={{ duration: 200, easing: cubicOut }}
              >
                {#if editingSiteId === site.id}
                  {@render EditForm(site)}
                {:else}
                  {@render SiteCard(site)}
                {/if}
              </div>
            {/each}
          </div>

          <!-- Pagination -->
          {#if totalCount > perPage}
            <div class="mt-4" transition:fade={{ duration: 200, easing: cubicOut }}>
              <DataPagination 
                currentCount={currentCount}
                totalCount={totalCount}
                currentPage={currentPage}
                totalPages={totalPages}
                perPage={perPage}
                onPageChange={handlePageChange}
                onPerPageChange={handlePerPageChange}
                onNext={handleNext}
                onPrev={handlePrev}
                unitLabel="sites"
              />
            </div>
          {/if}
        {/if}
      </div>
    </div>
  </div>
</div>


<!-- Snippet Definitions -->
{#snippet Header()}
  <div class="flex items-center justify-between mb-1">
    <h5 class="font-medium text-slate-900 text-[0.95rem]">Sites de travail</h5>
    <Button onclick={toggleAddForm} variant="outline" class="h-8 text-[0.875rem] shadow-fine">
      <AppIcon name={showAddForm ? "x" : "plus"} class={showAddForm ? "text-slate-300" : ""} size={16} />
      {showAddForm ? 'Annuler' : 'Nouveau site'}
    </Button>
  </div>
{/snippet}


{#snippet AddForm()}
  <div class="p-4 bg-slate-50 rounded-lg mb-4" transition:slide={{ duration: 300, easing: cubicOut }}>
    <h6 class="font-medium text-slate-800 text-[0.9rem] mb-3">Nouveau site de travail</h6>
    <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
      <div class="md:col-span-2">
        <Label class="text-[0.875rem]">Nom du site</Label>
        <Input
          value={formState.name}
          oninput={(e) => workSitesStore.updateFormField('name', e.currentTarget.value)}
          class="mt-1 shadow-fine"
          placeholder="Ex: Siège social Kinshasa"
        />
        <ValidationError errors={validationErrors} field="name" />
      </div>
      <div>
        <div class="flex items-center justify-between">
          <Label class="text-[0.875rem]">Latitude</Label>
          <Button
            type="button"
            variant="ghost"
            onclick={getCurrentLocation}
            disabled={isGettingLocation}
            class="h-6 px-2 py-0 text-[0.875rem] text-emerald-600 hover:text-emerald-700 hover:bg-emerald-50"
          >
            {#if isGettingLocation}
              <AnimateSpin text="" class="border-emerald-500 size-3" />
            {:else}
              <AppIcon name="map-pin" size={15} class="mr-1" />
            {/if}
            Ma position
          </Button>
        </div>
        <Input
          type="number"
          step="any"
          onkeydown={preventNonNumeric}
          value={formState.latitude ?? ''}
          oninput={(e) => workSitesStore.updateFormField('latitude', parseFloat(e.currentTarget.value) || null)}
          class="mt-1 shadow-fine"
          placeholder="-4.325"
        />
        <ValidationError errors={validationErrors} field="latitude" />
      </div>
      <div>
        <Label class="text-[0.875rem]">Longitude</Label>
        <Input
          type="number"
          step="any"
          onkeydown={preventNonNumeric}
          value={formState.longitude ?? ''}
          oninput={(e) => workSitesStore.updateFormField('longitude', parseFloat(e.currentTarget.value) || null)}
          class="mt-1 shadow-fine"
          placeholder="15.322"
        />
        <ValidationError errors={validationErrors} field="longitude" />
      </div>
      <div class="md:col-span-2">
        <Label class="text-[0.875rem]">Rayon autorisé (mètres)</Label>
        <Input
          type="number"
          onkeydown={preventNonNumeric}
          value={formState.allowed_radius}
          oninput={(e) => workSitesStore.updateFormField('allowed_radius', parseInt(e.currentTarget.value) || 100)}
          class="mt-1 shadow-fine"
          min={10}
          max={1000}
        />
        <ValidationError errors={validationErrors} field="allowed_radius" />
        <p class="text-[0.86rem] text-slate-400 mt-1">
          Distance maximale autorisée pour les pointages depuis ce site
        </p>
      </div>
    </div>
    <div class="flex justify-end gap-2 mt-4">
      <Button onclick={toggleAddForm} variant="outline" class="h-8">
        <AppIcon name="x" class="text-slate-300" size={16} />
        Annuler
      </Button>
      <Button 
        onclick={createWorkSite} 
        disabled={isSaving}
        class="h-8 bg-emerald-600 hover:bg-emerald-700 transition-all"
      >
        {#if isSaving}
          <AnimateSpin text="" class="border-white size-3" />
        {:else}
          <AppIcon name="check" size={16} />
        {/if}
        Créer le site
      </Button>
    </div>
  </div>
{/snippet}


{#snippet SiteCard(site: WorkSite)}
  <div class="flex items-center justify-between" transition:slide={{ duration: 200, easing: cubicOut }}>
    <div class="flex items-center gap-3">
      <div class="w-10 h-10 rounded-lg bg-emerald-100 flex items-center justify-center text-emerald-600">
        <AppIcon name="map-pin" size={20} />
      </div>
      <div>
        <div class="font-medium text-slate-800 text-[0.89rem]">{site.name}</div>
        <div class="text-[0.875rem] text-slate-500">
          Latitude: {typeof site.latitude === 'number' ? site.latitude.toFixed(4) : site.latitude}, 
          Longitude: {typeof site.longitude === 'number' ? site.longitude.toFixed(4) : site.longitude} · 
          Rayon autorisé (mètres): {site.allowed_radius}m · 
          {site.employees.length} employé{site.employees.length > 1 ? 's' : ''}
        </div>
      </div>
    </div>
    <div class="flex items-center gap-1">
      <Button 
        variant="ghost" 
        onclick={() => startEdit(site)}
        class="h-8 w-8 p-0 text-slate-500 hover:text-emerald-600 hover:bg-emerald-50"
      >
        <AppIcon name="edit" size={16} />
      </Button>
      <Button 
        variant="ghost" 
        onclick={() => deleteWorkSite(site.id)}
        class="h-8 w-8 p-0 text-red-500 hover:text-red-600 hover:bg-red-50"
      >
        <AppIcon name="trash-2" size={16} />
      </Button>
    </div>
  </div>
{/snippet}


{#snippet EditForm(site: WorkSite)}
  <div class="space-y-3" transition:slide={{ duration: 200, easing: cubicOut }}>
    <h6 class="font-medium text-slate-800 text-[0.875rem]">Modifier le site</h6>
    <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
      <div class="md:col-span-2">
        <Label>Nom du site</Label>
        <Input
          value={editForm.name}
          oninput={(e) => {
            editForm = { ...editForm, name: e.currentTarget.value };
            if (editValidationErrors.name) editValidationErrors = { ...editValidationErrors, name: '' };
          }}
          class="mt-1 shadow-fine"
        />
        <ValidationError errors={editValidationErrors} field="name" />
      </div>
      <div>
        <Label class="text-[0.83rem]">Latitude</Label>
        <Input
          type="number"
          step="any"
          onkeydown={preventNonNumeric}
          value={editForm.latitude ?? ''}
          oninput={(e) => {
            editForm = { ...editForm, latitude: parseFloat(e.currentTarget.value) || undefined };
            if (editValidationErrors.latitude) editValidationErrors = { ...editValidationErrors, latitude: '' };
          }}
          class="mt-1 shadow-fine"
        />
        <ValidationError errors={editValidationErrors} field="latitude" />
      </div>
      <div>
        <Label>Longitude</Label>
        <Input
          type="number"
          step="any"
          onkeydown={preventNonNumeric}
          value={editForm.longitude ?? ''}
          oninput={(e) => {
            editForm = { ...editForm, longitude: parseFloat(e.currentTarget.value) || undefined };
            if (editValidationErrors.longitude) editValidationErrors = { ...editValidationErrors, longitude: '' };
          }}
          class="mt-1 shadow-fine"
        />
        <ValidationError errors={editValidationErrors} field="longitude" />
      </div>
      <div class="md:col-span-2">
        <Label>Rayon autorisé (mètres)</Label>
        <Input
          type="number"
          onkeydown={preventNonNumeric}
          value={editForm.allowed_radius}
          oninput={(e) => {
            editForm = { ...editForm, allowed_radius: parseInt(e.currentTarget.value) || 100 };
            if (editValidationErrors.allowed_radius) editValidationErrors = { ...editValidationErrors, allowed_radius: '' };
          }}
          class="mt-1 shadow-fine"
          min={10}
          max={1000}
        />
        <ValidationError errors={editValidationErrors} field="allowed_radius" />
      </div>
    </div>
    <div class="flex justify-end gap-2">
      <Button onclick={cancelEdit} variant="outline" class="h-8 text-[0.83rem]">
        <AppIcon name="x" class="text-slate-300" size={16} />
        Annuler
      </Button>
      <Button 
        onclick={() => saveEdit(site.id)} 
        disabled={$updateMutation.isPending}
        class="h-8 bg-emerald-600 hover:bg-emerald-700 text-[0.83rem] transition-all"
      >
        {#if $updateMutation.isPending}
          <AnimateSpin text="" class="border-white size-3" />
        {:else}
          <AppIcon name="check" size={16} />
        {/if}
        Enregistrer
      </Button>
    </div>
  </div>
{/snippet}

