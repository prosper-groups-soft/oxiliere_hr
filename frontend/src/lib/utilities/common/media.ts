const API_BASE_URL = import.meta.env.VITE_PUBLIC_API_BASE_URL;


/**
 * Formate un chemin de média en URL complète
 */
export function getMediaUrl(path: string | null | undefined): string | undefined {
    if (!path) return undefined;
    if (path.startsWith('http')) return path;

    const cleanPath = path.startsWith('/') ? path : `/${path}`;
    return `${API_BASE_URL}${cleanPath}`;
}

