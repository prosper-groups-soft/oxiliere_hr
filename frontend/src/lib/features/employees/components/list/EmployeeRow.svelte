<script lang="ts">
  import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import { cn } from "@/utils";

  let { employee } = $props();

  const statusDotColors: Record<string, string> = {
    "Actif"         : "bg-emerald-400",
    "En intégration": "bg-amber-400",
    "Suspendu"      : "bg-rose-400",
    "Terminé"       : "bg-slate-300"
  };

  function getInitials(name: string) {
    return name.split(' ').map(n => n[0]).join('').substring(0, 2).toUpperCase();
  }

  const avatarPalettes = [
    { bg: "bg-indigo-50", text: "text-indigo-600" },
    { bg: "bg-emerald-50", text: "text-emerald-600" },
    { bg: "bg-rose-50", text: "text-rose-600" },
    { bg: "bg-amber-50", text: "text-amber-600" },
    { bg: "bg-sky-50", text: "text-sky-600" },
    { bg: "bg-violet-50", text: "text-violet-600" },
    { bg: "bg-slate-100", text: "text-slate-600" }
  ];

  function getAvatarPalette(name: string) {
    let hash = 0;
    for (let i = 0; i < name.length; i++) {
      hash = name.charCodeAt(i) + ((hash << 5) - hash);
    }
    const index = Math.abs(hash) % avatarPalettes.length;
    return avatarPalettes[index];
  }

  const palette = $derived(getAvatarPalette(employee.name));
</script>


<div class="group relative flex items-center h-[60px] px-0 bg-white hover:bg-[#F9FAFB] border-b border-[#F3F4F6] transition-colors duration-150 cursor-pointer overflow-hidden">
  
  <!-- Column 1: Profile - 35% -->
  <div class="flex items-center min-w-0 w-[35%]">
    <div class="w-[120px] shrink-0 flex items-center gap-3">
      <div class="h-10 w-10 rounded-full border border-slate-100 overflow-hidden flex items-center justify-center bg-slate-50 shrink-0 relative shadow-[inset_0_1px_2px_rgba(0,0,0,0.02)]">
        <Avatar class="h-full w-full">
          <AvatarImage src={employee.avatarUrl} alt={employee.name} />
          <AvatarFallback class={cn("font-bold text-[11px]", palette.bg, palette.text)}>
            {getInitials(employee.name)}
          </AvatarFallback>
        </Avatar>
      </div>
    </div>
    <div class="flex flex-col min-w-0">
      <span class="font-semibold text-[13px] text-[#111] truncate leading-tight">{employee.name}</span>
      <span class="text-[11px] text-[#666] truncate mt-0.5">{employee.jobTitle}</span>
    </div>
  </div>


  <!-- Column 2: Department - 20% -->
  <div class="flex items-center min-w-0 w-[20%]">
    <span class="inline-flex items-center px-2 py-0.5 rounded-[8px] bg-[#F3F4F6] text-[#666] text-[11px] font-medium truncate">
      {employee.department}
    </span>
  </div>

  <!-- Column 3: Contract & Join Date - 15% -->
  <div class="flex flex-col min-w-0 w-[15%]">
    <span class="text-[12px] text-[#111] font-medium truncate">{employee.contractType}</span>
    <span class="text-[10px] text-[#999] truncate mt-0.5">Depuis {new Date(employee.joinDate).toLocaleDateString('fr-FR', { month: 'short', year: 'numeric' })}</span>
  </div>

  <!-- Column 4: Location - 15% -->
  <div class="flex items-center min-w-0 w-[15%] gap-2">
    <AppIcon name="location" size={13} class="text-slate-400 shrink-0" />
    <span class="text-[12px] text-[#666] truncate">{employee.location}</span>
  </div>

  <!-- Column 5: Status - 15% (Extreme right) -->
  <div class="flex items-center gap-2 min-w-0 w-[15%]">
    <span class={cn("h-2 w-2 rounded-full shrink-0", statusDotColors[employee.status] || "bg-gray-400")}></span>
    <span class="text-[12px] text-[#666] truncate">{employee.status}</span>
  </div>

  <!-- Floating Actions (Hover only) - Overlay effect to save space -->
  <div class="absolute right-0 top-0 bottom-0 flex items-center px-4 bg-gradient-to-l from-[#F9FAFB] via-[#F9FAFB] to-transparent opacity-0 group-hover:opacity-100 transition-opacity">
    <button class="p-1.5 hover:bg-slate-200/50 rounded-md transition-colors text-slate-500 bg-white border border-slate-100 shadow-sm">
      <AppIcon name="more-horizontal" size={16} />
    </button>
  </div>
</div>

