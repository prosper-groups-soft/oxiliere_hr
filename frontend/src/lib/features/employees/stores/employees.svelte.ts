import type { Employee, EmployeeFilters } from "../types/types";


// Mock Data
const MOCK_EMPLOYEES: Employee[] = [
  { 
    id: 1, 
    name: "Alice Dupont", 
    jobTitle: "Ingénieur Frontend Senior", 
    department: "Ingénierie", 
    status: "Actif", 
    location: "Siège Paris", 
    contractType: "CDI",
    joinDate: "2021-03-15",
    avatarUrl: "" 
  },
  { 
    id: 2, 
    name: "Bob Martin", 
    jobTitle: "Chef de Produit", 
    department: "Produit", 
    status: "Actif", 
    location: "Télétravail", 
    contractType: "CDI",
    joinDate: "2022-06-01",
    avatarUrl: "" 
  },
  { 
    id: 3, 
    name: "Charlie Durand", 
    jobTitle: "Représentant Commercial", 
    department: "Vente", 
    status: "En intégration", 
    location: "Agence Lyon", 
    contractType: "CDD",
    joinDate: "2024-02-10",
    avatarUrl: "" 
  },
  { 
    id: 4, 
    name: "David Leroy", 
    jobTitle: "Spécialiste Marketing", 
    department: "Marketing", 
    status: "Actif", 
    location: "Siège Paris", 
    contractType: "CDI",
    joinDate: "2023-11-20",
    avatarUrl: "" 
  },
  { 
    id: 5, 
    name: "Eve Moreau", 
    jobTitle: "Coordinateur RH", 
    department: "Ressources Humaines", 
    status: "Suspendu", 
    location: "Hub Bordeaux", 
    contractType: "CDI",
    joinDate: "2022-09-12",
    avatarUrl: "" 
  },
  { 
    id: 6, 
    name: "Frank Petit", 
    jobTitle: "Analyste Financier", 
    department: "Finance", 
    status: "Terminé", 
    location: "Siège Paris", 
    contractType: "Freelance",
    joinDate: "2020-05-15",
    avatarUrl: "" 
  },
  { 
    id: 7, 
    name: "Grace Thomas", 
    jobTitle: "Développeur Backend", 
    department: "Ingénierie", 
    status: "Actif", 
    location: "Télétravail", 
    contractType: "CDI",
    joinDate: "2023-01-10",
    avatarUrl: "" 
  },
  { 
    id: 8, 
    name: "Hugo Richard", 
    jobTitle: "Designer UX", 
    department: "Produit", 
    status: "Actif", 
    location: "Agence Lyon", 
    contractType: "Apprentissage",
    joinDate: "2024-01-05",
    avatarUrl: "" 
  },
  { 
    id: 9, 
    name: "Ivy Bernard", 
    jobTitle: "Ingénieur DevOps", 
    department: "Ingénierie", 
    status: "Actif", 
    location: "Siège Paris", 
    contractType: "CDI",
    joinDate: "2021-12-01",
    avatarUrl: "" 
  },
  { 
    id: 10, 
    name: "Jack Simon", 
    jobTitle: "Responsable de Compte", 
    department: "Vente", 
    status: "Actif", 
    location: "Hub Bordeaux", 
    contractType: "CDI",
    joinDate: "2022-04-18",
    avatarUrl: "" 
  },
  { 
    id: 11, 
    name: "Kelly Rose", 
    jobTitle: "Rédacteur de Contenu", 
    department: "Marketing", 
    status: "Actif", 
    location: "Télétravail", 
    contractType: "Stage",
    joinDate: "2024-01-15",
    avatarUrl: "" 
  },
  { 
    id: 12, 
    name: "Leo Michel", 
    jobTitle: "Lead Technique", 
    department: "Ingénierie", 
    status: "Actif", 
    location: "Agence Lyon", 
    contractType: "CDI",
    joinDate: "2019-10-25",
    avatarUrl: "" 
  },
];


export class EmployeeStore {
  // State

  searchQuery = $state("");
  filters = $state<EmployeeFilters>({
    department: [],
    status: [],
    location: []
  });
  currentPage = $state(1);
  perPage = $state(8);

  // Derived
  filteredEmployees = $derived.by(() => {
    return MOCK_EMPLOYEES.filter(emp => {
      const searchLower = this.searchQuery.toLowerCase();
      const matchesSearch = emp.name.toLowerCase().includes(searchLower) || 
                            emp.jobTitle.toLowerCase().includes(searchLower) ||
                            emp.contractType.toLowerCase().includes(searchLower);
            
      const matchesDept = this.filters.department.length === 0 || this.filters.department.includes(emp.department);
      const matchesStatus = this.filters.status.length === 0 || this.filters.status.includes(emp.status);
      const matchesLoc = this.filters.location.length === 0 || this.filters.location.includes(emp.location);
        
      return matchesSearch && matchesDept && matchesStatus && matchesLoc;
    });
  });

  paginatedEmployees = $derived.by(() => {
    return this.filteredEmployees.slice((this.currentPage - 1) * this.perPage, this.currentPage * this.perPage);
  });

  totalCount = $derived(this.filteredEmployees.length);
  totalPages = $derived(Math.ceil(this.totalCount / this.perPage) || 1);
  activeFiltersCount = $derived(
    this.filters.department.length + 
    this.filters.status.length + 
    this.filters.location.length
  );

  // Actions
  setSearchQuery(query: string) {
    this.searchQuery = query;
    this.currentPage = 1;
  }

  toggleFilter(category: keyof EmployeeFilters, value: string) {
    const current = this.filters[category];
    if (current.includes(value)) {
      this.filters[category] = current.filter(v => v !== value);
    } else {
      this.filters[category] = [...current, value];
    }
    this.currentPage = 1;
  }

  setPage(page: number) {
    if (page >= 1 && page <= this.totalPages) {
      this.currentPage = page;
    }
  }

  setPerPage(val: number) {
    this.perPage = val;
    this.currentPage = 1; // Reset to first page when changing perPage
  }

  nextPage() {
    if (this.currentPage < this.totalPages) {
      this.currentPage++;
    }
  }

  prevPage() {
    if (this.currentPage > 1) {
      this.currentPage--;
    }
  }

  resetFilters() {
    this.filters = {
      department: [],
      status: [],
      location: []
    };
    this.searchQuery = "";
    this.currentPage = 1;
  }
}


// Create a global instance if needed, or instantiate in component context context
export const employeeStore = new EmployeeStore();

