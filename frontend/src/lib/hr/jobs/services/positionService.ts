import type { JobPosition, SeniorityLevel, SeniorityLevelDefinition } from '../types/types';

/**
 * Service utilitaire pour les opérations sur les positions
 * Contient les fonctions de calcul et de manipulation des données de position
 */

export class PositionService {
	/**
	 * Calcule la plage salariale complète d'une position à partir de tous ses niveaux de séniorité
	 */
	static getPositionSalaryRange(position: JobPosition): { min: number; max: number } | null {
		if (!position.seniority_levels || position.seniority_levels.length === 0) return null;
		const salaries = position.seniority_levels.map(ps => [ps.salary_min, ps.salary_max]).flat();
		return {
			min: Math.min(...salaries),
			max: Math.max(...salaries)
		};
	}

	/**
	 * Retourne la liste des niveaux de séniorité d'une position, triés par rang
	 */
	static getPositionSeniorityLevels(position: JobPosition): SeniorityLevel[] {
		return position.seniority_levels
			.sort((a, b) => a.rank - b.rank)
			.map(ps => ps.seniority_level.level);
	}

	/**
	 * Retourne le niveau de séniorité le plus bas d'une position
	 */
	static getMinSeniorityLevel(position: JobPosition): SeniorityLevelDefinition | null {
		if (!position.seniority_levels || position.seniority_levels.length === 0) return null;
		return position.seniority_levels.reduce((min, ps) => 
			ps.rank < min.rank ? ps : min, position.seniority_levels[0]
		).seniority_level;
	}

	/**
	 * Retourne le niveau de séniorité le plus élevé d'une position
	 */
	static getMaxSeniorityLevel(position: JobPosition): SeniorityLevelDefinition | null {
		if (!position.seniority_levels || position.seniority_levels.length === 0) return null;
		return position.seniority_levels.reduce((max, ps) => 
			ps.rank > max.rank ? ps : max, position.seniority_levels[0]
		).seniority_level;
	}

	/**
	 * Vérifie si une position a un niveau de séniorité spécifique
	 */
	static hasSeniorityLevel(position: JobPosition, level: SeniorityLevel): boolean {
		if (!position.seniority_levels || position.seniority_levels.length === 0) return false;
		return position.seniority_levels.some(ps => ps.seniority_level.level === level);
	}

	/**
	 * Retourne le salaire pour un niveau de séniorité spécifique
	 */
	static getSalaryForLevel(position: JobPosition, level: SeniorityLevel): { min: number; max: number } | null {
		if (!position.seniority_levels || position.seniority_levels.length === 0) return null;
		const seniorityLink = position.seniority_levels.find(ps => ps.seniority_level.level === level);
		if (!seniorityLink) return null;
		
		return {
			min: seniorityLink.salary_min,
			max: seniorityLink.salary_max
		};
	}

	/**
	 * Formate les niveaux de séniorité pour l'affichage (limité à un certain nombre)
	 */
	static formatSeniorityLevelsForDisplay(position: JobPosition, maxLevels: number = 3): {
		levels: typeof position.seniority_levels;
		hasMore: boolean;
		remainingCount: number;
	} {
		if (!position.seniority_levels || position.seniority_levels.length === 0) {
			return {
				levels: [],
				hasMore: false,
				remainingCount: 0
			};
		}

		// Créer une copie pour éviter la mutation d'état
		const sortedLevels = [...position.seniority_levels].sort((a, b) => a.rank - b.rank);
		const displayLevels = sortedLevels.slice(0, maxLevels);
		const hasMore = sortedLevels.length > maxLevels;
		const remainingCount = sortedLevels.length - maxLevels;

		return {
			levels: displayLevels,
			hasMore,
			remainingCount
		};
	}
}

export default PositionService;
