import type { CurrentOrganization } from "@/types/organization";
import store, { type StoreType } from "store2";
import {writable, type Writable} from 'svelte/store';


export function get_application_namespace(org?: CurrentOrganization): string | undefined{
  return org?.slug ? org?.slug : undefined; 
};


export function get_store(org?: CurrentOrganization, namespaced?: boolean){
  if (!namespaced) return store; // return de default store.

  const namespace = get_application_namespace(org);
  return namespace ? store.namespace(namespace) : store;
};


export function createPersistentStore<T>(key: string, initialValue: T, _store?: StoreType){
  const storage = _store ? _store : get_store();

  const wstore: Writable<T> = writable(initialValue, ()=>{

    if (typeof window !== 'undefined'){
        const savedValue = storage.get(key);
        if (savedValue !== null) {
            wstore.set(savedValue);
        }
    }

    const unsubscribe = wstore.subscribe((value: T)=> {
      if (typeof window !== 'undefined') {
        storage.set(key, value);
      }
    });

    return unsubscribe;
  });

  return wstore;
};

