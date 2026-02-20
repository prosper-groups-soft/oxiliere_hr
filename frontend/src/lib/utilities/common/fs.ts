import { 
  FILE_TYPES, 
  SUPPORTED_FILE_TYPES,
  UNITS_SIZE_FILE
} from '@/constants/features/files';
import { type Document } from '@/features/employees/types/types';


export function get_file_type(filename: string) {
  const ext = filename.toLowerCase().split('.').pop();
  return ext ? FILE_TYPES[ext] ?? FILE_TYPES['txt'] : {
    type : 'Fichier',
    extension: 'unknown'
  };
}


export function get_file_size(file: File) {
  let size = file?.size || 0;
  let index = 0;
  while(size > 1024 && index < UNITS_SIZE_FILE.length - 1) {
    size /= 1024;
    index++;
  }
  return `${size.toFixed(1)} ${UNITS_SIZE_FILE[index]}`;
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
    FILE_TYPES['unknown'].icon
  );
}


/**
 * Return the icon matching the extension of file
 */
export const getFileIconName = (type: string): string => {
  const lowerType = type.toLowerCase();
  if (['jpg', 'jpeg', 'png', 'gif', 'svg'].includes(lowerType)) return 'image';
  if (['pdf'].includes(lowerType)) return 'pdf';
  if (['doc', 'docx'].includes(lowerType)) return 'doc';
  if (['xls', 'xlsx'].includes(lowerType)) return 'xls';
  return 'file';
};

/**
 * Calculate the visual status of document according to his expiration date
 */
export const getStatusConfig = (doc: Document) => {
  const today = new Date();
  
  if (!doc.expiry) {
    return { 
      label: 'Permanent', 
      class: 'bg-slate-50 text-slate-500 border-slate-100', 
      icon: 'shield-check' 
    };
  }
  
  const expiryDate = new Date(doc.expiry);
  
  // Cas : Expiré
  if (expiryDate < today) {
    return { 
      label: 'Expiré', 
      class: 'bg-red-50 text-red-600 border-red-100', 
      icon: 'alert-circle' 
    };
  }
  
  // Case : Alert (less than 3 months)
  const alertThreshold = new Date();
  alertThreshold.setMonth(today.getMonth() + 3);
  
  if (expiryDate < alertThreshold) {
    return { 
      label: 'Expire bientôt', 
      class: 'bg-amber-50 text-amber-600 border-amber-100', 
      icon: 'alert-triangle' 
    };
  }
  
  // Case : Valid
  return { 
    label: 'Valide', 
    class: 'bg-emerald-50 text-emerald-600 border-emerald-100', 
    icon: 'check-circle' 
  };
};

