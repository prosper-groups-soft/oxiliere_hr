<script lang="ts">
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import { cn } from "@/utilities/common/css";
  import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
  import { getInitials } from "@/utilities/common/string";
  import { getAvatarPalette } from "@/utilities/common/func";

  let { employee } = $props();
  const palette = $derived(getAvatarPalette(employee.name));
</script>


<a
  href="/employees/{employee.id}"
  class="group block bg-white border border-slate-200 rounded-xl p-5 hover:shadow-md hover:border-blue-200 transition-all cursor-pointer relative overflow-hidden no-underline outline-none focus-visible:ring-2 focus-visible:ring-blue-500"
>
  <!-- Status indicator -->
  <div class="absolute top-3 right-3">
    <span class={cn(
      "h-2.5 w-2.5 rounded-full block",
      employee.status === "Actif" ? "bg-emerald-400" : "bg-amber-400"
    )}></span>
  </div>

  <div class="flex flex-col items-center text-center">
    <Avatar class="h-20 w-20 mb-4 ring-slate-50 group-hover:ring-blue-50 transition-all border shadow-none">
      <AvatarImage src={employee.avatarUrl} alt={employee.name} />
      <AvatarFallback class={cn("text-xl font-bold", palette.bg, palette.text)}>
        {getInitials(...employee.name.split(' '))}
      </AvatarFallback>
    </Avatar>

    <h3 class="font-bold text-slate-900 group-hover:text-blue-600 transition-colors">
      {employee.name}
    </h3>
    <p class="text-[0.85rem] text-slate-500 mb-3">{employee.jobTitle}</p>

    <div class="flex flex-wrap justify-center gap-2 mt-2">
      <span class="px-2 py-1 rounded-md bg-slate-100 text-slate-600 text-[0.7rem] font-medium">
        {employee.department}
      </span>
      <span class="px-2 py-1 rounded-md bg-blue-50 text-blue-600 text-[0.7rem] font-medium">
        {employee.contractType}
      </span>
    </div>
  </div>

  <div class="mt-5 pt-4 border-t border-slate-50 flex items-center justify-between text-slate-400">
    <div class="flex items-center gap-1.5 text-[0.75rem]">
      <AppIcon name="location" size={14} />
      <span class="text-slate-500 text-[0.82rem]">{employee.location}</span>
    </div>
    <div class="text-[0.82rem] text-slate-500">
      Depuis {new Date(employee.joinDate).getFullYear()}
    </div>
  </div>
</a>

