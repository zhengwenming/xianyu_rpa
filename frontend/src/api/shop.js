import axios from 'axios'

const BASE = '/api/shops'

export function listShops() { return axios.get(BASE) }
export function createShop(data) { return axios.post(BASE, data) }
export function updateShop(id, data) { return axios.put(`${BASE}/${id}`, data) }
export function deleteShop(id) { return axios.delete(`${BASE}/${id}`) }
export function authorizeShop(id) { return axios.post(`${BASE}/${id}/authorize`) }
export function revokeShop(id) { return axios.post(`${BASE}/${id}/revoke`) }
export function checkLoginStatus(id) { return axios.get(`${BASE}/${id}/login-status`) }
export function clearSession(id) { return axios.delete(`${BASE}/${id}/session`) }
