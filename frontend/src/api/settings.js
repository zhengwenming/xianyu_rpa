import axios from 'axios'

const BASE = '/api/settings'

export function getSettings() { return axios.get(BASE) }
export function updateSettings(data) { return axios.put(BASE, data) }
export function resetSettings() { return axios.post(`${BASE}/reset`) }
export function getSuppliers() { return axios.get(`${BASE}/blacklist/suppliers`) }
export function addSupplier(supplier) { return axios.post(`${BASE}/blacklist/suppliers`, null, { params: { supplier } }) }
export function removeSupplier(supplier) { return axios.delete(`${BASE}/blacklist/suppliers`, { params: { supplier } }) }
export function getKeywords() { return axios.get(`${BASE}/blacklist/keywords`) }
export function addKeyword(keyword) { return axios.post(`${BASE}/blacklist/keywords`, null, { params: { keyword } }) }
export function removeKeyword(keyword) { return axios.delete(`${BASE}/blacklist/keywords`, { params: { keyword } }) }