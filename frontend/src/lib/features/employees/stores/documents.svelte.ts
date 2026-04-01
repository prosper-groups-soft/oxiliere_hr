import type { Document } from '../types/types';

// Mock Data
const MOCK_DOCUMENTS: Document[] = [
	{
		id: 1,
		name: "Pièce d'Identité",
		type: 'PDF',
		size: '1.2 MB',
		expiry: '2026-05-20',
		status: 'valid'
	},
	{
		id: 2,
		name: 'Contrat de Travail',
		type: 'PDF',
		size: '4.5 MB',
		expiry: null,
		status: 'valid'
	},
	{
		id: 3,
		name: 'Attestation Mutuelle',
		type: 'JPG',
		size: '850 KB',
		expiry: '2026-02-15',
		status: 'warning'
	},
	{
		id: 4,
		name: 'Permis de Conduire',
		type: 'PDF',
		size: '2.1 MB',
		expiry: '2023-12-01',
		status: 'expired'
	},
	{
		id: 5,
		name: 'Certificat Médical',
		type: 'PDF',
		size: '980 KB',
		expiry: '2026-08-15',
		status: 'valid'
	},
	{
		id: 6,
		name: 'Diplôme',
		type: 'PDF',
		size: '2.8 MB',
		expiry: null,
		status: 'valid'
	},
	{
		id: 7,
		name: 'Photo Profil',
		type: 'PNG',
		size: '450 KB',
		expiry: null,
		status: 'valid'
	}
];

export class DocumentStore {
	documents = $state<Document[]>(MOCK_DOCUMENTS);

	getById(id: string | number): Document | undefined {
		const numId = typeof id === 'string' ? parseInt(id, 10) : id;
		return this.documents.find((doc) => doc.id === numId);
	}

	getDocuments(): Document[] {
		return this.documents;
	}

	addDocument(doc: Omit<Document, 'id'>) {
		const existingIds = this.documents
			.map((d) => (typeof d.id === 'number' ? d.id : parseInt(d.id as string, 10)))
			.filter((id) => !isNaN(id));
		const newId = existingIds.length > 0 ? Math.max(...existingIds) + 1 : 1;

		this.documents.push({
			...doc,
			id: newId,
			status: this.calculateStatus(doc.expiry)
		});
	}

	updateDocument(id: number | string, updatedDoc: Partial<Document>) {
		const index = this.documents.findIndex((d) => d.id === id);
		if (index !== -1) {
			const doc = { ...this.documents[index], ...updatedDoc };
			// Recalculate status if expiry changed
			if (updatedDoc.expiry !== undefined) {
				doc.status = this.calculateStatus(doc.expiry);
			}
			this.documents[index] = doc;
		}
	}

	deleteDocument(id: number | string) {
		this.documents = this.documents.filter((d) => d.id !== id);
	}

	private calculateStatus(expiry: string | null): 'valid' | 'warning' | 'expired' {
		if (!expiry) return 'valid';

		const today = new Date();
		const expiryDate = new Date(expiry);

		if (expiryDate < today) return 'expired';

		const threeMonthsFromNow = new Date();
		threeMonthsFromNow.setMonth(today.getMonth() + 3);

		if (expiryDate < threeMonthsFromNow) return 'warning';

		return 'valid';
	}
}

// Create a global instance if needed,
// or instantiate in component context context
export const documentStore = new DocumentStore();
