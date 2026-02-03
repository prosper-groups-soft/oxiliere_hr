/**
 * useObserveResizeNode.ts
 * Version Svelte 5 de la fonction d'observation des redimensionnements
 */

/**
 * Hook pour observer les changements de taille d'un élément DOM
 * @param onChange Fonction appelée lorsque l'élément est redimensionné
 * @param observeBody Si true, observe également le body du document
 */
export function useObserveResizeNode<NodeType extends HTMLElement>(
    onChange: (node: NodeType) => void,
    observeBody = false,
  ) {
    // En Svelte 5, on utilise $state au lieu de useState
    let node = $state<NodeType | undefined>(undefined);
    
    // Fonction pour initialiser l'observateur quand le nœud est disponible
    $effect(() => {
      if (node) {
        const resizeObserver = new ResizeObserver(() => {
          window.requestAnimationFrame(() => {
            if (node) {
              onChange(node);
            }
          });
        });
  
        resizeObserver.observe(node as unknown as Element);
        if (observeBody) {
          resizeObserver.observe(window.document.body);
        }
  
        // Nettoyage lors de la destruction du composant
        return () => {
          resizeObserver.disconnect();
        };
      }
    });
  
    // En Svelte, on peut simplement retourner une référence à la variable
    return { 
      ref: node, 
      // La fonction pour définir la référence
      setRef: (element: NodeType) => {
        node = element;
      } 
    };
}
