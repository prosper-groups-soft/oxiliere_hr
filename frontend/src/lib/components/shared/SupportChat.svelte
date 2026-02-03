<script lang="ts">
	import * as Chat from '$lib/components/ui/chat';
	import { Button } from '$lib/components/ui/button';
    import { Textarea } from '$lib/components/ui/textarea';
	import { Send, Info, MessageSquare, X} from 'lucide-svelte';
	import * as data from './data';
	import { formatShortTime, get_initials } from '$lib/utils/string';
	import { fly } from 'svelte/transition';

	let message = $state('');

	const messages = $state(data.messages);

	let open = $state(false);

	function toggleChat() {
		open = !open;
	}

	function handleKeydown(event: KeyboardEvent) {
		if (event.key === 'Enter' && !event.shiftKey) {
			event.preventDefault();
			sendMessage();
		}
	}

	function sendMessage() {
		if (message.trim() !== '') {
			messages.push({ 
				message, 
				senderId: data.user.id, 
				sentAt: formatShortTime(new Date()) 
			});
			message = '';
		}
	}
</script>

<!-- Floating button to toggle the chat -->
<div class="fixed bottom-6 right-6 z-50">
	<Button
		variant="default"
		size="icon-lg"
		class="rounded-full shadow-lg hover:shadow-xl transition-all duration-300"
		onclick={toggleChat}
	>
		{#if open}
			<X />
		{:else}
			<MessageSquare />
		{/if}
	</Button>
</div>

<!-- Chat interface -->
{#if open}
<div 
	class="fixed bottom-24 right-6 z-40 w-80 md:w-96 shadow-xl rounded-lg overflow-hidden"
	transition:fly={{ y: 20, duration: 300 }}
	class:hidden={!open}
>
	<div class="border-border w-full border bg-background rounded-lg">
	<div class="bg-background flex place-items-center justify-between border-b p-2">
		<div class="flex place-items-center gap-2 pl-2">
			<div class="flex flex-col">
				<span class="text-sm font-medium">Support</span>
				<span class="text-xs">Active 2 mins ago</span>
			</div>
		</div>
		<div class="flex place-items-center">
			<Button variant="ghost" size="icon" class="rounded-full">
				<Info />
			</Button>
		</div>
	</div>
	<Chat.List class="max-h-[400px]">
		{#each messages as message (message)}
			{@const sender = data.users.find((u) => u.id === message.senderId)}
			<Chat.Bubble variant={message.senderId === data.user.id ? 'sent' : 'received'}>
				<Chat.BubbleAvatar>
					<Chat.BubbleAvatarImage src={sender?.img} alt={sender?.username} />
					<Chat.BubbleAvatarFallback>
						{message.senderId === data.user.id ? "Me" : "Support"}
					</Chat.BubbleAvatarFallback>
				</Chat.BubbleAvatar>
				<Chat.BubbleMessage class="flex flex-col gap-1">
					<p>{message.message}</p>
					<div class="w-full text-xs group-data-[variant='sent']/chat-bubble:text-end">
						{message.sentAt}
					</div>
				</Chat.BubbleMessage>
			</Chat.Bubble>
		{/each}
		<Chat.Bubble variant="received">
			<Chat.BubbleAvatar>
				<Chat.BubbleAvatarImage src={data.friend.img} alt={data.friend.username} />
				<Chat.BubbleAvatarFallback>
					{get_initials(data.friend.name)}
				</Chat.BubbleAvatarFallback>
			</Chat.BubbleAvatar>
			<Chat.BubbleMessage typing />
		</Chat.Bubble>
	</Chat.List>
	<form
		onsubmit={(e) => {
			e.preventDefault();
			sendMessage();
		}}
		class="flex place-items-center gap-2 p-2"
	>

		<Textarea 
			bind:value={message} 
			class="min-h-[40px] max-h-[120px] rounded-lg resize-none py-2 px-4" 
			placeholder="Type a message..." 
			rows={1}
			onkeydown={handleKeydown}
		/>
		<Button
			type="submit"
			variant="default"
			size="icon"
			class="shrink-0 rounded-full"
			disabled={message === ''}
		>
			<Send />
		</Button>
	</form>
</div>
</div>
{/if}
