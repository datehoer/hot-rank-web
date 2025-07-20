import axios from 'axios'
import type {
  AxiosInstance,
  AxiosRequestConfig,
  AxiosResponse,
  InternalAxiosRequestConfig,
} from 'axios'

// 创建axios实例
const request: AxiosInstance = axios.create({
  baseURL: 'http://127.0.0.1:8000',
  timeout: 60000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// 请求拦截器
request.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    // 可以在这里添加token等认证信息
    console.log('Request:', config.url)
    return config
  },
  (error) => {
    console.error('Request Error:', error)
    return Promise.reject(error)
  },
)

// 响应拦截器
request.interceptors.response.use(
  (response: AxiosResponse) => {
    console.log('Response:', response.data)
    return response.data
  },
  (error) => {
    console.error('Response Error:', error)
    return Promise.reject(error)
  },
)

// 封装GET请求
export const get = <T = any>(url: string, params?: any): Promise<T> => {
  return request.get(url, { params })
}

// 封装POST请求
export const post = <T = any>(url: string, data?: any): Promise<T> => {
  return request.post(url, data)
}

// 封装PUT请求
export const put = <T = any>(url: string, data?: any): Promise<T> => {
  return request.put(url, data)
}

// 封装DELETE请求
export const del = <T = any>(url: string): Promise<T> => {
  return request.delete(url)
}

export default request
