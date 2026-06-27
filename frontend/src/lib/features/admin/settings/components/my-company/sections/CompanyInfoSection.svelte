<script lang="ts">
  import { Input } from "@/components/ui/input";
  import { Label } from "@/components/ui/label";
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import { currencySettingsStore } from "../../../stores/currencySettingsStore.svelte";

  const config = $derived(currencySettingsStore.config);
</script>


<div class="p-4 bg-white rounded-xl border border-slate-200 mx-6 mr-8 hidden">
  <div class="flex items-start gap-4">
    <div class="w-12 h-12 rounded-xl bg-indigo-50 flex items-center justify-center text-indigo-600 shrink-0">
      <AppIcon name="office" size={24} />
    </div>
    <div class="flex-1">
      <h5 class="font-medium text-slate-900 text-[0.95rem]">
        Informations légales
      </h5>
      <p class="text-[0.875rem] text-slate-500 mb-4">
        Données d'identification de l'entreprise telles qu'enregistrées auprès des autorités congolaises.
        Ces informations apparaissent sur les documents officiels et bulletins de paie.
      </p>
      
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <Label class="text-[0.875rem]">Nom de l'entreprise</Label>
          <Input
            value={config.companyInfo.name}
            oninput={(e) => currencySettingsStore.updateCompanyInfo({ name: e.currentTarget.value })}
            class="mt-1 shadow-fine"
            placeholder="Oxilière SARL"
          />
        </div>
        <div>
          <Label class="text-[0.875rem]">ID National (ID.NAT)</Label>
          <Input
            value={config.companyInfo.idNat}
            oninput={(e) => currencySettingsStore.updateCompanyInfo({ idNat: e.currentTarget.value })}
            class="mt-1 shadow-fine"
            placeholder="ID National"
          />
        </div>
        <div>
          <Label class="text-[0.875rem]">RCCM</Label>
          <Input
            value={config.companyInfo.rccm}
            oninput={(e) => currencySettingsStore.updateCompanyInfo({ rccm: e.currentTarget.value })}
            class="mt-1 shadow-fine"
            placeholder="CD/..."
          />
        </div>
        <div>
          <Label class="text-[0.875rem]">Numéro d'impôt</Label>
          <Input
            value={config.companyInfo.taxNumber}
            oninput={(e) => currencySettingsStore.updateCompanyInfo({ taxNumber: e.currentTarget.value })}
            class="mt-1 shadow-fine"
            placeholder="Numéro d'impôt"
          />
        </div>
        <div class="md:col-span-2">
          <Label class="text-[0.875rem]">Adresse siège social</Label>
          <Input
            value={config.companyInfo.address}
            oninput={(e) => currencySettingsStore.updateCompanyInfo({ address: e.currentTarget.value })}
            class="mt-1 shadow-fine"
            placeholder="23 Avenue..."
          />
        </div>
      </div>
    </div>
  </div>
</div>

