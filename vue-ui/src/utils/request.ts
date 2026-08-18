import axios from 'axios'
import type {
  AxiosInstance,
  AxiosResponse,
  InternalAxiosRequestConfig,
} from 'axios'
const baseURL = import.meta.env.VITE_API_BASE_URL
// 创建axios实例
const request: AxiosInstance = axios.create({
  baseURL,
  timeout: 60000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// 请求拦截器
request.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    // 可以在这里添加token等认证信息
    // console.log('Request:', config.url)
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
    // console.log('Response:', response.data)
    return response
  },
  (error) => {
    console.error('Response Error:', error)
    return Promise.reject(error)
  },
)

// 封装GET请求
export const get = async <T = unknown>(
  url: string,
  params?: Record<string, unknown>,
): Promise<T> => {
  const response = await request.get<T>(url, { params })
  return response.data
}

// 封装POST请求
export const post = async <T = unknown>(url: string, data?: unknown): Promise<T> => {
  const response = await request.post<T>(url, data)
  return response.data
}

// 封装PUT请求
export const put = async <T = unknown>(url: string, data?: unknown): Promise<T> => {
  const response = await request.put<T>(url, data)
  return response.data
}

// 封装DELETE请求
export const del = async <T = unknown>(url: string): Promise<T> => {
  const response = await request.delete<T>(url)
  return response.data
}

export default request
