<script lang="ts">

    import {
        Breadcrumb,
        BreadcrumbItem,
        BreadcrumbLink,
        BreadcrumbList,
        BreadcrumbSeparator,
    } from "$lib/components/ui/breadcrumb";


    const items: any[] = [];

</script>


<Breadcrumb>
    <BreadcrumbList>
    <BreadcrumbItem>
        <BreadcrumbLink>
        Home
        </BreadcrumbLink>
    </BreadcrumbItem>
    <BreadcrumbSeparator />
    {#each items as item }
        <BreadcrumbItem>
            <BreadcrumbLink>
                Link Here {item}
            </BreadcrumbLink>
        </BreadcrumbItem>,
    {/each}
    </BreadcrumbList>
</Breadcrumb>

