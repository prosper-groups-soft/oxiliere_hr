<script lang="ts">
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import { Button } from "@/components/ui/button";
  import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
  import { getInitials } from "@/utilities/common/string";
  import { getAvatarPalette } from "@/utilities/common/func";
  import { cn } from "@/utilities/common/css";
  import type { WorkPolicy, PolicyAssignment } from "../../../types/types";
  import type { Employee } from "@/features/employees/types/types";
  import * as DropdownMenu from "@/components/ui/dropdown-menu";
  import { formatDate } from "date-fns";
  import { buildFullName } from "@/utilities/common/employee.utils";
  import { getMediaUrl } from "@/utilities/common/media";
  import { getEmployeeStatusDotConfig } from "@/features/employees/constants/employeeStatus";
  import AvatarGallery from "@/components/shared/media/AvatarGallery.svelte";
  import { RECURRENCE_LABELS } from "../../../constants/attendance.constants";


  interface EmployeeWithAssignment extends Employee {
    baseAssignment?: PolicyAssignment;
    overrideAssignment?: PolicyAssignment;
    basePolicy?: WorkPolicy;
    overridePolicy?: WorkPolicy;
  }

  let { 
    employee,
    onRemove,
    onEdit,
    onViewDetail
  } = $props<{
    employee: EmployeeWithAssignment;
    onRemove?: (employee: EmployeeWithAssignment) => void;
    onEdit?: (employee: EmployeeWithAssignment) => void;
    onViewDetail?: (employee: EmployeeWithAssignment) => void;
  }>();

  const hasAssignment = $derived(!!employee.basePolicy);
  const fullName = $derived(buildFullName(employee) || employee.name || '');
  const profilePhoto = $derived(
    getMediaUrl(employee.profile_photo || employee.avatarUrl || employee.user?.photo)
  );
  const palette = $derived(getAvatarPalette(fullName || employee.name || ''));
  const initials = $derived(getInitials(employee.last_name ?? '', employee.middle_name ?? '', employee.first_name ?? ''));
  const statusDotConfig = $derived(getEmployeeStatusDotConfig(employee.current_status?.status));

  // Override recurrence count — pre-computed by backend
  const overrideRecurrenceCount = $derived<number | null | undefined>(
    employee.overrideAssignment?.recurrenceCount
  );
</script>


<div
  class="group flex flex-col rounded-lg border border-slate-200 bg-white overflow-hidden transition-all hover:border-slate-300 hover:shadow-sm group/card cursor-pointer"
  onclick={() => onEdit?.(employee)}
  role="none"
>
  <!-- Header: avatar gallery + name + job title + 3-dot menu -->
  <div class="flex items-center gap-2 px-3 pt-2.5 pb-1">
    <!-- Avatar with gallery + status dot -->
    <div class="relative shrink-0" role="none">
      <AvatarGallery
        name={fullName}
        src={profilePhoto}
        onUpload={() => {}}
        disableUploadHover={true}
        iconSize={12}
        iconStroke={2}
        class="h-11 w-11 rounded-full shadow-none"
      >
        <Avatar class="h-full w-full border border-slate-200 overflow-hidden rounded-full">
          <AvatarImage src={profilePhoto} alt={fullName} class="object-cover" />
          <AvatarFallback class={cn("text-[0.8rem] font-bold", palette.bg, palette.text)}>
            {initials}
          </AvatarFallback>
        </Avatar>
      </AvatarGallery>
      {#if statusDotConfig.color}
        <div
          class={cn("absolute bottom-0.5 -right-0.5 h-2.5 w-2.5 rounded-full border border-white shadow-fine", statusDotConfig.color)}
          title={statusDotConfig.title}
        ></div>
      {/if}
    </div>

    <!-- Name + job title -->
    <div class="flex-1 min-w-0">
      <div class="font-semibold text-[0.85rem] text-slate-900 leading-tight truncate group-hover:text-indigo-600 transition-colors">{fullName}</div>
      {#if employee.jobTitle}
        <div class="text-[0.84rem] text-slate-500 truncate leading-tight">{employee.jobTitle}</div>
      {/if}
    </div>

    <!-- 3-dot menu -->
    <DropdownMenu.Root>
      <DropdownMenu.Trigger asChild>
        <Button variant="ghost" size="icon" class="size-6 shrink-0">
          <AppIcon name="more-horizontal" size={16} class="text-slate-700" />
        </Button>
      </DropdownMenu.Trigger>
      <DropdownMenu.Content align="end" sideOffset={4} class="min-w-40 p-1 rounded-lg border border-slate-200 bg-white shadow-md z-50">
        <DropdownMenu.Item onclick={() => onEdit?.(employee)} class="flex items-center gap-2 px-3 py-1 rounded-md text-[0.8rem] text-slate-700 hover:bg-slate-50 cursor-pointer outline-none transition-colors">
          <AppIcon name="edit" size={16} class="text-slate-400" /> 
          Modifier
        </DropdownMenu.Item>
        <DropdownMenu.Item onclick={() => onViewDetail?.(employee)} class="flex items-center gap-2 px-3 py-1 rounded-md text-[0.8rem] text-slate-700 hover:bg-slate-50 cursor-pointer outline-none transition-colors">
          <AppIcon name="eye" size={16} class="text-slate-400" /> 
          Consulter
        </DropdownMenu.Item>
        <div class="h-px bg-slate-100 my-1"></div>
        <DropdownMenu.Item onclick={() => onRemove?.(employee)} class="flex items-center gap-2 px-3 py-1 rounded-md text-[0.8rem] text-red-600! hover:bg-red-50! cursor-pointer outline-none transition-colors">
          <AppIcon name="trash" size={16} class="text-red-500" />
          Supprimer
        </DropdownMenu.Item>
      </DropdownMenu.Content>
    </DropdownMenu.Root>
  </div>

  <!-- Content: policy badges -->
  <div class="px-3 pb-2.5 space-y-1.5">
    {#if hasAssignment}
      <!-- Base policy badge (blue) -->
      <div class="flex flex-col gap-0.5 px-2 py-1.5 rounded-md bg-blue-50 border border-blue-100">
        <div class="flex items-center justify-between min-w-0">
          <div class="flex items-center gap-1.5 min-w-0">
            <AppIcon name="briefcase" size={16} class="text-blue-600 shrink-0" />
            <span class="text-[0.85rem] font-medium text-blue-900 truncate">{employee.basePolicy!.name}</span>
            {#if employee.baseAssignment?.recurrence && employee.baseAssignment.recurrence !== 'NONE'}
              <span class="text-[0.65rem] font-medium text-blue-500 uppercase tracking-wide bg-blue-100 px-1 py-0.5 rounded shrink-0">
                {RECURRENCE_LABELS[employee.baseAssignment.recurrence]}
              </span>
            {/if}
          </div>
        </div>
        {#if employee.baseAssignment?.startDate}
          <div class="flex items-center text-[0.8rem] text-blue-500 font-medium">
            {formatDate(new Date(employee.baseAssignment.startDate), 'dd/MM/yy')}
            {#if employee.baseAssignment?.endDate}
              <span class="mx-1">→</span>
              {formatDate(new Date(employee.baseAssignment.endDate), 'dd/MM/yy')}
            {:else}
              <span class="mx-1">→</span>
              <span class="text-blue-400">∞</span>
            {/if}
          </div>
        {/if}
      </div>

      <!-- Override badge (amber) -->
      {#if employee.overridePolicy}
        <div class="flex flex-col gap-0.5 px-2 py-1.5 rounded-md bg-amber-50 border border-amber-100">
          <div class="flex items-center justify-between min-w-0">
            <div class="flex items-center gap-1.5 min-w-0">
              <AppIcon name="zap" size={16} class="text-amber-600 shrink-0" />
              <span class="text-[0.85rem] font-medium text-amber-900 truncate">{employee.overridePolicy.name}</span>
              {#if employee.overrideAssignment?.recurrence && employee.overrideAssignment.recurrence !== 'NONE'}
                <span class="text-[0.65rem] font-medium text-amber-600 uppercase tracking-wide bg-amber-100 px-1 py-0.5 rounded shrink-0">
                  {RECURRENCE_LABELS[employee.overrideAssignment.recurrence]}
                  {#if overrideRecurrenceCount}
                    <span class="text-[0.6rem]">×{overrideRecurrenceCount}</span>
                  {/if}
                </span>
              {/if}
            </div>
          </div>
          {#if employee.overrideAssignment?.startDate || employee.overrideAssignment?.endDate}
            <div class="flex items-center text-[0.8rem] text-amber-600 font-medium">
              {#if employee.overrideAssignment?.startDate}
                {formatDate(new Date(employee.overrideAssignment.startDate), 'dd/MM/yy')}
              {/if}
              {#if employee.overrideAssignment?.endDate}
                <span class="mx-1">→</span>
                {formatDate(new Date(employee.overrideAssignment.endDate), 'dd/MM/yy')}
              {:else if employee.overrideAssignment?.startDate}
                <span class="mx-1">→</span>
                <span class="text-amber-400">∞</span>
              {/if}
            </div>
          {/if}
        </div>
      {:else}
        <!-- No override indicator -->
        <div class="flex items-center gap-1.5 px-2 py-5 rounded-md border border-dashed border-amber-200 bg-amber-50/40">
          <AppIcon name="zap" size={14} class="text-amber-300 shrink-0" />
          <span class="text-[0.8rem] text-amber-400">Aucun remplacement</span>
        </div>
      {/if}
    {:else}
      <!-- Empty state: no policy assigned -->
      <div class="flex items-center justify-center px-2 py-2.5 rounded-md border border-dashed border-slate-200 bg-slate-50/50">
        <span class="text-[0.84rem] text-slate-400">Aucun modèle</span>
      </div>
    {/if}
  </div>
</div>

