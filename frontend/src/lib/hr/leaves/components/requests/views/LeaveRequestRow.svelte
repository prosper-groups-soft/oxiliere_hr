<script lang="ts">
  import type { LeaveRequest } from '../../../types/types';
  import { LEAVE_TYPE_LABELS, LEAVE_TYPE_COLORS, CIRCUMSTANCE_TYPE_LABELS, CIRCUMSTANCE_TYPE_ICONS } from '../../../constants/leaves';
  import LeaveStatusBadge from '../../shared/LeaveStatusBadge.svelte';
  import AppIcon from '@/components/layout/elements/AppIcon.svelte';
  import { Button } from '@/components/ui/button';
  import { cn } from '@/utilities/common/css';
  import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
  import { getInitials } from "@/utilities/common/string";
  import { getAvatarPalette } from "@/utilities/common/func";
  import { getMediaUrl } from "@/utilities/common/media";
  import AvatarGallery from "@/components/shared/media/AvatarGallery.svelte";


  let { 
    request,
    onApprove,
    onReject,
    onEdit,
    onShowAttachment,
  }: { 
    request: LeaveRequest;
    onApprove?: (request: LeaveRequest) => void;
    onReject?: (request: LeaveRequest) => void;
    onEdit?: (request: LeaveRequest) => void;
    onShowAttachment?: (request: LeaveRequest) => void;
  } = $props();

  const typeColors = $derived(LEAVE_TYPE_COLORS[request.type]);
  const typeLabel = $derived(LEAVE_TYPE_LABELS[request.type]);
  const circumstanceLabel = $derived(
    request.circumstanceType ? CIRCUMSTANCE_TYPE_LABELS[request.circumstanceType as keyof typeof CIRCUMSTANCE_TYPE_LABELS] : null
  );
  const circumstanceIcon = $derived(
    request.circumstanceType ? CIRCUMSTANCE_TYPE_ICONS[request.circumstanceType as keyof typeof CIRCUMSTANCE_TYPE_ICONS] ?? 'ellipsis' : null
  );
  const palette = $derived(getAvatarPalette(request.employeeName));
  const profilePhoto = $derived(getMediaUrl(request.avatarUrl));

  const initials = $derived(
    request.firstName && request.lastName
      ? getInitials(request.firstName, request.lastName)
      : getInitials(...request.employeeName.split(' '))
  );

  function formatDate(dateStr: string) {
    return new Date(dateStr).toLocaleDateString('fr-FR', { day: 'numeric', month: 'short' });
  }

  function formatDateRange(start: string, end: string) {
    const s = formatDate(start);
    const e = formatDate(end);
    return s === e ? s : `${s} — ${e}`;
  }

  function formatDateFull(dateStr: string) {
    return new Date(dateStr).toLocaleDateString('fr-FR', { day: 'numeric', month: 'long', year: 'numeric' });
  }

  const approverDisplay = $derived.by(() => {
    const text = request.approver;
    if (!text) return null;
    const match = text.match(/^(\[[^\]]+\])\s*(.*)$/);
    if (!match) return { label: '', details: text };
    let label = match[1];
    let details = match[2];
    // Format the date in details: "Par dev@oxiliere.com le 2026-06-22" → "Par dev@oxiliere.com le 22 juin 2026"
    const dateMatch = details.match(/^(.*?\ble\s+)(\d{4}-\d{2}-\d{2})(\.?)$/);
    if (dateMatch) {
      const formatted = formatDateFull(dateMatch[2]);
      details = dateMatch[1] + formatted + (dateMatch[3] || '');
    }
    return { label, details };
  });
</script>


<div
  class="group grid grid-cols-[25%_15%_18%_12%_10%_20%] px-6 py-3 border-b border-slate-50 hover:bg-indigo-50/50 transition-colors cursor-pointer"
  onclick={() => request.status === 'pending' && onEdit?.(request)}
  role="none"
>
  <!-- Employee -->
  <div class="flex items-center gap-3 min-w-0">
    <AvatarGallery
      name={request.employeeName}
      src={profilePhoto}
      onUpload={() => {}}
      disableUploadHover={true}
      iconSize={16}
      iconStroke={2}
      class="h-10 w-10 rounded-full shadow-fine shrink-0"
    >
      <Avatar class="h-full w-full border border-slate-200">
        <AvatarImage src={profilePhoto} alt={request.employeeName} class="object-cover" />
        <AvatarFallback class={cn("text-[0.75rem] font-medium", palette.bg, palette.text)}>
          {initials}
        </AvatarFallback>
      </Avatar>
    </AvatarGallery>
    <div class="min-w-0">
      <p class="text-[0.875rem] font-semibold text-slate-800 truncate group-hover:text-primary">{request.employeeName}</p>
      <p class="text-[0.85rem] text-slate-500 truncate group-hover:text-primary">{request.jobTitle || request.orgUnit}</p>
    </div>
  </div>

  <!-- Type -->
  <div class="">
    <span class={cn(
      "inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[0.75rem] font-medium",
      typeColors.bg, typeColors.text
    )}>
      <span class={cn("h-1.5 w-1.5 rounded-full", typeColors.dot)}></span>
      {typeLabel}
    </span>
    {#if circumstanceLabel}
      <div class="flex items-center gap-1 mt-1 pl-1">
        <AppIcon name={circumstanceIcon!} size={12} class="text-amber-600 shrink-0" />
        <span class="text-[0.75rem] text-slate-500 truncate">{circumstanceLabel}</span>
      </div>
    {/if}
  </div>

  <!-- Dates -->
  <div class="">
    <p class="text-[0.875rem] text-slate-700 truncate">{formatDateRange(request.startDate, request.endDate)}</p>
    <p class="text-[0.85rem] text-slate-500">{parseInt(request.days as any)} jour{parseInt(request.days as any) > 1 ? 's' : ''}</p>
  </div>

  <!-- Reason + Attachment -->
  <div class="min-w-0 flex flex-col items-start gap-1.5">
    <p class="text-[0.85rem] text-slate-600 truncate flex items-center gap-1 w-full">
      {#if request.reason}
        <AppIcon name="quote" size={12} class="text-slate-400 shrink-0 -rotate-180" />
      {/if}
      <span class="text-[0.85rem]">{request.reason || '—'}</span>
    </p>
    {#if request.type === 'sick' && request.attachment}
      <button
        onclick={(ev) => { ev.stopPropagation(); onShowAttachment?.(request); }}
        class="shrink-0 p-1 rounded-md hover:bg-indigo-100 text-indigo-500 transition-colors cursor-pointer flex gap-1 text-[0.85rem] items-center justify-center"
        title="Voir le justificatif médical"
      >
        <AppIcon name="file" size={16} class="text-indigo-500" />
        Le jutificatif
      </button>
    {/if}
  </div>

  <!-- Status -->
  <div class="text-right">
    <LeaveStatusBadge status={request.status} />
  </div>

  <!-- Actions -->
  <div class="flex items-center justify-end gap-2 min-w-0">
    {#if request.status === 'pending'}
      <div class="flex items-center opacity-100 transition-opacity gap-1.5 shrink-0">
          <Button
            variant="outline"
            size="sm"
            onclick={() => onEdit?.(request)}
            class="px-1.5! h-7 border-slate-200 text-slate-500 hover:text-slate-700 hover:bg-slate-100 hover:border-slate-300 rounded-lg shadow-none transition-all cursor-pointer"
            title="Modifier la demande"
          >
            <AppIcon name="edit" size={16} />
          </Button>
          <Button
          variant="outline"
          size="sm"
          onclick={() => onApprove?.(request)}
          class="gap-1.5 px-2! h-7 border-emerald-200 text-[0.78rem] font-medium text-emerald-600 hover:text-white hover:bg-emerald-500 hover:border-emerald-500 rounded-lg shadow-none transition-all cursor-pointer"
        >
          <AppIcon name="check" size={15} />
          Approuver
        </Button>
        <Button
          variant="outline"
          size="sm"
          onclick={() => onReject?.(request)}
          class="gap-1.5 px-2! h-7 border-rose-200 text-[0.78rem] font-medium text-rose-500 hover:text-white hover:bg-rose-500 hover:border-rose-500 rounded-lg shadow-none transition-all cursor-pointer"
        >
          <AppIcon name="x" size={15} />
          Refuser
        </Button>
      </div>
    {:else if approverDisplay}
      <div class="flex flex-col items-end min-w-0">
        <span class="text-[0.84rem] font-bold tracking-wide"
          class:status={true}
          style:color={approverDisplay.label.startsWith('[APPROUVÉ]') ? '#059669' : approverDisplay.label.startsWith('[REJETÉ]') ? '#e11d48' : '#64748b'}
        >
          {approverDisplay.label}
        </span>
        <span class="text-[0.84rem] text-slate-400 max-w-full">{approverDisplay.details}</span>
      </div>
    {:else}
      <span class="text-[0.84rem] text-slate-400 font-medium">—</span>
    {/if}
  </div>
</div>

