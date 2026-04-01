import type { ComponentEvents, ComponentProps, SvelteComponent } from 'svelte';
import type { CellContext, Column, ColumnDef, Row } from '@tanstack/table-core';

import { ROW_HEIGHT_MAP, TABLE_HEADER_Z_INDEX, TABLE_ROW_Z_INDEX } from '$lib/constants/shared';
import {
	CELL_VERTICAL_ALIGNMENT,
	COLUMN_ACTIONS_ID,
	COLUMN_SELECT_ID,
	ROW_HEIGHT
} from '$lib/types/shared';

export type SvelteComponentConstructor<T extends SvelteComponent = SvelteComponent> =
	new (options: {
		target: Element | DocumentFragment;
		props?: ComponentProps<T>;
		events?: ComponentEvents<T>;
	}) => T;

export interface BaseCellRendererParams<TData, TValue> extends CellContext<TData, TValue> {}

export interface SelectHeaderRendererParams<TData, TValue> extends BaseCellRendererParams<
	TData,
	TValue
> {
	isChecked: boolean | 'indeterminate';
	onToggle: (checked: boolean) => void;
	onHeaderClick: (event: MouseEvent) => void;
}
export interface SelectCellRendererParams<TData, TValue> extends BaseCellRendererParams<
	TData,
	TValue
> {
	isChecked: boolean;
	isDisabled: boolean;
	onToggle: (checked: boolean) => void;
	onCellClick: (event: MouseEvent) => void;
}

export const calculateHeightStyle = (rowHeight: ROW_HEIGHT): Record<string, string | number> => {
	return ROW_HEIGHT_MAP[rowHeight];
};

export const getCommonPinningStyles = <TData>(
	column: Column<TData>,
	isHeader: boolean = false,
	applyStickyWorkaround = false
): Record<string, string | number | undefined> => {
	const isPinned = column.getIsPinned();
	const isLastLeftPinnedColumn = isPinned === 'left' && column.getIsLastColumn('left');
	const isFirstRightPinnedColumn = isPinned === 'right' && column.getIsFirstColumn('right');

	return {
		boxShadow: isLastLeftPinnedColumn
			? 'inset -1px 0px 0px 0px rgb(226, 232, 240)'
			: isFirstRightPinnedColumn
				? 'inset 1px 0px 0px 0px rgb(226, 232, 240)'
				: undefined,
		left: isPinned === 'left' ? `${column.getStart('left')}px` : undefined,
		right: isPinned === 'right' ? `${column.getAfter('right')}px` : undefined,
		...(isPinned && {
			position: applyStickyWorkaround ? 'unset' : ('sticky' as any),
			zIndex: isHeader ? TABLE_HEADER_Z_INDEX + 1 : TABLE_ROW_Z_INDEX + 1
		})
	};
};

export const getCommonPinningClasses = <TData>(
	column: Column<TData>,
	isHeader: boolean = false
): string => {
	const isPinned = column.getIsPinned();
	return isPinned ? (isHeader ? 'bg-[#FBFCFD]' : 'bg-white') : '';
};

const getRowRange = <TData>(
	rows: Array<Row<TData>>,
	clickedRowID: string,
	previousClickedRowID: string
): Array<Row<TData>> => {
	const range: Array<Row<TData>> = [];
	const processedRowsMap: Record<string, boolean> = {
		[clickedRowID]: false,
		[previousClickedRowID]: false
	};
	for (const row of rows) {
		if (row.id === clickedRowID || row.id === previousClickedRowID) {
			if (previousClickedRowID === '') {
				range.push(row);
				break;
			}
			processedRowsMap[row.id] = true;
		}
		if (
			(processedRowsMap[clickedRowID] || processedRowsMap[previousClickedRowID]) &&
			!row.getIsGrouped()
		) {
			range.push(row);
		}
		if (processedRowsMap[clickedRowID] && processedRowsMap[previousClickedRowID]) {
			break;
		}
	}
	return range;
};

export const shiftCheckboxClickHandler = <TData>(
	event: MouseEvent,
	context: CellContext<TData, unknown>,
	previousClickedRowID: string,
	updatePreviousClickedRowID: (id: string) => void
) => {
	if (event.shiftKey) {
		const { rows, rowsById } = context.table.getRowModel();
		const rowsToToggle = getRowRange(
			rows,
			context.row.id,
			rows.map((r) => r.id).includes(previousClickedRowID) ? previousClickedRowID : ''
		);
		const isLastSelected = !rowsById[context.row.id]?.getIsSelected() || false;
		rowsToToggle.forEach((row) => row.toggleSelected(isLastSelected));
	}
	updatePreviousClickedRowID(context.row.id);
};

interface SelectColumnMeta<TData> {
	verticalAlignment?: CELL_VERTICAL_ALIGNMENT;
	headerComponent?: SvelteComponentConstructor;
	getHeaderProps?: (
		context: CellContext<TData, unknown>
	) => SelectHeaderRendererParams<TData, unknown>;
	cellComponent?: SvelteComponentConstructor;
	getCellProps?: (
		context: CellContext<TData, unknown>,
		previousClickedRowID: string,
		updatePreviousClickedRowID: (id: string) => void
	) => SelectCellRendererParams<TData, unknown>;
	cellWrapperComponent?: SvelteComponentConstructor;
	headerWrapperComponent?: SvelteComponentConstructor;
	checkboxComponent?: SvelteComponentConstructor;
}

export const generateSelectColumDef = <TData>(paramMeta?: {
	verticalAlignment?: CELL_VERTICAL_ALIGNMENT;
	HeaderWrapperComponent: SvelteComponentConstructor;
	CellWrapperComponent: SvelteComponentConstructor;
	CheckboxComponent: SvelteComponentConstructor;
}) => {
	let previousSelectedRowID = '';
	const updatePreviousClickedRowID = (id: string) => {
		previousSelectedRowID = id;
	};

	const columnDef: ColumnDef<TData, unknown> & { meta?: SelectColumnMeta<TData> } = {
		id: COLUMN_SELECT_ID,
		meta: {
			verticalAlignment: paramMeta?.verticalAlignment,
			headerWrapperComponent: paramMeta?.HeaderWrapperComponent,
			cellWrapperComponent: paramMeta?.CellWrapperComponent,
			checkboxComponent: paramMeta?.CheckboxComponent,
			getHeaderProps: (context: any) => ({
				...context,
				isChecked: context.table.getIsAllPageRowsSelected()
					? true
					: context.table.getIsSomePageRowsSelected()
						? 'indeterminate'
						: false,
				onToggle: (value: any) => context.table.toggleAllPageRowsSelected(!!value),
				onHeaderClick: (event: any) => event.stopPropagation()
			}),
			getCellProps: (context: any) => ({
				...context,
				isChecked: context.row.getIsSelected(),
				isDisabled: !context.row.getCanSelect(),
				onToggle: (value: any) => context.row.toggleSelected(!!value),
				onCellClick: (event: any) => {
					event.stopPropagation();
					shiftCheckboxClickHandler(
						event,
						context,
						previousSelectedRowID,
						updatePreviousClickedRowID
					);
				}
			})
		},
		header: 'Select',
		cell: 'SelectCell',
		size: 50,
		enableResizing: false,
		enableSorting: false,
		enableHiding: false
	};
	return columnDef as ColumnDef<TData, unknown>;
};

interface ActionsColumnMeta<TData> {
	custom?: unknown;
	cellComponent?: SvelteComponentConstructor;
	getCellProps?: (context: CellContext<TData, unknown>) => any;
}

export const generateActionsColumDef = <TData>({
	customMeta,
	ActionCellComponent,
	getActionCellProps
}: {
	customMeta?: unknown;
	ActionCellComponent: SvelteComponentConstructor;
	getActionCellProps: (context: CellContext<TData, unknown>) => any;
}) => {
	const columnDef: ColumnDef<TData, unknown> & { meta?: ActionsColumnMeta<TData> } = {
		id: COLUMN_ACTIONS_ID,
		meta: {
			custom: customMeta,
			cellComponent: ActionCellComponent,
			getCellProps: getActionCellProps
		},
		header: '',
		cell: 'ActionsCell',
		size: 56,
		enableHiding: false,
		enableResizing: false,
		enableSorting: false
	};
	return columnDef as ColumnDef<TData, unknown>;
};
