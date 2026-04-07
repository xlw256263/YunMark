import axios from 'axios'

const request = axios.create({
  baseURL: '/api/v1',
  timeout: 10000
})

// 请求拦截器
request.interceptors.request.use(
  config => {
    const token = localStorage.getItem('token')
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
request.interceptors.response.use(
  response => {
    return response.data
  },
  error => {
    console.error('响应错误:', error)
    
    if (error.response) {
      const status = error.response.status
      
      switch (status) {
        case 401:
          // Token 过期或无效
          localStorage.removeItem('token')
          localStorage.removeItem('username')
          localStorage.removeItem('email')
          window.location.href = '/'
          break
        case 403:
          alert('没有权限访问')
          break
        case 404:
          alert('请求的资源不存在')
          break
        case 500:
          alert('服务器错误，请稍后重试')
          break
        default:
          alert(error.response.data?.detail || '请求失败')
      }
    } else if (error.request) {
      alert('网络连接失败，请检查网络')
    } else {
      alert('请求配置错误')
    }
    
    return Promise.reject(error)
  }
)

export default request