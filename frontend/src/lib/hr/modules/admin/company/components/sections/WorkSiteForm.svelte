<script lang="ts">
  import { Button } from "@/components/ui/button";
  import { Input } from "@/components/ui/input";
  import { Label } from "@/components/ui/label";
  import AppIcon from "@/hr/components/layout/elements/AppIcon.svelte";
  import AnimateSpin from "@/hr/components/layout/elements/AnimateSpin.svelte";
  import ValidationError from "@/hr/components/ui/validation-error";
  import { preventNonNumeric } from "@/hr/utilities/common/number";

  
  interface Values {
    name: string;
    latitude: number | undefined | null;
    longitude: number | undefined | null;
    allowed_radius: number | null;
  }

  interface Props {
    values: Values;
    errors: Record<string, string>;
    isPending?: boolean;
    isGettingLocation?: boolean;
    showGeoButton?: boolean;
    submitLabel?: string;
    onGetLocation?: () => void;
    onUpdate: (field: keyof Values, value: any) => void;
    onSubmit: () => void;
    onCancel: () => void;
  }

  let {
    values,
    errors,
    isPending = false,
    isGettingLocation = false,
    showGeoButton = false,
    submitLabel = "Enregistrer",
    onGetLocation,
    onUpdate,
    onSubmit,
    onCancel
  }: Props = $props();
</script>


<div class="grid grid-cols-1 md:grid-cols-2 gap-3">
  <div class="md:col-span-2">
    <Label class="text-[0.875rem]">Nom du site</Label>
    <Input
      value={values.name}
      oninput={(e) => onUpdate('name', e.currentTarget.value)}
      class="mt-1 shadow-fine"
      placeholder="Ex: Siège social Kinshasa"
    />
    <ValidationError {errors} field="name" />
  </div>

  <div>
    <div class="flex items-center justify-between h-6">
      <Label class="text-[0.875rem]">Latitude</Label>
      {#if showGeoButton && onGetLocation}
        <Button
          type="button"
          variant="ghost"
          onclick={onGetLocation}
          disabled={isGettingLocation}
          class="h-6 px-2 py-0 text-[0.875rem] text-emerald-600 hover:text-emerald-700 hover:bg-emerald-50"
        >
          {#if isGettingLocation}
            <AnimateSpin text="" class="border-emerald-500 size-3" />
          {:else}
            <AppIcon name="map-pin" size={18} class="mr-1" />
          {/if}
          Ma position
        </Button>
      {/if}
    </div>
    <Input
      type="number"
      step="any"
      onkeydown={preventNonNumeric}
      value={values.latitude ?? ''}
      oninput={(e) => onUpdate('latitude', parseFloat(e.currentTarget.value) || null)}
      class="mt-1 shadow-fine"
      placeholder="-4.325"
    />
    <ValidationError {errors} field="latitude" />
  </div>

  <div>
    <div class="flex items-center h-6">
      <Label class="text-[0.875rem]">Longitude</Label>
    </div>
    <Input
      type="number"
      step="any"
      onkeydown={preventNonNumeric}
      value={values.longitude ?? ''}
      oninput={(e) => onUpdate('longitude', parseFloat(e.currentTarget.value) || null)}
      class="mt-1 shadow-fine"
      placeholder="15.322"
    />
    <ValidationError {errors} field="longitude" />
  </div>

  <div class="md:col-span-2">
    <Label class="text-[0.875rem]">Rayon autorisé (mètres)</Label>
    <Input
      type="number"
      onkeydown={preventNonNumeric}
      value={values.allowed_radius ?? ''}
      oninput={(e) => {
        const raw = e.currentTarget.value;
        onUpdate('allowed_radius', raw === '' ? null : (parseInt(raw) || null));
      }}
      class="mt-1 shadow-fine"
      placeholder="Ex: 100"
      min={10}
      max={1000}
    />
    <ValidationError {errors} field="allowed_radius" />
    <p class="text-[0.86rem] text-slate-400 mt-1">
      Distance maximale autorisée pour les pointages depuis ce site
    </p>
  </div>
</div>

<div class="flex justify-end gap-2 mt-4">
  <Button onclick={onCancel} variant="outline" class="h-8">
    <AppIcon name="x" class="text-slate-300" size={18} />
    Annuler
  </Button>
  <Button onclick={onSubmit} disabled={isPending} class="h-8 bg-emerald-600 hover:bg-emerald-700 transition-all">
    {#if isPending}
      <AnimateSpin text="" class="border-white size-3" />
    {:else}
      <AppIcon name="check" size={18} />
    {/if}
    {submitLabel}
  </Button>
</div>

