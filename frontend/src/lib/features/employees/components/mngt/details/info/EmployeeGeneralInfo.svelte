<script lang="ts">
  import AppIcon from '@/components/layout/elements/AppIcon.svelte';
  import { 
    Card, 
    CardContent, 
    CardHeader, 
    CardTitle 
  } from '@/components/ui/card';
  import { Separator } from '@/components/ui/separator';
  import type { Employee } from '@/features/employees/types/types';

  let { employee } = $props<{ employee: Employee }>();
</script>


<Card class="shadow-none">
  <CardHeader>
    <CardTitle class="flex items-center gap-2">
      <AppIcon name="user" size={20} />
      Informations générales
    </CardTitle>
  </CardHeader>
  <CardContent class="space-y-4">
    <div class="grid grid-cols-2 gap-4">
      <div>
        <div class="text-sm font-medium text-slate-500">Email</div>
        <p class="text-sm text-slate-900">{employee.email}</p>
      </div>
      <div>
        <div class="text-sm font-medium text-slate-500">Téléphone</div>
        <p class="text-sm text-slate-900">{employee.phone || '+33 6 00 00 00 00'}</p>
      </div>
      <div>
        <div class="text-sm font-medium text-slate-500">Département</div>
        <p class="text-sm text-slate-900">{employee.department}</p>
      </div>
      <div>
        <div class="text-sm font-medium text-slate-500">Poste</div>
        <p class="text-sm text-slate-900">{employee.role || 'Consultant'}</p>
      </div>
    </div>
    
    <Separator />
    
    <div>
      <div class="text-sm font-medium text-slate-500">Date d'arrivée</div>
      <p class="text-sm text-slate-900 mt-1">12 Mars 2022</p>
    </div>
    
    <Separator />
    
    <div>
      <div class="text-sm font-medium text-slate-500">Statut</div>
      <div class="flex items-center gap-2 mt-1">
        <div class="h-2 w-2 bg-emerald-500 rounded-full"></div>
        <span class="text-sm text-slate-700">Actif</span>
      </div>
    </div>
  </CardContent>
</Card>

