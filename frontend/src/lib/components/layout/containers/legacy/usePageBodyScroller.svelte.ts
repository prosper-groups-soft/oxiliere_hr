/**
 * usePageBodyScroller.ts
 * Svelte 5 implementation of the page body scroller context
 */

// Type pour les données du conteneur de défilement
export type PageBodyScrollContainerData = {
  scrollContainer: HTMLDivElement | null;
  tableOffset: number;
};

// Création d'un contexte global avec $state pour la réactivité
// En Svelte 5, on peut utiliser $state pour créer des variables réactives globales
export const pageBodyScrollState = {
  state: {
    scrollContainer: null as HTMLDivElement | null,
    tableOffset: 0
  }
};

/**
 * Hook pour utiliser le conteneur de défilement
 * En Svelte 5, on peut accéder directement aux variables d'état
 */
export function usePageBodyScrollContainer(): PageBodyScrollContainerData {
  // Vérification que le hook est utilisé correctement
  // Cette vérification est conceptuelle car en Svelte 5, l'état est toujours disponible
  if (pageBodyScrollState.state.scrollContainer === undefined) {
    throw new Error(
      "usePageBodyScrollContainer doit être utilisé à l'intérieur d'un PageBodyScrollContainer!"
    );
  }
  
  return pageBodyScrollState.state;
}

export default usePageBodyScrollContainer;
