## 1. Organisation de la Sidebar par "Groupes Métiers"

Ne listez pas tout en vrac. Regroupez les modules par affinité pour réduire la charge cognitive :

    **CORE RH** : Employees, Jobs.
    **OPÉRATIONS** : Attendance, Calendar, Leaves.
    **FINANCE** : Payroll, Banking.
    **TALENTS** : Recruitment.

src/lib/
|-- core/ # Logique transverse (Auth, API Client, Layout global)
|-- shared/ # Composants UI atomiques (Button, Avatar, Modal, Badge)
|-- features/ # LE CŒUR : Un dossier par module métier
|-- employees/
|-- components/ # Composants spécifiques (EmployeeRow, OnboardingStepper)
|-- services/ # Appels API TanStack Query (getEmployee, updateStatus)
|-- stores/ # État local au module (filtres persistants)
|-- schemas/ # Validations Zod (IdentitySchema, FamilySchema)
|-- types/ # Types TS (Employee, Dependent)
|-- payroll/
|-- attendance/
