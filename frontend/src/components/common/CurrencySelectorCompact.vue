<template>
  <div class="currency-selector-compact">
    <div class="relative" ref="currencyMenu">
      <button
        @click="showMenu = !showMenu"
        class="flex items-center space-x-2 px-3 py-2 text-gray-600 hover:text-black hover:bg-gray-50 rounded-lg transition-all duration-200"
        :title="`Current currency: ${selectedCurrency}`"
      >
        <span class="text-lg">{{ currentSymbol }}</span>
        <span class="text-sm font-medium hidden sm:inline">{{ selectedCurrency }}</span>
        <svg class="h-4 w-4 transition-transform" :class="{ 'rotate-180': showMenu }" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      <!-- Currency Dropdown -->
      <transition name="fade">
        <div v-if="showMenu" class="absolute right-0 mt-2 w-56 bg-white rounded-lg shadow-lg border border-gray-200 py-1 max-h-80 overflow-y-auto z-50">
          <div class="px-3 py-2 border-b border-gray-100">
            <p class="text-xs font-semibold text-gray-500 uppercase">Select Currency</p>
          </div>
          <button
            v-for="currency in activeCurrencies"
            :key="currency.code"
            @click="selectCurrency(currency.code)"
            class="w-full text-left px-4 py-2 text-sm hover:bg-gray-100 transition-colors flex items-center justify-between"
            :class="{ 'bg-gray-50 text-black font-medium': currency.code === selectedCurrency }"
          >
            <div class="flex items-center space-x-3">
              <span class="text-lg">{{ currency.symbol }}</span>
              <div>
                <div class="font-medium">{{ currency.code }}</div>
                <div class="text-xs text-gray-500">{{ currency.name }}</div>
              </div>
            </div>
            <svg v-if="currency.code === selectedCurrency" class="h-4 w-4 text-black" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
            </svg>
          </button>
          <div v-if="exchangeRate !== 1" class="px-4 py-2 border-t border-gray-100 bg-gray-50">
            <p class="text-xs text-gray-600">
              1 USD = {{ exchangeRate.toFixed(4) }} {{ selectedCurrency }}
            </p>
          </div>
        </div>
      </transition>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useCurrencyStore } from '../../store/currency'

const currencyStore = useCurrencyStore()
const showMenu = ref(false)
const currencyMenu = ref(null)

const selectedCurrency = computed({
  get: () => currencyStore.selectedCurrency,
  set: (value) => currencyStore.setSelectedCurrency(value)
})

const activeCurrencies = computed(() => currencyStore.activeCurrencies)
const currentSymbol = computed(() => currencyStore.currentCurrency?.symbol || '$')
const exchangeRate = computed(() => currencyStore.exchangeRate)

const selectCurrency = (code) => {
  selectedCurrency.value = code
  showMenu.value = false
}

// Close menu when clicking outside
const handleClickOutside = (event) => {
  if (currencyMenu.value && !currencyMenu.value.contains(event.target)) {
    showMenu.value = false
  }
}

onMounted(async () => {
  document.addEventListener('click', handleClickOutside)
  currencyStore.loadSavedCurrency()
  await currencyStore.fetchCurrencies()
  await currencyStore.fetchExchangeRates()
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>

<style scoped>
.currency-selector-compact {
  position: relative;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

.fade-enter-to,
.fade-leave-from {
  opacity: 1;
  transform: translateY(0);
}

.rotate-180 {
  transform: rotate(180deg);
}
</style>
