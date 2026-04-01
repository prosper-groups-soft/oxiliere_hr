<script lang="ts">
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import { cn } from "@/utilities/common/css";
  import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
  import * as DropdownMenu from "@/components/ui/dropdown-menu"; // Ajouté
  import { getInitials } from "@/utilities/common/string";
  import { getAvatarPalette } from "@/utilities/common/func";
  import { goto } from '$app/navigation';
  import AvatarGallery from "@/components/shared/media/AvatarGallery.svelte";

  let { employee } = $props();

  const statusDotColors: Record<string, string> = {
    "Actif": "bg-emerald-400",
    "En intégration": "bg-amber-400",
    "Suspendu": "bg-rose-400",
    "Terminé": "bg-slate-300"
  };

  const palette = $derived(getAvatarPalette(employee.name));

  function toEmployeeDetails() {
    goto(`/employees/${employee.id}`);
  }

  function handleAvatarUpload(file: File) {
    console.log(`Nouvel avatar pour ${employee.name}:`, file);
  }
</script>


<div 
  role="link"
  tabindex="0"
  onclick={toEmployeeDetails}
  onkeydown={(e) => e.key === 'Enter' && toEmployeeDetails()}
  class="group/row relative hover:bg-hover flex items-center h-16.5! shrink-0 px-0 border-b border-[#F3F4F6] transition-colors duration-150 cursor-pointer overflow-hidden"
>
  <div class="flex items-center min-w-0 w-[30%] pl-4"> 
    <div class="w-13 shrink-0 flex items-center">
      <div role="none" onclick={(e) => e.stopPropagation()}>
        <AvatarGallery 
          name={employee.name}
          src={employee.avatarUrl}
          onUpload={handleAvatarUpload}
          iconSize={16}
          iconStroke={2}
          class="h-12 w-12 rounded-full shadow-fine"
        >
          <Avatar class="h-full w-full border border-slate-300">
            <AvatarImage src={employee.avatarUrl} alt={employee.name} />
            <AvatarFallback class={cn("font-bold text-[0.83rem]", palette.bg, palette.text)}>
              {getInitials(...employee.name.split(' '))}
            </AvatarFallback>
          </Avatar>
        </AvatarGallery>
      </div>
    </div>
    <div class="flex flex-col min-w-0 ml-2"> 
      <span class="font-semibold text-[0.88rem] text-[#111] truncate leading-tight group-hover/row:text-primary transition-colors">
        {employee.name}
      </span>
      <span class="text-[0.833rem] text-slate-700 truncate mt-0.5">
        {employee.jobTitle}
      </span>
    </div>
  </div>

  <div class="flex items-center min-w-0 w-[20%]">
    <span class="inline-flex items-center px-2 py-0.5 rounded-lg bg-[#F3F4F6] text-[#555] text-[0.75rem] font-medium truncate">
      {employee.department}
    </span>
  </div>

  <div class="flex flex-col min-w-0 w-[15%]">
    <span class="text-[0.85rem] text-[#111] font-medium truncate">{employee.contractType}</span>
    <span class="text-[0.83rem] text-slate-600 truncate mt-0.5 text-nowrap">
        Depuis {new Date(employee.joinDate).toLocaleDateString('fr-FR', { month: 'short', year: 'numeric' })}
    </span>
  </div>
  
  <div class="flex items-center min-w-0 w-[15%] gap-2">
    <AppIcon name="location" size={19} class="text-slate-500 shrink-0" />
    <span class="text-[0.83rem] text-slate-700 truncate">{employee.location}</span>
  </div>

  <div class="flex items-center gap-2 min-w-0 w-[15%]">
    <span class={cn("h-2.5 w-2.5 rounded-full shrink-0", statusDotColors[employee.status] || "bg-gray-400")}></span>
    <span class="text-[0.83rem] text-slate-800 truncate">{employee.status}</span>
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
        <DropdownMenu.Group>          
          <DropdownMenu.Item onclick={toEmployeeDetails} class="cursor-pointer gap-2 py-2 text-[0.85rem]!">
            <AppIcon name="user" size={19} class="text-slate-500" />
            Détails du profil
          </DropdownMenu.Item>

          <DropdownMenu.Item class="cursor-pointer gap-2 py-2 text-[0.85rem]!">
            <AppIcon name="download" size={19} class="text-slate-500" />
            Exporter profile
          </DropdownMenu.Item>
          
          <DropdownMenu.Item class="cursor-pointer gap-2 py-2 text-[0.85rem]!">
            <AppIcon name="file-text" size={19} class="text-slate-500" />
            Générer contrat
          </DropdownMenu.Item>
        </DropdownMenu.Group>

        <DropdownMenu.Separator class="my-1 bg-slate-50" />

        <DropdownMenu.Group>
          <DropdownMenu.Item class="text-red-600 hover:text-red-700! hover:bg-red-50! cursor-pointer gap-2 py-2 text-[0.85rem]!">
            <AppIcon name="user-minus" size={19} class="text-red-600" />
            Lancer l'offboarding
          </DropdownMenu.Item>
        </DropdownMenu.Group>
      </DropdownMenu.Content>
    </DropdownMenu.Root>
  </div>
{/snippet}

