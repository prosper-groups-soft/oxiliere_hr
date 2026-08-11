<script lang="ts">
  import AppIcon from '@/components/layout/elements/AppIcon.svelte';
  import AnimateSpin from '@/components/layout/elements/AnimateSpin.svelte';
  import { Button } from '@/components/ui/button';
  import { Switch } from '@/components/ui/switch';
  import type { ProfessionalCategory } from '@/features/payroll/types/types';
  import SettingSection from '../SettingSection.svelte';
  import { notification } from '@/stores/notification.svelte';


  let {
    categories = [],
    isLoading = false,
    onToggle,
    onReset,
  }: {
    categories?: ProfessionalCategory[];
    isLoading?: boolean;
    onToggle?: (category: ProfessionalCategory, isActive: boolean) => Promise<void> | void;
    onReset?: () => Promise<void> | void;
  } = $props();

  const classes = $derived(
    Array.from(new Set(categories.map((c) => c.classe)))
      .sort((a, b) => a - b)
  );

  const classLabel = (classe: number) => {
    const labels: Record<number, string> = {
      1: 'Manœuvre ordinaire',
      2: 'Ouvrier spécialisé',
      3: 'Ouvrier qualifié / Agent de maîtrise',
      4: 'Agent de maîtrise supérieur / Technicien',
      5: 'Cadre subalterne',
      6: 'Cadre moyen',
      7: 'Cadre supérieur',
    };
    return labels[classe] ?? `Classe ${classe}`;
  };

  const categoryFor = (classe: number, echelon: number) =>
    categories.find((c) => c.classe === classe && c.echelon === echelon) ?? null;

  const echelons = $derived(
    Array.from(new Set(categories.map((c) => c.echelon)))
      .sort((a, b) => a - b)
  );

  const activeCount = $derived(categories.filter((c) => c.is_active).length);

  const requestReset = () => {
    notification.confirm({
      title: 'Réinitialiser la grille ?',
      message:
        'Toutes les classes et échelons seront réinitialisés aux valeurs légales de la grille (7 classes × 4 échelons). Vos modifications seront écrasées.',
      type: 'warning',
      yesText: 'Réinitialiser',
      noText: 'Annuler',
      onYes: () => onReset?.(),
    });
  };

  let togglingId = $state<string | null>(null);

  async function handleToggle(cat: ProfessionalCategory, active: boolean) {
    togglingId = cat.id;
    try {
      await onToggle?.(cat, active);
    } catch (e: any) {
      notification.toast.error(e?.message ?? "Impossible de mettre à jour la classe");
    } finally {
      togglingId = null;
    }
  }
</script>


<SettingSection
  icon="layers"
  title="Classes & Échelons (grille des catégories professionnelles)"
  description="Grille légale RDC de 7 classes × 4 échelons, applicable aux contrats et au calcul des salaires."
  iconClass="bg-indigo-50"
>
  <!-- Barre d'outils -->
  <div class="mb-4 flex flex-wrap items-center justify-between gap-2">
    <div class="flex items-center gap-2 text-[0.82rem] text-slate-500">
      <AppIcon name="layers" size={15} />
      <span class="text-[0.82rem]">
        {categories.length} postes · {classes.length} classes · {activeCount} actifs
      </span>
    </div>

    <Button
      size="sm"
      variant="outline"
      class="h-9 px-2.5 text-[0.82rem] text-slate-500 hover:text-rose-600 hover:border-rose-200"
      onclick={requestReset}
      disabled={isLoading}
    >
      <AppIcon name="rotate-ccw" size={15} />
      Réinitialiser
    </Button>
  </div>

  {#if isLoading && categories.length === 0}
    <div class="py-10">
      <AnimateSpin text="Chargement de la grille" class="border-primary text-slate-500" />
    </div>
  {:else if categories.length === 0}
    <div class="py-10 text-center">
      <AppIcon name="layers" size={28} class="text-slate-300 mx-auto mb-2" strokeWidth={1.3} />
      <p class="text-[0.85rem] text-slate-500">
        Aucune catégorie professionnelle configurée. Cliquez sur « Réinitialiser » pour charger la grille légale.
      </p>
    </div>
  {:else}
    <div class="overflow-x-auto rounded-xl border border-slate-100">
      <table class="w-full text-left">
        <thead class="bg-slate-50">
          <tr>
            <th class="px-3.5 py-2.5 text-[0.82rem] font-bold uppercase tracking-widest text-slate-500">
              Classe
            </th>
            {#each echelons as echelon}
              <th class="px-3.5 py-2.5 text-center text-[0.82rem] font-bold uppercase tracking-widest text-slate-500">
                Échelon {echelon}
              </th>
            {/each}
          </tr>
        </thead>
        <tbody class="divide-y divide-slate-50">
          {#each classes as classe}
            <tr class="hover:bg-slate-50/40 transition-colors">
              <td class="px-3.5 py-2.5">
                <div class="flex items-center gap-2">
                  <div class="w-7 h-7 rounded-lg bg-indigo-50 text-indigo-600 flex items-center justify-center font-bold text-[0.85rem] shrink-0">
                    {classe}
                  </div>
                  <div class="min-w-0">
                    <p class="text-[0.85rem] font-medium text-slate-700">{classLabel(classe)}</p>
                  </div>
                </div>
              </td>
              {#each echelons as echelon}
                {@const cat = categoryFor(classe, echelon)}
                <td class="px-3.5 py-2.5 text-center">
                  {#if cat}
                    <Switch
                      checked={cat.is_active}
                      onCheckedChange={(checked) => handleToggle(cat, checked)}
                      disabled={togglingId === cat.id}
                      aria-label={`Classe ${classe} - Échelon ${echelon}`}
                      class="mx-auto"
                    />
                  {:else}
                    <span class="text-[0.85rem] text-slate-300">—</span>
                  {/if}
                </td>
              {/each}
            </tr>
          {/each}
        </tbody>
      </table>
    </div>

    <p class="text-[0.85rem] text-slate-500 mt-3 flex items-center gap-1">
      <AppIcon name="info" size={12} />
      Chaque classe/échelon peut être désactivé : les contrats concernés basculent sur l'échelon inférieur actif.
    </p>
  {/if}
</SettingSection>

