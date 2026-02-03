/**
 * Utility functions for exporting data from tables to various formats
 */

/**
 * Convert an array of objects to CSV format
 * @param data Array of objects to convert
 * @param headers Optional custom headers (if not provided, will use object keys)
 * @returns CSV formatted string
 */
export function objectsToCSV(data: Array<Record<string, any>>, headers?: string[]): string {
    if (!data || data.length === 0) return '';
    
    // Get headers from first object if not provided
    const keys = headers || Object.keys(data[0]);
    
    // Create CSV header row
    const headerRow = keys.join(',');
    
    // Create data rows
    const rows = data.map(obj => {
        return keys.map(key => {
            // Handle values that need quotes (contain commas, quotes, or newlines)
            const value = obj[key]?.toString() || '';
            if (value.includes(',') || value.includes('"') || value.includes('\n')) {
                return `"${value.replace(/"/g, '""')}"`;
            }
            return value;
        }).join(',');
    });
    
    // Combine header and data rows
    return [headerRow, ...rows].join('\n');
}

/**
 * Download data as a CSV file
 * @param data Array of objects to export
 * @param filename Name of the file to download
 * @param headers Optional custom headers
 */
export function downloadCSV(data: Array<Record<string, any>>, filename: string, headers?: string[]): void {
    const csv = objectsToCSV(data, headers);
    downloadFile(csv, filename, 'text/csv');
}

/**
 * Download any content as a file
 * @param content Content to download
 * @param filename Name of the file to download
 * @param contentType MIME type of the content
 */
export function downloadFile(content: string, filename: string, contentType: string): void {
    // Create a blob with the data and specified content type
    const blob = new Blob([content], { type: contentType });
    
    // Create a download link
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = filename;
    
    // Append to the document, click it, and remove it
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

/**
 * Format object data for export from KeyValueTable
 * @param values Object with method names as keys and arrays of values
 * @param columnHeaders Array of column headers
 * @returns Array of objects ready for CSV export
 */
export function formatKeyValueTableForExport(
    values: Record<string, number[]>, 
    columnHeaders: any[]
): Array<Record<string, any>> {
    return Object.keys(values).map(method => {
        const row: Record<string, any> = { Method: method };
        
        // Add each column value
        values[method].forEach((value, index) => {
            if (index < columnHeaders.length) {
                row[columnHeaders[index]] = value;
            }
        });
        
        return row;
    });
}

/**
 * Format standard table data for export
 * @param data Array of objects representing table data
 * @returns The same data, ready for export
 */
export function formatTableDataForExport(
    data: Array<Record<string, string>>
): Array<Record<string, any>> {
    return data;
}

