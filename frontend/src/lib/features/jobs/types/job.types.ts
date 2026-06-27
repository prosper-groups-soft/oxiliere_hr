/**
 * Types pour le Job Repository (Positions et Familles de métiers)
 */

export interface JobFamily {
  id: string;
  name: string;
  description: string;
}


export interface Position {
  id: string;
  title: string;
  name?: string; // Backend utilise 'name' au lieu de 'title'
  level: string;
  level_display?: string;
  description?: string;
  job_family?: JobFamily;
  orgUnitId?: string; // Pour compatibilité frontend
}


export interface PositionCreate {
  name: string;
  family_name: string;
  level: string;
  description?: string;
}


export interface CareerHistory {
  id: string;
  position: Position;
  org_unit?: {
    id: string;
    name: string;
    type?: string;
  };
  start_date: string;
  end_date?: string;
  is_current: boolean;
  description?: string;
  days_spent?: number;
}


export interface EmployeeMove {
  new_position_id: string;
  new_org_unit_id?: string;
  effective_date?: string;
  description?: string;
}


export interface InitialAssignment {
  position_id: string;
  org_unit_id: string;
  start_date?: string;
}

