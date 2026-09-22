import type { UserRole } from "../types/user.types";

export interface AvatarColors {
  bg: string;
  text: string;
  border: string;
}

export function getAvatarColors(role: UserRole): AvatarColors {
  switch (role) {
    case 'RH_ADMIN':
      return { bg: 'bg-blue-100', text: 'text-blue-700', border: 'border-blue-200' };
    case 'MANAGER':
      return { bg: 'bg-green-100', text: 'text-green-700', border: 'border-green-200' };
    case 'EMPLOYEE':
      return { bg: 'bg-slate-100', text: 'text-slate-700', border: 'border-slate-200' };
    default:
      return { bg: 'bg-blue-100', text: 'text-blue-700', border: 'border-blue-200' };
  }
}
