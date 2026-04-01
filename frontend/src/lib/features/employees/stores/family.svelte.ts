import type { EmergencyContact, Child } from '../types/types';

const MOCK_FAMILY = {
	emergencyContacts: [
		{
			id: 1,
			name: 'Marc Durand',
			relation: 'Époux',
			phone: '+33 6 12 34 56 78',
			primary: true
		},
		{
			id: 2,
			name: 'Julie Leroy',
			relation: 'Sœur',
			phone: '+33 6 98 76 54 32',
			primary: false
		}
	] as EmergencyContact[],
	children: [
		{
			id: 1,
			name: 'Léo',
			birthDate: '2018-05-12',
			gender: 'M'
		},
		{
			id: 2,
			name: 'Léa',
			birthDate: '2021-11-30',
			gender: 'F'
		}
	] as Child[]
};

class FamilyStore {
	emergencyContacts = $state<EmergencyContact[]>(MOCK_FAMILY.emergencyContacts);
	children = $state<Child[]>(MOCK_FAMILY.children);

	// Simple getters that return the raw data
	getEmergencyContacts() {
		return this.emergencyContacts;
	}

	getChildren() {
		return this.children;
	}

	// Mutations for Children
	addChild(child: Omit<Child, 'id'>) {
		const existingIds = this.children
			.map((c) => (typeof c.id === 'number' ? c.id : parseInt(c.id as string, 10)))
			.filter((id) => !isNaN(id));
		const newId = existingIds.length > 0 ? Math.max(...existingIds) + 1 : 1;
		this.children.push({ ...child, id: newId });
	}

	updateChild(id: number | string, updatedChild: Partial<Child>) {
		const index = this.children.findIndex((c) => c.id === id);
		if (index !== -1) {
			this.children[index] = { ...this.children[index], ...updatedChild };
		}
	}

	deleteChild(id: number | string) {
		this.children = this.children.filter((c) => c.id !== id);
	}

	// Mutations for Emergency Contacts
	addEmergencyContact(contact: Omit<EmergencyContact, 'id'>) {
		const existingIds = this.emergencyContacts
			.map((c) => (typeof c.id === 'number' ? c.id : parseInt(c.id as string, 10)))
			.filter((id) => !isNaN(id));
		const newId = existingIds.length > 0 ? Math.max(...existingIds) + 1 : 1;

		// If new contact is primary, unmark others
		if (contact.primary) {
			this.emergencyContacts.forEach((c) => (c.primary = false));
		}

		this.emergencyContacts.push({ ...contact, id: newId });
	}

	updateEmergencyContact(id: number | string, updatedContact: Partial<EmergencyContact>) {
		const index = this.emergencyContacts.findIndex((c) => c.id === id);
		if (index !== -1) {
			// If updating to primary, unmark others
			if (updatedContact.primary) {
				this.emergencyContacts.forEach((c) => (c.primary = false));
			}
			this.emergencyContacts[index] = { ...this.emergencyContacts[index], ...updatedContact };
		}
	}

	deleteEmergencyContact(id: number | string) {
		this.emergencyContacts = this.emergencyContacts.filter((c) => c.id !== id);
	}

	// Automatic derivative calculation
	countChildren = $derived(this.children.length);
	countEmergencyContacts = $derived(this.emergencyContacts.length);
}

export const familyStore = new FamilyStore();
