// import { api } from '@/api/base'; // Temporairement désactivé pour les tests
import type {
	Candidate,
	Interview,
	JobOffer,
	CreateCandidateInput,
	UpdateCandidateInput,
	CreateInterviewInput,
	CreateJobOfferInput
} from '../types/types';

export const recruitmentService = {
	// Candidates
	async list(filters?: any) {
		// TODO: Implémenter avec API
		console.log('list candidates:', filters);
		return [];
	},

	async get(id: string) {
		// TODO: Implémenter avec API
		console.log('get candidate:', id);
		return null;
	},

	async create(data: CreateCandidateInput) {
		// TODO: Implémenter avec API
		console.log('create candidate:', data);
		return null;
	},

	async update(id: string, data: UpdateCandidateInput) {
		// TODO: Implémenter avec API
		console.log('update candidate:', id, data);
		return null;
	},

	async updateStage(id: string, stage: string) {
		// TODO: Implémenter avec API
		console.log('update candidate stage:', id, stage);
		return null;
	},

	async delete(id: string) {
		// TODO: Implémenter avec API
		console.log('delete candidate:', id);
	},

	// Interviews
	async listInterviews(candidateId?: string) {
		// TODO: Implémenter avec API
		console.log('list interviews:', candidateId);
		return [];
	},

	async createInterview(data: CreateInterviewInput) {
		// TODO: Implémenter avec API
		console.log('create interview:', data);
		return null;
	},

	async updateInterview(id: string, data: Partial<Interview>) {
		// TODO: Implémenter avec API
		console.log('update interview:', id, data);
		return null;
	},

	async deleteInterview(id: string) {
		// TODO: Implémenter avec API
		console.log('delete interview:', id);
	},

	// Job Offers
	async listOffers(candidateId?: string) {
		// TODO: Implémenter avec API
		console.log('list offers:', candidateId);
		return [];
	},

	async createOffer(data: CreateJobOfferInput) {
		// TODO: Implémenter avec API
		console.log('create offer:', data);
		return null;
	},

	async updateOffer(id: string, data: Partial<JobOffer>) {
		// TODO: Implémenter avec API
		console.log('update offer:', id, data);
		return null;
	},

	async sendOffer(id: string) {
		// TODO: Implémenter avec API
		console.log('send offer:', id);
		return null;
	},

	// File upload for resumes
	async uploadResume(file: File) {
		// TODO: Implémenter avec API
		console.log('upload resume:', file);
		return null;
	},

	// Generate video meeting links
	async generateVideoLink(interviewData: {
		candidateId: string;
		interviewerId: string;
		scheduledDate: string;
	}) {
		// TODO: Implémenter avec API
		console.log('generate video link:', interviewData);
		return null;
	}
};
