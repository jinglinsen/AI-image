import axios from 'axios'
import config from '../config'
import authService from './authService'

// 创建axios实例
const api = axios.create({
  baseURL: config.api.baseURL,
  timeout: config.api.timeout,
  headers: {
    'Content-Type': 'application/json',
  }
})

// 请求拦截器 - 添加认证Token
api.interceptors.request.use(
  config => {
    console.log('API请求:', config.method?.toUpperCase(), config.url, config.data)
    
    // 添加认证Token
    const token = authService.getToken()
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    
    return config
  },
  error => {
    console.error('请求错误:', error)
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  response => {
    console.log('API响应:', response.config.url, response.status, response.data)
    return response
  },
  error => {
    // 只处理有响应的错误
    if (error.response) {
      console.error('响应错误:', error.response.status, error.response.data)
      
      // 统一错误处理
      const message = error.response.data?.error || error.message || '网络请求失败'
      
      // 可以在这里添加全局错误提示
      if (typeof window !== 'undefined' && window.$message) {
        window.$message.error(message)
      }
    } else if (error.request) {
      // 请求已发出但没有收到响应
      console.error('请求无响应:', error.message)
    } else {
      // 其他错误
      console.error('请求配置错误:', error.message)
    }
    
    return Promise.reject(error)
  }
)

export default api
