<script lang="ts">
  import AppIcon from '@/components/layout/elements/AppIcon.svelte';
  import AnimateSpin from '@/components/layout/elements/AnimateSpin.svelte';
  import { Button } from '@/components/ui/button';
  import { cn } from '@/utilities/common/css';

  
  type EmptyStateVariant = 'loading' | 'empty' | 'error' | 'offline' | '404';

  interface Props {
    variant: EmptyStateVariant;
    title?: string;
    description?: string;
    /** Callback quand l'utilisateur clique sur Réessayer */
    onRetry?: () => void;
    /** Icône Lucide à afficher */
    icon?: string;
    class?: string;
  }

  let {
    variant,
    title,
    description,
    onRetry,
    icon,
    class: cls = '',
  }: Props = $props();

  const defaults: Record<EmptyStateVariant, { icon: string; iconColor: string; bgColor: string; defaultTitle: string; defaultDesc: string }> = {
    loading:    { icon: 'loader',          iconColor: 'text-blue-500',   bgColor: 'bg-blue-50',   defaultTitle: 'Chargement...',           defaultDesc: 'Connexion au serveur en cours.' },
    empty:      { icon: 'inbox',           iconColor: 'text-slate-400',  bgColor: 'bg-slate-50',  defaultTitle: 'Aucune donnée',          defaultDesc: 'Il n\'y a rien à afficher pour le moment.' },
    error:      { icon: 'alert-triangle',  iconColor: 'text-rose-500',   bgColor: 'bg-rose-50',   defaultTitle: 'Une erreur est survenue', defaultDesc: 'Veuillez réessayer ou contacter le support.' },
    offline:    { icon: 'wifi-off',        iconColor: 'text-amber-500',  bgColor: 'bg-amber-50',  defaultTitle: 'Hors connexion',          defaultDesc: 'Vérifiez votre connexion internet et réessayez.' },
    '404':      { icon: 'file-question',   iconColor: 'text-purple-500', bgColor: 'bg-purple-50', defaultTitle: 'Page introuvable',         defaultDesc: 'La ressource demandée n\'existe pas ou a été supprimée.' },
  };

  const def = $derived.by(() => defaults[variant]);
  const effectiveIcon = $derived.by(() => icon ?? def.icon);
  const effectiveTitle = $derived.by(() => title ?? def.defaultTitle);
  const effectiveDesc = $derived.by(() => description ?? def.defaultDesc);
</script>


<div class={cn('flex flex-col items-center justify-center py-16 px-6 text-center', variant === 'loading' && 'bg-white', cls)}>
  {#if variant === 'loading'}
    <div class="mb-5">
      <AnimateSpin text={effectiveTitle} />
    </div>
  {:else}
    <div class={cn('w-16 h-16 rounded-2xl flex items-center justify-center mb-5', def.bgColor)}>
      <AppIcon
        name={effectiveIcon}
        size={32}
        class={def.iconColor}
        strokeWidth={1.5}
      />
    </div>
  {/if}

  {#if variant !== 'loading'}
    <h3 class="text-[1rem] font-extrabold text-slate-700 mb-1.5">{effectiveTitle}</h3>
    <p class="text-[0.86rem] text-slate-400 max-w-xs leading-relaxed">{effectiveDesc}</p>
  {/if}

  {#if onRetry && (variant === 'error' || variant === 'offline')}
    <Button
      variant="outline"
      size="sm"
      onclick={onRetry}
      class="mt-5 h-8 px-4 text-[0.84rem] rounded-lg">
      <AppIcon name="refresh-cw" size={15} class="mr-1.5" />
      Réessayer
    </Button>
  {/if}
</div>

