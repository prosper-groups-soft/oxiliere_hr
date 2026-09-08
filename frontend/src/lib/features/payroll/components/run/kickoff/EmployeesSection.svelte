<script lang="ts">
  import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
  import { Input } from "@/components/ui/input";
  import { Badge } from "@/components/ui/badge";
  import { Label } from "@/components/ui/label";
  import { Checkbox } from "@/components/ui/checkbox";
  import { Switch } from "@/components/ui/switch";
  import { Button } from "@/components/ui/button";
  import * as DropdownMenu from "@/components/ui/dropdown-menu";
  import { cn } from "@/utilities/common/css";
  import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
  import { getInitials } from "@/utilities/common/string";
  import { getAvatarPalette } from "@/utilities/common/func";
  import { getMediaUrl } from "@/utilities/common/media";
  import { getOrgUnitIcon } from "@/features/jobs/constants/orgUnit.constants";
  import { getEmployeeStatusConfig, getEmployeeStatusDotConfig } from "@/features/employees/constants/employeeStatus";
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import AnimateSpin from "@/components/layout/elements/AnimateSpin.svelte";
  import type { ContractPayElementItem } from "@/features/payroll/types/types";


  export interface KickOffEmployee {
    id: string;
    name: string;
    jobTitle: string;
    orgUnit: string;
    contractType: string;
    location: string;
    joinDate: string;
    status: string;
    first_name: string;
    middle_name: string | null;
    last_name: string;
    /** Photo de profil (chemin API brut) — affichée si présente */
    photo?: string | null;
    /** Salaire de base contractuel (montant, devise, brut/net…) */
    contract?: {
      base_salary?: number | null;
      currency?: string;
      remuneration_type?: string;
      salary_base_type?: string;
      /** Validité du contrat — source de l'éligibilité sur la période de paie. */
      start_date?: string | null;
      end_date?: string | null;
    } | null;
    /** Éléments de paie S10 du contrat courant */
    pay_elements?: ContractPayElementItem[];
  }

  interface Props {
    employees: KickOffEmployee[];
    isLoadingEmployees: boolean;
    orgUnits: Array<{ id: string; name: string; type: string }>;
    isLoadingOrgUnits: boolean;
    includeAllEmployees: boolean;
    selectedEmployeeIds: string[];
    selectedOrgUnitIds: string[];
    employeeSearch: string;
    periodStart: string;
    periodEnd: string;
    onIncludeAllChange: (checked: boolean) => void;
    onToggleEmployee: (id: string) => void;
    onToggleOrgUnit: (id: string) => void;
    onClearOrgUnits: () => void;
    onSearchChange: (value: string) => void;
  }

  let {
    employees,
    isLoadingEmployees,
    orgUnits,
    isLoadingOrgUnits,
    includeAllEmployees,
    selectedEmployeeIds,
    selectedOrgUnitIds,
    employeeSearch,
    periodStart,
    periodEnd,
    onIncludeAllChange,
    onToggleEmployee,
    onToggleOrgUnit,
    onClearOrgUnits,
    onSearchChange
  }: Props = $props();

  function initialsFromName(name: string): string {
    return name.split(' ').map(n => n[0]).filter(Boolean).slice(0, 2).join('').toUpperCase();
  }

  /** Formate une date ISO en français court (ex. « 1 sept. 2026 »), sans dépendance. */
  function fmtDate(value?: string | null): string {
    if (!value) return '';
    const d = new Date(value.slice(0, 10) + 'T00:00:00');
    if (Number.isNaN(d.getTime())) return '';
    return new Intl.DateTimeFormat('fr-FR', { day: 'numeric', month: 'short', year: 'numeric' }).format(d);
  }

  /**
   * Éligibilité d'un employé : son contrat doit CHEVAUCHER la période de paie
   * [periodStart, periodEnd] — même règle que le moteur backend
   * (services/contract_eligibility.py).
   * Tant que la période n'est pas renseignée, on ne bloque rien.
   */
  function contractOverlapsPeriod(emp: KickOffEmployee): boolean {
    const ps = periodStart ? periodStart.slice(0, 10) : '';
    const pe = periodEnd ? periodEnd.slice(0, 10) : '';
    if (!ps || !pe) return true;
    const cs = emp.contract?.start_date ? emp.contract.start_date.slice(0, 10) : null;
    if (!cs) return false;
    const ce = emp.contract?.end_date ? emp.contract.end_date.slice(0, 10) : null;
    return cs <= pe && (ce === null || ce >= ps);
  }

  /** Raison d'inéligibilité affichée à l'utilisateur. */
  function ineligibilityReason(emp: KickOffEmployee): string {
    if (!emp.contract?.start_date) return 'Aucun contrat actif';
    return 'Contrat hors de la période de paie';
  }

  /** Libellé de validité du contrat (ex. « du 01 sept. 2026 au 30 sept. 2026 »). */
  function contractWindow(emp: KickOffEmployee): string {
    if (!emp.contract?.start_date) return 'Sans contrat';
    const start = fmtDate(emp.contract.start_date);
    const end = emp.contract.end_date ? (fmtDate(emp.contract.end_date) || 'CDI') : 'CDI';
    return `${start} → ${end}`;
  }

  const eligibleCount = $derived(
    employees.filter((e) => contractOverlapsPeriod(e)).length
  );

  const filteredEmployees = $derived.by(() => {
    const q = employeeSearch.trim().toLowerCase();
    if (!q) return employees;
    return employees.filter(e => e.name.toLowerCase().includes(q) || e.jobTitle.toLowerCase().includes(q) || e.orgUnit.toLowerCase().includes(q));
  });

  // Garde-fou : getEmployeeStatusConfig peut retourner undefined pour un statut
  // inconnu (fallback cassé en amont). On garantit toujours un objet complet.
  const FALLBACK_STATUS_CONFIG = {
    dot: 'bg-slate-300',
    bg: 'bg-slate-100',
    color: 'text-slate-500',
    label: 'Statut inconnu'
  } as const;

  function safeStatusConfig(status: string | undefined) {
    return getEmployeeStatusConfig(status) ?? FALLBACK_STATUS_CONFIG;
  }

  /** Formate un montant dans la devise (code ISO), ex. 1 850 000 CDF. */
  function formatAmount(value?: number | null, currency?: string): string {
    if (value == null || Number.isNaN(Number(value))) return '—';
    const formatted = Number(value).toLocaleString('fr-FR', { maximumFractionDigits: 0 });
    return currency ? `${formatted} ${currency}` : formatted;
  }

  /** Libellé court du mode de rémunération. */
  function remunerationLabel(type?: string): string {
    if (type === 'FIXED') return 'Salaire fixe';
    if (type === 'HOURLY') return 'Taux horaire';
    return '';
  }

  /** Nature du montant de base affiché : BASE = avant déductions, NET = brutage à appliquer. */
  function salaryKindLabel(base?: string): string {
    if (base === 'NET') return 'Net (brutage)';
    return 'Salaire de base';
  }

  /** Valeur d'un élément de paie.
   *  - % : appliqué sur le salaire brut (base orchestrateur).
   *  - sinon montant personnalisé > montant catalogue, avec devise. */
  function formatPayElementValue(el: ContractPayElementItem, currency?: string): string {
    if (el.custom_percentage != null) return `${el.custom_percentage} % du brut`;
    if (el.custom_amount != null) return formatAmount(Number(el.custom_amount), currency);
    if (el.amount != null) return formatAmount(Number(el.amount), currency);
    // Élément en % : % par défaut du catalogue (si exposé par le backend).
    if (el.value_type === 'PERCENTAGE' && el.catalog_percentage != null) {
      return `${el.catalog_percentage} % du brut (défaut)`;
    }
    if (el.value_type === 'PERCENTAGE') return '% du brut (défaut config)';
    return 'Montant à configurer';
  }
</script>


<Card class="border-slate-200 shadow-sm rounded-2xl">
  <CardHeader class="px-5 pt-5 pb-0">
    <div class="flex items-center justify-between gap-3">
      <div>
        <CardTitle class="text-[0.98rem] font-bold text-slate-900 tracking-tight">
          Employés
        </CardTitle>
        <CardDescription class="text-[0.875rem]">
          Sélection des contrats à inclure dans le calcul.
        </CardDescription>
      </div>
      {#if employees.length > 0}
        <span class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-indigo-50 border border-indigo-100 text-[0.85rem] font-semibold text-indigo-600 shrink-0">
          <AppIcon name="users" size={12} />
          {employees.length} actif{employees.length > 1 ? 's' : ''}
        </span>
      {/if}
    </div>
  </CardHeader>
  <CardContent class="px-5 py-5 space-y-4">
    <!-- Mode : Tous -->
    {@render ModeAll()}

    <div class="space-y-4">
      <!-- Filtre par unités organisationnelles (DropdownMenu) -->
      {@render EmployeesFilter()}

      <!-- Liste des employés (masquée quand « Tous » est coché) -->
      {@render EmployeesList()}
    </div>
  </CardContent>
</Card>


{#snippet ModeAll()}
  <Label class="flex items-center gap-3 p-3.5 bg-slate-50 rounded-xl cursor-pointer hover:bg-slate-100 transition-colors border border-slate-100">
    <Switch
      checked={includeAllEmployees}
      onCheckedChange={(checked) => onIncludeAllChange(!!checked)}
      class="cursor-pointer"
    />
    <div class="flex flex-col gap-2">
      <span class="text-[0.86rem] font-semibold text-slate-700">Tous les employés actifs</span>
      <p class="text-[0.85rem] text-slate-500 mt-0.5">
        Inclut les employés actifs dont le contrat couvre la période : {eligibleCount} éligible{eligibleCount > 1 ? 's' : ''}.
      </p>
    </div>
  </Label>
{/snippet}


{#snippet EmployeesFilter()}
  <div class="flex items-center justify-between gap-3">
    <h4 class="text-[0.9rem] font-semibold text-slate-900 flex items-center gap-1.5">
      <AppIcon name="building-2" size={15} class="text-slate-400" />
      Filtrer par unité
      {#if selectedOrgUnitIds.length > 0}
        <span class="text-[0.85rem] font-semibold text-indigo-600">({selectedOrgUnitIds.length})</span>
      {/if}
    </h4>

    <DropdownMenu.Root>
      <DropdownMenu.Trigger>
        <Button
          variant="ghost"
          size="sm"
          class="h-7 px-2.5 text-[0.85rem] text-slate-600 hover:text-slate-900 hover:bg-slate-100"
        >
          <AppIcon name="building-2" size={15} class="mr-1.5" />
          Unité
          {#if selectedOrgUnitIds.length > 0}
            <span class="ml-1.5 flex h-4 w-4 items-center justify-center rounded-full bg-primary text-[0.7rem] font-medium text-white">
              {selectedOrgUnitIds.length}
            </span>
          {/if}
        </Button>
      </DropdownMenu.Trigger>

      <DropdownMenu.Content align="end" class="w-56 p-1 z-100">
        <DropdownMenu.Label class="text-[0.8rem] font-semibold text-slate-500 uppercase tracking-wider px-2 py-1.5">
          Unité organisationnelle
        </DropdownMenu.Label>

        {#if isLoadingOrgUnits}
          <div class="px-2 py-2 text-[0.85rem] text-slate-400 italic">Chargement des unités…</div>
        {:else if orgUnits.length === 0}
          <div class="px-2 py-2 text-[0.85rem] text-slate-400 italic">Aucune unité disponible.</div>
        {:else}
          {#each orgUnits as unit}
            {@const active = selectedOrgUnitIds.includes(unit.id)}
            {@const unitIcon = getOrgUnitIcon(unit.type)}
            <DropdownMenu.Item
              onclick={() => onToggleOrgUnit(unit.id)}
              class={[
                "text-[0.86rem] py-1.5 cursor-pointer flex items-center justify-between",
                active && "bg-slate-50 font-medium"
              ]}
            >
              <span class="flex items-center gap-2 text-[0.86rem]">
                <AppIcon name={unitIcon} size={16} class="text-slate-500" />
                {unit.name}
              </span>
              {#if active}
                <AppIcon name="check" size={14} class="text-slate-600" />
              {/if}
            </DropdownMenu.Item>
          {/each}
        {/if}

        {#if selectedOrgUnitIds.length > 0}
          <DropdownMenu.Separator />
          <DropdownMenu.Item
            onclick={() => onClearOrgUnits()}
            class="text-[0.86rem] text-red-600 hover:bg-red-50/30! hover:text-red-700! cursor-pointer"
          >
            <AppIcon name="x" size={16} class="text-inherit" />
            Réinitialiser
          </DropdownMenu.Item>
        {/if}
      </DropdownMenu.Content>
    </DropdownMenu.Root>
  </div>
{/snippet}


{#snippet EmployeesList()}
  <div class="space-y-3">
    <h4 class="text-[0.9rem] font-semibold text-slate-900 border-b border-slate-100 pb-2 flex items-center gap-1.5">
      <AppIcon name="user-check" size={15} class="text-slate-400" />
      Sélection individuelle
      {#if selectedEmployeeIds.length > 0}
        <span class="ml-auto text-[0.85rem] font-semibold text-indigo-600">({selectedEmployeeIds.length})</span>
      {/if}
    </h4>

    {#if includeAllEmployees}
      <div class="flex items-center gap-2 px-3.5 py-2.5 bg-slate-50 rounded-lg border border-slate-100 text-[0.85rem] text-slate-500">
        <AppIcon name="users" size={15} class="text-slate-400 shrink-0" />
        Tous les employés actifs dont le contrat couvre la période ({eligibleCount}) sont inclus — désélectionnez « Tous » pour choisir individuellement.
      </div>
    {:else}
    <div class="relative">
      <AppIcon name="search" size={14} class="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
      <Input 
        type="text"
        value={employeeSearch}
        oninput={(e) => onSearchChange((e.currentTarget as HTMLInputElement).value)}
        placeholder="Rechercher un employé…"
        class="h-9 pl-9 bg-white border-slate-200 focus:ring-1 focus:ring-primary focus:border-primary rounded-md shadow-fine" 
      />
    </div>

    <div class="rounded-xl border border-slate-200 overflow-hidden bg-white shadow-fine">
      <!-- Corps scrollable — l'en-tête sticky est DANS le scroll pour que les
           colonnes restent alignées avec la scrollbar (pattern standard). -->
      <div class="max-95 overflow-y-auto">
        <!-- En-tête des colonnes (sticky au scroll) -->
        <div class="sticky top-0 z-10 flex items-center px-4 py-2 bg-slate-50 border-b border-slate-100 font-semibold text-slate-400 uppercase tracking-wider">
          <div class="w-[48%] text-[0.85rem] flex items-center gap-3">
            <span class="w-4 shrink-0"></span>
            <span class="w-9 shrink-0"></span>
            Employé
          </div>
          <div class="w-[12%] text-[0.85rem]">Contrat</div>
          <div class="w-[24%] text-[0.85rem]">Rémunération</div>
          <div class="w-[16%] text-[0.85rem] flex items-center justify-end pr-2">Statut</div>
        </div>

        {#if isLoadingEmployees}
          <div class="flex items-center justify-center gap-2 px-4 py-3 text-[0.85rem] text-slate-400">
            <AnimateSpin text="Chargement des employés" class="size-3 border-slate-400" />
          </div>
        {:else if filteredEmployees.length === 0}
          <div class="px-4 py-3 text-[0.85rem] text-slate-400 italic">Aucun employé trouvé.</div>
        {:else}
          {#each filteredEmployees as emp (emp.id)}
            {@render EmployeeRow(emp)}
          {/each}
        {/if}
      </div>
    </div>
    {/if}
  </div>
{/snippet}


{#snippet EmployeeRow(employee: KickOffEmployee)}
  {@const palette = getAvatarPalette(employee.name || '')}
  {@const statusCfg = safeStatusConfig(employee.status)}
  {@const dotCfg = getEmployeeStatusDotConfig(employee.status)}
  {@const eligible = contractOverlapsPeriod(employee)}
  {@const reason = ineligibilityReason(employee)}
  {@const windowLabel = contractWindow(employee)}
  <div class={cn('group/row flex items-center py-2.5 px-4 border-b border-slate-50 last:border-b-0 transition-colors', eligible ? 'hover:bg-indigo-50/30' : 'opacity-60')}>
    <!-- Checkbox + Avatar + Identité -->
    <div class="w-[48%] flex items-center gap-3 min-w-0">
      <Checkbox
        checked={selectedEmployeeIds.includes(employee.id) && eligible}
        disabled={!eligible}
        onCheckedChange={() => onToggleEmployee(employee.id)}
        class="shrink-0 bg-white"
      />
      <div class="relative shrink-0">
        <Avatar class="h-11 w-11 rounded-full border border-slate-200">
          {#if employee.photo}
            <AvatarImage src={getMediaUrl(employee.photo)} alt={employee.name} class="object-cover" />
          {/if}
          <AvatarFallback class={cn('font-bold text-[0.85rem]', palette.bg, palette.text)}>
            {getInitials(employee.last_name, employee.middle_name ?? '', employee.first_name) || initialsFromName(employee.name)}
          </AvatarFallback>
        </Avatar>
        <div class={cn('z-10 absolute bottom-0 right-0 h-2.5 w-2.5 rounded-full border border-white shadow-fine transition-colors duration-300', dotCfg.color)} title={dotCfg.title}></div>
      </div>
      <div class="flex flex-col min-w-0">
        <span class="font-semibold text-[0.85rem] text-slate-800 truncate leading-tight group-hover/row:text-indigo-600 transition-colors">
          {employee.name}
        </span>
        <span class="text-[0.85rem] text-slate-500 truncate">
          {employee.jobTitle || 'Poste non défini'}
        </span>
        {#if eligible}
          <span class="text-[0.8rem] text-slate-400 truncate mt-0.5" title="Validité du contrat">
            {windowLabel}
          </span>
        {:else}
          <span class="text-[0.8rem] text-rose-600 font-medium flex items-center gap-1 mt-0.5">
            <AppIcon name="circle-alert" size={12} class="shrink-0" /> {reason}
          </span>
        {/if}
      </div>
    </div>

    <!-- Contrat -->
    <div class="w-[12%] min-w-0">
      {#if employee.contractType}
        <Badge variant="outline"
          class="w-fit bg-blue-50 text-blue-600 border-blue-200 text-[0.86rem] font-medium px-2 py-0.5 rounded-full">
          {employee.contractType}
        </Badge>
      {:else}
        <span class="text-[0.86rem] text-slate-400">
            Pas de type de contrat
        </span>
      {/if}
    </div>

    <!-- Rémunération : salaire de base + éléments de paie actifs -->
    <div class="w-[24%] min-w-0 pr-2">
      {#if employee.contract?.base_salary != null && Number(employee.contract.base_salary) > 0}
        <div class="text-[0.86rem] font-medium uppercase tracking-wide text-slate-400">
            {salaryKindLabel(employee.contract.salary_base_type)}
        </div>
        <div class="text-[0.86rem] text-slate-800 font-semibold whitespace-nowrap">
          {formatAmount(Number(employee.contract.base_salary), employee.contract.currency)}
        </div>
        <div class="text-[0.86rem] text-slate-400">
          {remunerationLabel(employee.contract.remuneration_type)}
        </div>
      {:else}
        <span class="text-[0.86rem] text-slate-400">
            Pas de rémunération
        </span>
      {/if}

      {#if (employee.pay_elements ?? []).length > 0}
        <div class="flex flex-wrap gap-1 mt-1">
          {#each (employee.pay_elements ?? []) as el}
            <span
              class="inline-flex items-center gap-1 text-[0.86rem] text-slate-600 bg-slate-50 border border-slate-100 rounded px-1.5 py-0.5 whitespace-nowrap"
              title={el.label}
            >
              {el.label}
              <span class="font-semibold text-slate-700 text-[0.86rem]">
                  {formatPayElementValue(el, employee.contract?.currency)}
              </span>
            </span>
          {/each}
        </div>
      {/if}
    </div>

    <!-- Statut -->
    <div class="w-[16%] flex items-center justify-end pr-2">
      <Badge variant="outline"
        class="{statusCfg.bg} {statusCfg.color} border-0 text-[0.86rem] font-semibold px-2.5 py-1 shadow-none rounded-full whitespace-nowrap flex items-center gap-1.5">
        <span class={cn('h-1.5 w-1.5 rounded-full', statusCfg.dot)}></span>
        {statusCfg.label}
      </Badge>
    </div>
  </div>
{/snippet}

