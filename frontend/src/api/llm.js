import axios from 'axios'

const BASE = '/api/llm'

export function listConfigs() { return axios.get(`${BASE}/configs`) }
export function createConfig(data) { return axios.post(`${BASE}/configs`, data) }
export function updateConfig(id, data) { return axios.put(`${BASE}/configs/${id}`, data) }
export function deleteConfig(id) { return axios.delete(`${BASE}/configs/${id}`) }
export function testConfig(id) { return axios.post(`${BASE}/configs/${id}/test`) }
export function activateConfig(id) { return axios.post(`${BASE}/configs/${id}/activate`) }
export function generateText(prompt) { return axios.post(`${BASE}/generate`, { prompt }) }
