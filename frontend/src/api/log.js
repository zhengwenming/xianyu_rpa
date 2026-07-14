import axios from 'axios'

const BASE = '/api/logs'

export function queryLogs(params) { return axios.get(BASE, { params }) }
export function exportLogs() { return axios.get(`${BASE}/export`, { responseType: 'blob' }) }
