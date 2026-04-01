/**
 * Hook to observe the resize of an element DOM
 * @param onChange Function called when the element is resized
 * @param observeBody If true, also observes the document body
 */
export function useObserveResizeNode<NodeType extends HTMLElement>(
	onChange: (node: NodeType) => void,
	observeBody = false
) {
	let node = $state<NodeType | undefined>(undefined);

	// Function to initialize the observer when the node is available
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

			// Cleanup when the component is destroyed
			return () => {
				resizeObserver.disconnect();
			};
		}
	});

	// In Svelte, we can simply return a reference to the variable
	return {
		ref: node,
		// The function to set the reference
		setRef: (element: NodeType) => {
			node = element;
		}
	};
}
