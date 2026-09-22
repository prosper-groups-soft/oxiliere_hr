/**
 * Guards de sécurité pour la gestion des permissions
 * Protège contre les actions qui pourraient casser le système
 */

import { SYSTEM_GROUPS } from '../constants/access.constants';


function isSystemGroup(slug: string): boolean {
  return SYSTEM_GROUPS.includes(slug as typeof SYSTEM_GROUPS[number]);
}


/**
 * Vérifie si un rôle est verrouillé (non modifiable)
 * @param slug - Slug du rôle
 */
export function isLockedRole(slug: string): boolean {
	return slug === 'admin';
}


/**
 * Guard 1: Empêche un utilisateur de se révoquer son propre groupe administrateur
 * @param currentUserId - ID de l'utilisateur connecté
 * @param targetUserId - ID de l'utilisateur cible de l'action
 * @param groupSlug - Slug du groupe à révoquer
 * @returns { canProceed: boolean; message?: string }
 */
export function guardSelfGroupRevoke(
	currentUserId: string,
	targetUserId: string,
	groupSlug: string
): { canProceed: boolean; message?: string } {
	// Si c'est le même utilisateur et un groupe système
	if (currentUserId === targetUserId && isSystemGroup(groupSlug)) {
		return {
			canProceed: false,
			message: `Vous ne pouvez pas vous retirer du groupe "${groupSlug}". Cela vous bloquerait l'accès administrateur. Demandez à un autre admin de le faire.`
		};
	}
	return { canProceed: true };
}


/**
 * Guard 2: Empêche de retirer le dernier membre d'un groupe système critique
 * @param groupSlug - Slug du groupe
 * @param currentMemberCount - Nombre actuel de membres dans le groupe
 * @returns { canProceed: boolean; message?: string }
 */
export function guardLastMemberRemoval(
	groupSlug: string,
	currentMemberCount: number
): { canProceed: boolean; message?: string } {
	// Si c'est un groupe système et qu'il ne reste qu'un seul membre
	if (isSystemGroup(groupSlug) && currentMemberCount <= 1) {
		return {
			canProceed: false,
			message: `Impossible de retirer le dernier membre du groupe "${groupSlug}". Ce groupe système doit toujours avoir au moins un membre pour garantir l'accès administrateur.`
		};
	}
	return { canProceed: true };
}


/**
 * Guard 3: Empêche la suppression d'un groupe système avec des membres
 * @param groupSlug - Slug du groupe à supprimer
 * @param memberCount - Nombre de membres dans le groupe
 * @returns { canProceed: boolean; message?: string }
 */
export function guardSystemGroupDelete(
	groupSlug: string,
	memberCount: number
): { canProceed: boolean; message?: string } {
	// Si c'est un groupe système avec des membres
	if (isSystemGroup(groupSlug) && memberCount > 0) {
		return {
			canProceed: false,
			message: `Le groupe "${groupSlug}" est un groupe système avec ${memberCount} membre(s). Vous devez d'abord retirer tous les membres avant de pouvoir le supprimer.`
		};
	}
	return { canProceed: true };
}


/**
 * Guard 3b: Empêche la suppression d'un groupe système (même sans membres, avertissement)
 * @param groupSlug - Slug du groupe à supprimer
 * @returns { canProceed: boolean; warning?: string }
 */
export function guardSystemGroupDeleteWarning(
	groupSlug: string
): { canProceed: boolean; warning?: string } {
	if (isSystemGroup(groupSlug)) {
		return {
			canProceed: true,
			warning: `ATTENTION: "${groupSlug}" est un groupe système. Sa suppression pourrait affecter la gestion des accès. Êtes-vous sûr ?`
		};
	}
	return { canProceed: true };
}


/**
 * Vérifie si l'utilisateur courant est le dernier admin avec access:w
 * @param currentUserId - ID de l'utilisateur connecté
 * @param allUsersWithAdminAccess - Liste des utilisateurs avec rôle admin et scope access:w
 * @returns { canProceed: boolean; message?: string }
 */
export function guardLastAdmin(
	currentUserId: string,
	allUsersWithAdminAccess: { id: string; email: string }[]
): { canProceed: boolean; message?: string } {
	if (allUsersWithAdminAccess.length === 1 && allUsersWithAdminAccess[0].id === currentUserId) {
		return {
			canProceed: false,
			message: 'Vous êtes le dernier administrateur avec droits d\'écriture sur la gestion des accès. Cette action est bloquée pour éviter de vous exclure du système.'
		};
	}
	return { canProceed: true };
}


/**
 * Guard 4: Empêche de retirer les droits administrateur au dernier admin
 * @param isCurrentlyAdmin - Si l'utilisateur est actuellement admin
 * @param adminCount - Nombre total d'admins dans le système
 * @param newValue - Nouvelle valeur (true = activer, false = désactiver)
 * @returns { canProceed: boolean; message?: string }
 */
export function guardLastAdminRoleToggle(
	isCurrentlyAdmin: boolean,
	adminCount: number,
	newValue: boolean
): { canProceed: boolean; message?: string } {
	// Permet d'activer (newValue = true)
	if (newValue) {
		return { canProceed: true };
	}
	// Empêche de désactiver si c'est le dernier admin
	if (isCurrentlyAdmin && adminCount <= 1) {
		return {
			canProceed: false,
			message: 'Impossible de retirer les droits administrateur au dernier administrateur'
		};
	}
	return { canProceed: true };
}


/**
 * Guard 5: Empêche de retirer les droits propriétaire au dernier owner
 * @param isCurrentlyOwner - Si l'utilisateur est actuellement propriétaire
 * @param ownerCount - Nombre total de propriétaires dans le système
 * @param newValue - Nouvelle valeur (true = activer, false = désactiver)
 * @returns { canProceed: boolean; message?: string }
 */
export function guardLastOwnerRoleToggle(
	isCurrentlyOwner: boolean,
	ownerCount: number,
	newValue: boolean
): { canProceed: boolean; message?: string } {
	// Permet d'activer (newValue = true)
	if (newValue) {
		return { canProceed: true };
	}
	// Empêche de désactiver si c'est le dernier owner
	if (isCurrentlyOwner && ownerCount <= 1) {
		return {
			canProceed: false,
			message: 'Impossible de retirer les droits propriétaire au dernier propriétaire'
		};
	}
	return { canProceed: true };
}


/**
 * Guard 6: Empêche de désactiver le compte du dernier admin ou owner
 * @param isCurrentlyActive - Si le compte est actuellement actif
 * @param isAdmin - Si l'utilisateur est admin
 * @param isOwner - Si l'utilisateur est propriétaire
 * @param adminCount - Nombre total d'admins
 * @param ownerCount - Nombre total de propriétaires
 * @param newValue - Nouvelle valeur (true = activer, false = désactiver)
 * @returns { canProceed: boolean; message?: string }
 */
export function guardLastPrivilegedUserDisable(
	isCurrentlyActive: boolean,
	isAdmin: boolean,
	isOwner: boolean,
	adminCount: number,
	ownerCount: number,
	newValue: boolean
): { canProceed: boolean; message?: string } {
	// Permet d'activer (newValue = true)
	if (newValue) {
		return { canProceed: true };
	}
	// Vérifie si on essaie de désactiver un compte privilégié
	if (isCurrentlyActive) {
		if (isAdmin && adminCount <= 1) {
			return {
				canProceed: false,
				message: 'Impossible de désactiver le dernier administrateur'
			};
		}
		if (isOwner && ownerCount <= 1) {
			return {
				canProceed: false,
				message: 'Impossible de désactiver le dernier propriétaire'
			};
		}
	}
	return { canProceed: true };
}


/**
 * Helper pour vérifier les permissions avant une action critique
 * @param currentUser - Utilisateur connecté
 * @param action - Type d'action
 * @param params - Paramètres de l'action
 */
export async function validateCriticalAction(
	currentUser: { id: string; email: string },
	action: 'revoke-group' | 'delete-group',
	params: { targetUserId?: string; groupSlug: string; memberCount?: number }
): Promise<{ canProceed: boolean; message?: string; warning?: string }> {
	switch (action) {
		case 'revoke-group': {
			if (!params.targetUserId) {
				return { canProceed: false, message: 'ID utilisateur cible requis' };
			}
			
			// Guard 1: Auto-révocation de groupe système
			const selfRevokeCheck = guardSelfGroupRevoke(
				currentUser.id,
				params.targetUserId,
				params.groupSlug
			);
			if (!selfRevokeCheck.canProceed) {
				return selfRevokeCheck;
			}
			
			return { canProceed: true };
		}
		
		case 'delete-group': {
			if (params.memberCount === undefined) {
				return { canProceed: false, message: 'Nombre de membres requis' };
			}
			
			// Guard 3: Groupe système avec membres
			const systemGroupCheck = guardSystemGroupDelete(
				params.groupSlug,
				params.memberCount
			);
			if (!systemGroupCheck.canProceed) {
				return systemGroupCheck;
			}
			
			// Warning si groupe système même sans membres
			const warningCheck = guardSystemGroupDeleteWarning(params.groupSlug);
			if (warningCheck.warning) {
				return warningCheck;
			}
			
			return { canProceed: true };
		}
		
		default:
			return { canProceed: true };
	}
}

