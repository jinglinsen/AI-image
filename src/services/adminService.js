/**
 * 管理员服务模块
 */
import config from '../config'
import authService from './authService'

class AdminService {
  /**
   * 获取用户列表
   */
  async getUsers(page = 1, perPage = 20) {
    try {
      const response = await fetch(
        `${config.api.baseURL}/admin/users?page=${page}&per_page=${perPage}`,
        {
          headers: authService.getAuthHeader()
        }
      )
      const data = await response.json()
      
      if (!response.ok) {
        throw new Error(data.error || '获取用户列表失败')
      }
      
      return { success: true, data }
    } catch (error) {
      return { success: false, error: error.message }
    }
  }

  /**
   * 获取用户统计信息
   */
  async getUserStats(userId) {
    try {
      const response = await fetch(
        `${config.api.baseURL}/admin/users/${userId}/stats`,
        {
          headers: authService.getAuthHeader()
        }
      )
      const data = await response.json()
      
      if (!response.ok) {
        throw new Error(data.error || '获取用户统计失败')
      }
      
      return { success: true, data }
    } catch (error) {
      return { success: false, error: error.message }
    }
  }

  /**
   * 删除用户
   */
  async deleteUser(userId) {
    try {
      const response = await fetch(
        `${config.api.baseURL}/admin/users/${userId}`,
        {
          method: 'DELETE',
          headers: authService.getAuthHeader()
        }
      )
      const data = await response.json()
      
      if (!response.ok) {
        throw new Error(data.error || '删除用户失败')
      }
      
      return { success: true, message: data.message }
    } catch (error) {
      return { success: false, error: error.message }
    }
  }

  /**
   * 管理员重置用户密码
   */
  async resetUserPassword(userId, newPassword) {
    try {
      const response = await fetch(
        `${config.api.baseURL}/admin/users/${userId}/reset-password`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            ...authService.getAuthHeader()
          },
          body: JSON.stringify({ new_password: newPassword })
        }
      )
      const data = await response.json()
      
      if (!response.ok) {
        throw new Error(data.error || '重置密码失败')
      }
      
      return { success: true, message: data.message }
    } catch (error) {
      return { success: false, error: error.message }
    }
  }

  /**
   * 生成邀请码
   */
  async generateInviteCodes(count = 1) {
    try {
      const response = await fetch(
        `${config.api.baseURL}/admin/invite-codes/generate`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            ...authService.getAuthHeader()
          },
          body: JSON.stringify({ count })
        }
      )
      const data = await response.json()
      
      if (!response.ok) {
        throw new Error(data.error || '生成邀请码失败')
      }
      
      return { success: true, data }
    } catch (error) {
      return { success: false, error: error.message }
    }
  }

  /**
   * 获取邀请码列表
   */
  async getInviteCodes(page = 1, perPage = 50) {
    try {
      const response = await fetch(
        `${config.api.baseURL}/admin/invite-codes?page=${page}&per_page=${perPage}`,
        {
          headers: authService.getAuthHeader()
        }
      )
      const data = await response.json()
      
      if (!response.ok) {
        throw new Error(data.error || '获取邀请码列表失败')
      }
      
      return { success: true, data }
    } catch (error) {
      return { success: false, error: error.message }
    }
  }

  /**
   * 获取邀请码统计
   */
  async getInviteCodeStats() {
    try {
      const response = await fetch(
        `${config.api.baseURL}/admin/invite-codes/stats`,
        {
          headers: authService.getAuthHeader()
        }
      )
      const data = await response.json()
      
      if (!response.ok) {
        throw new Error(data.error || '获取统计信息失败')
      }
      
      return { success: true, data }
    } catch (error) {
      return { success: false, error: error.message }
    }
  }

  // ============ 金币系统 ============

  /**
   * 获取金币系统设置
   */
  async getCoinSettings() {
    try {
      const response = await fetch(
        `${config.api.baseURL}/admin/coin-settings`,
        {
          headers: authService.getAuthHeader()
        }
      )
      const data = await response.json()
      
      if (!response.ok) {
        throw new Error(data.error || '获取金币设置失败')
      }
      
      return { success: true, data }
    } catch (error) {
      return { success: false, error: error.message }
    }
  }

  /**
   * 更新金币系统设置
   */
  async updateCoinSettings(settings) {
    try {
      const response = await fetch(
        `${config.api.baseURL}/admin/coin-settings`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            ...authService.getAuthHeader()
          },
          body: JSON.stringify(settings)
        }
      )
      const data = await response.json()
      
      if (!response.ok) {
        throw new Error(data.error || '更新金币设置失败')
      }
      
      return { success: true, message: data.message }
    } catch (error) {
      return { success: false, error: error.message }
    }
  }

  /**
   * 给用户充值金币
   */
  async rechargeCoins(userId, amount) {
    try {
      const response = await fetch(
        `${config.api.baseURL}/admin/users/${userId}/coins`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            ...authService.getAuthHeader()
          },
          body: JSON.stringify({ amount })
        }
      )
      const data = await response.json()
      
      if (!response.ok) {
        throw new Error(data.error || '充值失败')
      }
      
      return { success: true, message: data.message, user: data.user }
    } catch (error) {
      return { success: false, error: error.message }
    }
  }

  /**
   * 批量充值金币
   */
  async batchRechargeCoins(userIds, amount) {
    try {
      const response = await fetch(
        `${config.api.baseURL}/admin/users/coins/batch`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            ...authService.getAuthHeader()
          },
          body: JSON.stringify({ user_ids: userIds, amount })
        }
      )
      const data = await response.json()
      
      if (!response.ok) {
        throw new Error(data.error || '批量充值失败')
      }
      
      return { success: true, message: data.message, failed_users: data.failed_users }
    } catch (error) {
      return { success: false, error: error.message }
    }
  }
}

export default new AdminService()

