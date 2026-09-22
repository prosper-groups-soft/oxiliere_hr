const API_BASE_URL = import.meta.env.VITE_PUBLIC_API_BASE_URL;
const MEDIA_PREFIX = 'media/';


/**
 * Formate un chemin de média en URL complète.
 *
 * Conventions gérées :
 * - chemin HTTP(s) → renvoyé tel quel ;
 * - chemin déjà complet relatif à l'origine (commence par « / ») → inchangé ;
 * - chemin relatif « media/… » (ex. retourné par profile_photo.url) → inchangé ;
 * - nom brut « employee_photos/… » (ex. photo_path des bulletins) → préfixé
 *   `media/` pour produire une URL résoluble (/media/…), conformément à
 *   MEDIA_URL côté backend.
 */
export function getMediaUrl(path: string | null | undefined): string | undefined {
    if (!path) return undefined;
    if (path.startsWith('http')) return path;
    if (path.startsWith('/')) return `${API_BASE_URL}${path}`;

    const clean = path.startsWith(MEDIA_PREFIX) ? path : `${MEDIA_PREFIX}${path}`;
    return `${API_BASE_URL}/${clean}`;
}

