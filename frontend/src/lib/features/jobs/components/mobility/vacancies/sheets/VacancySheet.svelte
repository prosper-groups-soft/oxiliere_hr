<script lang="ts">
	import * as Sheet from "@/components/ui/sheet";
	import { Button } from "@/components/ui/button";
	import { Input } from "@/components/ui/input";
	import { Label } from "@/components/ui/label";
	import {
		Select,
		SelectContent,
		SelectItem,
		SelectTrigger
	} from "@/components/ui/select";
	import AppIcon from "@/components/layout/elements/AppIcon.svelte";
	import { jobsStore } from "../../../../stores/jobs.svelte";
	import { notification } from "@/stores/notification.svelte";
	import type { Vacancy } from "../../../../types/types";
	import { fade, slide } from "svelte/transition";

	let {
		open = $bindable(false),
		vacancy = $bindable(null),
		prefilledDeptId = ''
	} = $props<{
		open: boolean,
		vacancy?: Vacancy | null,
		prefilledDeptId?: string
	}>();

	// Form state
	let formPositionId = $state('');
	let formPriority = $state<'HIGH' | 'MEDIUM' | 'LOW'>('MEDIUM');
	let formStatus = $state<'OPEN' | 'IN_PROGRESS' | 'RECRUITMENT' | 'CANCELLED'>('OPEN');
	let formOpenedDate = $state('');

	$effect(() => {
		if (open) {
			if (vacancy) {
				formPositionId = vacancy.positionId;
				formPriority = vacancy.priority;
				formStatus = vacancy.status as any;
				formOpenedDate = vacancy.openedDate;
			} else {
				formPositionId = '';
				formPriority = 'MEDIUM';
				formStatus = 'OPEN';
				formOpenedDate = new Date().toISOString().split('T')[0];
			}
		}
	});

	function handleSave() {
		if (!formPositionId) {
			notification.toast.error('Veuillez sélectionner un poste');
			return;
		}

		const selectedPosition = jobsStore.positions.find(p => p.id === formPositionId);
		if (!selectedPosition) {
			notification.toast.error('Poste non trouvé');
			return;
		}

		try {
			const data: Omit<Vacancy, 'id'> = {
				positionId: formPositionId,
				priority: formPriority,
				status: formStatus as any,
				openedDate: formOpenedDate
			};

			if (vacancy) {
				jobsStore.updateVacancy(vacancy.id, data);
				notification.toast.success('Besoin modifié avec succès');
			} else {
				jobsStore.addVacancy(data);
				notification.toast.success('Nouveau besoin créé avec succès');
			}
			open = false;
		} catch (error) {
			notification.toast.error('Erreur lors de l\'enregistrement');
		}
	}

	function handleDelete() {
		if (!vacancy) return;

		notification.confirm({
			title: 'Supprimer ce besoin',
			message: 'Êtes-vous sûr(e) de vouloir supprimer ce besoin ? Cette action est irréversible.',
			type: 'danger',
			yesText: 'Supprimer',
			noText: 'Annuler',
			onYes: () => {
				jobsStore.deleteVacancy(vacancy.id);
				notification.toast.success('Besoin supprimé');
				open = false;
			}
		});
	}

	const selectedPos = $derived(jobsStore.positions.find(p => p.id === formPositionId));
	const selectedDept = $derived(selectedPos?.departmentId ? jobsStore.getDepartmentById(selectedPos.departmentId) : null);

	const priorityConfig: Record<string, { icon: string, color: string, label: string }> = {
		'HIGH':   { icon: 'alert', color: 'text-red-500',   label: 'Urgente' },
		'MEDIUM': { icon: 'info',  color: 'text-amber-500', label: 'Normale' },
		'LOW':    { icon: 'check', color: 'text-green-500', label: 'Faible' }
	};

	const statusConfig: Record<string, { icon: string, color: string, label: string }> = {
		'OPEN':        { icon: 'pin',    color: 'text-blue-500',  label: 'Ouverte' },
		'IN_PROGRESS': { icon: 'rotate', color: 'text-amber-600', label: 'En cours' },
		'RECRUITMENT': { icon: 'consulting', color: 'text-purple-600', label: 'Réc. Externe' },
		'CANCELLED':   { icon: 'close',  color: 'text-red-400',   label: 'Annulée' }
	};

</script>


<Sheet.Root bind:open>
	<Sheet.Content side="right" class="sm:max-w-md bg-white p-0 flex flex-col h-full overflow-hidden">
		<!-- Header aligned with PositionSheet -->
		<Sheet.Header class="px-6 py-5 border-b bg-slate-50/50">
			<div class="flex items-center gap-3">
				<div class="h-10 w-10 rounded-xl bg-primary/10 text-primary flex items-center justify-center shrink-0">
					<AppIcon name="inbox" size={20} />
				</div>
				<div class="space-y-0.5 min-w-0">
					<Sheet.Title class="text-[1rem] font-black text-slate-900 truncate">
						{vacancy ? 'Modifier le besoin' : 'Nouveau besoin'}
					</Sheet.Title>
					<Sheet.Description class="text-[0.78rem] text-slate-500 truncate">
						{selectedPos?.title || 'Identification d\'un poste vacant'}
					</Sheet.Description>
				</div>
			</div>
		</Sheet.Header>

		<div class="flex-1 overflow-y-auto custom-scrollbar">
			<div class="p-6 space-y-7" in:fade={{ duration: 200 }}>
				
				<!-- Poste (Select Pattern) -->
				<div class="space-y-2.5">
					<Label class="text-slate-900">Poste à pourvoir <span class="text-red-500">*</span></Label>
					<Select type="single" value={formPositionId} onValueChange={(v) => formPositionId = v}>
						<SelectTrigger class="h-10 w-full bg-white border-slate-200 shadow-fine rounded-md">
							<span class="truncate text-[0.85rem] font-medium">
								{selectedPos?.title || 'Sélectionner un poste...'}
							</span>
						</SelectTrigger>
						<SelectContent class="z-9999">
							{#each jobsStore.positions as pos}
								<SelectItem value={pos.id} class="text-[0.85rem]">
									{pos.title}
								</SelectItem>
							{/each}
						</SelectContent>
					</Select>
				</div>

				<!-- Département (lecture seule) -->
				{#if selectedDept}
					<div class="space-y-2.5">
						<Label class="text-slate-900">Unité organisationnelle</Label>
						<div class="h-10 w-full bg-slate-50 border border-slate-200 rounded-md flex items-center px-3">
							<span class="truncate text-[0.85rem] font-medium text-slate-600">
								{selectedDept.name}
							</span>
						</div>
					</div>
				{/if}

				<div class="grid grid-cols-2 gap-4">
					<!-- Priorité -->
					<div class="space-y-2.5">
						<Label class="text-slate-900">Priorité</Label>
						<Select type="single" value={formPriority} onValueChange={(v) => formPriority = v as any}>
							<SelectTrigger class="h-10 w-full bg-white border-slate-200 shadow-fine rounded-md">
								<span class="truncate text-[0.85rem] font-medium">
									{priorityConfig[formPriority].label}
								</span>
							</SelectTrigger>
							<SelectContent class="z-9999">
								{#each Object.entries(priorityConfig) as [key, cfg]}
									<SelectItem value={key} class="text-[0.85rem]">
										{cfg.label}
									</SelectItem>
								{/each}
							</SelectContent>
						</Select>
					</div>

					<!-- Statut -->
					<div class="space-y-2.5">
						<Label class="text-slate-900">Statut</Label>
						<Select type="single" value={formStatus} onValueChange={(v) => formStatus = v as any}>
							<SelectTrigger class="h-10 w-full bg-white border-slate-200 shadow-fine rounded-md">
								<span class="truncate text-[0.85rem] font-medium">
									{statusConfig[formStatus].label}
								</span>
							</SelectTrigger>
							<SelectContent class="z-9999">
								{#each Object.entries(statusConfig) as [key, cfg]}
									<SelectItem value={key} class="text-[0.85rem]">
										{cfg.label}
									</SelectItem>
								{/each}
							</SelectContent>
						</Select>
					</div>
				</div>

				<!-- Visual Feedback Box -->
				<div class="p-5 rounded-2xl bg-slate-50 border border-slate-100 grid grid-cols-2 gap-4" in:slide={{ duration: 300 }}>
					<div class="flex items-center gap-3">
						<div class="h-9 w-9 rounded-xl bg-white flex items-center justify-center shadow-sm {priorityConfig[formPriority].color} border border-slate-100">
							<AppIcon name={priorityConfig[formPriority].icon} size={18} />
						</div>
						<div class="flex flex-col">
							<span class="text-[0.6rem] font-black text-slate-400 uppercase tracking-widest">Priorité</span>
							<span class="text-[0.8rem] font-bold text-slate-700">{priorityConfig[formPriority].label}</span>
						</div>
					</div>
					<div class="flex items-center gap-3">
						<div class="h-9 w-9 rounded-xl bg-white flex items-center justify-center shadow-sm {statusConfig[formStatus].color} border border-slate-100">
							<AppIcon name={statusConfig[formStatus].icon} size={18} />
						</div>
						<div class="flex flex-col">
							<span class="text-[0.6rem] font-black text-slate-400 uppercase tracking-widest">Statut</span>
							<span class="text-[0.8rem] font-bold text-slate-700">{statusConfig[formStatus].label}</span>
						</div>
					</div>
				</div>

				<!-- Date d'ouverture -->
				<div class="space-y-2.5">
					<Label for="vac-date" class="text-slate-900">Date d'ouverture</Label>
					<Input 
						id="vac-date"
						type="date"
						bind:value={formOpenedDate}
						class="h-10 bg-white border-slate-200 focus:ring-1 focus:ring-primary rounded-md shadow-fine"
					/>
				</div>
			</div>
		</div>

		<!-- Footer aligned with PositionSheet -->
		<Sheet.Footer class="px-6 py-5 border-t bg-slate-50/50 flex flex-col gap-3">
			<div class="flex gap-3 w-full">
				<Button 
					onclick={handleSave} 
					class="flex-1 bg-primary! text-white font-medium h-9 shadow-fine text-[0.88rem] hover:opacity-90 transition-all"
				>
					<AppIcon name="check" size={18} />
					Enregistrer
				</Button>
				<Sheet.Close class="flex-1">
					<Button variant="outline" class="w-full h-9 bg-white border-slate-200 shadow-fine text-slate-600 font-medium text-[0.88rem]">
						Annuler
					</Button>
				</Sheet.Close>
			</div>

			{#if vacancy}
				<Button 
					onclick={handleDelete}
					variant="ghost"
					class="w-full text-red-500 hover:text-red-600 hover:bg-red-50 font-medium h-9 text-[0.8rem] transition-colors"
				>
					<AppIcon name="trash" size={14} />
					Supprimer définitivement ce besoin
				</Button>
			{/if}
		</Sheet.Footer>
	</Sheet.Content>
</Sheet.Root>


<style>
	.custom-scrollbar::-webkit-scrollbar { width: 4px; }
	.custom-scrollbar::-webkit-scrollbar-track { background: transparent; }
	.custom-scrollbar::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 10px; }
</style>

