import axios from 'axios'

const BASE = '/api/reply'

export function getReplyStatus() { return axios.get(`${BASE}/status`) }
export function startReply(shopId) { return axios.post(`${BASE}/${shopId}/start`) }
export function stopReply(shopId) { return axios.post(`${BASE}/${shopId}/stop`) }
export function listConversations(shopId) { return axios.get(`${BASE}/${shopId}/conversations`) }
export function getConversation(shopId, userId) { return axios.get(`${BASE}/${shopId}/conversations/${userId}`) }
export function toggleTakeover(shopId, userId) { return axios.post(`${BASE}/${shopId}/conversations/${userId}/takeover`) }
export function sendMessage(shopId, userId, text) { return axios.post(`${BASE}/${shopId}/send`, null, { params: { user_id: userId, text } }) }
export function getExpertPrompts() { return axios.get(`${BASE}/experts/prompts`) }
export function updateExpertPrompt(data) { return axios.put(`${BASE}/experts/prompts`, data) }
export function listRules() { return axios.get(`${BASE}/rules`) }
export function createRule(keyword, reply) { return axios.post(`${BASE}/rules`, null, { params: { keyword, reply } }) }
export function deleteRule(id) { return axios.delete(`${BASE}/rules/${id}`) }