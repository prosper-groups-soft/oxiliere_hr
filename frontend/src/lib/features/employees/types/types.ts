export interface Employee {
  id: number;
  name: string;
  jobTitle: string;
  department: string;
  status: string;
  location: string;
  contractType: string;
  joinDate: string;
  avatarUrl: string;
}


export interface EmployeeFilters {
  department: string[];
  status: string[];
  location: string[];
}

