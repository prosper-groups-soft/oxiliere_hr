/**
 * Constantes pour les préfixes téléphoniques
 * Utilisées pour le formatage et la validation des numéros de téléphone
 */


export interface PhonePrefix {
  code: string;
  /** Code pays ISO 3166-1 alpha-2 (rendu du drapeau via flagcdn). */
  iso: string;
  name: string;
  flag: string;
  pattern: RegExp;
  maxLength: number;
}


export const PHONE_PREFIXES: PhonePrefix[] = [
  {
    code: '+243',
    iso: 'CD',
    name: 'RD Congo',
    flag: '🇨🇩',
    pattern: /^[0-9]{9}$/,
    maxLength: 9
  },
  {
    code: '+225',
    iso: 'CI',
    name: 'Côte d\'Ivoire',
    flag: '🇨🇮',
    pattern: /^[0-9]{10}$/,
    maxLength: 10
  },
  {
    code: '+237',
    iso: 'CM',
    name: 'Cameroun',
    flag: '🇨🇲',
    pattern: /^[0-9]{9}$/,
    maxLength: 9
  },
  {
    code: '+241',
    iso: 'GA',
    name: 'Gabon',
    flag: '🇬🇦',
    pattern: /^[0-9]{9}$/,
    maxLength: 9
  },
  {
    code: '+242',
    iso: 'CG',
    name: 'Congo-Brazzaville',
    flag: '🇨🇬',
    pattern: /^[0-9]{9}$/,
    maxLength: 9
  },
  {
    code: '+33',
    iso: 'FR',
    name: 'France',
    flag: '🇫🇷',
    pattern: /^[0-9]{9}$/,
    maxLength: 9
  },
  {
    code: '+32',
    iso: 'BE',
    name: 'Belgique',
    flag: '🇧🇪',
    pattern: /^[0-9]{9}$/,
    maxLength: 9
  },
  {
    code: '+41',
    iso: 'CH',
    name: 'Suisse',
    flag: '🇨🇭',
    pattern: /^[0-9]{9}$/,
    maxLength: 9
  },
  {
    code: '+1',
    iso: 'US',
    name: 'USA/Canada',
    flag: '🇺🇸',
    pattern: /^[0-9]{10}$/,
    maxLength: 10
  },
  {
    code: '+44',
    iso: 'GB',
    name: 'Royaume-Uni',
    flag: '🇬🇧',
    pattern: /^[0-9]{10}$/,
    maxLength: 10
  },
  {
    code: '+49',
    iso: 'DE',
    name: 'Allemagne',
    flag: '🇩🇪',
    pattern: /^[0-9]{10}$/,
    maxLength: 10
  },
  {
    code: '+34',
    iso: 'ES',
    name: 'Espagne',
    flag: '🇪🇸',
    pattern: /^[0-9]{9}$/,
    maxLength: 9
  },
  {
    code: '+351',
    iso: 'PT',
    name: 'Portugal',
    flag: '🇵🇹',
    pattern: /^[0-9]{9}$/,
    maxLength: 9
  },
  {
    code: '+39',
    iso: 'IT',
    name: 'Italie',
    flag: '🇮🇹',
    pattern: /^[0-9]{10}$/,
    maxLength: 10
  },
  {
    code: '+31',
    iso: 'NL',
    name: 'Pays-Bas',
    flag: '🇳🇱',
    pattern: /^[0-9]{9}$/,
    maxLength: 9
  },
  {
    code: '+86',
    iso: 'CN',
    name: 'Chine',
    flag: '🇨🇳',
    pattern: /^[0-9]{11}$/,
    maxLength: 11
  },
  {
    code: '+91',
    iso: 'IN',
    name: 'Inde',
    flag: '🇮🇳',
    pattern: /^[0-9]{10}$/,
    maxLength: 10
  },
  {
    code: '+81',
    iso: 'JP',
    name: 'Japon',
    flag: '🇯🇵',
    pattern: /^[0-9]{10}$/,
    maxLength: 10
  },
  {
    code: '+82',
    iso: 'KR',
    name: 'Corée du Sud',
    flag: '🇰🇷',
    pattern: /^[0-9]{10}$/,
    maxLength: 10
  },
  {
    code: '+55',
    iso: 'BR',
    name: 'Brésil',
    flag: '🇧🇷',
    pattern: /^[0-9]{10}$/,
    maxLength: 10
  },
  {
    code: '+54',
    iso: 'AR',
    name: 'Argentine',
    flag: '🇦🇷',
    pattern: /^[0-9]{10}$/,
    maxLength: 10
  },
  {
    code: '+52',
    iso: 'MX',
    name: 'Mexique',
    flag: '🇲🇽',
    pattern: /^[0-9]{10}$/,
    maxLength: 10
  },
  {
    code: '+61',
    iso: 'AU',
    name: 'Australie',
    flag: '🇦🇺',
    pattern: /^[0-9]{9}$/,
    maxLength: 9
  },
  {
    code: '+64',
    iso: 'NZ',
    name: 'Nouvelle-Zélande',
    flag: '🇳🇿',
    pattern: /^[0-9]{9}$/,
    maxLength: 9
  }
];


// Prfixe par défaut (RD Congo)
export const DEFAULT_PREFIX = PHONE_PREFIXES[0];


export function formatPhoneNumber(phone: string, prefix: PhonePrefix): string {
  // Supprimer tous les caractères non numériques
  const cleaned = phone.replace(/\D/g, '');
  
  // Limiter à la longueur maximale
  const truncated = cleaned.slice(0, prefix.maxLength);
  
  // Appliquer le formatage selon le pays
  switch (prefix.code) {
    case '+243': // RD Congo: XXX XXX XXX
      return truncated.replace(/(\d{3})(\d{3})(\d{3})/, '$1 $2 $3');
    case '+225': // Côte d'Ivoire: XX XX XX XX XX
      return truncated.replace(/(\d{2})(\d{2})(\d{2})(\d{2})(\d{2})/, '$1 $2 $3 $4 $5');
    case '+237': // Cameroun: XX XX XX XX
      return truncated.replace(/(\d{2})(\d{2})(\d{2})(\d{2})(\d{2})/, '$1 $2 $3 $4 $5');
    case '+241': // Gabon: XX XX XX XX
      return truncated.replace(/(\d{2})(\d{2})(\d{2})(\d{2})(\d{2})/, '$1 $2 $3 $4 $5');
    case '+242': // Congo-Brazzaville: XX XX XX XX
      return truncated.replace(/(\d{2})(\d{2})(\d{2})(\d{2})(\d{2})/, '$1 $2 $3 $4 $5');
    case '+33': // France: XX XX XX XX XX
      return truncated.replace(/(\d{2})(\d{2})(\d{2})(\d{2})(\d{1})/, '$1 $2 $3 $4 $5');
    case '+32': // Belgique: XXX XX XX XX
      return truncated.replace(/(\d{3})(\d{2})(\d{2})(\d{2})/, '$1 $2 $3 $4');
    case '+41': // Suisse: XXX XX XX XX
      return truncated.replace(/(\d{3})(\d{2})(\d{2})(\d{2})/, '$1 $2 $3 $4');
    case '+31': // Pays-Bas: XX XX XX XX
      return truncated.replace(/(\d{2})(\d{2})(\d{2})(\d{2})(\d{2})/, '$1 $2 $3 $4 $5');
    case '+1': // USA/Canada: (XXX) XXX-XXXX
      return truncated.replace(/(\d{3})(\d{3})(\d{4})/, '($1) $2-$3');
    case '+44': // UK: XXXX XXX XXX
      return truncated.replace(/(\d{4})(\d{3})(\d{3})/, '$1 $2 $3');
    case '+49': // Allemagne: XXX XXX XXXX
      return truncated.replace(/(\d{3})(\d{3})(\d{4})/, '$1 $2 $3 $4');
    case '+34': // Espagne: XXX XX XX XX
      return truncated.replace(/(\d{3})(\d{2})(\d{2})(\d{2})/, '$1 $2 $3 $4');
    case '+351': // Portugal: XX XX XX XX
      return truncated.replace(/(\d{2})(\d{2})(\d{2})(\d{2})(\d{2})/, '$1 $2 $3 $4 $5');
    case '+39': // Italie: XXX XXX XXXX
      return truncated.replace(/(\d{3})(\d{3})(\d{4})/, '$1 $2 $3 $4');
    case '+86': // Chine: XXX XXXX XXXX
      return truncated.replace(/(\d{3})(\d{4})(\d{4})/, '$1 $2 $3');
    case '+91': // Inde: XXXXX XXXXX
      return truncated.replace(/(\d{5})(\d{5})/, '$1 $2');
    case '+81': // Japon: XX XXXX XXXX
      return truncated.replace(/(\d{2})(\d{4})(\d{4})/, '$1 $2 $3');
    case '+82': // Corée du Sud: XXX-XXXX-XXXX
      return truncated.replace(/(\d{3})(\d{4})(\d{4})/, '$1-$2-$3');
    case '+55': // Brésil: XXXXX-XXXX
      return truncated.replace(/(\d{5})(\d{4})/, '$1-$2');
    case '+54': // Argentine: XXXX-XXXX
      return truncated.replace(/(\d{4})(\d{4})/, '$1-$2');
    case '+52': // Mexique: XXX XXX XXXX
      return truncated.replace(/(\d{3})(\d{3})(\d{4})/, '$1 $2 $3');
    case '+61': // Australie: XXX XXX XXX
      return truncated.replace(/(\d{3})(\d{3})(\d{3})/, '$1 $2 $3');
    case '+64': // Nouvelle-Zélande: XXX XXX XXX
      return truncated.replace(/(\d{3})(\d{3})(\d{3})/, '$1 $2 $3');
    default:
      // Format par défaut: groupes de 3-4 chiffres
      return truncated.replace(/(\d{3})(\d{3})(\d{4})/, '$1 $2 $3');
  }
}


export function validatePhoneNumber(phone: string, prefix: PhonePrefix): boolean {
  const cleaned = phone.replace(/\D/g, '');
  return prefix.pattern.test(cleaned) && cleaned.length === prefix.maxLength;
}

