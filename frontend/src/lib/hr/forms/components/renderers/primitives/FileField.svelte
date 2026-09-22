<script lang="ts">
	// Champ file (V0.2, catalogue) : upload 1 fichier (défaut) ou plusieurs
	// (`multiple`). Deux transports possibles :
	//  - uploader injecté (form.config.uploader) : upload en ARRIÈRE-PLAN dès la
	//    sélection — progression par fichier, annulation (×), la valeur du champ
	//    est remplacée par la référence serveur (string) à la réussite ; en cas
	//    d'échec le File reste dans la valeur → sac { files } au submit.
	//  - sans uploader (défaut) : le champ est un seau — valeur = File / File[],
	//    sortie du payload vers { files } au submit (upload 2-phases).
	// Drop zone + liste de fichiers (icône colorée par type, nom, taille) avec
	// téléchargement et suppression ; fichiers hors `accept`/`maxSize` rejetés
	// avec message inline. En lecture seule : noms affichés — une valeur string
	// ressemblant à une URL est téléchargeable (ancrage download).
	import type { FieldInstance, FileFieldConfig, FormInstance, UploadProgress } from '../../../core/types.js';
	import FieldLabel from '../shared/FieldLabel.svelte';
	import FieldMessages from '../shared/FieldMessages.svelte';
	import AppIcon from '@/hr/components/layout/elements/AppIcon.svelte';
	import { t } from '../../../validation/i18n.js';
	import { fileIconOf, fileColorOf, isFileUrlLike } from '@/hr/constants/ui/fileTypes.js';

	let {
		config,
		field,
		form
	}: { config: FileFieldConfig; field: FieldInstance; form?: FormInstance<any> } = $props();

	const multiple = $derived(config.multiple === true);
	const inputId = $derived(`${field.id}-input`);
	let dragOver = $state(false);
	/** Fichiers rejetés (accept/maxSize) — message inline, pas d'erreur de champ. */
	let rejected = $state<string[]>([]);
	let inputEl: HTMLInputElement | null = $state(null);

	const files = $derived.by<File[]>(() => {
		if (field.value == null) return [];
		const arr = multiple ? (Array.isArray(field.value) ? field.value : []) : [field.value];
		return arr.filter((v): v is File => v instanceof File);
	});

	/** Entrées normalisées de la valeur : File (sac défaut ou upload en cours)
	 * ET références serveur (strings, uploader branché). La liste éditable rend
	 * les deux — valueIndex pointe dans le tableau brut (suppression), et sert
	 * de composant d'index dans la clé d'état d'upload. */
	interface FileEntry {
		kind: 'file' | 'ref';
		valueIndex: number;
		file?: File;
		ref?: string;
		name: string;
		size?: number;
	}
	const entries = $derived.by<FileEntry[]>(() => {
		const v = field.value;
		if (v == null) return [];
		const arr: unknown[] = multiple ? (Array.isArray(v) ? v : []) : [v];
		const out: FileEntry[] = [];
		arr.forEach((x, i) => {
			if (x instanceof File) out.push({ kind: 'file', valueIndex: i, file: x, name: x.name, size: x.size });
			else if (typeof x === 'string' && x !== '') out.push({ kind: 'ref', valueIndex: i, ref: x, name: x });
		});
		return out;
	});

	/** Noms hydratés d'une entité (strings) — lecture seule : fichiers pas encore
	 * re-uploadés côté client. Une string URL est téléchargeable. */
	const existingNames = $derived.by<string[]>(() => {
		if (field.value == null) return [];
		const arr = multiple ? (Array.isArray(field.value) ? field.value : []) : [field.value];
		return arr.filter((v): v is string => typeof v === 'string');
	});
	
	const readonly = $derived(field.isReadonly || field.isDisabled);

	const isFileUrl = isFileUrlLike;

	// ── Upload en arrière-plan (si `uploader` injecté dans le formulaire) ──
	interface FileEntryState {
		progress: number; // 0–100 ; undefined si non tracké
		status: 'uploading' | 'done' | 'error';
		controller?: AbortController;
	}
	
	/** État d'upload indexé par `${field.name}:${f.name}:${f.size}:${index}`. */
	let uploadStates = $state<Record<string, FileEntryState>>({});
	const uploader = $derived(form?.getConfig().uploader);
	const uploading = $derived(
		Object.values(uploadStates).some((s) => s.status === 'uploading')
	);

	function entryKey(f: File, i: number): string {
		return `${field.name}:${f.name}:${f.size}:${i}`;
	}

	/** Lance l'upload d'un fichier ajouté ; à la réussite, remplace le File par
	 * la référence serveur dans la valeur du champ (le payload contiendra la ref,
	 * pas le fichier). À l'échec : File conservé → sac { files } au submit. */
	function startUpload(f: File, indexInValue: number) {
		if (!uploader) return;
		const key = entryKey(f, indexInValue);
		const controller = new AbortController();
		uploadStates[key] = { progress: 0, status: 'uploading', controller };
		uploader(f, {
			field: field.name,
			signal: controller.signal,
			onProgress: (p: UploadProgress) => {
				const st = uploadStates[key];
				if (st && p.total > 0) uploadStates[key] = { ...st, progress: Math.round((p.loaded / p.total) * 100) };
			}
		})
			.then((ref) => {
				const st = uploadStates[key];
				if (st?.status !== 'uploading') return; // annulé ou champ resetti
				uploadStates[key] = { ...st, status: 'done', progress: 100, controller: undefined };
				replaceWithRef(f, ref);
			})
			.catch(() => {
				const st = uploadStates[key];
				if (st?.status !== 'uploading') return;
				uploadStates[key] = { ...st, status: 'error', controller: undefined };
			});
	}

	/** Remplace l'entrée `File` (identité, pas position — le tableau peut avoir
	 * été réordonné/supprimé depuis le début de l'upload) par la référence
	 * serveur (string) — la valeur du champ devient la liste des refs. */
	function replaceWithRef(file: File, ref: unknown) {
		const current = field.value;
		let next: unknown;
		if (multiple) {
			const arr = Array.isArray(current) ? [...current] : [];
			const idx = arr.indexOf(file);
			if (idx >= 0) arr[idx] = ref;
			else arr.push(ref);
			next = arr;
		} else {
			next = ref;
		}
		field.setValue(next as any);
		config.onChange?.(next as any);
	}

	/** Annule un upload en cours (le File reste dans la valeur, en échec). */
	function abortUpload(key: string) {
		uploadStates[key]?.controller?.abort();
	}

	/** Téléchargement d'un File local : objectURL éphémère (révoqué après clic). */
	function downloadFile(f: File) {
		const url = URL.createObjectURL(f);
		const a = document.createElement('a');
		a.href = url;
		a.download = f.name;
		a.click();
		URL.revokeObjectURL(url);
	}

	function formatSize(bytes: number): string {
		if (bytes < 1024) return `${bytes} o`;
		if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(0)} Ko`;
		return `${(bytes / (1024 * 1024)).toFixed(1)} Mo`;
	}

	function acceptOk(f: File): boolean {
		if (!config.accept) return true;
		return config.accept.split(',').some((rule) => {
			const r = rule.trim().toLowerCase();
			if (r.endsWith('/*')) return f.type.toLowerCase().startsWith(r.slice(0, -1));
			if (r.startsWith('.')) return f.name.toLowerCase().endsWith(r);
			return f.type.toLowerCase() === r;
		});
	}

	function addFiles(incoming: FileList | File[] | null) {
		if (!incoming || readonly) return;
		rejected = [];
		const list = Array.from(incoming);
		const ok: File[] = [];
		for (const f of list) {
			if (!acceptOk(f) || (config.maxSize != null && f.size > config.maxSize)) {
				rejected.push(`${f.name} (${acceptOk(f) ? t('field.file.tooBig', { max: formatSize(config.maxSize!) }) : t('field.file.badType')})`);
				continue;
			}
			ok.push(f);
		}
		if (!ok.length) return;
		// Conserve les entrées existantes (Files ET refs déjà uploadées —
		// sinon un 2e ajout effacerait les refs) ; les nouveaux Files
		// s'ajoutent à la fin, leur index absolu = keep.length + j.
		const keep = multiple
			? (Array.isArray(field.value) ? field.value : []).filter(
					(x): x is File | string => x instanceof File || (typeof x === 'string' && x !== '')
				)
			: [];
		const next = multiple ? [...keep, ...ok] : [ok[0]];
		const value = multiple ? next : next[0];
		field.setValue(value as any);
		config.onChange?.(value as any);
		// Upload en arrière-plan dès la sélection (si uploader injecté) —
		// indexInValue = position absolue dans le tableau brut de la valeur.
		if (uploader) {
			const base = multiple ? keep.length : 0;
			ok.forEach((f, j) => startUpload(f, base + j));
		}
	}

	function removeAt(entry: FileEntry) {
		if (readonly) return;
		// Annule l'upload en cours éventuel (le × fait aussi « annuler »)
		if (entry.file) abortUpload(entryKey(entry.file, entry.valueIndex));
		const v = field.value;
		if (multiple) {
			const arr = Array.isArray(v) ? [...v] : [];
			arr.splice(entry.valueIndex, 1);
			field.setValue(arr as any);
			config.onChange?.(arr as any);
		} else {
			field.setValue(null as any);
			config.onChange?.(null as any);
		}
	}

	function onDrop(e: DragEvent) {
		dragOver = false;
		addFiles(e.dataTransfer?.files ?? null);
	}

	/** Noms affichés en lecture : fichiers locaux + strings hydratées. */
	const viewNames = $derived([...existingNames, ...files.map((f) => f.name)]);
</script>

<div class="grid gap-1.5 text-sm" data-field-wrapper={field.name}>
	<FieldLabel {config} {field} />
	{#if viewNames.length > 0 && readonly}
		<ul class="grid gap-1" role="list">
			{#each viewNames as name (name)}
				<li class="flex items-center gap-2 rounded-md border px-3 py-2 text-sm opacity-80">
					<AppIcon
						name={fileIconOf(name)}
						size={15}
						class="shrink-0 {fileColorOf(name)}"
					/>
					<span class="min-w-0 flex-1 truncate text-sm">{name}</span>
					{#if isFileUrl(name)}
						<a
							href={name}
							class="flex h-6 w-6 shrink-0 items-center justify-center rounded text-muted-foreground hover:bg-accent hover:text-foreground"
							aria-label={t('field.file.download')}
							title={t('field.file.download')}
							download
						>
							<AppIcon name="download" size={15} />
						</a>
					{/if}
				</li>
			{/each}
		</ul>
	{:else}
		<div
			class="flex min-h-20 cursor-pointer flex-col items-center justify-center gap-1 rounded-md border border-dashed p-4 text-center transition-colors
				{dragOver ? 'border-primary bg-accent/50' : 'border-border hover:border-primary/40 hover:bg-accent/30'}
				{field.isDisabled ? 'pointer-events-none opacity-50' : ''}"
			role="button"
			tabindex={field.isDisabled ? -1 : 0}
			aria-label={config.label ?? field.name}
			onclick={() => inputEl?.click()}
			onkeydown={(e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); inputEl?.click(); } }}
			ondragover={(e) => { e.preventDefault(); dragOver = true; }}
			ondragleave={() => (dragOver = false)}
			ondrop={onDrop}
		>
			<AppIcon name="upload" size={18} class="text-muted-foreground" />
			<span class="text-[0.85rem] text-muted-foreground">
				{multiple ? t('field.file.dropMultiple') : t('field.file.drop')}
			</span>
			{#if config.maxSize}
				<span class="text-[0.8rem] text-muted-foreground/70">
					{t('field.file.maxSizeHint', { max: formatSize(config.maxSize) })}
				</span>
			{/if}
		</div>
		<input
			bind:this={inputEl}
			id={inputId}
			data-field={field.name}
			type="file"
			class="hidden"
			{multiple}
			accept={config.accept}
			disabled={field.isDisabled}
			onchange={(e) => {
				addFiles((e.currentTarget as HTMLInputElement).files);
				(e.currentTarget as HTMLInputElement).value = '';
			}}
		/>
		{#if entries.length > 0}
			<ul class="grid gap-1" role="list">
				{#each entries as e (`${e.kind}:${e.valueIndex}:${e.name}`)}
					{@const st = e.file ? uploadStates[entryKey(e.file, e.valueIndex)] : undefined}
					<li class="flex items-center gap-2 rounded-md border bg-muted/30 px-3 py-1.5">
						<AppIcon
							name={fileIconOf(e.name, e.file?.type)}
							size={17}
							class="shrink-0 {fileColorOf(e.name, e.file?.type)}"
						/>
						<div class="min-w-0 flex-1">
							<div class="flex items-center gap-2">
								<span class="min-w-0 flex-1 truncate text-sm">{e.name}</span>
								{#if e.size != null}
									<span class="shrink-0 text-xs text-muted-foreground">{formatSize(e.size)}</span>
								{/if}
							</div>
							{#if st?.status === 'uploading'}
								<div class="mt-1 flex items-center gap-2">
									<div class="h-1 min-w-0 flex-1 overflow-hidden rounded-full bg-muted">
										<div
											class="h-full rounded-full bg-primary transition-[width] duration-200"
											style="width: {st.progress}%"
										></div>
									</div>
									<span class="shrink-0 text-[0.7rem] tabular-nums text-muted-foreground">{st.progress}%</span>
								</div>
							{/if}
						</div>
						{#if st?.status === 'uploading'}
							<AppIcon
								name="loading-circlex"
								size={15}
								class="shrink-0 animate-spin text-muted-foreground"
							/>
						{:else if st?.status === 'done'}
							<AppIcon name="check" size={15} class="shrink-0 text-emerald-600" />
						{:else if st?.status === 'error'}
							<AppIcon name="triangle-alert" size={15} class="shrink-0 text-amber-600" />
						{/if}
						{#if e.file}
							<button
								type="button"
								class="flex h-6 w-6 shrink-0 items-center justify-center rounded text-muted-foreground hover:bg-accent hover:text-foreground"
								aria-label={t('field.file.download')}
								title={t('field.file.download')}
								onclick={() => downloadFile(e.file!)}
							>
								<AppIcon name="download" size={15} />
							</button>
						{:else if e.ref && isFileUrl(e.ref)}
							<a
								href={e.ref}
								class="flex h-6 w-6 shrink-0 items-center justify-center rounded text-muted-foreground hover:bg-accent hover:text-foreground"
								aria-label={t('field.file.download')}
								title={t('field.file.download')}
								download
							>
								<AppIcon name="download" size={15} />
							</a>
						{/if}
						<button
							type="button"
							class="flex h-6 w-6 shrink-0 items-center justify-center rounded text-muted-foreground hover:bg-accent hover:text-destructive"
							aria-label={st?.status === 'uploading' ? t('field.file.cancelUpload') : t('field.file.remove')}
							onclick={() => removeAt(e)}
						>
							<AppIcon name="x" size={15} />
						</button>
					</li>
				{/each}
			</ul>
		{/if}
	{/if}
	{#if rejected.length > 0}
		<p class="text-[0.84rem] text-amber-600" role="alert">
			{rejected.join(' · ')}
		</p>
	{/if}
	<FieldMessages {config} {field} />
</div>
