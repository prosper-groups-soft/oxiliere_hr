<script lang="ts">
  import { onboardingStore } from "../../../stores/onboarding.svelte";
  import { Button } from "@/components/ui/button";
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import { 
    Card, 
    CardContent, 
    CardHeader, 
    CardTitle, 
    CardDescription 
  } from "@/components/ui/card";
  import { flip } from "svelte/animate";
  import { slide } from "svelte/transition";

  // Sub-components
  import EducationItem from "../education/EducationItem.svelte";
  import EducationForm from "../education/forms/EducationForm.svelte";


  // Form state
  let showAddForm = $state(false);
  let editingIndex = $state<number | null>(null);

  function handleAdd() {
    editingIndex = null;
    showAddForm = true;
  }

  function handleEdit(index: number) {
    editingIndex = index;
    showAddForm = true;
  }

  function handleCancel() {
    editingIndex = null;
    showAddForm = false;
  }

  const isEditing = $derived(editingIndex !== null);
</script>


<Card class="border-slate-200 shadow-none rounded-none border-0 p-0">
  <CardHeader class="px-0 pt-0 pb-0">
    <div class="flex items-center justify-between">
      <div class="flex items-center gap-3">
        <div class="p-2 bg-slate-50 rounded-lg border border-slate-100">
          <AppIcon name="graduation-cap" size={20} class="text-slate-500" />
        </div>
        <div>
          <CardTitle class="text-[0.98rem] font-bold text-slate-900 tracking-tight">
            Parcours académique
          </CardTitle>
          <CardDescription class="text-[0.835rem]">
            Ajoutez les diplômes et qualifications académiques.
          </CardDescription>
        </div>
      </div>
      <Button
        onclick={showAddForm ? handleCancel : handleAdd}
        variant="outline"
        size="sm"
        class="h-8 border-slate-200 bg-white hover:bg-slate-50 text-slate-800 text-[0.8rem] shadow-fine"
      >
        <AppIcon name={showAddForm ? "x" : "plus"} size={17} />
        {showAddForm ? "Annuler" : "Nouveau"}
      </Button>
    </div>
  </CardHeader>

  <CardContent class="px-0 py-0 space-y-2">
    {#if showAddForm}
      <div transition:slide={{ duration: 250 }}>
        <EducationForm
          onClose={handleCancel}
          initialData={isEditing ? onboardingStore.data.education.educations[editingIndex!] : null}
          editIndex={editingIndex}
        />
      </div>
    {/if}

    <div class="grid grid-cols-1 gap-3">
      {#each onboardingStore.data.education.educations as education, index (index)}
        <div animate:flip={{duration: 200}}>
          <EducationItem {education} {index} onEdit={handleEdit} />
        </div>
      {/each}

      {#if onboardingStore.data.education.educations.length === 0 && !showAddForm}
        <div class="py-10 flex flex-col items-center justify-center text-slate-600 bg-slate-50/40 rounded-xl border border-dashed border-slate-200 gap-2">
          <div class="w-12 h-12 bg-white rounded-full flex items-center justify-center border border-slate-100 shadow-sm mb-1">
            <AppIcon name="graduation-cap" size={24} strokeWidth={1.5} class="opacity-50" />
          </div>
          <p class="text-[0.83rem] font-medium">Aucune éducation ajoutée</p>
          <p class="text-[0.8rem] opacity-70">Ajoutez vos diplômes et qualifications.</p>
        </div>
      {/if}
    </div>
  </CardContent>
</Card>

