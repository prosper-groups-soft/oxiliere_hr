<script lang="ts">
	import type { FieldConfig, FieldInstance, FormInstance } from '../../core/types.js';
	import { isBusinessType } from './field-helpers.js';
	import { getTypeDefinition } from '../../core/typeRegistry.js';
	import TextField from './primitives/TextField.svelte';
	import TextareaField from './primitives/TextareaField.svelte';
	import BooleanField from './primitives/BooleanField.svelte';
	import SelectField from './primitives/SelectField.svelte';
	import DateField from './primitives/DateField.svelte';
	import NumberField from './primitives/NumberField.svelte';
	import CurrencyField from './primitives/CurrencyField.svelte';
	import PasswordField from './primitives/PasswordField.svelte';
	import PhoneField from './primitives/PhoneField.svelte';
	import CountryField from './primitives/CountryField.svelte';
	import TreeField from './primitives/TreeField.svelte';
	import FileField from './primitives/FileField.svelte';
	import CityField from './business/CityField.svelte';
	import RadioField from './primitives/RadioField.svelte';
	import BusinessField from './business/BusinessField.svelte';
	import RepeaterField from './shared/RepeaterField.svelte';
	import { isRepeaterField } from './field-helpers.js';

	let { config, field, form }: { config: FieldConfig; field: FieldInstance; form?: FormInstance<any> } = $props();

	// Dispatcher : route vers le sous-renderer selon le type.
	// Les branches gardent le même ordre qu'avant l'éclatement.
	const isBusiness = $derived(isBusinessType(config.type));
	// Behavior repeater (api §9) : prioritaire — le renderer du type est dupliqué par item.
	const isRepeater = $derived(isRepeaterField(config));
	const isBoolean = $derived(config.type === 'boolean' || config.type === 'checkbox' || config.type === 'switch');
	const isTextarea = $derived(config.type === 'textarea');
	const isDate = $derived(config.type === 'date');
	const isNumber = $derived(config.type === 'number');
	const isCurrency = $derived(config.type === 'currency');
	const isPassword = $derived(config.type === 'password');
	const isPhone = $derived(config.type === 'phone');
	const isCountry = $derived(config.type === 'country');
	const isTree = $derived(config.type === 'tree');
	const isFile = $derived(config.type === 'file');
	const isCity = $derived(config.type === 'city');
	const isRadio = $derived(config.type === 'radio');
	const isSelect = $derived(
		config.type === 'select' ||
			config.type === 'combobox' ||
			config.type === 'autocomplete'
	);
	// Fallback registre (api §14) : defaultRenderer d'un type enregistré via registerType.
	// Un composant enregistré a priorité sur tout (ex: EmployeePicker pour `employee`) ;
	// une string ('business') laisse le dispatcher standard router.
	const registryRenderer = $derived(getTypeDefinition(config.type)?.defaultRenderer);
	const isRegistryComponent = $derived(typeof registryRenderer === 'function');
</script>

{#if !field.isVisible}
	<!-- champ masqué : rien -->
{:else if isRepeater}
	<RepeaterField {config} {field} {form} />
{:else if isTextarea}
	<TextareaField {config} {field} />
{:else if isBoolean}
	<BooleanField {config} {field} />
{:else if isRegistryComponent}
	<!-- Renderer riche enregistré par l'app (registerType, api §14) -->
	{@const RegistryRenderer = registryRenderer}
	<RegistryRenderer {config} {field} {form} />
{:else if registryRenderer === 'business' || isBusiness}
	<BusinessField {config} {field} {form} />
{:else if isDate}
	<DateField {config} {field} />
{:else if isCurrency}
	<CurrencyField {config} {field} />
{:else if isNumber}
	<NumberField {config} {field} />
{:else if isPassword}
	<PasswordField {config} {field} />
{:else if isRadio}
	<RadioField {config} {field} />
	{:else if isPhone}
	<PhoneField {config} {field} />
	{:else if isCountry}
		<CountryField {config} {field} />
	{:else if isTree}
		<TreeField {config} {field} {form} />
	{:else if isFile}
		<FileField {config} {field} {form} />
	{:else if isCity}
	<CityField {config} {field} {form} />
	{:else if isSelect}
	<SelectField {config} {field} {form} />
{:else if registryRenderer}
	<!-- Type inconnu du dispatcher mais enregistré (registerType) : renderer par défaut du registre (api §14) -->
	{@const RegistryRenderer = registryRenderer}
	<RegistryRenderer {config} {field} {form} />
{:else}
	<TextField {config} {field} />
{/if}
