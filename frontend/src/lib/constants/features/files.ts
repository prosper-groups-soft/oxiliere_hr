export const FILE_TYPES: Record<string, Record<string, string>> = {
	jpg: {
		type: 'Image',
		extension: 'jpg',
		icon: 'image'
	},
	jpeg: {
		type: 'Image',
		extension: 'jpg',
		icon: 'image'
	},
	svg: {
		type: 'Image',
		extension: 'svg',
		icon: 'image'
	},
	png: {
		type: 'Image',
		extension: 'png',
		icon: 'image'
	},
	pdf: {
		type: 'Document PDF',
		extension: 'pdf',
		icon: 'pdf'
	},
	doc: {
		type: 'Document Word',
		extension: 'doc',
		icon: 'doc'
	},
	docx: {
		type: 'Document Word',
		extension: 'docx',
		icon: 'doc'
	},
	txt: {
		type: 'Document Text',
		extension: 'txt',
		icon: 'file'
	},
	xlsx: {
		type: 'Document Excel',
		extension: 'xlsx',
		icon: 'excel'
	},
	xls: {
		type: 'Document Excel',
		extension: 'xls',
		icon: 'excel'
	},
	csv: {
		type: 'Document CSV',
		extension: 'csv',
		icon: 'csv'
	},
	ppt: {
		type: 'Document Powerpoint',
		extension: 'ppt',
		icon: 'ppt'
	},
	pptx: {
		type: 'Document Powerpoint',
		extension: 'pptx',
		icon: 'ppt'
	},
	zip: {
		type: 'Fichier Archive',
		extension: 'zip',
		icon: 'zip'
	},
	rar: {
		type: 'Fichier Archive',
		extension: 'rar',
		icon: 'zip'
	},
	mp3: {
		type: 'Audio',
		extension: 'mp3',
		icon: 'music'
	},
	mp4: {
		type: 'Vidéo',
		extension: 'mp4',
		icon: 'video'
	},
	webm: {
		type: 'Vidéo',
		extension: 'webm',
		icon: 'video'
	},
	webp: {
		type: 'Vidéo',
		extension: 'webp',
		icon: 'video'
	},
	unknown: {
		type: 'Fichier',
		extension: 'unknown',
		icon: 'file'
	}
};

export const UNITS_SIZE_FILE = ['o', 'Ko', 'Mo', 'Go', 'To'];

export const SUPPORTED_FILE_TYPES = ['jpg', 'jpeg', 'png', 'pdf', 'mp3', 'mp4', 'webm', 'webp'];
