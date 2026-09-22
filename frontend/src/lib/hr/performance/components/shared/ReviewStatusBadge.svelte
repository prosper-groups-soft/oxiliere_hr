<script lang="ts">
	import { Badge } from '@/components/ui/badge';
	import type { ReviewStatus } from '../../types/types';
	import { REVIEW_STATUS_COLORS } from '../../constants';

	let {
		status,
		employeeSubmittedAt,
		managerSubmittedAt,
	}: {
		status: ReviewStatus;
		employeeSubmittedAt?: string | null;
		managerSubmittedAt?: string | null;
	} = $props();

	const colors = $derived(REVIEW_STATUS_COLORS[status] ?? REVIEW_STATUS_COLORS.EMPLOYEE_DRAFT);

	const label = $derived(
		status === 'EMPLOYEE_DRAFT'
			? employeeSubmittedAt && managerSubmittedAt
				? "Soumise"
				: employeeSubmittedAt
					? "En attente évaluateur"
					: managerSubmittedAt
						? "En attente employé"
						: "Auto-évaluation"
			: status === 'SUBMITTED'
				? "Soumise"
				: status === 'CALIBRATED'
					? "Soumise"
					: status === 'ACKNOWLEDGED'
						? "Approuvée"
						: status
	);
</script>


<Badge class="{colors.bg} {colors.text} rounded-full font-medium text-[0.83rem]">
	{label}
</Badge>

