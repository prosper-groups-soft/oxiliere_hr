import { goto } from '$app/navigation';
import { hr } from '@/hr/constants/navigation/navigation';
import { payrollStore } from '@/hr/modules/payroll/stores/payroll.svelte';


/**
 * Ouvre le workspace de paie :
 * - si un run est déjà en cours → redirige vers `/payroll/run` (sans en créer un autre)
 * - sinon → démarre une nouvelle paie (onglet dynamique « Nouvelle paie ») puis y navigue
 */
export function goToActiveOrNewPayroll() {
	if (!payrollStore.hasActiveRun) {
		payrollStore.beginNewRun();
	}
	return goto(hr('/payroll/run'));
}

