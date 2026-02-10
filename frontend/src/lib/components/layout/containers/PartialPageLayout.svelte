<script lang="ts">
    import Logo from "@/components/layout/shell/Logo.svelte";

    let { children } = $props();
    
    const UserMenu = "UserMenu";

</script>

<section class="relative flex h-screen min-h-0 w-screen min-w-0 flex-col overflow-hidden">
    <main>
        <nav class="comet-header-height flex w-full items-center justify-between gap-6 border-b pl-4 pr-6">
            <div class="flex-1">
                <a href="/$workspaceName/home">
                    <Logo expanded={false} />
                </a>
            </div>

            {#if UserMenu}
                {UserMenu}
            {/if}
        </nav>

        <section class="comet-header-inset absolute inset-x-0 bottom-0 overflow-auto bg-white px-6">
            {#if children}
                {children()}
            {/if}
        </section>
    </main>
</section>


