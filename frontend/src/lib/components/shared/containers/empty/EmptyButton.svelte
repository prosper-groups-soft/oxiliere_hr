<script lang="ts">
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import { Button } from "@/components/ui/button";

  let {
    labelElement = 'un élément',
    onNew
  }: {
    labelElement: string,
    onNew: () => void,
  } = $props();
  
</script>


<Button variant="default" size="sm" onclick={onNew} class="shadow-fine bg-primary text-white text-[0.83rem] hover:text-white rounded-lg">
  <AppIcon name="plus" size={16} />
  Créer {labelElement}
</Button>

