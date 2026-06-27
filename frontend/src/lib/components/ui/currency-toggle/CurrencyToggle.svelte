<script lang="ts">
  /**
   * Currency Toggle Component
   * 
   * A reusable toggle switch for switching between CDF and USD currencies
   * with a sliding background animation.
   * 
   * Usage:
   * <CurrencyToggle 
   *   currency={currentCurrency} 
   *   onChange={(newCurrency) => handleCurrencyChange(newCurrency)} 
   * />
   */
  
  import type { Currency } from '@/constants/finance';
  
  interface Props {
    currency: Currency;
    onChange?: (currency: Currency) => void;
    size?: 'sm' | 'md';
  }
  
  let { 
    currency = $bindable(),
    onChange,
    size = 'sm'
  }: Props = $props();
  
  const sizeClasses = {
    sm: {
      container: 'p-0.5',
      button: 'px-2.5 py-1 text-[0.8rem]',
      offset: 2
    },
    md: {
      container: 'p-1',
      button: 'px-4 py-2 text-[0.9rem]',
      offset: 4
    }
  };

  // Background spacing in pixels for inline styles (Tailwind can't scan dynamic classes)
  const bgSpacing = $derived(size === 'sm' ? 2 : 4);
  
  function handleClick(newCurrency: Currency) {
    currency = newCurrency;
    onChange?.(newCurrency);
  }
</script>


<div class="relative flex bg-slate-100 rounded-lg {sizeClasses[size].container}">
  <!-- Sliding background -->
  <div 
    class="absolute bg-white rounded-md shadow-sm transition-all duration-300 ease-out"
    style="
      top: {bgSpacing}px;
      bottom: {bgSpacing}px;
      width: calc(50% - {bgSpacing}px);
      left: {currency === 'CDF' ? `${bgSpacing}px` : '50%'};
    "
  ></div>
  
  <button
    class="relative z-10 {sizeClasses[size].button} rounded-md font-medium transition-colors duration-300 cursor-pointer {currency === 'CDF' ? 'text-slate-900' : 'text-slate-500 hover:text-slate-700'}"
    onclick={() => handleClick('CDF')}
  >
    CDF
  </button>
  
  <button
    class="relative z-10 {sizeClasses[size].button} rounded-md font-medium transition-colors duration-300 cursor-pointer {currency === 'USD' ? 'text-slate-900' : 'text-slate-500 hover:text-slate-700'}"
    onclick={() => handleClick('USD')}
  >
    USD
  </button>
</div>
