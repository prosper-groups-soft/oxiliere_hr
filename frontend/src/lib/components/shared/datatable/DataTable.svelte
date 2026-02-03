<script lang="ts" generics="TData">
	import { browser } from '$app/environment';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Card, CardContent } from '$lib/components/ui/card/index.js';
	import { FlexRender } from '$lib/components/ui/data-table';
	import { createSvelteTable } from '$lib/components/ui/data-table/data-table.svelte.js';
	import Input from '$lib/components/ui/input/input.svelte';
	import * as Table from '$lib/components/ui/table/index.js';
	import { Search } from '@lucide/svelte';
	import ChevronLeftIcon from '@lucide/svelte/icons/chevron-left';
	import {
		default as ChevronRightIcon,
		default as ChevronsRightIcon
	} from '@lucide/svelte/icons/chevron-right';
	import ChevronsLeftIcon from '@lucide/svelte/icons/chevrons-left';
	import { createQuery } from '@tanstack/svelte-query';
	import {
		type ColumnDef,
		type ColumnFiltersState,
		type PaginationState,
		type RowSelectionState,
		type SortingState,
		type Table as TableType,
		type VisibilityState,
		getCoreRowModel,
		getFacetedRowModel,
		getFacetedUniqueValues,
		getFilteredRowModel,
		getPaginationRowModel,
		getSortedRowModel
	} from '@tanstack/table-core';
	import type { Snippet } from 'svelte';
	import Empty from '../Empty.svelte';
	import ErrorWidget from '../ErrorWidget.svelte';
	import Loader from '../Loader.svelte';
	import type { SearchProps, setFilterFn } from './types';

	let {
		columns,
		items = [],
		showPagination = false,
		toolbar = false,
		serverSide = false,
		hasSelection = false,
		totalRows = 0,
		pageSize = 10,
		queryKey = ['data-table_default'],
		queryFn,
		emit,
		Filters,
		searchPlaceholder = 'Recherche....'
	}: {
		columns: ColumnDef<TData>[];
		items?: TData[];
		showPagination?: boolean;
		toolbar?: boolean;
		hasSelection?: boolean;
		serverSide?: boolean;
		totalRows?: number;
		queryKey?: any[];
		searchPlaceholder?: string;
		pageSize?: number;
		Filters?: Snippet<[setFilterFn]>;
		queryFn?: (context: { queryKey: any[] }) => Promise<{ results: TData[]; count: number }>;
		emit?: (event: string, detail: any) => void;
	} = $props();

	let rowSelection = $state<RowSelectionState>({});
	let columnVisibility = $state<VisibilityState>({});
	let columnFilters = $state<ColumnFiltersState>([]);
	let sorting = $state<SortingState>([]);
	let pagination = $state<PaginationState>({ pageIndex: 0, pageSize });
	let searchTerm = $state<string>('');
	let searchTimeout: ReturnType<typeof setTimeout> | null = null;
	let filters = $state<Record<string, any>>({});
	let initialLoading = $state<boolean>(true); // for UI/UX only

	let data: TData[] = $state([]);

	// Si serverSide est true et queryKey et queryFn sont fournis, créer la requête
	data = items;
	let query = $derived.by(() => {
		return createQuery({
			queryKey: [
				...queryKey,
				pagination,
				{
					search: searchTerm.length ? searchTerm : undefined,
					...filters
				},
				sorting
			],
			queryFn: queryFn,
			enabled: !!serverSide && !!queryKey && !!queryFn && browser
		});
	});

	function getTotalRowsCount() {
		if ($query.isSuccess) {
			return $query.data.count || 0;
		}
		return totalRows;
	}

	function getPageCount() {
		const count = getTotalRowsCount();
		return count > 0 ? Math.ceil(count / pagination.pageSize) : -1;
	}

	const table = createSvelteTable<TData>({
		get data() {
			if (serverSide && $query.isSuccess) {
				return $query.data.results || [];
			}
			return data;
		},
		state: {
			get sorting() {
				return sorting;
			},
			get columnVisibility() {
				return columnVisibility;
			},
			get rowSelection() {
				return rowSelection;
			},
			get columnFilters() {
				return columnFilters;
			},
			get pagination() {
				return pagination;
			}
		},
		columns,
		enableRowSelection: true,
		// Configuration pour la pagination côté serveur
		...(serverSide
			? {
					manualPagination: true,
					manualSorting: true,
					manualFiltering: true,
					get pageCount() {
						return getPageCount();
					}
				}
			: {}),
		onRowSelectionChange: (updater) => {
			if (typeof updater === 'function') {
				rowSelection = updater(rowSelection);
			} else {
				rowSelection = updater;
			}
		},
		onSortingChange: (updater) => {
			if (typeof updater === 'function') {
				sorting = updater(sorting);
			} else {
				sorting = updater;
			}

			if (emit) emit('sortingChange', sorting);
		},
		onColumnFiltersChange: (updater) => {
			if (typeof updater === 'function') {
				columnFilters = updater(columnFilters);
			} else {
				columnFilters = updater;
			}

			// Recherche basée sur les filtres de colonnes
			const searchFilter = columnFilters.find((filter) => filter.id === 'search');
			if (searchFilter) {
				searchTerm = searchFilter.value as string;
				if (emit) emit('search', searchTerm);
			}
		},
		onColumnVisibilityChange: (updater) => {
			if (typeof updater === 'function') {
				columnVisibility = updater(columnVisibility);
			} else {
				columnVisibility = updater;
			}
		},
		onPaginationChange: (updater) => {
			if (typeof updater === 'function') {
				pagination = updater(pagination);
			} else {
				pagination = updater;
			}

			const pageCount = getPageCount();

			// Valider que pageIndex ne dépasse pas pageCount
			if (serverSide && pageCount > 0) {
				const maxPageIndex = pageCount - 1;
				if (pagination.pageIndex > maxPageIndex) {
					pagination = { ...pagination, pageIndex: maxPageIndex };
				}
			}

			// Mettre à jour le store et émettre l'événement si emit est fourni
			if (emit) emit('paginationChange', pagination);
		},
		getCoreRowModel: getCoreRowModel(),
		...(!serverSide
			? {
					getFilteredRowModel: getFilteredRowModel(),
					getPaginationRowModel: getPaginationRowModel(),
					getSortedRowModel: getSortedRowModel(),
					getFacetedRowModel: getFacetedRowModel(),
					getFacetedUniqueValues: getFacetedUniqueValues()
				}
			: {})
	});

	function handleRowClick(detail: any) {
		emit?.('rowClick', detail);
	}

	function _handleSearch(value: string) {
		if (serverSide) {
			if (searchTimeout) {
				clearTimeout(searchTimeout);
			}

			searchTimeout = setTimeout(() => {
				searchTerm = value;
			}, 800);
		} else {
			table.getColumn('name')?.setFilterValue(value);
		}
	}

	function setFilter(key: string, value: any) {
		filters[key] = value;
	}

	$effect(() => {
		if (serverSide) {
			setTimeout(() => {
				initialLoading = false;
			}, 100);
		}
	});

	export { Toolbar };
</script>

{#snippet SearchInput({ table, handleSearch, value }: SearchProps<TData>)}
	<div class="flex flex-1 items-center">
		<div class="relative w-full">
			<Search
				class="text-muted-foreground absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 transform"
			/>
			<Input
				placeholder={searchPlaceholder}
				value={serverSide ? value : ((table.getColumn('name')?.getFilterValue() as string) ?? '')}
				oninput={(e) => {
					const _value = e.currentTarget.value;
					handleSearch(_value);
				}}
				class="h-8 w-full py-2 pl-9"
			/>
		</div>
	</div>
{/snippet}

{#snippet Toolbar({ table }: { table: TableType<TData> })}
	<div class="flex w-full flex-col justify-between gap-2 sm:flex-row sm:items-center sm:space-x-2">
		{@render SearchInput({ table, handleSearch: _handleSearch, value: searchTerm })}
		{@render Filters?.(setFilter)}
	</div>
{/snippet}

{#snippet Pagination({ table }: { table: TableType<TData> })}
	{@const count = getTotalRowsCount()}

	<div class="flex items-center {!hasSelection ? 'justify-end' : 'justify-between'} px-2">
		{#if hasSelection}
			<div class="text-muted-foreground flex-1 text-sm">
				{table.getFilteredSelectedRowModel().rows.length} sur
				{serverSide ? count : table.getFilteredRowModel().rows.length} lignes sélectionnées.
			</div>
		{:else}
			<div class="items- w-[100px] justify-center text-sm font-medium sm:hidden">
				Page {table.getState().pagination.pageIndex + 1} /
				{serverSide
					? Math.ceil(count / table.getState().pagination.pageSize)
					: table.getPageCount()}
			</div>
		{/if}

		<div class="flex items-center justify-end space-x-6 lg:space-x-8">
			<div class="hidden w-[100px] items-center justify-center text-sm font-medium sm:flex">
				Page {table.getState().pagination.pageIndex + 1} /
				{serverSide
					? Math.ceil(count / table.getState().pagination.pageSize)
					: table.getPageCount()}
			</div>

			<div class="flex items-center space-x-2">
				<Button
					variant="outline"
					class="hidden size-8 p-0 lg:flex"
					onclick={() => table.setPageIndex(0)}
					disabled={!table.getCanPreviousPage()}
				>
					<span class="sr-only">Aller a la premiere page</span>
					<ChevronsLeftIcon />
				</Button>
				<Button
					variant="outline"
					class="size-8 p-0"
					onclick={() => table.previousPage()}
					disabled={!table.getCanPreviousPage()}
				>
					<span class="sr-only">Page precendente</span>
					<ChevronLeftIcon />
				</Button>
				<Button
					variant="outline"
					class="size-8 p-0"
					onclick={() => table.nextPage()}
					disabled={!table.getCanNextPage()}
				>
					<span class="sr-only">Page Suivante</span>
					<ChevronRightIcon />
				</Button>
				<Button
					variant="outline"
					class="hidden size-8 p-0 lg:flex"
					onclick={() => {
						const lastPageIndex = serverSide
							? Math.ceil(count / table.getState().pagination.pageSize) - 1
							: table.getPageCount() - 1;
						table.setPageIndex(lastPageIndex);
					}}
					disabled={!table.getCanNextPage()}
				>
					<span class="sr-only">Aller a la derniere page</span>
					<ChevronsRightIcon />
				</Button>
			</div>
		</div>
	</div>
{/snippet}

{#if $query.isError}
	<ErrorWidget error={$query.error} showRetryButton />
{:else}
	<Card class="mb-6">
		<CardContent class="space-y-7 p-4">
			{#if toolbar}
				{@render Toolbar({ table })}
			{/if}

			<Table.Root>
				<Table.Header>
					{#each table.getHeaderGroups() as headerGroup (headerGroup.id)}
						<Table.Row>
							{#each headerGroup.headers as header (header.id)}
								<Table.Head colspan={header.colSpan}>
									{#if !header.isPlaceholder}
										<FlexRender
											content={header.column.columnDef.header}
											context={header.getContext()}
										/>
									{/if}
								</Table.Head>
							{/each}
						</Table.Row>
					{/each}
				</Table.Header>
				<Table.Body>
					{#if ($query.isLoading && serverSide) || initialLoading}
						<Table.Row>
							<Table.Cell colspan={columns.length} class="h-64 text-center">
								<Loader />
							</Table.Cell>
						</Table.Row>
					{:else}
						{#each table.getRowModel().rows as row (row.id)}
							<Table.Row
								data-state={row.getIsSelected() && 'selected'}
								class="cursor-pointer"
								onclick={() => handleRowClick(row.original)}
							>
								{#each row.getVisibleCells() as cell (cell.id)}
									<Table.Cell>
										<FlexRender content={cell.column.columnDef.cell} context={cell.getContext()} />
									</Table.Cell>
								{/each}
							</Table.Row>
						{:else}
							<Table.Row class="hover:bg-transparent">
								<Table.Cell colspan={columns.length} class="text-center h-64">
									<Empty class="py-5" />
								</Table.Cell>
							</Table.Row>
						{/each}
					{/if}
				</Table.Body>
			</Table.Root>

			{#if showPagination && getPageCount() > 1}
				{@render Pagination({ table })}
			{/if}
		</CardContent>
	</Card>
{/if}
