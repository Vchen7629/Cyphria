import axios from 'axios'

export const insights_api = axios.create({
    baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/',
    withCredentials: true
})