export const FILE_TYPES: Record<string, Record<string, string>> = {
  jpg: {
    type : 'Image',
    extension: 'jpg',
    icon: 'ri-image-fill'
  },
  jpeg: {
    type : 'Image',
    extension: 'jpg',
    icon: 'ri-image-fill'
  },
  svg: {
    type : 'Image',
    extension: 'svg',
    icon: 'ri-image-fill'
  },
  png: {
    type : 'Image',
    extension: 'png',
    icon: 'ri-image-fill'
  },
  pdf: {
    type : 'Document PDF',
    extension: 'pdf',
    icon: 'ri-file-pdf-fill'
  },
  doc: {
    type : 'Document Word',
    extension: 'doc',
    icon: 'ri-file-word-2-line'
  },
  docx: {
    type : 'Document Word',
    extension: 'docx',
    icon: 'ri-file-word-2-line'
  },
  txt: {
    type : 'Document Text',
    extension: 'txt',
    icon: 'ri-file-text-line'
  },
  xlsx: {
    type : 'Document Excel',
    extension: 'xlsx',
    icon: 'ri-file-excel-2-line'
  },
  xls: {
    type : 'Document Excel',
    extension: 'xls',
    icon: 'ri-file-excel-2-line'
  },
  csv: {
    type : 'Document CSV',
    extension: 'csv',
    icon: 'ri-file-csv-line'
  },
  ppt: {
    type : 'Document Powerpoint',
    extension: 'ppt',
    icon: 'ri-file-ppt-2-line'
  },
  pptx: {
    type : 'Document Powerpoint',
    extension: 'pptx',
    icon: 'ri-file-ppt-2-line'
  },
  zip: {
    type : 'Fichier Archive',
    extension: 'zip',
    icon: 'ri-file-zip-line'
  },
  rar: {
    type : 'Fichier Archive',
    extension: 'rar',
    icon: 'ri-file-zip-line'
  },
  mp3: {
    type : 'Audio',
    extension: 'mp3',
    icon: 'ri-file-music-line'
  },
  mp4: {
    type : 'Vidéo',
    extension: 'mp4',
    icon: 'ri-file-video-line'
  },
  webm: {
    type : 'Vidéo',
    extension: 'webm',
    icon: 'ri-file-video-line'
  },
  webp: {
    type : 'Vidéo',
    extension: 'webp',
    icon: 'ri-file-video-line'
  },
  unknown: {
    type : 'Fichier',
    extension: 'unknown',
    icon: 'ri-file-line'
  }
}


export const SUPPORTED_FILE_TYPES = [
  'jpg', 
  'jpeg', 
  'png', 
  'pdf', 
  'mp3', 
  'mp4', 
  'webm', 
  'webp'
];


export function get_file_type(filename: string) {
  const ext = filename.toLowerCase().split('.').pop();
  return ext ? FILE_TYPES[ext] ?? FILE_TYPES['txt'] : {
    type : 'Fichier',
    extension: 'unknown'
  };
}


export function get_file_size(file: File) {
  let size = file?.size || 0;
  const units = ['o', 'Ko', 'Mo', 'Go', 'To'];
  let index = 0;
  while(size > 1024 && index < units.length - 1) {
    size /= 1024;
    index++;
  }
  return `${size.toFixed(1)} ${units[index]}`;
}


export function is_supported_file_type(filename: string) {
  const ext = filename.toLowerCase().split('.').pop();
  return ext ? SUPPORTED_FILE_TYPES.includes(ext) : false;
}


export function get_file_icon(filename: string) {
  const ext = filename.toLowerCase().split('.').pop();
  return (
    ext ? 
    FILE_TYPES[ext]?.icon : 
    FILE_TYPES['unknown'].icon;
  )
}

