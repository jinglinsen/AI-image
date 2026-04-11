/**
 * 认证服务模块
 * 处理用户登录、注册、Token管理等
 */
import Cookies from 'js-cookie'
import config from '../config'

const TOKEN_KEY = 'aigc_token'
const USER_KEY = 'aigc_user'
const TOKEN_EXPIRATION_DAYS = 15

class AuthService {
  /**
   * 用户注册
   */
  async register(userData) {
    try {
      const response = await fetch(`${config.api.baseURL}/auth/register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(userData)
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.error || '注册失败')
      }

      return { success: true, data }
    } catch (error) {
      return { success: false, error: error.message }
    }
  }

  /**
   * 用户登录
   */
  async login(username, password) {
    try {
      const response = await fetch(`${config.api.baseURL}/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ username, password })
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.error || '登录失败')
      }

      // 保存Token到Cookie（15天有效期）
      this.setToken(data.token)
      
      // 保存用户信息到localStorage
      this.setUser(data.user)

      return { success: true, user: data.user, token: data.token }
    } catch (error) {
      return { success: false, error: error.message }
    }
  }

  /**
   * 用户登出
   */
  logout() {
    this.removeToken()
    this.removeUser()
  }

  /**
   * 修改密码
   */
  async changePassword(oldPassword, newPassword) {
    try {
      const token = this.getToken()
      if (!token) {
        throw new Error('未登录')
      }

      const response = await fetch(`${config.api.baseURL}/auth/change-password`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          oldPassword,
          newPassword
        })
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.error || '修改密码失败')
      }

      return { success: true, message: data.message }
    } catch (error) {
      return { success: false, error: error.message }
    }
  }

  /**
   * 获取当前用户信息
   */
  async getUserInfo() {
    try {
      const token = this.getToken()
      if (!token) {
        throw new Error('未登录')
      }

      const response = await fetch(`${config.api.baseURL}/auth/me`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })

      const data = await response.json()

      if (!response.ok) {
        // Token可能已过期
        if (response.status === 401) {
          this.logout()
        }
        throw new Error(data.error || '获取用户信息失败')
      }

      // 更新本地存储的用户信息
      this.setUser(data.user)

      return { success: true, user: data.user }
    } catch (error) {
      return { success: false, error: error.message }
    }
  }

  /**
   * 检查是否已登录
   */
  isAuthenticated() {
    const token = this.getToken()
    return !!token
  }

  /**
   * 检查是否是管理员
   */
  isAdmin() {
    const user = this.getUser()
    return user && user.is_admin === true
  }

  /**
   * 获取Token
   */
  getToken() {
    return Cookies.get(TOKEN_KEY)
  }

  /**
   * 设置Token
   */
  setToken(token) {
    Cookies.set(TOKEN_KEY, token, { expires: TOKEN_EXPIRATION_DAYS })
  }

  /**
   * 移除Token
   */
  removeToken() {
    Cookies.remove(TOKEN_KEY)
  }

  /**
   * 获取用户信息
   */
  getUser() {
    const userStr = localStorage.getItem(USER_KEY)
    if (!userStr) return null
    try {
      return JSON.parse(userStr)
    } catch {
      return null
    }
  }

  /**
   * 设置用户信息
   */
  setUser(user) {
    localStorage.setItem(USER_KEY, JSON.stringify(user))
  }

  /**
   * 移除用户信息
   */
  removeUser() {
    localStorage.removeItem(USER_KEY)
  }

  /**
   * 获取认证Header
   */
  getAuthHeader() {
    const token = this.getToken()
    if (token) {
      return { 'Authorization': `Bearer ${token}` }
    }
    return {}
  }
}

// 导出单例
export default new AuthService()

