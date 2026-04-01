<script lang="ts">
  import PageActions from "./PageActions.svelte";

  /**
   * Props interface for PageTitle
   * Removed 'actions' snippet prop as it's now managed via ui.addActions() 
   * in the page components themselves.
   */
  interface Props {
    title?: string;
  }

  let { title = "" }: Props = $props();
</script>


<div class="flex items-center justify-between h-10 px-5 border-b border-[#F3F4F6] bg-white overflow-hidden">
  <!-- LEFT: Stable Page Title -->
  <h1 class="text-[0.89rem] font-bold tracking-tight text-slate-800 truncate">
    {title}
  </h1>

  <!-- RIGHT: Delegated Actions 
       Now consuming the ui.pageActions stack internally 
  -->
  <PageActions />
</div>

