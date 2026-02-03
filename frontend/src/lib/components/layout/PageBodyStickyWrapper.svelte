<script lang="ts">
    import { TABLE_WRAPPER_ATTRIBUTE } from "./constant";

    let { children } = $props();
</script>

<div
    class="comet-sticky-table border-b"
    {...{
    [TABLE_WRAPPER_ATTRIBUTE]: "",
    }}
>
    {@render children?.()}
</div>
