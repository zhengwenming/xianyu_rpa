import axios from 'axios'

const BASE = '/api/listing-logs'

export function listListingLogs(params) { return axios.get(BASE, { params }) }
export function getListingLogSummary(params) { return axios.get(`${BASE}/summary`, { params }) }
export function getListingLog(id) { return axios.get(`${BASE}/${id}`) }
export function clearListingLogs(params) { return axios.delete(BASE, { params }) }
export function exportListingLogs(params) { return axios.get(`${BASE}/export`, { params, responseType: 'blob' }) }
