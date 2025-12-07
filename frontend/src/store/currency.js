// frontend/src/store/currency.js
import { defineStore } from 'pinia'
import currencyService from '../services/currency'

export const useCurrencyStore = defineStore('currency', {
  state: () => ({
    currencies: [],
    exchangeRates: [],
    selectedCurrency: 'USD',
    loading: false,
    error: null
  }),

  getters: {
    activeCurrencies: (state) => {
      return state.currencies.filter(c => c.is_active)
    },

    currentCurrency: (state) => {
      return state.currencies.find(c => c.code === state.selectedCurrency)
    },

    // Получить курс для конвертации из USD в выбранную валюту
    exchangeRate: (state) => {
      if (state.selectedCurrency === 'USD') return 1
      
      const rate = state.exchangeRates.find(
        r => r.base_currency === 'USD' && r.target_currency === state.selectedCurrency
      )
      return rate ? parseFloat(rate.rate) : 1
    }
  },

  actions: {
    async fetchCurrencies() {
      this.loading = true
      this.error = null
      try {
        this.currencies = await currencyService.getCurrencies()
      } catch (error) {
        console.error('Ошибка загрузки валют:', error)
        this.error = error.message
      } finally {
        this.loading = false
      }
    },

    async fetchExchangeRates() {
      this.loading = true
      this.error = null
      try {
        this.exchangeRates = await currencyService.getLatestRates('USD')
      } catch (error) {
        console.error('Ошибка загрузки курсов:', error)
        this.error = error.message
      } finally {
        this.loading = false
      }
    },

    async convertPrice(amount, fromCurrency = 'USD', toCurrency = null) {
      if (!toCurrency) toCurrency = this.selectedCurrency
      
      if (fromCurrency === toCurrency) return parseFloat(amount)

      try {
        const result = await currencyService.convertCurrency(amount, fromCurrency, toCurrency)
        return parseFloat(result.converted_amount)
      } catch (error) {
        console.error('Ошибка конвертации:', error)
        return parseFloat(amount)
      }
    },

    setSelectedCurrency(currencyCode) {
      this.selectedCurrency = currencyCode
      // Сохраняем выбор в localStorage
      localStorage.setItem('selectedCurrency', currencyCode)
    },

    // Загрузить сохраненную валюту из localStorage
    loadSavedCurrency() {
      const saved = localStorage.getItem('selectedCurrency')
      if (saved) {
        this.selectedCurrency = saved
      }
    },

    // Конвертировать цену локально (без API запроса)
    convertPriceLocally(price) {
      return (parseFloat(price) * this.exchangeRate).toFixed(2)
    }
  }
})
