src/routes/
  |-- employees/
      |-- +page.svelte        <-- C'est ton "Command Center" (Vue Liste)
      |-- [id]/               
          |-- +layout.svelte  <-- Le Header "Identité" du Profil 360°
          |-- +page.svelte    <-- L'onglet principal (Infos perso)
          |-- vault/
              |-- +page.svelte <-- L'onglet Documents
          |-- family/
              |-- +page.svelte <-- Le Hub Famille
      |-- onboarding/
          |-- +page.svelte    <-- L'assistant multi-étapes
      |-- +layout.svelte    <-- Le Header "Identité" du Profil 360°

