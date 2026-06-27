/**
 * Constants pour les pays et nationalités
 * Source unique pour toutes les listes de pays dans l'application
 */


export interface CountryOption {
  value: string;
  label: string;
  code: string;
  flag: string;
}


export const COUNTRY_OPTIONS: CountryOption[] = [
  // Afrique
  { value: "CD", label: "RD Congo", code: "CD", flag: "🇨🇩" },
  { value: "FR", label: "France", code: "FR", flag: "🇫🇷" },
  { value: "US", label: "États-Unis", code: "US", flag: "🇺🇸" },
  { value: "BE", label: "Belgique", code: "BE", flag: "🇧🇪" },
  { value: "CH", label: "Suisse", code: "CH", flag: "🇨🇭" },
  { value: "CA", label: "Canada", code: "CA", flag: "🇨🇦" },
  { value: "CM", label: "Cameroun", code: "CM", flag: "🇨🇲" },
  { value: "GA", label: "Gabon", code: "GA", flag: "🇬🇦" },
  { value: "AO", label: "Angola", code: "AO", flag: "🇦🇴" },
  { value: "CG", label: "Congo-Brazzaville", code: "CG", flag: "🇨🇬" },
  { value: "CI", label: "Côte d'Ivoire", code: "CI", flag: "🇨🇮" },
  { value: "DZ", label: "Algérie", code: "DZ", flag: "🇩🇿" },
  { value: "MA", label: "Maroc", code: "MA", flag: "🇲🇦" },
  { value: "TN", label: "Tunisie", code: "TN", flag: "🇹🇳" },
  { value: "SN", label: "Sénégal", code: "SN", flag: "🇸🇳" },
  { value: "ML", label: "Mali", code: "ML", flag: "🇲🇱" },
  { value: "BF", label: "Burkina Faso", code: "BF", flag: "🇧🇫" },
  { value: "NE", label: "Niger", code: "NE", flag: "🇳🇪" },
  { value: "TD", label: "Tchad", code: "TD", flag: "🇹🇩" },
  { value: "CF", label: "Centrafrique", code: "CF", flag: "🇨🇫" },
  { value: "GQ", label: "Guinée Équatoriale", code: "GQ", flag: "🇬🇶" },
  { value: "RW", label: "Rwanda", code: "RW", flag: "🇷🇼" },
  { value: "BI", label: "Burundi", code: "BI", flag: "🇧🇮" },
  { value: "UG", label: "Ouganda", code: "UG", flag: "🇺🇬" },
  { value: "KE", label: "Kenya", code: "KE", flag: "🇰🇪" },
  { value: "TZ", label: "Tanzanie", code: "TZ", flag: "🇹🇿" },
  { value: "MZ", label: "Mozambique", code: "MZ", flag: "🇲🇿" },
  { value: "ZM", label: "Zambie", code: "ZM", flag: "🇿🇲" },
  { value: "ZW", label: "Zimbabwe", code: "ZW", flag: "🇿🇼" },
  { value: "BW", label: "Botswana", code: "BW", flag: "🇧🇼" },
  { value: "NA", label: "Namibie", code: "NA", flag: "🇳🇦" },
  { value: "SZ", label: "Eswatini", code: "SZ", flag: "🇸🇿" },
  { value: "LS", label: "Lesotho", code: "LS", flag: "🇱🇸" },
  { value: "MW", label: "Malawi", code: "MW", flag: "🇲🇼" },
  { value: "GM", label: "Gambie", code: "GM", flag: "🇬🇲" },
  { value: "SL", label: "Sierra Leone", code: "SL", flag: "🇸🇱" },
  { value: "LR", label: "Libéria", code: "LR", flag: "🇱🇷" },
  { value: "GH", label: "Ghana", code: "GH", flag: "🇬🇭" },
  { value: "NG", label: "Nigéria", code: "NG", flag: "🇳🇬" },
  { value: "ZA", label: "Afrique du Sud", code: "ZA", flag: "🇿🇦" },
  { value: "EG", label: "Égypte", code: "EG", flag: "🇪🇬" },
  { value: "LY", label: "Libye", code: "LY", flag: "🇱🇾" },
  { value: "ET", label: "Éthiopie", code: "ET", flag: "🇪🇹" },
  { value: "ER", label: "Érythrée", code: "ER", flag: "🇪🇷" },
  { value: "DJ", label: "Djibouti", code: "DJ", flag: "🇩🇯" },
  { value: "SO", label: "Somalie", code: "SO", flag: "🇸🇴" },
  { value: "SD", label: "Soudan", code: "SD", flag: "🇸🇩" },
  { value: "SS", label: "Soudan du Sud", code: "SS", flag: "🇸🇸" },
  { value: "KM", label: "Comores", code: "KM", flag: "🇰🇲" },
  { value: "MU", label: "Maurice", code: "MU", flag: "🇲🇺" },
  { value: "SC", label: "Seychelles", code: "SC", flag: "🇸🇨" },
  { value: "MG", label: "Madagascar", code: "MG", flag: "🇲🇬" },
  { value: "RE", label: "Réunion", code: "RE", flag: "🇷🇪" },
  // Europe
  { value: "GB", label: "Royaume-Uni", code: "GB", flag: "🇬🇧" },
  { value: "DE", label: "Allemagne", code: "DE", flag: "🇩🇪" },
  { value: "IT", label: "Italie", code: "IT", flag: "🇮🇹" },
  { value: "ES", label: "Espagne", code: "ES", flag: "🇪🇸" },
  { value: "PT", label: "Portugal", code: "PT", flag: "🇵🇹" },
  { value: "NL", label: "Pays-Bas", code: "NL", flag: "🇳🇱" },
  // Asie
  { value: "CN", label: "Chine", code: "CN", flag: "🇨🇳" },
  { value: "IN", label: "Inde", code: "IN", flag: "🇮🇳" },
  { value: "JP", label: "Japon", code: "JP", flag: "🇯🇵" },
  { value: "KR", label: "Corée du Sud", code: "KR", flag: "🇰🇷" },
  // Amérique
  { value: "BR", label: "Brésil", code: "BR", flag: "🇧🇷" },
  { value: "AR", label: "Argentine", code: "AR", flag: "🇦🇷" },
  { value: "MX", label: "Mexique", code: "MX", flag: "🇲🇽" },
  { value: "AU", label: "Australie", code: "AU", flag: "🇦🇺" },
  // Océanie
  { value: "NZ", label: "Nouvelle-Zélande", code: "NZ", flag: "🇳🇿" },
  { value: "FJ", label: "Fidji", code: "FJ", flag: "🇫🇯" }
];


/**
 * Fonction utilitaire pour chercher un pays par code ou nom
 */
export function searchCountry(query: string): CountryOption[] {
  if (!query) return COUNTRY_OPTIONS;
  
  const lowerQuery = query.toLowerCase();
  return COUNTRY_OPTIONS.filter(country => 
    country.label.toLowerCase().includes(lowerQuery) ||
    country.code.toLowerCase().includes(lowerQuery) ||
    country.value.toLowerCase().includes(lowerQuery)
  ).slice(0, 10); // Limite à 10 résultats pour la performance
}
