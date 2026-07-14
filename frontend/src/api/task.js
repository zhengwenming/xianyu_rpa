import axios from 'axios'

const BASE = '/api/tasks'

export function listTasks(params) { return axios.get(BASE, { params }) }
export function createTask(data) { return axios.post(BASE, data) }
export function getTask(id) { return axios.get(`${BASE}/${id}`) }
export function startTask(id) { return axios.post(`${BASE}/${id}/start`) }
export function pauseTask(id) { return axios.post(`${BASE}/${id}/pause`) }
export function resumeTask(id) { return axios.post(`${BASE}/${id}/resume`) }
export function cancelTask(id) { return axios.post(`${BASE}/${id}/cancel`) }
export function deleteTask(id) { return axios.delete(`${BASE}/${id}`) }
export function getTaskProgress(id) { return axios.get(`${BASE}/${id}/progress`) }
