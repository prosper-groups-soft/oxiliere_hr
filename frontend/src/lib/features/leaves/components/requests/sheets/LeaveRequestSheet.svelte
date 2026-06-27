<script lang="ts">
  import { fade } from 'svelte/transition';
  import { LEAVE_TYPE_LABELS, LEAVE_TYPE_COLORS, CIRCUMSTANCE_TYPE_LABELS, CIRCUMSTANCE_TYPE_ICONS, CIRCUMSTANCE_TYPE_OPTIONS, BACKEND_CIRCUMSTANCE_TYPES } from '../../../constants/leaves';
  import type { LeaveType, CircumstanceType, WorkingDaysCount } from '../../../types/types';
  import type { BalanceSummary } from '../../../api/leaveRequests.endpoints';
  import { useCreateLeaveRequestMutation, useUpdateLeaveRequestMutation, leaveQueryKeys } from '../../../queries/leaveQueries';
  import { useQueryClient } from '@tanstack/svelte-query';
  import { leaveRequestsEndpoint } from '../../../api/leaveRequests.endpoints';
  import { Button } from '@/components/ui/button';
  import * as Sheet from '@/components/ui/sheet';
  import * as Select from '@/components/ui/select';
  import { Label } from '@/components/ui/label';
  import { Input } from '@/components/ui/input';
  import AppIcon from '@/components/layout/elements/AppIcon.svelte';
  import { cn } from '@/utilities/common/css';
  import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
  import { getInitials } from '@/utilities/common/string';
  import { getAvatarPalette } from '@/utilities/common/func';
  import { buildFullName } from '@/utilities/common/employee.utils';
  import { getMediaUrl } from '@/utilities/common/media';
  import { useAllEmployees } from '@/features/employees/queries/employeeQueries';
  import { useLeaveConfigQuery } from '../../../queries/leaveQueries';
  import { DEFAULT_LEAVE_CONFIG } from '@/features/admin/settings/types/leave.types';
  import ValidationError from '@/components/ui/validation-error';
  import AnimateSpin from '@/components/layout/elements/AnimateSpin.svelte';


  let {
    open = $bindable(false),
    request = $bindable(null),
  } = $props<{ open: boolean; request?: any }>();

  const isEditing = $derived(!!request);

  const createLeaveRequestMutation = useCreateLeaveRequestMutation();
  const updateLeaveRequestMutation = useUpdateLeaveRequestMutation();
  const queryClient = useQueryClient();

  // Employees query via the proper architecture layer (query → service → endpoint)
  // Seuls les employés avec un horaire (EmploymentScheme) sont pertinents pour les congés
  const employeesQuery = useAllEmployees(() => ({ has_scheme: true }));
  let allEmployees = $derived($employeesQuery.data || []);

  // Leave config query — single object combining policies + rules
  const leaveConfigQuery = useLeaveConfigQuery();
  let leaveConfig = $derived($leaveConfigQuery.data ?? DEFAULT_LEAVE_CONFIG);

  // Form state
  let selectedType = $state<string>('annual');
  let selectedCircumstanceType = $state<string>('');
  let startDate = $state('');
  let endDate = $state('');
  let reason = $state('');
  let selectedEmployeeStr = $state('');
  let isSaving = $state(false);
  let validationErrors = $state<Record<string, string>>({});
  let attachment = $state<File | null>(null);
  let submitError = $state<string | null>(null);

  // Working days preview state
  let workingDaysData = $state<WorkingDaysCount | null>(null);
  let isCalculating = $state(false);
  let previewError = $state<string | null>(null);
  let showDayDetail = $state(false);

  // Overlap detection (all leave types: warns if another leave overlaps)
  let overlapData = $state<{ hasOverlap: boolean; leaves: any[] } | null>(null);

  const selectedTypeObj = $derived(selectedType as LeaveType);

  // Derive employee display helpers (matching EmployeeRow pattern)
  const selectedEmployeeObj = $derived(
    selectedEmployeeStr
      ? allEmployees.find((e) => String(e.id) === selectedEmployeeStr)
      : undefined
  );

  // Debounce timer reference
  let debounceTimer: ReturnType<typeof setTimeout> | null = null;

  // Calculate days via API with debounce
  async function fetchWorkingDays() {
    if (!startDate || !endDate || !selectedEmployeeStr || !isValidUUID(selectedEmployeeStr)) {
      workingDaysData = null;
      return;
    }

    isCalculating = true;
    previewError = null;

    try {
      const result = await leaveRequestsEndpoint.countWorkingDays(
        selectedEmployeeStr,
        startDate,
        endDate
      );
      workingDaysData = result;
    } catch (err: any) {
      console.warn('[LeaveRequestSheet] Failed to fetch working days:', err);
      previewError = 'Impossible de calculer les jours ouvrés.';
      workingDaysData = null;
    } finally {
      isCalculating = false;
    }
  }

  function scheduleWorkingDaysFetch() {
    if (debounceTimer) clearTimeout(debounceTimer);
    if (!startDate || !endDate) {
      workingDaysData = null;
      return;
    }
    debounceTimer = setTimeout(() => {
      fetchWorkingDays();
    }, 300);
  }

  // Reactive triggers for debounced fetch
  $effect(() => {
    // Accessing these makes the effect reactive to changes
    const _emp = selectedEmployeeStr;
    const _start = startDate;
    const _end = endDate;
    scheduleWorkingDaysFetch();
  });

  // When startDate changes, ensure endDate doesn't fall before it
  $effect(() => {
    if (startDate && endDate && endDate < startDate) {
      endDate = startDate;
    }
  });

  // Helper: check if employee string is a valid UUID
  function isValidUUID(str: string): boolean {
    return /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i.test(str);
  }

  // Derive if employee has no schedule (all day details are 'no_scheme')
  const hasNoSchedule = $derived(
    !!selectedEmployeeStr && !!startDate && !!endDate &&
    workingDaysData !== null && !isCalculating &&
    workingDaysData.dayDetails.length > 0 &&
    workingDaysData.dayDetails.every(d => d.reason === 'no_scheme')
  );

  // Fallback naive calculation (used when API fails)
  const fallbackDays = $derived.by(() => {
    if (!startDate || !endDate) return 0;
    const start = new Date(startDate);
    const end = new Date(endDate);
    const diffTime = Math.abs(end.getTime() - start.getTime());
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24)) + 1;
    return diffDays;
  });

  // Display days: prefer API result, fallback to naive
  const displayDays = $derived(workingDaysData?.workingDays ?? fallbackDays);
  const displayCalendarDays = $derived(workingDaysData?.calendarDays ?? fallbackDays);
  const isAnnualLeave = $derived(selectedType === 'annual');
  const isCircumstantial = $derived(selectedType === 'circumstantial');
  const requiresAttachment = $derived(
    selectedType === 'sick' ||
    (isCircumstantial && selectedCircumstanceType === 'CHILD_HOSPITALIZATION')
  );

  // Sub-type circonstanciel sélectionné (objet)
  const selectedSpecialLeave = $derived(
	isCircumstantial && selectedCircumstanceType
		? leaveConfig.specialLeaves.find(sl => sl.type === selectedCircumstanceType)
		: undefined
  );

  // Validate against leave settings
  const settingsWarnings = $derived.by((): string[] => {
    const warnings: string[] = [];
    if (!startDate || !endDate) return warnings;

    if (selectedType === 'annual') {
      // 1. Max consecutive days check
      const maxCons = leaveConfig.maxConsecutiveDays;
      if (maxCons > 0 && displayDays > maxCons) {
        warnings.push(`Le maximum de jours consécutifs autorisé pour un congé annuel est de ${maxCons} jours (actuel: ${displayDays}). Veuillez réduire la période.`);
      }

      // 2. Annual leave days limit check
      const annualMax = leaveConfig.annualLeaveDays;
      if (displayDays > annualMax) {
        warnings.push(`Le nombre maximum de jours de congé annuel est de ${annualMax} jours (actuel: ${displayDays}). Veuillez réduire la période.`);
      }

      // 3. Balance check vs annual allocation
      if (currentBalance && displayDays > currentBalance.available) {
        warnings.push(`Votre solde disponible est de ${currentBalance.available} jours. Cette demande dépasse votre solde de ${displayDays - currentBalance.available} jours.`);
      }

      // 4. Notice period check
      const noticePeriod = leaveConfig.noticePeriodDays;
      if (noticePeriod > 0) {
        const today = new Date();
        today.setHours(0, 0, 0, 0);
        const start = new Date(startDate + 'T00:00:00');
        const daysDiff = Math.ceil((start.getTime() - today.getTime()) / (1000 * 60 * 60 * 24));
        if (daysDiff < noticePeriod) {
          warnings.push(`Le délai de préavis est de ${noticePeriod} jours (actuel: ${daysDiff}j).`);
        }
      }
    }

    if (selectedType === 'circumstantial') {
      const specialLeaves = leaveConfig.specialLeaves;

      // Si un sous-type spécifique est sélectionné, on utilise sa valeur
      if (selectedCircumstanceType) {
        const sl = specialLeaves.find(s => s.type === selectedCircumstanceType);
        if (sl && sl.daysAllowed > 0 && displayDays > sl.daysAllowed) {
          warnings.push(`Le maximum pour « ${sl.label} » est de ${sl.daysAllowed} jours (actuel: ${displayDays}).`);
        }
      } else if (specialLeaves.length > 0) {
        // Fallback: affiche un avertissement générique
        const maxAllowed = Math.max(...specialLeaves.map(sl => sl.daysAllowed));
        if (displayDays > maxAllowed) {
          warnings.push(`Veuillez sélectionner un type de circonstance. Le maximum autorisé est de ${maxAllowed} jours.`);
        }
      }
    }

    return warnings;
  });

  /** Vrai si une ou plusieurs limites sont violées (bloque la soumission) */
  const hasBlockingViolation = $derived(
	(settingsWarnings.length > 0 &&
	  !!startDate && !!endDate && displayDays > 0) ||
	(requiresAttachment && !attachment && !(isEditing && request?.attachment)) ||
	!!submitError
  );

  /** Message affiché dans le badge du bouton Soumettre quand bloqué */
  const submissionBlockReason = $derived.by((): string | null => {
	if (!hasBlockingViolation) return null;
	if (requiresAttachment && !attachment && !(isEditing && request?.attachment)) {
	  return 'Le justificatif est requis';
	}
	if (selectedType === 'annual') {
	  return 'Corrigez les avertissements ci-dessus avant de soumettre';
	}
	if (selectedType === 'circumstantial') {
	  return 'La période dépasse les limites autorisées';
	}
	return 'Veuillez corriger les erreurs';
  });

  // Validate
  function clearValidationError(field: string) {
    validationErrors = { ...validationErrors, [field]: '' };
  }

  function validateForm(): boolean {
    const errors: Record<string, string> = {};
    if (!startDate) errors.startDate = 'La date de début est requise';
    if (!endDate) errors.endDate = 'La date de fin est requise';
    if (startDate && endDate && endDate < startDate) errors.endDate = 'La date de fin doit être postérieure à la date de début';
    if (!reason.trim()) errors.reason = 'Le motif est requis';
    if (startDate && endDate && displayDays <= 0) errors.dates = 'La période est invalide';
    if (isCircumstantial && !selectedCircumstanceType) errors.circumstanceType = 'Veuillez sélectionner un type de circonstance';
    if (settingsWarnings.length > 0) errors.settings = settingsWarnings.join(' ');
    if (requiresAttachment && !attachment && !(isEditing && request?.attachment)) errors.attachment = 'Le justificatif est requis pour ce type de congé';
    validationErrors = errors;
    return Object.keys(errors).length === 0;
  }

  // Get real employee balance from DB via fetch on employee change
  let balanceData = $state<BalanceSummary | null>(null);
  let balanceLoading = $state(false);

  // Fetch balance reactively when employee changes
  $effect(() => {
    const empId = selectedEmployeeStr;
    if (!empId || !isValidUUID(empId)) {
      balanceData = null;
      return;
    }
    balanceLoading = true;
    leaveRequestsEndpoint.getBalanceSummary(empId)
      .then((data) => {
        balanceData = data;
      })
      .catch(() => {
        balanceData = null;
      })
      .finally(() => {
        balanceLoading = false;
      });
  });

  const currentBalance = $derived(balanceData);

  // Fetch overlapping leaves for current employee/dates/type
  let overlapLoading = $state(false);
  $effect(() => {
    const empId = selectedEmployeeStr;
    const start = startDate;
    const end = endDate;
    const leaveType = selectedType;
    const sheetOpen = open;
    const editing = isEditing; // Skip overlap check in edit mode

    if (!empId || !isValidUUID(empId) || !start || !end || !sheetOpen || editing) {
      overlapData = null;
      return;
    }

    // Pour les congés maladie, on exclut les autres catégories (un employé peut
    // tomber malade pendant ses vacances). Pour les autres types, on vérifie tout.
    const excludedCategories = leaveType === 'sick'
      ? 'ANNUAL,CIRCUMSTANCE,UNPAID'
      : undefined;

    overlapLoading = true;
    leaveRequestsEndpoint.checkOverlap(empId, start, end, excludedCategories)
      .then((data) => {
        overlapData = data;
      })
      .catch(() => {
        overlapData = null;
      })
      .finally(() => {
        overlapLoading = false;
      });
  });

  async function handleSubmit() {
    if (!validateForm()) return;

    if (isEditing && request) {
      // Mode édition
      isSaving = true;
      try {
        const payload: any = {
          requestId: request.id,
          type: selectedType as LeaveType,
          startDate,
          endDate,
          reason: reason.trim(),
        };
        if (isCircumstantial && selectedCircumstanceType) {
          const backendType = BACKEND_CIRCUMSTANCE_TYPES[selectedCircumstanceType as CircumstanceType];
          if (backendType) {
            payload.circumstanceType = backendType;
          }
        }
        if (attachment) {
          payload.attachment = attachment;
        }

        await $updateLeaveRequestMutation.mutateAsync(payload);
        resetForm();
        request = null;
        open = false;
      } catch (err: unknown) {
        const axiosErr = err as { response?: { data?: { detail?: string } } };
        const message = axiosErr?.response?.data?.detail
          || (err instanceof Error ? err.message : String(err));
        submitError = typeof message === 'string' ? message : String(message);
      } finally {
        isSaving = false;
      }
      return;
    }

    const emp = selectedEmployeeStr
      ? allEmployees.find((e) => String(e.id) === selectedEmployeeStr)
      : undefined;
    if (!emp || !emp.id || !isValidUUID(String(emp.id))) return;

    isSaving = true;
    try {
      // Préparer le payload avec le circumstanceType si circonstanciel
      const payload: Parameters<typeof $createLeaveRequestMutation.mutateAsync>[0] = {
        employeeId: String(emp.id),
        type: selectedType as LeaveType,
        startDate,
        endDate,
        reason: reason.trim(),
      };
      if (isCircumstantial && selectedCircumstanceType) {
        const backendType = BACKEND_CIRCUMSTANCE_TYPES[selectedCircumstanceType as CircumstanceType];
        if (backendType) {
          payload.circumstanceType = backendType;
        }
      }
      if (attachment) {
        payload.attachment = attachment;
      }

      await $createLeaveRequestMutation.mutateAsync(payload);

      await queryClient.invalidateQueries({ queryKey: leaveQueryKeys.requests() });

      resetForm();
      open = false;
    } catch (err: unknown) {
      // Extract the real backend message from the response detail
      const axiosErr = err as { response?: { data?: { detail?: string } } };
      const message = axiosErr?.response?.data?.detail
        || (err instanceof Error ? err.message : String(err));

      if (typeof message === 'string' && message.toLowerCase().includes('overlap')) {
        submitError = 'Cette période chevauche une demande de congé déjà soumise. Veuillez choisir une autre période.';
      } else {
        submitError = typeof message === 'string' ? message : String(message);
      }
    } finally {
      isSaving = false;
    }
  }

  // Clear submit error when employee or dates change
  $effect(() => {
    const _ = selectedEmployeeStr;
    const _2 = startDate;
    const _3 = endDate;
    submitError = null;
  });

  function resetForm() {
    selectedType = 'annual';
    selectedCircumstanceType = '';
    startDate = '';
    endDate = '';
    reason = '';
    selectedEmployeeStr = allEmployees[0]?.id.toString() || '';
    validationErrors = {};
    workingDaysData = null;
    showDayDetail = false;
    attachment = null;
    submitError = null;
    overlapData = null;
  }

  // Set default dates respecting notice period when opening
  // Pre-fill form when editing an existing request
  $effect(() => {
    if (open && request) {
      // Édition — pré-remplir depuis la demande existante
      const r = request;
      selectedType = r.type;
      selectedCircumstanceType = r.circumstanceType || '';
      startDate = r.startDate;
      endDate = r.endDate;
      reason = r.reason || '';
      selectedEmployeeStr = r.employeeId;
      validationErrors = {};
      submitError = null;
      overlapData = null;
      attachment = null;
    } else if (open && !request) {
      // Nouvelle demande
      validationErrors = {};

      // Refetch leave config to pickup latest changes (limits, rules, etc.)
      queryClient.invalidateQueries({ queryKey: leaveQueryKeys.leaveConfig() });

      if (!startDate) {
        const today = new Date();
        if (selectedType === 'annual' && leaveConfig.noticePeriodDays > 0) {
          const defaultStart = new Date();
          defaultStart.setDate(defaultStart.getDate() + leaveConfig.noticePeriodDays);
          const startStr = defaultStart.toISOString().split('T')[0];
          startDate = startStr;
          endDate = startStr;
        } else {
          // Maladie, circonstanciel → aujourd'hui
          const startStr = today.toISOString().split('T')[0];
          startDate = startStr;
          endDate = startStr;
        }
      }
    }
  });

  // Map day reason to CSS class
  function getDayReasonClass(reason: string): string {
    const classes: Record<string, string> = {
      'working': 'day-working',
      'public_holiday': 'day-holiday',
      'company_closure': 'day-closure',
      'non_working_day': 'day-off',
      'no_scheme': 'day-unknown',
    };
    return classes[reason] || 'day-unknown';
  }

  // Map day reason to icon
  function getDayIcon(reason: string): string {
    if (reason === 'working') return 'check-circle';
    if (reason === 'public_holiday' || reason === 'company_closure') return 'calendar-off';
    return 'minus-circle';
  }

  // Format day name in French short format
  const DAY_NAMES_SHORT: Record<string, string> = {
    'MONDAY': 'Lun',
    'TUESDAY': 'Mar',
    'WEDNESDAY': 'Mer',
    'THURSDAY': 'Jeu',
    'FRIDAY': 'Ven',
    'SATURDAY': 'Sam',
    'SUNDAY': 'Dim',
  };

  function getShortDayName(dayName: string): string {
    return DAY_NAMES_SHORT[dayName] || dayName;
  }

  // Format date to DD/MM
  function formatShortDate(dateStr: string): string {
    const d = new Date(dateStr + 'T00:00:00');
    return `${String(d.getDate()).padStart(2, '0')}/${String(d.getMonth() + 1).padStart(2, '0')}`;
  }

  // Conflict detection disabled in Phase 2 — will be moved to backend
  const existingLeaveDates = $derived(new Set<string>());

  // Check if a date has a conflicting leave
  function hasLeaveConflict(dateStr: string): boolean {
    return existingLeaveDates.has(dateStr);
  }
</script>


<Sheet.Root bind:open>
  <Sheet.Content side="right" class="sm:max-w-xl flex flex-col h-full overflow-hidden p-0">
    <Sheet.Header class="px-6 py-2.5 border-b bg-slate-50/50">
      <Sheet.Title class="font-bold text-[1rem] flex items-center gap-2">
        {#if isEditing}
          Modifier la demande
        {:else}
          Nouvelle demande de congé
        {/if}
      </Sheet.Title>
    </Sheet.Header>

    <div class="flex-1 overflow-y-auto custom-scrollbar">
      <div class="p-6 space-y-6" in:fade={{ duration: 200 }}>
        <!-- Employee Selection -->
        <div class="space-y-2">
          <Label for="employee-select" class="text-slate-900">
            Employé <span class="text-red-500">*</span>
          </Label>
          <Select.Root type="single" bind:value={selectedEmployeeStr}>
            <Select.Trigger class={cn(
              "h-10 w-full bg-white border border-slate-200 rounded-lg cursor-pointer shadow-fine",
            )}>
              {#if selectedEmployeeObj}
                {@const empPalette = getAvatarPalette(buildFullName(selectedEmployeeObj) || '')}
                <div class="flex items-center gap-2 truncate">
                  <Avatar class="h-7 w-7 rounded-full border border-slate-200 shrink-0">
                    <AvatarImage src={getMediaUrl(selectedEmployeeObj.profile_photo || selectedEmployeeObj.avatarUrl || '')} alt={buildFullName(selectedEmployeeObj)} class="object-cover" />
                    <AvatarFallback class={cn("text-[0.6rem] font-bold", empPalette.bg, empPalette.text)}>
                      {getInitials(selectedEmployeeObj.last_name || '', selectedEmployeeObj.middle_name || '', selectedEmployeeObj.first_name || '')}
                    </AvatarFallback>
                  </Avatar>
                  <span class="text-[0.87rem] font-medium truncate">{buildFullName(selectedEmployeeObj)}</span>
                </div>
              {:else}
                <span class="text-[0.87rem] font-medium truncate text-slate-400">
                  <AppIcon name="user" size={17} class="text-slate-300 inline-block -mt-0.5" />
                  Sélectionner un employé
                </span>
              {/if}
            </Select.Trigger>
            <Select.Content class="max-h-60 z-100">
              {#if $employeesQuery.isLoading}
                <div class="flex items-center justify-center py-4 text-slate-400 text-[0.85rem]">
                  <AnimateSpin textPosition="right" text="Chargement des employés" class="size-3" />
                </div>
              {:else if allEmployees.length === 0}
                <div class="px-3 py-4 text-slate-400 text-[0.82rem] text-center flex items-center justify-center gap-1">
                  <AppIcon name="circle-x" size={17} class="text-slate-300" />
                  Aucun employé trouvé
                </div>
              {:else}
                {#each allEmployees as employee}
                  {@const empFullName = buildFullName(employee) || ''}
                  {@const empPalette = getAvatarPalette(empFullName)}
                  {@const empPhoto = getMediaUrl(employee.profile_photo || employee.avatarUrl || '')}
                  <Select.Item value={employee.id.toString()} class="py-2.5 cursor-pointer">
                    <div class="flex items-center gap-3">
                      <Avatar class="h-8.5 w-8.5 rounded-full border border-slate-200 shrink-0">
                        <AvatarImage src={empPhoto} alt={empFullName} class="object-cover" />
                        <AvatarFallback class={cn("text-[0.65rem] font-bold", empPalette.bg, empPalette.text)}>
                          {getInitials(employee.last_name || '', employee.middle_name || '', employee.first_name || '')}
                        </AvatarFallback>
                      </Avatar>
                      <div class="flex flex-col min-w-0">
                        <span class="text-[0.87rem] font-medium truncate">
                          {empFullName}
                        </span>
                        <span class="text-[0.75rem] text-slate-500 truncate flex items-center gap-1">
                          {#if employee.jobTitle}
                            <span class="text-[0.87rem]">{employee.jobTitle}</span>
                            {#if employee.orgUnit}
                              <span class="text-slate-300">·</span>
                            {/if}
                          {/if}
                          {#if employee.orgUnit}
                            <span class="text-[0.87rem]">{employee.orgUnit}</span>
                          {/if}
                        </span>
                      </div>
                    </div>
                  </Select.Item>
                {/each}
              {/if}
            </Select.Content>
          </Select.Root>
        </div>

        <!-- Leave Type -->
        <div class="space-y-2">
          <Label class="text-slate-900">
            Type de congé <span class="text-red-500">*</span>
          </Label>
          <Select.Root type="single" bind:value={selectedType}>
            <Select.Trigger class="h-10 w-full bg-white border border-slate-200 rounded-lg cursor-pointer shadow-fine">
              <div class="flex items-center gap-2 text-[0.87rem]">
                <div class={cn("w-2 h-2 rounded-full", LEAVE_TYPE_COLORS[selectedTypeObj].dot)}></div>
                <span class="font-medium text-[0.87rem]">{LEAVE_TYPE_LABELS[selectedTypeObj]}</span>
              </div>
            </Select.Trigger>
            <Select.Content class="z-100">
              {#each Object.entries(LEAVE_TYPE_LABELS) as [value, label]}
                <Select.Item {value} class="py-2.5 cursor-pointer">
                  <div class="flex items-center gap-2">
                    <div class={cn("w-2 h-2 rounded-full", LEAVE_TYPE_COLORS[value as LeaveType].dot)}></div>
                    <span class="text-[0.87rem] font-medium">{label}</span>
                  </div>
                </Select.Item>
              {/each}
            </Select.Content>
          </Select.Root>
        </div>

        <!-- Annual Leave Info Card (visible when 'annual' is selected) -->
        {#if isAnnualLeave}
          <div class="rounded-xl border border-blue-200 bg-linear-to-br from-blue-50 to-indigo-50/40 overflow-hidden shadow-fine" in:fade={{ duration: 200 }}>
            <div class="px-4 py-3 space-y-2">
              <div class="flex items-center gap-2 text-[0.875rem] font-semibold text-slate-800">
                <AppIcon name="info" size={16} class="text-blue-600" />
                Limites applicables — Congé annuel
              </div>
              <div class="grid grid-cols-2 gap-2 text-[0.84rem]">
                <!-- Jours annuels -->
                <div class="flex items-center gap-2 p-2.5 bg-white/80 rounded-lg">
                  <div class="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center shrink-0">
                    <AppIcon name="calendar-range" size={15} class="text-blue-600" />
                  </div>
                  <div>
                    <span class="text-slate-500 text-[0.84rem]">Jours annuels</span>
                    <div class="font-semibold text-slate-800 tabular-nums text-[0.84rem]">
                      {leaveConfig.annualLeaveDays} jours / an
                    </div>
                  </div>
                </div>

                <!-- Max consécutifs -->
                <div class={cn(
                  "flex items-center gap-2 p-2.5 rounded-lg",
                  startDate && endDate && displayDays > leaveConfig.maxConsecutiveDays
                    ? "bg-red-50 border border-red-200"
                    : "bg-white/80"
                )}>
                  <div class={cn(
                    "w-8 h-8 rounded-full flex items-center justify-center shrink-0",
                    startDate && endDate && displayDays > leaveConfig.maxConsecutiveDays
                      ? "bg-red-100"
                      : "bg-amber-100"
                  )}>
                    <AppIcon name="arrow-left-right" size={15} class={cn(
                      startDate && endDate && displayDays > leaveConfig.maxConsecutiveDays
                        ? "text-red-600"
                        : "text-amber-600"
                    )} />
                  </div>
                  <div>
                    <span class="text-slate-500 text-[0.84rem]">Max consécutifs</span>
                    <div class={cn(
                      "font-semibold tabular-nums text-[0.84rem]",
                      startDate && endDate && displayDays > leaveConfig.maxConsecutiveDays
                        ? "text-red-700"
                        : "text-slate-800"
                    )}>
                      {leaveConfig.maxConsecutiveDays} jours
                    </div>
                  </div>
                </div>

                {#if leaveConfig.noticePeriodDays > 0}
                  {@const _noticeDiff = (() => {
                    if (!startDate) return null;
                    const today = new Date();
                    today.setHours(0, 0, 0, 0);
                    const start = new Date(startDate + 'T00:00:00');
                    return Math.ceil((start.getTime() - today.getTime()) / (1000 * 60 * 60 * 24));
                  })()}
                  <div class={cn(
                    "flex items-center gap-2 p-2.5 rounded-lg col-span-2",
                    _noticeDiff !== null && _noticeDiff < leaveConfig.noticePeriodDays
                      ? "bg-red-50 border border-red-200"
                      : "bg-white"
                  )}>
                    <div class={cn(
                      "w-8 h-8 rounded-full flex items-center justify-center shrink-0",
                      _noticeDiff !== null && _noticeDiff < leaveConfig.noticePeriodDays
                        ? "bg-red-100"
                        : "bg-violet-100"
                    )}>
                      <AppIcon name="clock" size={15} class={cn(
                        _noticeDiff !== null && _noticeDiff < leaveConfig.noticePeriodDays
                          ? "text-red-600"
                          : "text-violet-600"
                      )} />
                    </div>
                    <div class="flex-1">
                      <span class="text-slate-500 text-[0.84rem]">Préavis requis</span>
                      <div class={cn(
                        "font-semibold tabular-nums text-[0.84rem]",
                        _noticeDiff !== null && _noticeDiff < leaveConfig.noticePeriodDays
                          ? "text-red-700"
                          : "text-slate-800"
                      )}>
                        {leaveConfig.noticePeriodDays} jours avant le
                        {#if _noticeDiff !== null}
                          {#if _noticeDiff < leaveConfig.noticePeriodDays}
                            <span class="font-normal text-red-600 text-[0.84rem]">
                              début du congé (actuel: {_noticeDiff}j)
                            </span>
                          {:else}
                            <span class="font-normal text-slate-400 text-[0.84rem]">
                              début du congé
                            </span>
                          {/if}
                        {/if}
                      </div>
                    </div>
                  </div>
                {/if}
              </div>
            </div>
          </div>
        {/if}

        <!-- Circumstance Sub-type (visible only when 'circumstantial' is selected) -->
        {#if isCircumstantial}
          <div class="space-y-2" in:fade={{ duration: 200 }}>
            <Label class="text-slate-900">
              Type de circonstance <span class="text-red-500">*</span>
            </Label>
            <Select.Root type="single" bind:value={selectedCircumstanceType}>
              <Select.Trigger class="h-10 w-full bg-white border border-slate-200 rounded-lg cursor-pointer shadow-fine">
                <div class="flex items-center gap-2 text-[0.87rem]">
                  {#if selectedCircumstanceType}
                    {@const sl = leaveConfig.specialLeaves.find(s => s.type === selectedCircumstanceType)}
                    {@const iconName = CIRCUMSTANCE_TYPE_ICONS[selectedCircumstanceType as CircumstanceType] ?? 'ellipsis'}
                    <AppIcon name={iconName} size={17} class="text-amber-600 shrink-0" />
                    <span class="font-medium truncate text-[0.84rem]">
                      {CIRCUMSTANCE_TYPE_LABELS[selectedCircumstanceType as CircumstanceType]}
                    </span>
                    {#if sl}
                      <span class="text-slate-400 text-[0.84rem] shrink-0 ml-auto tabular-nums">
                        {sl.daysAllowed} jr{sl.daysAllowed > 1 ? 's' : ''}
                        {sl.isPaid === false ? '· Non payé' : ''}
                      </span>
                    {/if}
                  {:else}
                    <span class="text-slate-400 text-[0.84rem]">
                      Sélectionner une circonstance
                    </span>
                  {/if}
                </div>
              </Select.Trigger>
              <Select.Content class="z-100 max-h-72">
                {#each CIRCUMSTANCE_TYPE_OPTIONS as opt}
                  {@const sl = leaveConfig.specialLeaves.find(s => s.type === opt.value)}
                  {@const iconName = CIRCUMSTANCE_TYPE_ICONS[opt.value] ?? 'ellipsis'}
                  <Select.Item value={opt.value} class="py-2.5 cursor-pointer">
                    <div class="flex items-center gap-3 w-full">
                      <AppIcon name={iconName} size={18} class="text-amber-600 shrink-0" />
                      <div class="flex-1 min-w-0">
                        <div class="text-[0.87rem] font-medium truncate">{opt.label}</div>
                        {#if sl}
                          <div class="flex items-center gap-2 text-slate-500">
                            <span class="text-[0.84rem]">{sl.daysAllowed} jour{sl.daysAllowed > 1 ? 's' : ''}</span>
                            {#if sl.isPaid === false}
                              <span class="px-1 py-0.5 bg-slate-100 text-slate-600 rounded text-[0.78rem]">
                                Non payé
                              </span>
                            {:else}
                              <span class="px-1 py-0.5 bg-green-50 text-green-700 rounded text-[0.78rem]">
                                Payé
                              </span>
                            {/if}
                          </div>
                        {/if}
                      </div>
                      <ValidationError errors={validationErrors} field="circumstanceType" />
                    </div>
                  </Select.Item>
                {/each}
              </Select.Content>
            </Select.Root>
            <ValidationError errors={validationErrors} field="circumstanceType" />

            <!-- Info card for selected sub-type -->
            {#if selectedSpecialLeave}
              <div class="p-3 rounded-lg bg-amber-50 border border-amber-200 flex items-start gap-3">
                <AppIcon name="info" size={17} class="text-amber-600 mt-0.5 shrink-0" />
                <div class="text-[0.84rem] text-amber-800">
                  <strong class="text-[0.84rem]">{selectedSpecialLeave.label}</strong> — 
                  {selectedSpecialLeave.daysAllowed} jour{selectedSpecialLeave.daysAllowed > 1 ? 's' : ''} maximum
                  {#if selectedSpecialLeave.isPaid === false}
                    <span class="font-medium text-[0.84rem]">(non payé)</span>
                  {:else}
                    <span class="font-medium text-[0.84rem]">(payé)</span>
                  {/if}
                  {#if selectedSpecialLeave.description}
                    <br>
                    <span class="text-amber-700/70 text-[0.84rem]">
                      {selectedSpecialLeave.description}
                    </span>
                  {/if}
                </div>
              </div>
            {/if}
          </div>
        {/if}
        <!-- /Circumstance Sub-type -->

        <!-- Sick Leave Info Card (visible when 'sick' is selected) -->
        {#if selectedType === 'sick'}
          <div class="rounded-xl border border-rose-200 bg-linear-to-br from-rose-50 to-orange-50/30 overflow-hidden shadow-fine" in:fade={{ duration: 200 }}>
            <div class="px-4 py-3 space-y-2">
              <div class="flex items-center gap-2 text-[0.875rem] font-semibold text-slate-800">
                <AppIcon name="stethoscope" size={16} class="text-rose-600" />
                Congé maladie
              </div>
              <p class="text-[0.84rem] text-slate-600 leading-relaxed">
                Les congés maladie n'ont pas de limite de durée prédéfinie. Un <strong class="text-rose-600 font-bold text-[0.84rem]">certificat médical</strong> 
                est requis pour justifier l'absence.
              </p>
              <div class="grid grid-cols-1 sm:grid-cols-2 gap-2 text-[0.84rem]">
                <div class="flex items-center gap-2 p-2.5 bg-white/80 rounded-lg">
                  <div class="w-8 h-8 rounded-full bg-rose-100 flex items-center justify-center shrink-0">
                    <AppIcon name="file" size={15} class="text-rose-600" />
                  </div>
                  <div>
                    <span class="text-slate-500 text-[0.84rem]">Justificatif</span>
                    <div class="font-semibold text-slate-800 text-[0.84rem]">Certificat médical obligatoire</div>
                  </div>
                </div>
                <div class="flex items-center gap-2 p-2.5 bg-white/80 rounded-lg">
                  <div class="w-8 h-8 rounded-full bg-orange-100 flex items-center justify-center shrink-0">
                    <AppIcon name="circle-check" size={15} class="text-orange-600" />
                  </div>
                  <div>
                    <span class="text-slate-500 text-[0.84rem]">Durée</span>
                    <div class="font-semibold text-slate-800 text-[0.84rem]">Variable selon prescription</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        {/if}

        <!-- Date Range -->
        <div class="grid grid-cols-2 gap-4">
          <div class="space-y-2">
            <Label for="startDate" class="text-slate-900">Date de début <span class="text-red-500">*</span></Label>
            <Input
              id="startDate"
              type="date"
              bind:value={startDate}
              min={new Date().toISOString().split('T')[0]}
              oninput={() => clearValidationError('startDate')}
              class={cn(
                "h-10 bg-white shadow-fine",
                validationErrors.startDate && "border-red-500 focus:ring-red-500"
              )}
            />
            <ValidationError errors={validationErrors} field="startDate" />
          </div>
          <div class="space-y-2">
            <Label for="endDate" class="text-slate-900">Date de fin <span class="text-red-500">*</span></Label>
            <Input
              id="endDate"
              type="date"
              bind:value={endDate}
              min={startDate}
              oninput={() => clearValidationError('endDate')}
              class={cn(
                "h-10 bg-white shadow-fine",
                validationErrors.endDate && "border-red-500 focus:ring-red-500"
              )}
            />
            <ValidationError errors={validationErrors} field="endDate" />
          </div>
        </div>

        <!-- Validation Error for dates -->
        <ValidationError errors={validationErrors} field="dates" />

        <!-- Period Preview: Working Days Breakdown -->
        {#if selectedEmployeeStr && startDate && endDate && workingDaysData && !hasNoSchedule}
          <div class="rounded-xl border border-slate-200 bg-white overflow-hidden shadow-fine">
            <!-- Preview Header -->
            <button
              onclick={() => showDayDetail = !showDayDetail}
              class="w-full flex items-center justify-between px-4 py-3 hover:bg-slate-50 transition-colors cursor-pointer"
            >
              <div class="flex items-center gap-2">
                <AppIcon name="calendar" size={17} class="text-primary" />
                <span class="text-[0.875rem] font-semibold text-slate-800">Aperçu de la période</span>
                {#if isCalculating}
                  <AnimateSpin class="border-primary size-3.5" text="" />
                {/if}
              </div>
              <div class="flex items-center gap-2">
                {#if workingDaysData && !isCalculating}
                  <span class="text-[0.85rem] font-bold text-primary">{displayDays} jour{displayDays > 1 ? 's' : ''} ouvré{displayDays > 1 ? 's' : ''}</span>
                {/if}
                <AppIcon
                  name={showDayDetail ? 'chevron-up' : 'chevron-down'}
                  size={16}
                  class="text-slate-400"
                />
              </div>
            </button>

            <!-- Day-by-day detail list -->
            {#if showDayDetail && workingDaysData?.dayDetails}
              <div class="border-t border-slate-100">
                <div class="divide-y divide-slate-50">
                  {#each workingDaysData.dayDetails as day (day.date)}
                    <div class="flex items-center gap-3 px-4 py-2 text-[0.8rem] {getDayReasonClass(day.reason)}">
                      
                      <!-- Status icon -->
                      <div class="w-5 h-5 flex items-center justify-center shrink-0">
                        {#if day.isWorking}
                          <div class="w-2 h-2 rounded-full bg-emerald-500" title="Travaillé"></div>
                        {:else if day.reason === 'public_holiday'}
                          <div class="w-2 h-2 rounded-full bg-red-500" title="Férié"></div>
                        {:else if day.reason === 'company_closure'}
                          <div class="w-2 h-2 rounded-full bg-amber-500" title="Fermeture"></div>
                        {:else}
                          <div class="w-2 h-2 rounded-full bg-slate-300" title="Non travaillé"></div>
                        {/if}
                      </div>

                      <!-- Date + day name -->
                      <span class="font-medium text-slate-700 w-20 shrink-0 text-[0.85rem]">
                        {getShortDayName(day.dayName)} {formatShortDate(day.date)}
                      </span>

                      <!-- Work hours (if working) -->
                      {#if day.isWorking && day.startTime}
                        <span class="text-slate-400 text-[0.83rem] w-16 shrink-0 tabular-nums">
                          {day.startTime}-{day.endTime}
                        </span>
                      {:else}
                        <span class="w-16 shrink-0"></span>
                      {/if}

                      <!-- Reason label -->
                      <span class="text-slate-500 truncate flex-1">
                        {#if day.reason === 'public_holiday'}
                          <span class="text-red-600 font-medium text-[0.84rem]">Jour férié</span>
                          {#if day.eventName}
                            <span class="text-slate-400 text-[0.84rem]">— {day.eventName}</span>
                          {/if}
                        {:else if day.reason === 'company_closure'}
                          <span class="text-amber-600 font-medium text-[0.84rem]">Fermeture</span>
                          {#if day.eventName}
                            <span class="text-slate-400 text-[0.84rem]">— {day.eventName}</span>
                          {/if}
                        {:else if day.reason === 'working'}
                          <span class="text-emerald-600 text-[0.84rem]">Travaillé</span>
                        {:else if day.reason === 'non_working_day'}
                          <span class="text-slate-400 text-[0.84rem]">Repos (planning)</span>
                        {:else if day.reason === 'no_scheme'}
                          <span class="text-slate-300 text-[0.84rem]">Planning non défini</span>
                        {/if}
                      </span>

                      <!-- Conflict indicator -->
                      {#if hasLeaveConflict(day.date)}
                        <span class="text-amber-500 shrink-0" title="Congé déjà posé">
                          <AppIcon name="triangle-alert" size={15} />
                        </span>
                      {/if}
                    </div>
                  {/each}
                </div>
              </div>
            {/if}

            <!-- Preview Summary Footer -->
            <div class="border-t border-slate-100 px-4 py-2.5 bg-slate-50/50 flex items-center justify-between">
              <div class="flex items-center gap-4">
                <span class="text-slate-600 text-[0.85rem]">
                  <strong class="text-primary font-bold tabular-nums text-[0.84rem]">{displayDays}</strong> jour{displayDays > 1 ? 's' : ''} ouvré{displayDays > 1 ? 's' : ''}
                </span>
                <span class="text-slate-400 text-[0.85rem]">
                  <strong class="tabular-nums text-[0.84rem] text-semibold">{displayCalendarDays}</strong> jour{displayCalendarDays > 1 ? 's' : ''} calendaire{displayCalendarDays > 1 ? 's' : ''}
                </span>
                {#if workingDaysData?.excluded?.totalExcluded}
                  <span class="text-slate-400 text-[0.85rem]">
                    <strong class="tabular-nums text-[0.85rem] text-semibold">{workingDaysData.excluded.totalExcluded}</strong> exclu{workingDaysData.excluded.totalExcluded > 1 ? 's' : ''}
                  </span>
                {/if}
              </div>
              {#if !workingDaysData && !isCalculating}
                <button
                  onclick={fetchWorkingDays}
                  class="text-[0.84rem] text-primary hover:underline cursor-pointer"
                >
                  Recalculer
                </button>
              {/if}
            </div>
          </div>
        {/if}

        <!-- Error preview -->
        {#if previewError}
          <div class="p-3 rounded-lg bg-amber-50 border border-amber-200 text-amber-700 text-[0.8rem] flex items-center gap-2">
            <AppIcon name="triangle-alert" size={15} />
            {previewError}
          </div>
        {/if}

        <!-- Balance Display (congé annuel uniquement) -->
        {#if isAnnualLeave && currentBalance}
          <div class="p-4 rounded-xl bg-linear-to-br from-blue-50 to-indigo-50 border border-blue-100/50">
            <div class="flex items-center justify-between">
              <span class="text-[0.85rem] font-medium text-slate-700">Solde disponible</span>
              <span class="font-semibold text-emerald-600 tabular-nums text-[0.85rem]">
                {currentBalance.totalAvailable} jour{currentBalance.totalAvailable > 1 ? 's' : ''} disponible{currentBalance.totalAvailable > 1 ? 's' : ''}
                {#if currentBalance.allocated !== currentBalance.totalAvailable}
                  <span class="text-slate-400 font-normal text-[0.85rem]"> / {currentBalance.allocated} alloué{currentBalance.allocated > 1 ? 's' : ''}</span>
                {/if}
              </span>
            </div>

            <!-- Légende : décomposition du solde -->
            <div class="mt-3 text-[0.84rem] text-slate-500 leading-relaxed space-y-2">
              <!-- Ligne "Alloué" -->
              <div class="flex items-start gap-2">
                <span class="inline-flex items-center justify-center size-6 rounded-lg bg-blue-100 text-blue-600 shrink-0 mt-0.5">
                  <AppIcon name="calendar" size={15} />
                </span>
                <div>
                  <strong class="text-slate-600 font-bold text-[0.85rem]">Alloué</strong>
                  <span class="text-slate-500 text-[0.85rem]">
                    {#if currentBalance.allocated === leaveConfig.annualLeaveDays}
                      Vous avez droit à {currentBalance.allocated} jour{currentBalance.allocated > 1 ? 's' : ''}, sur les {leaveConfig.annualLeaveDays} jours annuels prévus.
                    {:else}
                      Vous avez droit à {currentBalance.allocated} jour{currentBalance.allocated > 1 ? 's' : ''}, calculé{currentBalance.allocated > 1 ? 's' : ''} au prorata depuis votre date d'embauche.
                    {/if}
                  </span>
                </div>
              </div>

              <!-- Ligne "Consommé" -->
              {#if currentBalance.deducted > 0}
                <div class="flex items-start gap-2">
                  <span class="inline-flex items-center justify-center size-6 rounded-lg bg-amber-100 text-amber-600 shrink-0 mt-0.5">
                    <AppIcon name="check" size={15} />
                  </span>
                  <div>
                    <strong class="text-slate-600 font-bold text-[0.85rem]">Consommé</strong>
                    <span class="text-slate-500 text-[0.85rem]">
                      {#if currentBalance.deducted === 1}
                        Vous avez déjà posé 1 jour (approuvé ou en attente).
                      {:else}
                        Vous avez déjà posé {currentBalance.deducted} jours (approuvés ou en attente).
                      {/if}
                    </span>
                  </div>
                </div>
              {/if}

              <!-- Ligne "Disponible" -->
              <div class="flex items-start gap-2">
                <span class="inline-flex items-center justify-center size-6 rounded-lg bg-emerald-100 text-emerald-600 shrink-0 mt-0.5">
                  <AppIcon name="circle-check" size={15} />
                </span>
                <div>
                  <strong class="text-slate-600 font-bold text-[0.85rem]">Disponible</strong>
                  <span class="text-slate-500 text-[0.85rem]">
                    Il vous reste {currentBalance.available} jour{currentBalance.available > 1 ? 's' : ''} à prendre.
                  </span>
                </div>
              </div>
            </div>

            <!-- Carry-over detail -->
            {#if currentBalance.carryOver?.available}
              <div class="mt-3 pt-2 border-t border-blue-200/50 flex flex-wrap items-center gap-x-1.5 gap-y-0.5 text-[0.85rem] text-slate-500">
                <AppIcon name="file" size={15} class="shrink-0" />
                <span class="text-[0.85rem]">
                  dont {currentBalance.carryOver.available} jour{currentBalance.carryOver.available > 1 ? 's' : ''} reporté{currentBalance.carryOver.available > 1 ? 's' : ''} de l'année précédente
                </span>
                {#if currentBalance.carryOver.expiresAt}
                  <span class="text-amber-500 text-[0.85rem]">
                    <AppIcon name="clock" size={15} class="inline-block -mt-0.5" />
                    expire {new Date(currentBalance.carryOver.expiresAt + 'T00:00:00').toLocaleDateString('fr-FR', { month: 'long', year: 'numeric' })}
                  </span>
                {/if}
              </div>
            {/if}

            <!-- Seniority bonus hint (annual only) -->
            {#if isAnnualLeave && leaveConfig.seniorityBonus.enabled}
              <div class="mt-0.5 text-[0.85rem] text-slate-400 flex items-center gap-1">
                <AppIcon name="award" size={15} />
                Bonus ancienneté: +{leaveConfig.seniorityBonus.bonusDays} jour{leaveConfig.seniorityBonus.bonusDays > 1 ? 's' : ''} / {leaveConfig.seniorityBonus.yearsPerBonus} an{leaveConfig.seniorityBonus.yearsPerBonus > 1 ? 's' : ''}
              </div>
            {/if}

            <!-- Balance sufficiency -->
            {#if currentBalance.totalAvailable < displayDays}
              <div class="mt-2 flex items-center gap-1.5 text-amber-600 font-medium text-[0.84rem]">
                <AppIcon name="triangle-alert" size={15} />
                Solde insuffisant — il manque {displayDays - currentBalance.totalAvailable} jour{(displayDays - currentBalance.totalAvailable) > 1 ? 's' : ''}
              </div>
            {:else}
              <div class="mt-2 flex items-center gap-1.5 text-emerald-600 font-medium text-[0.84rem]">
                <AppIcon name="circle-check" size={15} />
                Solde suffisant
              </div>
            {/if}
          </div>
        {:else if balanceLoading}
          <div class="p-4 rounded-xl bg-slate-50 border border-slate-200 flex items-center gap-2 text-[0.8rem] text-slate-400">
            <AnimateSpin class="border-slate-400 size-3" textPosition="right" text="Chargement du solde" />
          </div>
        {/if}

        <!-- Reason -->
        <div class="space-y-2">
          <Label for="reason" class="text-slate-900">
            Motif <span class="text-red-500">*</span>
          </Label>
          <textarea
            id="reason"
            bind:value={reason}
            oninput={() => clearValidationError('reason')}
            placeholder="Précisez le motif de votre demande..."
            rows="5"
            class={cn(
              "flex w-full rounded-md border border-input bg-background px-3 py-2.5 text-[0.87rem] ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-4 focus-visible:ring-indigo-500/40 disabled:cursor-not-allowed disabled:opacity-50 resize-none shadow-fine transition-colors",
              validationErrors.reason && "border-red-500 focus-visible:ring-red-500/40"
            )}
          ></textarea>
          <ValidationError errors={validationErrors} field="reason" />
        </div>

        <!-- Attachment File Picker (conditionnel selon le type de congé) -->
        {#if requiresAttachment || isCircumstantial}
          <div class="space-y-2" in:fade={{ duration: 200 }}>
            <Label for="attachment" class="text-slate-900">
              Justificatif
              {#if requiresAttachment}
                <span class="text-red-500">*</span>
              {/if}
            </Label>
            <div class={cn(
              "relative flex items-center gap-3 p-3 rounded-lg border-2 border-dashed transition-colors cursor-pointer",
              requiresAttachment && !attachment
                ? "border-rose-300 bg-rose-50/50 hover:bg-rose-50"
                : attachment
                  ? "border-emerald-300 bg-emerald-50/50"
                  : "border-slate-200 bg-white hover:bg-slate-50"
            )}>
              {#if attachment}
                <div class="w-9 h-9 rounded-full bg-emerald-100 flex items-center justify-center shrink-0">
                  <AppIcon name="file-text" size={17} class="text-emerald-600" />
                </div>
                <div class="flex-1 min-w-0">
                  <div class="text-[0.84rem] font-medium text-slate-800 truncate">{attachment.name}</div>
                  <div class="text-[0.78rem] text-slate-500">
                    {(attachment.size / 1024).toFixed(1)} Ko
                  </div>
                </div>
                <button
                  onclick={() => { attachment = null; }}
                  class="p-1.5 rounded-full hover:bg-slate-200 transition-colors cursor-pointer shrink-0"
                  type="button"
                >
                  <AppIcon name="x" size={16} class="text-slate-400" />
                </button>
              {:else}
                <div class={cn(
                  "w-9 h-9 rounded-full flex items-center justify-center shrink-0",
                  requiresAttachment ? "bg-rose-100" : "bg-slate-100"
                )}>
                  <AppIcon name="file" size={17} class={cn(
                    requiresAttachment ? "text-rose-500" : "text-slate-400"
                  )} />
                </div>
                <div class="flex-1">
                  <div class="text-[0.84rem] font-medium text-slate-600">
                    {#if requiresAttachment}
                      Télécharger le justificatif
                    {:else}
                      Ajouter un justificatif (optionnel)
                    {/if}
                  </div>
                  <div class="text-[0.78rem] text-slate-400">
                    PDF, JPG ou PNG — max 5 Mo
                  </div>
                </div>
                <input
                  id="attachment"
                  type="file"
                  accept=".pdf,.jpg,.jpeg,.png"
                  onchange={(e) => {
                    const target = e.currentTarget as HTMLInputElement;
                    const file = target.files?.[0] || null;
                    attachment = file;
                    // Reset input value so re-selecting the same file triggers the event
                    target.value = '';
                  }}
                  class="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                />
              {/if}
            </div>
            <ValidationError errors={validationErrors} field="attachment" />
          </div>
        {/if}
      </div>
    </div>

    <!-- Fixed Settings Warnings Bar (always visible) -->
    {#if hasBlockingViolation || settingsWarnings.length > 0 || hasNoSchedule || submitError || overlapData?.hasOverlap || overlapLoading}
      <div class={cn(
        "px-6 py-3 border-t space-y-1.5",
        hasBlockingViolation
          ? "bg-red-50 border-red-200"
          : "bg-amber-50 border-amber-200"
      )}>
        {#each settingsWarnings as warning}
          <div class="flex items-start gap-2 text-[0.8rem]">
            <AppIcon
              name="triangle-alert"
              size={17}
              class={cn("mt-0.5 shrink-0", hasBlockingViolation ? "text-red-500" : "text-amber-600")}
            />
            <span class={cn("text-[0.84rem]", hasBlockingViolation ? "text-red-700 font-medium" : "text-amber-700")}>{warning}</span>
          </div>
        {/each}

        {#if hasNoSchedule}
          <div class="flex items-start gap-2 text-[0.8rem]">
            <AppIcon
              name="triangle-alert"
              size={17}
              class="mt-0.5 shrink-0 text-amber-600"
            />
            <span class="text-[0.84rem] text-amber-700">
              L'employé sélectionné n'a pas d'horaire défini. L'aperçu des jours ouvrés n'est pas disponible.
            </span>
          </div>
        {/if}

        {#if requiresAttachment && !attachment && !(isEditing && request?.attachment) && !submitError}
          <div class="flex items-start gap-2 text-[0.8rem]">
            <AppIcon name="triangle-alert" size={17} class="mt-0.5 shrink-0 text-red-500" />
            <span class="text-[0.84rem] text-red-700 font-medium">
              Un justificatif est requis pour ce type de congé. Veuillez joindre un fichier avant de soumettre.
            </span>
          </div>
        {/if}

        {#if overlapData?.hasOverlap && overlapData.leaves.length > 0}
          {#if selectedType === 'sick'}
            <div class="flex items-start gap-2 text-[0.8rem]">
              <AppIcon name="info" size={17} class="mt-0.5 shrink-0 text-blue-500" />
              <span class="text-[0.84rem] text-blue-700">
                {#each overlapData.leaves as leave}
                  Cette période chevauche un congé annuel du {new Date(leave.start_date + 'T00:00:00').toLocaleDateString('fr-FR')} au {new Date(leave.end_date + 'T00:00:00').toLocaleDateString('fr-FR')} ({leave.requested_days} jour{leave.requested_days > 1 ? 's' : ''}).{/each}
                Ces jours seront automatiquement convertis en congé maladie lors de l'approbation.
              </span>
            </div>
          {:else}
            <div class="flex items-start gap-2 text-[0.8rem]">
              <AppIcon name="triangle-alert" size={17} class="mt-0.5 shrink-0 text-amber-600" />
              <span class="text-[0.84rem] text-amber-700">
                {#each overlapData.leaves as leave}
                  Cette période chevauche une autre demande de congé du {new Date(leave.start_date + 'T00:00:00').toLocaleDateString('fr-FR')} au {new Date(leave.end_date + 'T00:00:00').toLocaleDateString('fr-FR')} ({leave.requested_days} jour{leave.requested_days > 1 ? 's' : ''}).{/each}
                Veuillez choisir une autre période ou annuler la demande existante.
              </span>
            </div>
          {/if}
        {:else if overlapLoading}
          <div class="flex items-center gap-2 text-[0.8rem] text-slate-400">
            <AnimateSpin class="border-slate-400 size-3" text="Vérification des chevauchements" textPosition="right" />
          </div>
        {/if}

        {#if submitError}
          <div class="flex items-start gap-2 text-[0.8rem]">
            <AppIcon name="triangle-alert" size={17} class="mt-0.5 shrink-0 text-red-500" />
            <span class="text-[0.84rem] text-red-700 font-medium">{submitError}</span>
          </div>
        {/if}
      </div>
    {/if}

    <!-- Footer -->
    <Sheet.Footer class="px-6 py-2.5 border-t bg-slate-50/50 flex flex-col gap-3">
      <div class="flex gap-3 w-full">
        <Sheet.Close class="flex-1">
          <Button variant="outline" class="w-full h-9 bg-white border-slate-200 shadow-fine text-slate-600 font-medium text-[0.88rem]">
            <AppIcon name="x" size={17} class="text-slate-300" />
            Annuler
          </Button>
        </Sheet.Close>
        <Button
          onclick={handleSubmit}
          disabled={isSaving || hasBlockingViolation || hasNoSchedule}
          class={cn(
            "flex-1 text-white font-medium h-9 shadow-fine text-[0.88rem] transition-all",
            hasBlockingViolation || hasNoSchedule
              ? "bg-slate-400 cursor-not-allowed"
              : "bg-primary hover:opacity-90"
          )}
        >
          {#if isSaving}
            <AnimateSpin class="border-white size-3" text="" />
          {:else}
            <AppIcon name="check" size={17} />
          {/if}
          {#if hasBlockingViolation && submissionBlockReason}
            <span class="text-[0.8rem]">{submissionBlockReason}</span>
          {:else if hasNoSchedule}
            <span class="text-[0.8rem]">Aucun horaire défini</span>
          {:else}
            Soumettre
          {/if}
        </Button>
      </div>
    </Sheet.Footer>
  </Sheet.Content>
</Sheet.Root>


<style>
  .custom-scrollbar::-webkit-scrollbar { width: 4px; }
  .custom-scrollbar::-webkit-scrollbar-thumb { background: #e2e8f0; border-radius: 10px; }
  .custom-scrollbar::-webkit-scrollbar-track { background: transparent; }

  /* Day row highlight by reason */
  .day-working { background: transparent; }
  .day-working:hover { background: #f0fdf4; }
  .day-holiday { background: #fef2f2; }
  .day-holiday:hover { background: #fee2e2; }
  .day-closure { background: #fffbeb; }
  .day-closure:hover { background: #fef3c7; }
  .day-off { background: transparent; }
  .day-off:hover { background: #f8fafc; }
  .day-unknown { background: #f8fafc; }
</style>

