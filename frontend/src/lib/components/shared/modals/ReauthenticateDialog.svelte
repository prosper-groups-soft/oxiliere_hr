<script lang="ts">
  import * as Dialog from "@/components/ui/dialog/index.js";
  import { Button } from "@/components/ui/button/index.js";
  import { Input } from "@/components/ui/input/index.js";
  import { Label } from "@/components/ui/label/index.js";
  import { Spinner } from "@/components/ui/spinner/index.js";
  import { AuthEndpoint } from "@/features/auth/api/auth.endpoints";
  import { Lock, Smartphone } from "@lucide/svelte";
  import { toast } from "svelte-sonner";

  interface Props {
    mode: 'password' | 'totp';
    isOpen: boolean;
    onSuccess?: () => void;
    onCancel?: () => void;
    title?: string;
    description?: string;
  }

  let {
    mode = $bindable('password'),
    isOpen = $bindable(false),
    onSuccess,
    onCancel,
    title = mode === 'password' ? 'Confirmer votre mot de passe' : 'Code d\'authentification',
    description = mode === 'password' 
      ? 'Veuillez saisir votre mot de passe pour continuer'
      : 'Veuillez saisir votre code d\'authentification à 6 chiffres'
  }: Props = $props();

  let password = $state('');
  let totpCode = $state('');
  let loading = $state(false);
  let error = $state('');

  function closeModal() {
    isOpen = false;
    password = '';
    totpCode = '';
    error = '';
    onCancel?.();
  }

  async function handleSubmit() {
    if (loading) return;
      
    error = '';
    loading = true;

    try {
      if (mode === 'password') {
        if (!password.trim()) {
          error = 'Le mot de passe est requis';
          return;
        }

        await AuthEndpoint.reauthenticate.create({
          password: password
        });
              
        toast.success('Authentification réussie');
        onSuccess?.();
        closeModal();
      } else {
        if (!totpCode.trim() || totpCode.length !== 6) {
          error = 'Le code doit contenir 6 chiffres';
          return;
        }

        await MFAEndpoint.reauthenticate.create({
          code: totpCode
        });
        toast.success('Code TOTP validé');
        onSuccess?.();
        closeModal();
      }
    } catch (err: any) {
      console.error('Erreur de ré-authentification:', err);
          
      if (err.response?.status === 400) {
        error = mode === 'password' 
          ? 'Mot de passe incorrect'
          : 'Code d\'authentification invalide';
      } else {
        error = 'Une erreur est survenue. Veuillez réessayer.';
      }
    } finally {
      loading = false;
    }
  }

  function handleKeydown(event: KeyboardEvent) {
    if (event.key === 'Enter') {
      handleSubmit();
    }
  }

  function switchMode() {
    // Réinitialiser les champs et erreurs lors du changement de mode
    password = '';
    totpCode = '';
    error = '';
    mode = mode === 'password' ? 'totp' : 'password';
  }
</script>

<Dialog.Root bind:open={isOpen}>
    <Dialog.Content class="sm:max-w-md">
        <Dialog.Header>
            <div class="flex items-center space-x-3 mb-4">
                <div class="flex h-12 w-12 items-center justify-center rounded-full bg-blue-100">
                    {#if mode === 'password'}
                        <Lock class="h-6 w-6 text-blue-600" />
                    {:else}
                        <Smartphone class="h-6 w-6 text-blue-600" />
                    {/if}
                </div>
                <div>
                    <Dialog.Title class="text-lg font-semibold text-gray-900">
                        {title}
                    </Dialog.Title>
                    <Dialog.Description class="text-sm text-gray-600">
                        {description}
                    </Dialog.Description>
                </div>
            </div>
        </Dialog.Header>

        <div class="space-y-4">
            {#if mode === 'password'}
                <div class="space-y-2">
                    <Label for="password">Mot de passe</Label>
                    <Input
                      id="password"
                      type="password"
                      bind:value={password}
                      placeholder="Saisissez votre mot de passe"
                      disabled={loading}
                      onkeydown={handleKeydown}
                      class="w-full"
                    />
                </div>
            {:else}
                <div class="space-y-2">
                    <Label for="totp">Code d'authentification</Label>
                    <Input
                        id="totp"
                        type="text"
                        bind:value={totpCode}
                        placeholder="000000"
                        maxlength={6}
                        disabled={loading}
                        onkeydown={handleKeydown}
                        class="w-full text-center text-lg tracking-widest font-mono"
                    />
                    <p class="text-xs text-gray-500">
                        Ouvrez votre application d'authentification et saisissez le code à 6 chiffres
                    </p>
                </div>
            {/if}
            
            <div class="flex justify-end w-full">
                <Button 
                    variant="link" 
                    onclick={switchMode}
                    disabled={loading}
                    class="text-sm p-0"
                >
                    {mode === 'password' ? 'Utiliser l\'authentification à deux facteurs' : 'Utiliser le mot de passe'}
                </Button>
            </div>

            {#if error}
                <div class="rounded-md bg-red-50 p-3">
                    <p class="text-sm text-red-800">{error}</p>
                </div>
            {/if}
        </div>

        <Dialog.Footer class="flex flex-col-reverse sm:flex-row sm:justify-end sm:space-x-2 space-y-2 space-y-reverse sm:space-y-0 mt-6">
            <Button
                variant="outline"
                onclick={closeModal}
                disabled={loading}
                class="w-full sm:w-auto"
            >
                Annuler
            </Button>
            
            <Button
                onclick={handleSubmit}
                disabled={loading || (mode === 'password' ? !password.trim() : !totpCode.trim())}
                class="w-full sm:w-auto bg-blue-600 hover:bg-blue-700 text-white"
            >
                {#if loading}
                    <Spinner size="small" class="mr-2 text-current" />
                {/if}
                {mode === 'password' ? 'Confirmer' : 'Valider le code'}
            </Button>
        </Dialog.Footer>
    </Dialog.Content>
</Dialog.Root>
