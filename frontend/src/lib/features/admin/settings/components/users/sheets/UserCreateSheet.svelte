<script lang="ts">
  import { Button } from "@/components/ui/button";
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import * as Sheet from "@/components/ui/sheet";
  import UserCreateForm from "../forms/UserCreateForm.svelte";
  import type { CreateUserInput } from "../../../types/user.types";

  interface Props {
    open?: boolean;
    onClose?: () => void;
    onSave?: (data: CreateUserInput) => void;
  }

  let { open = $bindable(false), onClose, onSave }: Props = $props();

  let formData = $state<CreateUserInput>({
    email: '',
    firstName: '',
    lastName: '',
    role: 'EMPLOYEE',
    orgUnit: '',
    phone: ''
  });

  function handleSave() {
    if (formData) {
      onSave?.(formData);
      open = false;
    }
  }

  function handleClose() {
    open = false;
    onClose?.();
  }
</script>


<Sheet.Root bind:open>
  <Sheet.Content side="right" class="sm:max-w-md flex flex-col h-full overflow-hidden p-0">
    <Sheet.Header class="px-6 py-4 border-b bg-slate-50/50">
      <Sheet.Title class="font-bold text-[1rem]">Nouvel utilisateur</Sheet.Title>
    </Sheet.Header>

    <div class="flex-1 overflow-y-auto px-6 py-6 custom-scrollbar">
      <UserCreateForm
        bind:formData
        onSubmit={handleSave}
      />
    </div>

    <Sheet.Footer class="px-6 py-4 border-t flex flex-row gap-3 bg-slate-50/50">
      <Sheet.Close onclick={handleClose} class="flex-1">
        <Button variant="outline" class="w-full h-9">
          Annuler
        </Button>
      </Sheet.Close>
      <Button
        onclick={handleSave}
        class="flex-1 h-9 bg-blue-600 hover:bg-blue-700 text-white font-medium"
      >
        <AppIcon name="plus" size={17} />
        Créer
      </Button>
    </Sheet.Footer>
  </Sheet.Content>
</Sheet.Root>


<style>
  .custom-scrollbar::-webkit-scrollbar {
    width: 4px;
  }
  .custom-scrollbar::-webkit-scrollbar-thumb {
    background: #e2e8f0;
    border-radius: 10px;
  }
  .custom-scrollbar::-webkit-scrollbar-track {
    background: transparent;
  }
</style>

