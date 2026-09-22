import { vacancyEndpoint } from '../api/vacancy.endpoints';
import type { Vacancy, VacancyPriority, VacancyStatus } from '../types/types';
import { notification } from '@/hr/stores/notification.svelte';
import { getFriendlyErrorMessage } from '@/hr/constants/errors';


class VacancyService {
	async listVacancies(params: {
		page?: number;
		per_page?: number;
		search?: string;
		priority?: VacancyPriority;
		status?: VacancyStatus;
	} = {}) {
		try {
			return await vacancyEndpoint.list(
				params.priority,
				params.status,
				params.page,
				params.per_page,
				params.search
			);
		} catch (error: any) {
			console.error('[VacancyService] Error listing vacancies:', error);
			const message = getFriendlyErrorMessage(error);
			notification.toast.error(message);
			throw error;
		}
	}

	async getVacancy(id: string): Promise<Vacancy> {
		try {
			return await vacancyEndpoint.get(id);
		} catch (error: any) {
			console.error('[VacancyService] Error getting vacancy:', error);
			const message = getFriendlyErrorMessage(error);
			notification.toast.error(message);
			throw error;
		}
	}

	async createVacancy(data: {
		position_id: string;
		priority: VacancyPriority;
		status: VacancyStatus;
		opened_date?: string;
		target_date?: string | null;
		reason?: string;
	}): Promise<Vacancy> {
		try {
			const vacancy = await vacancyEndpoint.create(data);
			notification.toast.success('Besoin créé avec succès');
			return vacancy;
		} catch (error: any) {
			console.error('[VacancyService] Error creating vacancy:', error);
			const message = getFriendlyErrorMessage(error);
			notification.toast.error(message);
			throw error;
		}
	}

	async updateVacancy(id: string, data: Partial<{
		position_id: string;
		priority: VacancyPriority;
		status: VacancyStatus;
		opened_date: string;
		target_date: string | null;
		reason: string;
		filled_date: string | null;
	}>): Promise<Vacancy> {
		try {
			const vacancy = await vacancyEndpoint.update(id, data);
			notification.toast.success('Besoin mis à jour avec succès');
			return vacancy;
		} catch (error: any) {
			console.error('[VacancyService] Error updating vacancy:', error);
			const message = getFriendlyErrorMessage(error);
			notification.toast.error(message);
			throw error;
		}
	}

	async deleteVacancy(id: string): Promise<void> {
		try {
			await vacancyEndpoint.delete(id);
			notification.toast.success('Besoin supprimé');
		} catch (error: any) {
			console.error('[VacancyService] Error deleting vacancy:', error);
			const message = getFriendlyErrorMessage(error);
			notification.toast.error(message);
			throw error;
		}
	}

	async closeVacancy(id: string, transition_id?: string): Promise<Vacancy> {
		try {
			const vacancy = await vacancyEndpoint.close(id, transition_id);
			notification.toast.success('Besoin marqué comme pourvu');
			return vacancy;
		} catch (error: any) {
			console.error('[VacancyService] Error closing vacancy:', error);
			const message = getFriendlyErrorMessage(error);
			notification.toast.error(message);
			throw error;
		}
	}
}


export const vacancyService = new VacancyService();
