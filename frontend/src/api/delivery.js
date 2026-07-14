import axios from 'axios'

const BASE = '/api/delivery'

export function listDeliveryConfigs(params) { return axios.get(`${BASE}/configs`, { params }) }
export function createDeliveryConfig(data) { return axios.post(`${BASE}/configs`, data) }
export function updateDeliveryConfig(id, data) { return axios.put(`${BASE}/configs/${id}`, data) }
export function deleteDeliveryConfig(id) { return axios.delete(`${BASE}/configs/${id}`) }
export function getProductConfig(productId) { return axios.get(`${BASE}/configs/${productId}`) }
export function listOrders() { return axios.get(`${BASE}/orders`) }
export function listDeliveryLogs(params) { return axios.get(`${BASE}/logs`, { params }) }
export function getDeliveryLogSummary() { return axios.get(`${BASE}/logs/summary`) }
export function getCardPool(productId) { return axios.get(`${BASE}/cards/${productId}`) }
export function addCards(productId, cards) { return axios.post(`${BASE}/cards/${productId}`, cards) }