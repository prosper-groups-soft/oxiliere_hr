import { writable } from "svelte/store";



export let sideBarExpanded = writable(true);
export let selectedMenuItem = writable<string | null>("home");
export let initialLoading = writable(true);


export function activePage(page: string) {
    selectedMenuItem.set(page);
    initialLoading.set(false);
}

