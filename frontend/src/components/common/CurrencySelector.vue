
<script setup>
import { computed, onMounted } from 'vue'
import { useCurrencyStore } from '../../store/currency'

const currencyStore = useCurrencyStore()

const selectedCurrency = computed({
  get: () => currencyStore.selectedCurrency,
  set: (value) => currencyStore.setSelectedCurrency(value)
})

const activeCurrencies = computed(() => currencyStore.activeCurrencies)
const currentCurrency = computed(() => currencyStore.currentCurrency)
const exchangeRate = computed(() => currencyStore.exchangeRate)

const handleCurrencyChange = async () => {
  console.log('Валюта изменена на:', selectedCurrency.value)
  // Store автоматически обновит цены через геттер
}

onMounted(async () => {
  currencyStore.loadSavedCurrency()
  await currencyStore.fetchCurrencies()
  await currencyStore.fetchExchangeRates()
})
</script>

<style scoped>
.currency-selector {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 15px;
  background: #f8f9fa;
  border-radius: 8px;
  margin-bottom: 20px;
}

.currency-label {
  display: flex;
  align-items: center;
  gap: 5px;
  font-weight: 500;
  color: #495057;
  margin: 0;
}

.currency-icon {
  font-size: 1.2em;
}

.currency-select {
  padding: 8px 12px;
  border: 1px solid #ced4da;
  border-radius: 6px;
  background: white;
  font-size: 14px;
  cursor: pointer;
  transition: border-color 0.2s;
  min-width: 200px;
}

.currency-select:hover {
  border-color: #86b7fe;
}

.currency-select:focus {
  outline: none;
  border-color: #0d6efd;
  box-shadow: 0 0 0 0.2rem rgba(13, 110, 253, 0.25);
}

.exchange-rate {
  font-size: 12px;
  color: #6c757d;
  padding: 5px 10px;
  background: white;
  border-radius: 4px;
  border: 1px solid #dee2e6;
}
</style>
