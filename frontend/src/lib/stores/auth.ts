import type { Organization } from '@/types/organization';
import type { SessionUser } from '@/types/users';
import { get, writable } from 'svelte/store'
import type { Writable } from 'svelte/store';
import {createPersistentStore} from './base';
import { OXILIERE_LABEL } from '@/constants/base';



export const current_organization_store: Writable<Organization | null> = writable();
export const current_user_store: Writable<SessionUser | null> = createPersistentStore<SessionUser | null>('current_user', null);
export const auth_required : Writable<boolean> = createPersistentStore<boolean>('auth_required', false);
export const user_logging_out : Writable<boolean> = createPersistentStore<boolean>('user_logging_out', false);


export function getOrganizationName(){
    const _org = get(current_organization_store);
    return _org && _org.name ? _org.name : OXILIERE_LABEL;
};
