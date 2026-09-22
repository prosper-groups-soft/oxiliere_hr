// Helpers d'upload & de payload (api §4/§7, catalogue `file`) :
//  - xhrUploader : UploadHandler prêt à l'emploi (XHR) avec progression
//    (upload.onprogress) et annulation (AbortSignal → xhr.abort()).
//  - buildFormData : conversion data (+ files) en FormData multipart —
//    pour les backends qui préfèrent un seul appel multipart au JSON + upload.
import type { UploadHandler, UploadProgress } from '../core/types.js';

/** UploadHandler XHR : POST le fichier vers `endpoint` (champ multipart
 * `fieldName`, défaut 'file'), progression via onProgress, annulation via le
 * signal. Résout avec la réponse JSON du serveur (référence à stocker). */
export function xhrUploader(
	endpoint: string,
	opts?: { fieldName?: string; headers?: Record<string, string> }
): UploadHandler {
	const fieldName = opts?.fieldName ?? 'file';
	return (file, ctx) =>
		new Promise((resolve, reject) => {
			const xhr = new XMLHttpRequest();
			xhr.open('POST', endpoint);
			for (const [k, v] of Object.entries(opts?.headers ?? {})) {
				xhr.setRequestHeader(k, v);
			}
			const onAbort = () => {
				xhr.abort();
				reject(new Error('upload aborted'));
			};
			ctx.signal?.addEventListener('abort', onAbort, { once: true });
			xhr.upload.onprogress = (e) => {
				if (e.lengthComputable) {
					ctx.onProgress?.({ loaded: e.loaded, total: e.total } satisfies UploadProgress);
				}
			};
			xhr.onload = () => {
				ctx.signal?.removeEventListener('abort', onAbort);
				if (xhr.status >= 200 && xhr.status < 300) {
					try {
						resolve(JSON.parse(xhr.responseText));
					} catch {
						resolve(xhr.responseText);
					}
				} else {
					reject(new Error(`upload failed: HTTP ${xhr.status}`));
				}
			};
			xhr.onerror = () => reject(new Error('upload failed'));
			const body = new FormData();
			body.append(fieldName, file);
			xhr.send(body);
		});
}

/** Convertit le payload (`data`) + le sac de fichiers (`files`) en FormData
 * multipart — un seul appel backend quand il n'y a pas d'upload 2-phases.
 * Tableaux → une entrée par élément (clés `k[i]`) ; Date → ISO. */
export function buildFormData<T extends Record<string, any>>(
	data: T,
	files?: Record<string, File[]>
): FormData {
	const fd = new FormData();
	for (const [k, v] of Object.entries(data)) {
		if (v === null || v === undefined) continue;
		if (Array.isArray(v)) {
			v.forEach((item, i) => {
				fd.append(`${k}[${i}]`, item instanceof Date ? item.toISOString() : String(item));
			});
		} else if (v instanceof Date) {
			fd.append(k, v.toISOString());
		} else if (typeof v === 'object') {
			fd.append(k, JSON.stringify(v));
		} else {
			fd.append(k, String(v));
		}
	}
	for (const [k, list] of Object.entries(files ?? {})) {
		for (const f of list) fd.append(k, f, f.name);
	}
	return fd;
}
