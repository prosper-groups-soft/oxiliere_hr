<script lang="ts" generics="TData">
    import {
        type Column,
    } from "@tanstack/table-core";
    import * as DropdownMenu from "@/components/ui/dropdown-menu/index.js";
    import { Button } from "@/components/ui/button/index.js";
    import ArrowUpIcon from "@lucide/svelte/icons/arrow-up";
    import ArrowDownIcon from "@lucide/svelte/icons/arrow-down";
    import ChevronsUpDownIcon from "@lucide/svelte/icons/chevrons-up-down";
    import EyeOffIcon from "@lucide/svelte/icons/eye-off";
    import type { HTMLAttributes } from "svelte/elements";
    import { cn } from "$lib/utils.js";


    const {
        column,
        title,
        class: className,
        ...restProps
    }: { column: Column<TData>; title: string } & HTMLAttributes<HTMLDivElement> = $props();
</script>


{#if !column?.getCanSort()}
    <div class={className} {...restProps}>
        {title}
    </div>
{:else}
    <div class={cn("flex items-center", className)} {...restProps}>
        <DropdownMenu.Root>
            <DropdownMenu.Trigger>
                {#snippet child({ props })}
                    <Button
                        {...props}
                        variant="ghost"
                        size="sm"
                        class="data-[state=open]:bg-accent -ml-3 h-8"
                    >
                        <span>
                            {title}
                        </span>
                        {#if column.getIsSorted() === "desc"}
                            <ArrowDownIcon />
                        {:else if column.getIsSorted() === "asc"}
                            <ArrowUpIcon />
                        {:else}
                            <ChevronsUpDownIcon />
                        {/if}
                    </Button>
                {/snippet}
            </DropdownMenu.Trigger>
            <DropdownMenu.Content align="start">
                <DropdownMenu.Item onclick={() => column.toggleSorting(false)}>
                    <ArrowUpIcon class="text-muted-foreground/70 mr-2 size-3.5" />
                    Asc
                </DropdownMenu.Item>
                <DropdownMenu.Item onclick={() => column.toggleSorting(true)}>
                    <ArrowDownIcon class="text-muted-foreground/70 mr-2 size-3.5" />
                    Desc
                </DropdownMenu.Item>
                <DropdownMenu.Separator />
                <DropdownMenu.Item onclick={() => column.toggleVisibility(false)}>
                    <EyeOffIcon class="text-muted-foreground/70 mr-2 size-3.5" />
                    Cacher
                </DropdownMenu.Item>
            </DropdownMenu.Content>
        </DropdownMenu.Root>
    </div>
{/if}
