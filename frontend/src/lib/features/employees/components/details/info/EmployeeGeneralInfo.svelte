<script lang="ts">
  import AppIcon from '@/components/layout/elements/AppIcon.svelte';
  import { Badge } from '@/components/ui/badge';
  import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
  import type { Employee } from '../../../types/types';

  let { employee } = $props<{ employee: Employee }>();
</script>


<Card class="overflow-hidden shadow-none p-0">
  <CardHeader class="border-b border-slate-200 bg-white p-0! py-2!">
    <CardTitle class="text-[1.1rem] font-extrabold flex items-center gap-3 text-slate-800">
      <div class="p-2 bg-slate-100 rounded-lg text-slate-600">
        <AppIcon name="user" size={20} />
      </div>
      Informations Générales
    </CardTitle>
  </CardHeader>
  
  <CardContent class="p-6">
    <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
      <div class="space-y-6">
        <div class="flex items-start gap-4 group">
          <div class="p-2.5 rounded-xl bg-blue-50 text-blue-600 group-hover:scale-110 transition-transform">
            <AppIcon name="mail" size={20} />
          </div>
          <div class="space-y-1">
            <p class="text-[0.7rem] font-bold text-slate-400 uppercase tracking-widest">Email Professionnel</p>
            <p class="text-[0.9rem] font-semibold text-slate-700">{employee.email}</p>
          </div>
        </div>

        <div class="flex items-start gap-4 group">
          <div class="p-2.5 rounded-xl bg-emerald-50 text-emerald-600 group-hover:scale-110 transition-transform">
            <AppIcon name="phone" size={20} />
          </div>
          <div class="space-y-1">
            <p class="text-[0.7rem] font-bold text-slate-400 uppercase tracking-widest">Téléphone</p>
            <p class="text-[0.9rem] font-semibold text-slate-700">{employee.phone || '+33 6 00 00 00 00'}</p>
          </div>
        </div>
      </div>

      <div class="space-y-6">
        <div class="flex items-start gap-4 group">
          <div class="p-2.5 rounded-xl bg-purple-50 text-purple-600 group-hover:scale-110 transition-transform">
            <AppIcon name="office" size={20} />
          </div>
          <div class="space-y-1">
            <p class="text-[0.7rem] font-bold text-slate-400 uppercase tracking-widest">Département</p>
            <Badge variant="secondary" class="bg-purple-100/50 text-purple-700 border-none font-bold text-[0.75rem] px-3">
              {employee.department}
            </Badge>
          </div>
        </div>

        <div class="flex items-start gap-4 group">
          <div class="p-2.5 rounded-xl bg-amber-50 text-amber-600 group-hover:scale-110 transition-transform">
            <AppIcon name="calendar" size={20} />
          </div>
          <div class="space-y-1">
            <p class="text-[0.7rem] font-bold text-slate-400 uppercase tracking-widest">Date d'arrivée</p>
            <p class="text-[0.9rem] font-semibold text-slate-700">12 Mars 2022</p>
          </div>
        </div>
      </div>
    </div>
  </CardContent>
</Card>

