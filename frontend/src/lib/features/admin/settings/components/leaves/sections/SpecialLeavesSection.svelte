<script lang="ts">
  import { Input } from "@/components/ui/input";
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import TooltipWrapper from "@/components/shared/containers/TooltipWrapper.svelte";
  import { leaveSettingsStore } from "../../../stores/leaveSettingsStore.svelte";
  import { preventNonNumeric } from "@/utilities/common/number";
  import { fade } from 'svelte/transition';
  import { cubicOut } from 'svelte/easing';


  const config = $derived(leaveSettingsStore.config);

  const leaveIcons: Record<string, string> = {
    heart: 'heart',
    baby: 'baby',
    'flower-2': 'star',
    stethoscope: 'activity',
    moving: 'truck',
    'file-plus': 'file-plus'
  };

  const leaveIconColors: Record<string, string> = {
    heart: 'text-rose-500',
    baby: 'text-sky-500',
    'flower-2': 'text-violet-500',
    stethoscope: 'text-emerald-500',
    moving: 'text-orange-500',
    'file-plus': 'text-slate-500'
  };
</script>


<div class="p-4 bg-white rounded-xl border border-slate-200 mx-6 mr-8">
  <h5 class="font-medium text-slate-900 mb-2 text-[0.94rem]">
    Congés de circonstances
  </h5>
  <p class="text-[0.875rem] text-slate-500 mb-4">
    Congés exceptionnels prévus par le Code du Travail RDC pour des événements personnels spécifiques
    (mariage, naissance, décès, déménagement, etc.). Ces congés sont non cumulables avec les congés annuels.
  </p>
  
  <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
    {#each config.specialLeaves as leave (leave.type)}
      {@const isEditing = leaveSettingsStore.editingLeaveType === leave.type}
      <div 
        class="flex items-center gap-3 p-3 bg-slate-50 rounded-lg cursor-pointer hover:bg-slate-100 transition-colors" 
        role="none" 
        onclick={() => leaveSettingsStore.startEditingLeave(leave.type)}
      >
        <div class="w-10 h-10 rounded-lg bg-white flex items-center justify-center shrink-0">
          <AppIcon 
            name={leaveIcons[leave.icon || '']} 
            size={20} 
            class={leaveIconColors[leave.icon || ''] || 'text-slate-600'} 
          />
        </div>
        <div class="flex-1 min-w-0">
          <div class="flex items-center gap-2">
            <div class="font-medium text-slate-900 text-[0.875rem]">{leave.label}</div>
            {#if leave.isPaid}
              <span class="text-[0.8rem] px-1.5 py-0.5 bg-green-100 text-green-700 rounded-full font-medium">Payé</span>
            {:else}
              <span class="text-[0.8rem] px-1.5 py-0.5 bg-slate-100 text-slate-600 rounded-full font-medium">Non payé</span>
            {/if}
          </div>
          <div class="text-[0.875rem] text-slate-600 truncate">{leave.description}</div>
        </div>
        
        {#if isEditing}
          <div 
            class="flex items-center gap-2" 
            role="none" 
            onclick={(e) => e.stopPropagation()}
            transition:fade={{ duration: 150, easing: cubicOut }}
          >
            <Input
              type="number"
              value={leaveSettingsStore.editForm.daysAllowed}
              onkeydown={preventNonNumeric}
              oninput={(e) => leaveSettingsStore.editForm = { ...leaveSettingsStore.editForm, daysAllowed: parseInt(e.currentTarget.value) || 0 }}
              class="w-16 text-center h-8 text-[0.875rem] shadow-fine"
              min={0}
              max={30}
            />
            <button 
              onclick={(e) => { e.stopPropagation(); leaveSettingsStore.saveLeaveEdit(); }} 
              class="w-7 h-7 rounded-md bg-green-100 text-green-600 flex items-center justify-center hover:bg-green-200 cursor-pointer"
            >
              <AppIcon name="check" size={16} />
            </button>
            <button 
              onclick={(e) => { e.stopPropagation(); leaveSettingsStore.cancelLeaveEdit(); }} 
              class="w-7 h-7 rounded-md bg-slate-200 text-slate-600 flex items-center justify-center hover:bg-slate-300 cursor-pointer"
            >
              <AppIcon name="x" size={16} />
            </button>
          </div>
        {:else}
          <div class="flex items-center gap-2">
            <div>
              <TooltipWrapper content="Jours accordés - Cliquez pour modifier">
                {#snippet children(props)}
                  <span {...props} class="text-[0.875rem] font-semibold text-slate-700 px-2 cursor-pointer hover:text-indigo-600">
                    {leave.daysAllowed} jr{leave.daysAllowed > 1 ? 's' : ''}
                  </span>
                {/snippet}
              </TooltipWrapper>
            </div>
            <button 
              onclick={(e) => { e.stopPropagation(); leaveSettingsStore.startEditingLeave(leave.type); }} 
              class="w-7 h-7 rounded-md hover:bg-slate-200 flex items-center justify-center text-slate-500 cursor-pointer"
            >
              <AppIcon name="edit" size={16} />
            </button>
          </div>
        {/if}
      </div>
    {/each}
  </div>
  
  <div class="mt-4 p-3 bg-slate-50 rounded-lg">
    <p class="text-[0.88rem] text-slate-500">
      <strong class="text-[0.88rem] text-slate-700 font-semibold">Note:</strong> Ces valeurs sont conformes aux articles 131 à 135 du Code du Travail de la RDC. 
      Les jours affichés sont les maximums légaux; l'employeur peut accorder moins selon sa politique interne.
    </p>
  </div>
</div>

