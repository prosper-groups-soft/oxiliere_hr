<script lang="ts">
  import { Button } from "@/components/ui/button";
  import AppIcon from "@/hr/components/layout/elements/AppIcon.svelte";
  import AnimateSpin from "@/hr/components/layout/elements/AnimateSpin.svelte";
  import DataPagination from "@/hr/components/layout/elements/DataPagination.svelte";
  import { fade, slide } from 'svelte/transition';
  import { cubicOut } from 'svelte/easing';
  import { workSitesStore } from "../../stores/workSitesStore.svelte";
  import { useWorkSitesQuery, useCreateWorkSiteMutation, useUpdateWorkSiteMutation, useDeleteWorkSiteMutation } from "../../queries/workSitesQueries";
  import type { WorkSite, WorkSiteUpdate } from "../../types/workSites.types";
  import { notification } from '@/hr/stores/notification.svelte';
  import { round6 } from "../../stores/workSitesStore.svelte";
  import WorkSiteForm from "./WorkSiteForm.svelte";


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

  // Add form — unified "top form" (create vs edit)
  // editingSiteId !== null  => edit mode (form en haut)
  // showAddForm             => create mode
  const isFormOpen = $derived(showAddForm || editingSiteId !== null);

  function toggleAddForm() {
    if (editingSiteId !== null) { cancelEdit(); return; }
    workSitesStore.toggleAddForm();
  }

  function closeForm() {
    if (editingSiteId !== null) cancelEdit();
    else if (showAddForm) workSitesStore.closeAddForm();
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
    if (editForm.allowed_radius === undefined || editForm.allowed_radius === null || isNaN(editForm.allowed_radius as number)) {
      errors.allowed_radius = 'Le rayon est requis';
    } else if ((editForm.allowed_radius as number) < 10 || (editForm.allowed_radius as number) > 1000) {
      errors.allowed_radius = 'Le rayon doit être entre 10 et 1000 mètres';
    }
    editValidationErrors = errors;
    return Object.keys(errors).length === 0;
  }

  function startEdit(site: WorkSite) {
    // bascule le form du haut en mode édition
    if (showAddForm) workSitesStore.closeAddForm();
    editingSiteId = site.id;
    editForm = {
      name: site.name,
      latitude: site.latitude,
      longitude: site.longitude,
      allowed_radius: site.allowed_radius
    };
    editValidationErrors = {};
  }

  function cancelEdit() {
    editingSiteId = null;
    editForm = { name: '', latitude: undefined, longitude: undefined, allowed_radius: 100 };
    editValidationErrors = {};
  }

  async function saveEdit() {
    if (editingSiteId === null) return;
    if (!validateEditForm()) return;
    const payload: WorkSiteUpdate & { name: string } = {
      name: editForm.name,
      latitude: round6(editForm.latitude) as number,
      longitude: round6(editForm.longitude) as number,
      allowed_radius: editForm.allowed_radius
    };
    $updateMutation.mutate({ siteId: editingSiteId, data: payload });
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
    const apply = (lat: number, lon: number) => {
      const rLat = round6(lat) as number;
      const rLon = round6(lon) as number;
      if (editingSiteId !== null) {
        editForm = { ...editForm, latitude: rLat, longitude: rLon } as any;
        if (editValidationErrors.latitude || editValidationErrors.longitude) {
          const { latitude: _a, longitude: _b, ...rest } = editValidationErrors;
          editValidationErrors = rest;
        }
      } else {
        workSitesStore.updateFormField('latitude', rLat);
        workSitesStore.updateFormField('longitude', rLon);
      }
    };
    isGettingLocation = true;
    navigator.geolocation.getCurrentPosition(
      (position) => {
        apply(position.coords.latitude, position.coords.longitude);
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
      <div class="flex items-center justify-between mb-1">
        <h5 class="font-medium text-slate-900 text-[0.95rem]">Sites de travail</h5>
        <Button onclick={toggleAddForm} variant="outline" class="h-8 text-[0.875rem] shadow-fine">
          <AppIcon name={isFormOpen ? "x" : "plus"} class={isFormOpen ? "text-slate-300" : ""} size={18} />
          {isFormOpen ? 'Annuler' : 'Nouveau site'}
        </Button>
      </div>
      
      <!-- Description -->
      <p class="text-[0.875rem] text-slate-500 mb-4">
        Gérez les emplacements physiques où vos employés travaillent. 
        Chaque site peut être configuré avec des coordonnées GPS pour la géolocalisation des pointages.
      </p>

      <!-- Single top form: create OR edit — 1 seul WorkSiteForm -->
      {#if isFormOpen}
        <div class="p-4 bg-slate-50 rounded-lg mb-4" transition:slide={{ duration: 300, easing: cubicOut }}>
          <h6 class="font-medium text-slate-800 text-[0.9rem] mb-3">
            {editingSiteId !== null ? 'Modifier le site' : 'Nouveau site de travail'}
          </h6>
          <WorkSiteForm
            values={editingSiteId !== null ? (editForm as any) : (formState as any)}
            errors={editingSiteId !== null ? editValidationErrors : validationErrors}
            isPending={editingSiteId !== null ? $updateMutation.isPending : isSaving}
            isGettingLocation={isGettingLocation}
            showGeoButton={true}
            submitLabel={editingSiteId !== null ? 'Enregistrer' : 'Créer le site'}
            onGetLocation={getCurrentLocation}
            onUpdate={(field, value) => {
              if (editingSiteId !== null) {
                editForm = { ...editForm, [field]: value === null ? undefined : value } as any;
                if (editValidationErrors[field]) editValidationErrors = { ...editValidationErrors, [field]: '' };
              } else {
                workSitesStore.updateFormField(field as any, value);
              }
            }}
            onSubmit={() => editingSiteId !== null ? saveEdit() : createWorkSite()}
            onCancel={closeForm}
          />
        </div>
      {/if}

      <!-- Sites List -->
      <div>
        {#if isLoading}
          <div class="grid grid-cols-1 gap-3">
            {#each Array(3) as _, i}
              <div class="rounded-xl border border-slate-200 bg-white p-4 animate-pulse">
                <div class="flex gap-3">
                  <div class="w-10 h-10 rounded-xl bg-slate-100 shrink-0"></div>
                  <div class="flex-1 space-y-2">
                    <div class="h-3.5 w-32 bg-slate-100 rounded"></div>
                    <div class="h-3 w-56 bg-slate-50 rounded"></div>
                  </div>
                </div>
                <div class="mt-3 grid grid-cols-3 gap-2">
                  <div class="h-[52px] bg-slate-50 rounded-lg border border-slate-100"></div>
                  <div class="h-[52px] bg-slate-50 rounded-lg border border-slate-100"></div>
                  <div class="h-[52px] bg-slate-50 rounded-lg border border-slate-100"></div>
                </div>
              </div>
            {/each}
          </div>
        {:else if workSites.length === 0}
          {@render EmptyState()}
        {:else}
          <div class="grid grid-cols-1 gap-3 max-h-88 overflow-y-auto custom-scrollbar pr-1 -mr-1">
            {#each workSites as site (site.id)}
              <div
                class="group relative rounded-xl border bg-white p-4 transition-all {editingSiteId === site.id ? 'border-amber-300 bg-amber-50/40 shadow-sm ring-1 ring-amber-200' : 'border-slate-200 hover:border-slate-300 hover:shadow-fine'}"
                transition:fade={{ duration: 180, easing: cubicOut }}
              >
                {@render SiteCard(site)}
              </div>
            {/each}
          </div>

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


{#snippet SiteCard(site: WorkSite)}
  <div class="flex items-start justify-between gap-3">
    <div class="flex gap-3 min-w-0">
      <div class="w-10 h-10 rounded-xl bg-linear-to-br from-emerald-500 to-teal-600 flex items-center justify-center text-white shadow-sm shrink-0">
        <AppIcon name="map-pin" size={18} color="white" />
      </div>
      <div class="min-w-0">
        <div class="flex items-center gap-2 flex-wrap">
          <h6 class="font-semibold text-slate-900 text-[0.92rem] leading-none truncate">{site.name}</h6>
          {#if editingSiteId === site.id}
            <span class="inline-flex items-center gap-1 rounded-full bg-amber-100 text-amber-700 border border-amber-200 px-2 py-0.5 text-[0.83rem] font-medium">
              <span class="w-1.5 h-1.5 rounded-full bg-amber-500 animate-pulse"></span>
              En édition
            </span>
          {/if}
        </div>
        <p class="mt-1 inline-flex items-center gap-1.5 text-[0.83rem] text-slate-500">
          <AppIcon name="users" size={18} class="text-slate-400" />
          {site.employees.length} employé{site.employees.length > 1 ? 's' : ''} assigné{site.employees.length > 1 ? 's' : ''}
          <span class="w-1 h-1 rounded-full bg-slate-300"></span>
          <a
            href="https://www.google.com/maps?q={site.latitude},{site.longitude}"
            target="_blank" rel="noopener"
            class="inline-flex items-center gap-1 text-emerald-600 hover:text-emerald-700 font-medium text-sm"
          >
            Voir carte <AppIcon name="external-link" size={18} />
          </a>
        </p>
      </div>
    </div>
    <div class="flex items-center gap-1 shrink-0">
      <Button
        variant="ghost"
        onclick={() => startEdit(site)}
        class="h-8 w-8 p-0 rounded-lg text-slate-400 hover:text-emerald-600 hover:bg-emerald-50 border border-transparent hover:border-emerald-100"
        title="Modifier"
      >
        <AppIcon name="edit" size={18} />
      </Button>
      <Button
        variant="ghost"
        onclick={() => deleteWorkSite(site.id)}
        class="h-8 w-8 p-0 rounded-lg text-red-400 hover:text-red-600 hover:bg-red-50 border border-transparent hover:border-red-100"
        title="Supprimer"
      >
        <AppIcon name="trash-2" size={18} />
      </Button>
    </div>
  </div>

  <div class="mt-3.5 grid grid-cols-3 gap-2">
    {@render StatBox("Latitude", site.latitude, "crosshair")}
    {@render StatBox("Longitude", site.longitude, "crosshair")}
    {@render StatBox("Rayon", site.allowed_radius, "ruler", "m")}
  </div>
{/snippet}


{#snippet StatBox(label: string, value: number, icon: string, suffix = "")}
  <div class="rounded-lg bg-slate-50 border border-slate-100 px-2.5 py-2.5">
    <div class="flex items-center gap-1.5 text-[0.83rem] font-semibold tracking-widest uppercase text-slate-400">
      <AppIcon name={icon} size={18} class="text-slate-400" />
      {label}
    </div>
    <div class="mt-1 font-mono text-[0.86rem] font-semibold text-slate-800 leading-none truncate" title="{value}{suffix}">
      {typeof value === 'number' ? (suffix ? `${value}${suffix}` : value.toFixed(6)) : value}
    </div>
  </div>
{/snippet}


{#snippet EmptyState()}
  <div class="rounded-xl border border-dashed border-slate-200 bg-slate-50/60 py-10 px-6 text-center">
    <div class="w-14 h-14 rounded-2xl bg-white border border-slate-200 shadow-fine flex items-center justify-center mx-auto text-slate-300">
      <AppIcon name="map-pin" size={26} />
    </div>
    <h6 class="mt-4 font-medium text-slate-800 text-[0.92rem]">Aucun site pour le moment</h6>
    <p class="mt-1 text-[0.84rem] text-slate-500 max-w-sm mx-auto leading-relaxed">Ajoutez votre premier site pour activer la géolocalisation des pointages et le contrôle de présence.</p>
    <Button onclick={toggleAddForm} class="mt-5 h-8 bg-emerald-600 hover:bg-emerald-700 text-white shadow-sm">
      <AppIcon name="plus" size={18} /> Nouveau site
    </Button>
  </div>
{/snippet}

