// Champs métier RH (api §4 — catalogue §métier) : wrappers typés SANS dataSource par défaut.
// Principe standalone (vision §3) : forms ne connaît ni les endpoints ni les stores.
// La DataSource est injectée par l'appelant via config.dataSource (metamodel §7, api §7),
// ou via le registre registerType({ defaultDataSource }) (api §14).
// Exemple : orgUnit('ou', { dataSource: { type: 'function', fn: (p) => searchOrgUnits(p?.search) } })
import type { BusinessFieldConfig, FieldConfig } from '../core/types';


type Cfg = Partial<Omit<BusinessFieldConfig, 'id' | 'type'>>;

function biz(type: FieldConfig['type'], id: string, config?: Cfg): FieldConfig {
	return { ...config, id, type } as FieldConfig;
}

export const employee = (id: string, c?: Cfg) => biz('employee', id, c);
export const orgUnit = (id: string, c?: Cfg): FieldConfig =>
	biz('orgUnit', id, {
		placeholder: 'Sélectionner une unité organisationnelle…',
		...c
	});
export const manager = (id: string, c?: Cfg) => biz('manager', id, c);
export const contract = (id: string, c?: Cfg) => biz('contract', id, c);
export const position = (id: string, c?: Cfg) => biz('position', id, c);
export const organization = (id: string, c?: Cfg) => biz('organization', id, c);
export const branch = (id: string, c?: Cfg) => biz('branch', id, c);
export const country = (id: string, c?: Cfg) => biz('country', id, c);
export const city = (id: string, c?: Cfg) => biz('city', id, c);
export const leaveType = (id: string, c?: Cfg) => biz('leaveType', id, c);
export const payroll = (id: string, c?: Cfg) => biz('payroll', id, c);
export const seniorityLevel = (id: string, c?: Cfg) => biz('seniorityLevel', id, c);
export const jobFamily = (id: string, c?: Cfg) => biz('jobFamily', id, c);
export const workSite = (id: string, c?: Cfg) => biz('workSite', id, c);
export const group = (id: string, c?: Cfg) => biz('group', id, c);
export const bankInstitution = (id: string, c?: Cfg) => biz('bankInstitution', id, c);
export const gender = (id: string, c?: Cfg) => biz('gender', id, c);
export const maritalStatus = (id: string, c?: Cfg) => biz('maritalStatus', id, c);
export const contractType = (id: string, c?: Cfg) => biz('contractType', id, c);
export const remunerationType = (id: string, c?: Cfg) => biz('remunerationType', id, c);
export const paymentPeriod = (id: string, c?: Cfg) => biz('paymentPeriod', id, c);
export const salaryBaseType = (id: string, c?: Cfg) => biz('salaryBaseType', id, c);
export const initialStatus = (id: string, c?: Cfg) => biz('initialStatus', id, c);
export const documentType = (id: string, c?: Cfg) => biz('documentType', id, c);

/** Type custom enregistré au runtime (api §14 — ex: enums, types bancaires).
 * Le nom du type n'appartient pas à l'union statique `FieldConfig['type']`,
 * d'où le cast — la vérification fine se fait au rendu par le registre. */
export const regSelect = (type: string, id: string, c?: Cfg): FieldConfig =>
	({ ...c, id, type }) as unknown as FieldConfig;
