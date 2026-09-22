<script lang="ts">
  import { Button } from "@/components/ui/button";
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import { fade, slide } from "svelte/transition";
  import { onboardingStore } from "../../../stores/onboarding.svelte";
  import { notification } from "@/stores/notification.svelte";
  import ConfirmAction from "@/components/shared/actions/ConfirmAction.svelte";

  interface Props {
    show: boolean;
    onClose: () => void;
    onRequest?: () => void;
    onCancel?: () => void;
  }

  let { show, onClose }: Props = $props();

  let archivedDrafts = $state<any[]>([]);
  let confirmingArchiveIndex = $state<number | null>(null);
  let confirmingRestoreIndex = $state<number | null>(null);
  let confirmingDeleteIndex = $state<number | null>(null);

  function formatDate(dateString: string) {
    return new Date(dateString).toLocaleDateString('fr-FR', {
      day: 'numeric',
      month: 'short',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  }

  function getStepLabel(stepId: string): string {
    const stepLabels: Record<string, string> = {
      'identity': 'Identité',
      'account': 'Compte & Accès',
      'contract': 'Contrat',
      'documents': 'Documents',
      'family': 'Famille'
    };
    return stepLabels[stepId] || stepId;
  }

  function archiveCurrentDraft() {
    onboardingStore.archiveDraft();
    archivedDrafts = onboardingStore.getArchivedDrafts();
    notification.toast.success("Brouillon archivé !");
    confirmingArchiveIndex = null; // Réinitialiser après action réussie
    onboardingStore.checkDraft(); // Mettre à jour l'état du brouillon
  }

  function restoreDraft(draft: any, index: number) {
    if (onboardingStore.restoreFromArchive(draft)) {
      notification.toast.success("Brouillon restauré avec succès !");
      onClose();
      confirmingRestoreIndex = null; // Réinitialiser après action réussie
      onboardingStore.checkDraft(); // Mettre à jour l'état du brouillon
    } else {
      notification.toast.error("Erreur lors de la restauration du brouillon.");
      confirmingRestoreIndex = null; // Réinitialiser même en cas d'erreur
      onboardingStore.checkDraft(); // Mettre à jour l'état du brouillon
    }
  }

  function deleteDraft(index: number) {
    if (onboardingStore.deleteFromArchive(index)) {
      archivedDrafts = onboardingStore.getArchivedDrafts();
      notification.toast.success("Brouillon supprimé.");
      confirmingDeleteIndex = null; // Réinitialiser après action réussie
      onboardingStore.checkDraft(); // Mettre à jour l'état du brouillon
    } else {
      notification.toast.error("Erreur lors de la suppression du brouillon.");
      confirmingDeleteIndex = null; // Réinitialiser même en cas d'erreur
      onboardingStore.checkDraft(); // Mettre à jour l'état du brouillon
    }
  }

  $effect(() => {
    if (show) {
      archivedDrafts = onboardingStore.getArchivedDrafts();
    }
  });
</script>

{#if show}
  <div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50" role="none" onclick={onClose}>
    <div 
      class="bg-white rounded-lg p-6 max-w-2xl w-full max-h-[80vh] overflow-hidden" 
      onclick={(e) => e.stopPropagation()} 
      role="none" 
      in:fade={{ duration: 250, delay: 30 }} 
      out:fade={{ duration: 200 }}
    >
      <div class="flex justify-between items-center mb-4" transition:slide={{ duration: 300, delay: 50 }}>
        <h2 class="text-xl font-semibold">Brouillons archivés</h2>
        <Button variant="outline" onclick={onClose}>
          <AppIcon name="x" size={17} />
        </Button>
      </div>

      <!-- Brouillon actif -->
      {#if onboardingStore.hasDraft}
        <div class="mb-6 p-4 py-3 bg-indigo-50 border border-indigo-200 rounded-lg" transition:fade={{ duration: 250, delay: 100 }}>
          <div class="flex justify-between items-start mb-3">
            <div class="w-[40%]">
              <h3 class="font-medium text-blue-900 mb-1 text-[0.9rem]">Brouillon actif</h3>
              <div class="text-indigo-700 space-y-1">
                <div class="flex justify-between">
                  <span class="text-sm">Nom :</span>
                  <span class="text-sm">{onboardingStore.draftMetadata?.employeeName || 'Nouveau employé'}</span>
                </div>
                <div class="flex justify-between">
                  <span class="text-sm">Dernière sauvegarde :</span>
                  <span class="text-sm">{onboardingStore.lastSaved || 'Jamais'}</span>
                </div>
                <div class="flex justify-between">
                  <span class="text-sm">Étape actuelle :</span>
                  <span class="text-sm">{getStepLabel(onboardingStore.currentStep)}</span>
                </div>
              </div>
            </div>
            <div class="flex gap-2">
              <ConfirmAction
                isConfirming={confirmingArchiveIndex === -1}
                onConfirm={archiveCurrentDraft}
                onRequest={() => confirmingArchiveIndex = -1}
                onCancel={() => confirmingArchiveIndex = null}
                variant="neutral"
                labels={{ action: "Archiver", confirm: "Archiver", cancel: "Annuler" }}
                icons={{ action: "archive", confirm: "archive", cancel: "x" }}
              />
            </div>
          </div>
        </div>
      {/if}

      {#if archivedDrafts.length === 0}
        <div class="text-center py-8 text-gray-500">
          <AppIcon name="archive" size={48} class="mx-auto mb-4 text-gray-300" />
          <p class="text-[0.89rem]">
            {onboardingStore.hasDraft ? 'Aucun brouillon archivé' : 'Aucun brouillon trouvé'}
          </p>
        </div>
      {:else}
        <div class="overflow-y-auto max-h-[70vh] px-2">
          {#each archivedDrafts as draft, index}
            <div class="border rounded-lg p-4 py-3 mb-3 hover:bg-indigo-50/30 transition-colors cursor-pointer">
              <div class="flex justify-between items-start">
                <div class="w-[40%]">
                  <div class="font-medium text-[0.9rem]">{draft.metadata.employeeName}</div>
                  <div class="text-gray-600 space-y-1">
                    <div class="flex justify-between">
                      <span class="text-sm">Statut :</span>
                      <span class="text-sm">{draft.metadata.status === 'submitted' ? 'Soumis' : 'Actif'}</span>
                    </div>
                    <div class="flex justify-between">
                      <span class="text-sm">Créé :</span>
                      <span class="text-sm">{formatDate(draft.metadata.createdAt)}</span>
                    </div>
                    <div class="flex justify-between">
                      <span class="text-sm">Archivé :</span>
                      <span class="text-sm">{formatDate(draft.archivedAt)}</span>
                    </div>
                    <div class="flex justify-between">
                      <span class="text-sm">Dernière étape :</span>
                      <span class="text-sm">{getStepLabel(draft.currentStep)}</span>
                    </div>
                  </div>
                </div>
                <div class="flex gap-2 ml-4">
                  <ConfirmAction
                    isConfirming={confirmingRestoreIndex === index}
                    onConfirm={() => restoreDraft(draft, index)}
                    onRequest={() => confirmingRestoreIndex = index}
                    onCancel={() => confirmingRestoreIndex = null}
                    variant="neutral"
                    labels={{ action: "Restaurer", confirm: "Restaurer", cancel: "Annuler" }}
                    icons={{ action: "refresh", confirm: "refresh", cancel: "x" }}
                  />
                  <ConfirmAction
                    isConfirming={confirmingDeleteIndex === index}
                    onConfirm={() => deleteDraft(index)}
                    onRequest={() => confirmingDeleteIndex = index}
                    onCancel={() => confirmingDeleteIndex = null}
                    variant="danger"
                    labels={{ action: "Supprimer", confirm: "Supprimer", cancel: "Annuler" }}
                    icons={{ action: "trash", confirm: "trash", cancel: "x" }}
                  />
                </div>
              </div>
            </div>
          {/each}
        </div>
      {/if}
    </div>
  </div>
{/if}
