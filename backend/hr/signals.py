from django.dispatch import Signal


# --- Signaux de domaine (découplage inter-modules) ---
#
# Direction : payroll / jobs / leaves … ÉMETTENT un événement métier générique
# (`employee_changed`) sans connaître le module `employees`.
# Le module `hr.employees` ÉCOUTE ce signal pour purger ses propres caches
# (detail API + cacheops ORM). Ainsi, aucune dépendance directionnelle
# n'est créée entre les modules : chacun reste responsable de son cache.

# Signal émis lorsqu'une donnée dépendante d'un employé change
# (contrat, poste, etc.). `sender` = modèle à l'origine du changement,
# `kwargs['employee_id']` = UUID de l'employé concerné.
employee_changed = Signal()
