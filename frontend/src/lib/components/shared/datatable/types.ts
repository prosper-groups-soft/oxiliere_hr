import { type Table as TableType } from '@tanstack/table-core';

export type SearchProps<T> = {
	table: TableType<T>;
	handleSearch: (v: string) => void;
	value: string;
};

export type setFilterFn = (key: string, value: any) => void;
