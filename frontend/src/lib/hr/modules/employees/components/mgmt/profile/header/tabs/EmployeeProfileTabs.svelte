<script lang="ts">
  import NavTabs from "@/hr/navigation/components/NavTabs.svelte";
  import { hr } from '@/hr/constants/navigation/navigation';
  import { goto } from '$app/navigation';

  let { employeeId, activeTabId, counts }: { employeeId: string | number; activeTabId: string; counts: { education?: number; documents?: number } } = $props();

  const tabs = $derived([
    { id: 'profile', label: 'Profil', icon: 'user', path: hr(`/employees/${employeeId}`) },
    { id: 'contract', label: 'Contrat', icon: 'briefcase', path: hr(`/employees/${employeeId}/contract`) },
    { id: 'education', label: 'Éducation', icon: 'graduation-cap', path: hr(`/employees/${employeeId}/education`), count: counts.education },
    { id: 'family', label: 'Famille', icon: 'users', path: hr(`/employees/${employeeId}/family`) },
    { id: 'account', label: 'Accès', icon: 'shield', path: hr(`/employees/${employeeId}/account`) },
    { id: 'documents', label: 'Documents', icon: 'files', path: hr(`/employees/${employeeId}/documents`), count: counts.documents },
    { id: 'timeline', label: 'Parcours', icon: 'clock', path: hr(`/employees/${employeeId}/timeline`) }
  ]);
</script>

<NavTabs {tabs} activeId={activeTabId} variant="underline" />
