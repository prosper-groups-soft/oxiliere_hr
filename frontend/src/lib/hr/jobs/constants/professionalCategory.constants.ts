/**
 * Constants — Grille des catégories professionnelles RDC (catalogue.md §6)
 *
 * 7 classes × 4 échelons. Libellés alignés avec la fixture
 * backend/hr/fixtures/payroll/cd/professional_categories.json
 * et l'écran S8 « Classes & Échelons » (payroll-settings).
 */

export interface ProfessionalClass {
	/** Numéro de classe (1-7) */
	classe: number;
	/** Libellé de la classe (catalogue §6) */
	label: string;
	/** Profil de personnel concerné */
	application: string;
}

/** Les 7 classes professionnelles légales RDC (catalogue §6) */
export const PROFESSIONAL_CLASSES: ProfessionalClass[] = [
	{ classe: 1, label: 'Manœuvre ordinaire', application: 'Personnel non qualifié' },
	{ classe: 2, label: 'Ouvrier spécialisé', application: 'Personnel avec formation de base' },
	{ classe: 3, label: 'Ouvrier qualifié / Agent de maîtrise', application: 'Personnel avec qualification technique' },
	{ classe: 4, label: 'Agent de maîtrise supérieur / Technicien', application: 'Personnel avec diplôme technique' },
	{ classe: 5, label: 'Cadre subalterne', application: 'Personnel avec diplôme universitaire (BAC+2/3)' },
	{ classe: 6, label: 'Cadre moyen', application: 'Personnel avec BAC+4/5' },
	{ classe: 7, label: 'Cadre supérieur / Cadre de collaboration', application: 'Personnel avec haute qualification' },
];

/** Les 4 échelons intra-classe (1-4) */
export const PROFESSIONAL_ECHELONS: number[] = [1, 2, 3, 4];

/** Libellé d'une classe (retourne le libellé ou une valeur par défaut) */
export function getProfessionalClassLabel(classe: number | null | undefined): string {
	if (classe == null) return '—';
	return PROFESSIONAL_CLASSES.find((c) => c.classe === classe)?.label ?? `Classe ${classe}`;
}

/** Libellé court « Classe X · Éch. Y » pour l'affichage des grilles */
export function formatClassEchelon(classe: number | null | undefined, echelon: number | null | undefined): string {
	if (classe == null && echelon == null) return '—';
	const parts: string[] = [];
	if (classe != null) parts.push(`Cl. ${classe}`);
	if (echelon != null) parts.push(`Éch. ${echelon}`);
	return parts.join(' · ');
}
