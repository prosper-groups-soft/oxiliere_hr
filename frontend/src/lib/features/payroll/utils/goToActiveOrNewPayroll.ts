import { goto } from '$app/navigation';
import { payrollStore } from '@/features/payroll/stores/payroll.svelte';


/**
 * Ouvre le workspace de paie :
 * - si un run est déjà en cours → redirige vers `/payroll/run` (sans en créer un autre)
 * - sinon → démarre une nouvelle paie (onglet dynamique « Nouvelle paie ») puis y navigue
 */
export function goToActiveOrNewPayroll() {
	if (!payrollStore.hasActiveRun) {
		payrollStore.beginNewRun();
	}
	return goto('/payroll/run');
}

