/**
 * Couleurs d'affichage des unités organisationnelles.
 *
 * Les unités sont dynamiques et viennent du backend, on ne peut donc pas les
 * mapper nom → couleur dans une table statique. On utilise plutôt une palette
 * déterministe : on hache le nom de l'unité pour choisir une couleur stable
 * dans le temps (le nom étant stable, la couleur l'est aussi entre deux rendus).
 */

export interface OrgUnitBadgeColor {
  bg: string;
  text: string;
  dot: string;
}

export const ORG_UNIT_PALETTES: OrgUnitBadgeColor[] = [
  { bg: 'bg-blue-50', text: 'text-blue-700', dot: 'bg-blue-500' },
  { bg: 'bg-rose-50', text: 'text-rose-700', dot: 'bg-rose-500' },
  { bg: 'bg-emerald-50', text: 'text-emerald-700', dot: 'bg-emerald-500' },
  { bg: 'bg-amber-50', text: 'text-amber-700', dot: 'bg-amber-500' },
  { bg: 'bg-indigo-50', text: 'text-indigo-700', dot: 'bg-indigo-500' },
  { bg: 'bg-cyan-50', text: 'text-cyan-700', dot: 'bg-cyan-500' },
  { bg: 'bg-violet-50', text: 'text-violet-700', dot: 'bg-violet-500' },
  { bg: 'bg-sky-50', text: 'text-sky-700', dot: 'bg-sky-500' },
  { bg: 'bg-fuchsia-50', text: 'text-fuchsia-700', dot: 'bg-fuchsia-500' },
  { bg: 'bg-orange-50', text: 'text-orange-700', dot: 'bg-orange-500' },
  { bg: 'bg-teal-50', text: 'text-teal-700', dot: 'bg-teal-500' },
  { bg: 'bg-lime-50', text: 'text-lime-700', dot: 'bg-lime-600' }
];

export function getOrgUnitColor(orgUnit: string): OrgUnitBadgeColor {
  let hash = 0;
  for (let i = 0; i < orgUnit.length; i++) {
    hash = orgUnit.charCodeAt(i) + ((hash << 5) - hash);
  }
  return ORG_UNIT_PALETTES[Math.abs(hash) % ORG_UNIT_PALETTES.length];
}
