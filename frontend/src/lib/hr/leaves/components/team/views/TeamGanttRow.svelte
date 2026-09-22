<script lang="ts">
  import { LEAVE_TYPE_LABELS, LEAVE_TYPE_COLORS } from '../../../constants/leaves';
  import type { LeaveType } from '../../../types/types';
  import { cn } from '@/utilities/common/css';
  import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
  import { getInitials } from "@/utilities/common/string";
  import { getAvatarPalette } from "@/utilities/common/func";
  import { getMediaUrl } from "@/utilities/common/media";
  import AvatarGallery from "@/components/shared/media/AvatarGallery.svelte";
  import * as Tooltip from "@/components/ui/tooltip";
  import { Tooltip as TooltipPrimitive } from "bits-ui";
  import AppIcon from '@/components/layout/elements/AppIcon.svelte';
  import { getOrgUnitIcon } from '@/hr/jobs/constants/orgUnit.constants';


  interface Props {
    employee: {
      id: string;
      name: string;
      jobTitle?: string;
      orgUnit: string;
      orgUnitType?: string;
      avatarUrl?: string;
    };
    days: { iso: string; isWeekend: boolean }[];
    getLeaveForDay: (employeeId: string, dayIso: string) => { type: LeaveType; status: string } | null;
  }

  let { employee, days, getLeaveForDay }: Props = $props();

  const palette = $derived(getAvatarPalette(employee.name));
  const profilePhoto = $derived(getMediaUrl(employee.avatarUrl));

  const initials = $derived(
    getInitials(...employee.name.split(' '))
  );

  // Statistiques de congés du mois pour cet employé
  type LeaveStats = Record<LeaveType, { approved: number; pending: number }>;
  const leaveStats = $derived.by(() => {
    const stats: LeaveStats = {
      annual: { approved: 0, pending: 0 },
      sick: { approved: 0, pending: 0 },
      circumstantial: { approved: 0, pending: 0 },
      unpaid: { approved: 0, pending: 0 },
    };
    let totalPending = 0;

    for (const d of days) {
      const leave = getLeaveForDay(employee.id, d.iso);
      if (leave) {
        if (leave.status === 'pending') {
          stats[leave.type].pending += 1;
        } else {
          stats[leave.type].approved += 1;
        }
      }
    }

    return stats;
  });

  const hasLeave = $derived(
    Object.values(leaveStats).some(s => s.approved > 0 || s.pending > 0)
  );

  const totalDays = $derived(
    Object.values(leaveStats).reduce((acc, s) => acc + s.approved + s.pending, 0)
  );

  const totalPending = $derived(
    Object.values(leaveStats).reduce((acc, s) => acc + s.pending, 0)
  );
</script>


<div class="flex border-b border-slate-100 hover:bg-slate-50/30 transition-colors group">
  <!-- Employee Info (comme LeaveRequestRow) with rich tooltip -->
  <div class="w-52 px-4 py-2.5 bg-white border-r border-slate-100">
    <Tooltip.Root>
      <Tooltip.Trigger class="w-full text-left">
        <div class="flex items-start gap-2.5 cursor-pointer">
          <AvatarGallery
            name={employee.name}
            src={profilePhoto}
            onUpload={() => {}}
            disableUploadHover={true}
            iconSize={15}
            iconStroke={2}
            class="h-10 w-10 rounded-full shadow-fine shrink-0"
          >
            <Avatar class="h-full w-full border border-slate-200">
              <AvatarImage src={profilePhoto} alt={employee.name} class="object-cover" />
              <AvatarFallback class={cn("text-[0.85rem] font-bold uppercase", palette.bg, palette.text)}>
                {initials}
              </AvatarFallback>
            </Avatar>
          </AvatarGallery>
          <div class="flex flex-col gap-0.5">
            <span class="text-[0.8rem] font-semibold text-slate-800">{employee.name}</span>
            <span class="flex items-center gap-1 text-[0.8rem] text-slate-600">
            {employee.jobTitle || employee.orgUnit}
            </span>
          </div>
        </div>
      </Tooltip.Trigger>
      <Tooltip.Content side="right" collisionPadding={16} class="z-200">
        <div class="flex items-start gap-3 p-1 min-w-44">
          <AvatarGallery
            name={employee.name}
            src={profilePhoto}
            onUpload={() => {}}
            disableUploadHover={true}
            iconSize={15}
            iconStroke={2}
            class="h-11 w-11 rounded-full shadow-fine shrink-0"
          >
            <Avatar class="h-full w-full border border-slate-200">
              <AvatarImage src={profilePhoto} alt={employee.name} class="object-cover" />
              <AvatarFallback class={cn("text-[0.84rem] font-bold uppercase", palette.bg, palette.text)}>
                {initials}
              </AvatarFallback>
            </Avatar>
          </AvatarGallery>
          <div class="flex flex-col gap-0.5">
            <span class="text-[0.8rem] font-semibold text-white">
              {employee.name}
            </span>
            {#if employee.jobTitle}
              <span class="text-[0.8rem] text-slate-50">
                {employee.jobTitle}
              </span>
            {/if}
            <span class="flex items-center gap-1 text-[0.8rem] text-slate-50">
              <AppIcon name={getOrgUnitIcon(employee.orgUnitType ?? '')} size={16} class="shrink-0" />
              {employee.orgUnit}
            </span>
          </div>
        </div>
        <TooltipPrimitive.Arrow />
      </Tooltip.Content>
    </Tooltip.Root>
  </div>

  <!-- Day Cells with row-level tooltip -->
  <Tooltip.Root>
    <Tooltip.Trigger>
      <div class="flex flex-1" role="button" tabindex="0">
        {#each days as d (d.iso)}
          {@const leave = getLeaveForDay(employee.id, d.iso)}

          <div 
            class={cn(
              "flex-1 min-w-9 h-10 shrink-0 border-r border-slate-100 flex items-center justify-center",
              d.isWeekend ? "bg-slate-50/60" : "bg-white",
            )}
          >
            {#if leave}
              <div 
                class={cn(
                  "w-7 h-6 rounded-sm flex items-center justify-center",
                  leave.status === 'pending'
                    ? "bg-slate-100 border border-dashed border-slate-300"
                    : LEAVE_TYPE_COLORS[leave.type].bg
                )}
                title={`${LEAVE_TYPE_LABELS[leave.type]} (${leave.status === 'pending' ? 'En attente' : 'Approuvé'})`}
              >
                {#if leave.status !== 'pending'}
                  <div class={cn("h-1.5 w-1.5 rounded-full", LEAVE_TYPE_COLORS[leave.type].dot)}></div>
                {/if}
              </div>
            {/if}
          </div>
        {/each}
      </div>
    </Tooltip.Trigger>
    <Tooltip.Content side="bottom" collisionPadding={16} class="z-200">
      <div class="flex items-start gap-3 p-1 min-w-48">
        <AvatarGallery
          name={employee.name}
          src={profilePhoto}
          onUpload={() => {}}
          disableUploadHover={true}
          iconSize={15}
          iconStroke={2}
          class="h-10 w-10 rounded-full shadow-fine shrink-0"
        >
          <Avatar class="h-full w-full border border-slate-200">
            <AvatarImage src={profilePhoto} alt={employee.name} class="object-cover" />
            <AvatarFallback class={cn("text-[0.84rem] font-bold uppercase", palette.bg, palette.text)}>
              {initials}
            </AvatarFallback>
          </Avatar>
        </AvatarGallery>
        <div class="flex flex-col gap-1.5">
          <div class="flex flex-col">
            <span class="text-sm font-semibold text-white">{employee.name}</span>
            {#if employee.orgUnit}
              <span class="flex items-center gap-1 text-[0.8rem] text-slate-300">
                <AppIcon name={getOrgUnitIcon(employee.orgUnitType ?? '')} size={15} />
                {employee.orgUnit}
              </span>
            {/if}
          </div>

          {#if hasLeave}
            <div class="flex flex-col gap-1 pt-1 border-t border-white/10">
              {#each Object.entries(leaveStats) as [type, counts]}
                {@const total = counts.approved + counts.pending}
                {#if total > 0}
                  <div class="flex items-center gap-2">
                    <div class={cn("h-2 w-2 rounded-full shrink-0", LEAVE_TYPE_COLORS[type as LeaveType].dot)}></div>
                    <span class="text-[0.8rem] text-slate-50 flex-1">{LEAVE_TYPE_LABELS[type as LeaveType]}</span>
                    <span class="text-[0.8rem] font-medium text-white tabular-nums">
                      {total}j
                      {#if counts.pending > 0}
                        <span class="text-amber-300 text-[0.8rem]">({counts.pending} en att.)</span>
                      {/if}
                    </span>
                  </div>
                {/if}
              {/each}
              <div class="flex items-center gap-2 pt-1 border-t border-white/10">
                <span class="text-[0.8rem] text-slate-50 flex-1">Total</span>
                <span class="text-[0.8rem] font-semibold text-white tabular-nums">
                  {totalDays}j
                  {#if totalPending > 0}
                    <span class="text-amber-300 text-[0.8rem]">({totalPending} en att.)</span>
                  {/if}
                </span>
              </div>
            </div>
          {:else}
            <span class="flex gap-1 justify-start items-center text-[0.8rem] text-slate-200">
              <AppIcon name='circle-x' size={15} class="text-slate-200" />
              Aucun congé ce mois
            </span>
          {/if}
        </div>
      </div>
    </Tooltip.Content>
  </Tooltip.Root>
</div>

