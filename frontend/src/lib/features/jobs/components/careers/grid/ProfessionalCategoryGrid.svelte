<script lang="ts">
  import AppIcon from '@/components/layout/elements/AppIcon.svelte';
  import AnimateSpin from '@/components/layout/elements/AnimateSpin.svelte';
  import type { ProfessionalCategory } from '@/features/jobs/types/types';


  let {
    categories = [],
    isLoading = false,
  }: {
    categories?: ProfessionalCategory[];
    isLoading?: boolean;
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

  const echelonLabel = (echelon: number) => {
    const labels: Record<number, string> = {
      1: 'Entrée de classe',
      2: 'Progression intermédiaire',
      3: 'Phase avancée',
      4: 'Maturité de classe',
    };
    return labels[echelon] ?? `Échelon ${echelon}`;
  };

  const echelonDescription = (echelon: number) => {
    const descriptions: Record<number, string> = {
      1: 'Début de la classe, phase d’intégration et de validation des compétences de base.',
      2: 'Consolidation des acquis, autonomie en progression et responsabilités initiales.',
      3: 'Expertise affirmée avec un rôle plus autonome et des missions plus complexes.',
      4: 'Maturité complète de la classe, leadership technique et référence interne.',
    };
    return descriptions[echelon] ?? 'Position de l’échelon dans la classe professionnelle.';
  };

  const categoryFor = (classe: number, echelon: number) =>
    categories.find((c) => c.classe === classe && c.echelon === echelon) ?? null;

  const echelons = $derived(
    Array.from(new Set(categories.map((c) => c.echelon)))
      .sort((a, b) => a - b)
  );

  const activeCount = $derived(categories.filter((c) => c.is_active).length);

  const classApplications: Record<number, string> = {
    1: 'Personnel non qualifié',
    2: 'Formation de base',
    3: 'Qualification technique',
    4: 'Diplôme technique',
    5: 'BAC+2/3',
    6: 'BAC+4/5',
    7: 'Haute qualification',
  };

  const classApplication = (classe: number) => classApplications[classe] ?? 'Application inconnue';

</script>

<section class="rounded-0 border-none bg-white shadow-none overflow-auto">
  <div class="flex flex-col gap-4 border-b border-slate-100 px-6 py-5 sm:flex-row sm:items-center sm:justify-between">
    <div class="flex items-start gap-3 min-w-0">
      <div class="flex h-11 w-11 items-center justify-center rounded-2xl bg-indigo-50 text-indigo-700">
        <AppIcon name="layers" size={18} />
      </div>
      <div class="min-w-0">
        <p class="text-sm font-semibold text-slate-900">Classes & Échelons (grille des catégories professionnelles)</p>
        <p class="mt-1 text-sm text-slate-500">
          Grille légale RDC de 7 classes × 4 échelons. Référence RH pour la classification ; les salaires sont aujourd'hui définis par les contrats.
        </p>
      </div>
    </div>

    <div class="flex flex-wrap items-center gap-2 text-slate-500">
      <div class="flex items-center gap-2">
        <AppIcon name="layers" size={15} />
        <span class="text-[0.85rem]">
          {categories.length} catégories · {classes.length} classes · {activeCount} actifs
        </span>
      </div>
    </div>
  </div>

  {#if isLoading && categories.length === 0}
    <div class="py-10 px-6">
      <AnimateSpin text="Chargement de la grille" class="border-primary text-slate-500" />
    </div>
  {:else if categories.length === 0}
    <div class="py-10 px-6 text-center">
      <AppIcon name="layers" size={28} class="text-slate-300 mx-auto mb-2" strokeWidth={1.3} />
      <p class="text-[0.85rem] text-slate-500">
        Aucune catégorie professionnelle configurée. Cliquez sur « Réinitialiser » pour charger la grille légale.
      </p>
    </div>
  {:else}
    <div class="space-y-3 p-6 text-slate-500">
      <div class="flex items-start gap-2">
        <AppIcon name="info" size={14} class="mt-0.5" />
        <div>
          <p class="font-medium text-slate-700 text-[0.85rem]">
            Ce que représentent les classes et échelons
          </p>
          <p class="text-[0.85rem]">
            Il s'agit d'une grille de classification professionnelle conforme aux conventions collectives RDC.
            La classe indique le niveau de qualification ; l'échelon traduit la progression dans cette classe.
          </p>
        </div>
      </div>

      <div class="grid gap-4 md:grid-cols-2">
        <div class="rounded-xl bg-slate-50 border border-slate-100 p-4">
          <p class="text-[0.85rem] font-medium text-slate-800 mb-3">Classe / Libellé / Application</p>
          <div class="grid gap-3">
            {#each Object.entries(classApplications) as [num, app]}
              <div class="rounded-2xl border border-slate-100 bg-white p-3">
                <p class="text-[0.82rem] font-semibold text-slate-700">Classe {num}</p>
                <p class="mt-1 text-[0.82rem] text-slate-600">{classLabel(Number(num))}</p>
                <p class="mt-2 text-[0.78rem] text-slate-500">{app}</p>
              </div>
            {/each}
          </div>
        </div>

        <div class="rounded-xl bg-slate-50 border border-slate-100 p-4">
          <p class="text-[0.85rem] font-medium text-slate-800 mb-3">Échelons</p>
          <div class="grid gap-3">
            {#each echelons as echelon}
              <div class="rounded-2xl border border-slate-100 bg-white p-3">
                <p class="text-[0.82rem] font-semibold text-slate-700">Échelon {echelon}</p>
                <p class="mt-1 text-[0.82rem] text-slate-600">{echelonDescription(echelon)}</p>
              </div>
            {/each}
          </div>
        </div>
      </div>

      <div class="rounded-xl bg-slate-50 border border-slate-100 p-3 text-slate-600">
        <p class="text-[0.85rem] font-medium text-slate-800">Usage actuel</p>
        <ul class="list-disc pl-5 space-y-1 mt-1">
          <li class="text-[0.85rem]">La grille est une référence RH et un outil de classification des catégories.</li>
          <li class="text-[0.85rem]">Elle n'est pas utilisée pour le calcul automatique de la paie.</li>
          <li class="text-[0.85rem]">Le salaire est aujourd'hui déterminé par le contrat (<code class="text-[0.85rem]">contract.base_salary</code>).</li>
        </ul>
      </div>
      <p class="text-[0.85rem] text-slate-500">
        Pour que la classe et l'échelon pilotent le salaire, il faut associer une valeur de référence salariale à chaque ligne et adapter le calcul de paie.
      </p>
    </div>
  {/if}
</section>

