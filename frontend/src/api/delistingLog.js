import axios from 'axios'

const BASE = '/api/delisting-logs'

export function listDelistingLogs(params) { return axios.get(BASE, { params }) }
export function getDelistingLogSummary(params) { return axios.get(`${BASE}/summary`, { params }) }
export function getDelistingLog(id) { return axios.get(`${BASE}/${id}`) }
export function clearDelistingLogs(params) { return axios.delete(BASE, { params }) }
