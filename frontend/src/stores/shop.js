import { defineStore } from 'pinia'
import { ref } from 'vue'
import * as api from '../api/shop'

export const useShopStore = defineStore('shop', () => {
  const shops = ref([])
  const loading = ref(false)

  async function fetchShops() {
    loading.value = true
    try {
      const res = await api.listShops()
      shops.value = res.data.data || []
    } catch (e) {
      console.error('fetch shops error:', e)
    } finally {
      loading.value = false
    }
    return shops.value
  }

  async function addShop(data) {
    const res = await api.createShop(data)
    await fetchShops()
    return res.data
  }

  return { shops, loading, fetchShops, addShop }
})