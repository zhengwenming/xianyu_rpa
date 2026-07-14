import axios from 'axios'

const BASE = '/api/task-logs'

export function listTaskLogs(params) { return axios.get(BASE, { params }) }
export function getTaskLogSummary(params) { return axios.get(`${BASE}/summary`, { params }) }
export function getTaskLog(id) { return axios.get(`${BASE}/${id}`) }
export function getTaskListings(id) { return axios.get(`${BASE}/${id}/listings`) }
export function clearTaskLogs(confirm) { return axios.delete(BASE, { params: { confirm } }) }
