// frontend/src/services/currency.js
import api from './api'

export const currencyService = {
  // Получить список всех валют
  async getCurrencies() {
    const response = await api.get('/currency/currencies/')
    return response.data
  },

  // Получить активные валюты
  async getActiveCurrencies() {
    const response = await api.get('/currency/currencies/active/')
    return response.data
  },

  // Получить курсы обмена
  async getExchangeRates(params = {}) {
    const response = await api.get('/currency/rates/', { params })
    return response.data
  },

  // Получить последние курсы для базовой валюты
  async getLatestRates(baseCurrency = 'USD') {
    const response = await api.get('/currency/rates/latest/', {
      params: { base: baseCurrency }
    })
    return response.data
  },

  // Конвертировать сумму
  async convertCurrency(amount, fromCurrency, toCurrency) {
    const response = await api.post('/currency/rates/convert/', {
      amount,
      from_currency: fromCurrency,
      to_currency: toCurrency
    })
    return response.data
  }
}

export default currencyService
