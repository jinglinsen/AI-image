import api from './api'
import config from '../config'
import authService from './authService'

/**
 * Amazon AIGC助手API服务
 */
export class AIGCService {
  
  /**
   * 健康检查
   */
  static async healthCheck() {
    try {
      const response = await api.get('/health')
      return response.data
    } catch (error) {
      throw new Error('后端服务连接失败')
    }
  }

  /**
   * 流式生成图片
   * @param {Object} params 生成参数
   * @param {Function} onProgress 进度回调
   * @param {Function} onImageComplete 单张图片完成回调
   * @param {Function} onError 错误回调
   * @returns {Promise<Object>} 完成信息
   */
  static async generateImagesStream(params, onProgress, onImageComplete, onError, onTaskStart) {
    try {
      // 获取认证Token
      const authHeaders = authService.getAuthHeader()
      
      const response = await fetch(`${config.api.baseURL}/generate-images-stream`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...authHeaders
        },
        body: JSON.stringify({
          ...params,
          allowTextInImage: !!params.allowTextInImage
        })
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const reader = response.body.getReader()
      const decoder = new TextDecoder()

      while (true) {
        const { value, done } = await reader.read()
        if (done) break

        const chunk = decoder.decode(value)
        const lines = chunk.split('\n')

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6))
              
              switch (data.type) {
                case 'status':
                  console.log('任务开始:', data)
                  // 🆕 调用任务开始回调，传递task_id
                  if (onTaskStart && data.task_id) {
                    onTaskStart(data.task_id)
                  }
                  break
                case 'progress':
                  console.log('生成进度:', data)
                  if (onProgress) onProgress(data)
                  break
                case 'image_complete':
                  console.log('图片完成:', data)
                  if (onImageComplete) onImageComplete(data)
                  break
                case 'image_error':
                  console.log('图片错误:', data)
                  if (onError) onError(data)
                  break
                case 'complete':
                  console.log('任务完成:', data)
                  return data
                case 'error':
                  console.error('任务错误:', data)
                  throw new Error(data.error)
              }
            } catch (e) {
              console.warn('解析SSE数据失败:', e)
            }
          }
        }
      }
    } catch (error) {
      console.error('流式生成失败:', error)
      throw error
    }
  }

  /**
   * 生成图片（传统方式）
   * @param {Object} params 生成参数
   * @returns {Promise<Object>} 任务信息
   */
  static async generateImages(params) {
    try {
      const response = await api.post('/generate-images', {
        productForm: params.productForm,
        selectedImageTypes: params.selectedImageTypes,
        mainPrompt: params.mainPrompt,
        productImages: params.productImages || [],
        referenceImagesByType: params.referenceImagesByType || {},
        competitors: params.competitors || [],
        selectedSize: params.selectedSize,
        selectedRatio: params.selectedRatio,
        selectedModel: params.selectedModel,
        allowTextInImage: !!params.allowTextInImage
      })
      
      return response.data
    } catch (error) {
      const message = error.response?.data?.error || '图片生成请求失败'
      throw new Error(message)
    }
  }

  /**
   * 查询任务状态
   * @param {string} taskId 任务ID
   * @returns {Promise<Object>} 任务状态
   */
  static async getTaskStatus(taskId) {
    try {
      const response = await api.get(`/task-status/${taskId}`)
      return response.data
    } catch (error) {
      const message = error.response?.data?.error || '获取任务状态失败'
      throw new Error(message)
    }
  }

  /**
   * 重新生成图片
   * @param {Object} params 重新生成参数
   * @returns {Promise<Object>} 新任务信息
   */
  static async regenerateImage(params) {
    try {
      const response = await api.post('/regenerate-image', {
        original_image_id: params.originalImageId,
        modifications: {
          prompt_modifications: params.promptModifications
        },
        reference_images: params.referenceImages || []
      })
      
      return response.data
    } catch (error) {
      const message = error.response?.data?.error || '重新生成请求失败'
      throw new Error(message)
    }
  }

  /**
   * 终止生成任务
   * @param {string} taskId 任务ID
   * @returns {Promise<Object>} 终止结果
   */
  static async cancelTask(taskId) {
    try {
      const response = await api.post(`/cancel-task/${taskId}`)
      return response.data
    } catch (error) {
      const message = error.response?.data?.error || '终止任务失败'
      throw new Error(message)
    }
  }

  /**
   * 上传图片
   * @param {File} file 图片文件
   * @returns {Promise<Object>} 上传结果
   */
  static async uploadImage(file) {
    try {
      const formData = new FormData()
      formData.append('image', file)
      
      const response = await api.post('/upload-image', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      })
      
      return response.data
    } catch (error) {
      const message = error.response?.data?.error || '图片上传失败'
      throw new Error(message)
    }
  }

  /**
   * 获取图片URL
   * @param {string} filename 文件名或相对路径
   * @returns {string} 图片URL
   */
  static getImageUrl(filename) {
    console.log('AIGCService.getImageUrl 调用:', {
      filename,
      configBaseURL: config.api.baseURL,
      configImageBaseURL: config.api.imageBaseURL,
      nodeEnv: process.env.NODE_ENV
    })
    
    // 如果是完整的URL，直接返回
    if (filename.startsWith('http://') || filename.startsWith('https://')) {
      console.log('返回完整URL:', filename)
      return filename
    }
    
    // 如果是相对路径且以/api开头，构建完整URL
    if (filename.startsWith('/api/')) {
      // 使用专门的图片基础URL
      const imageBaseURL = config.api.imageBaseURL || config.api.baseURL.replace('/api', '')
      const fullUrl = `${imageBaseURL}${filename}`
      console.log('构建完整URL:', { 
        configBaseURL: config.api.baseURL,
        imageBaseURL, 
        filename, 
        fullUrl 
      })
      return fullUrl
    }
    
    // 默认处理（旧格式兼容）
    const imageBaseURL = config.api.imageBaseURL || config.api.baseURL.replace('/api', '')
    const fullUrl = `${imageBaseURL}/api/image/${filename}`
    console.log('默认URL构建:', { imageBaseURL, filename, fullUrl })
    return fullUrl
  }

  /**
   * 获取多个可能的图片URL
   * @param {string} filename 文件名或相对路径
   * @returns {Array<string>} 可能的URL列表
   */
  static getImageUrls(filename) {
    const urls = []
    const imageBaseURL = config.api.imageBaseURL || config.api.baseURL.replace('/api', '')
    
    if (filename.startsWith('http://') || filename.startsWith('https://')) {
      urls.push(filename)
    } else if (filename.startsWith('/api/')) {
      // 直接使用返回的API路径
      urls.push(`${imageBaseURL}${filename}`)
      // 备选路径：替换为uploads路径
      urls.push(`${imageBaseURL}${filename.replace('/api/', '/uploads/')}`)
    } else {
      // 构建多种可能的路径
      urls.push(`${imageBaseURL}/api/upload/${filename}`)
      urls.push(`${imageBaseURL}/uploads/${filename}`)
      urls.push(`${imageBaseURL}/api/image/${filename}`)
    }
    
    console.log('生成的可能URL列表:', urls)
    return urls
  }

  /**
   * 测试图片URL是否可访问
   * @param {string} url 图片URL
   * @returns {Promise<boolean>} 是否可访问
   */
  static async testImageUrl(url) {
    try {
      const response = await fetch(url, { method: 'HEAD' })
      return response.ok
    } catch (error) {
      return false
    }
  }

  /**
   * 轮询任务状态直到完成
   * @param {string} taskId 任务ID
   * @param {Function} onProgress 进度回调
   * @param {number} interval 轮询间隔（毫秒）
   * @returns {Promise<Object>} 最终任务结果
   */
  static async pollTaskStatus(taskId, onProgress = null, interval = 2000) {
    return new Promise((resolve, reject) => {
      const poll = async () => {
        try {
          const status = await this.getTaskStatus(taskId)
          
          // 调用进度回调
          if (onProgress && typeof onProgress === 'function') {
            onProgress(status)
          }
          
          // 检查任务状态
          if (status.status === 'completed') {
            resolve(status)
          } else if (status.status === 'failed') {
            reject(new Error(status.error_message || '任务执行失败'))
          } else {
            // 继续轮询
            setTimeout(poll, interval)
          }
        } catch (error) {
          reject(error)
        }
      }
      
      // 开始轮询
      poll()
    })
  }

/**
   * 批量下载图片（处理跨域问题）
   * @param {Array} images 图片列表
   */
static async downloadImages(images) {
  for (let i = 0; i < images.length; i++) {
    const image = images[i];
    try {
      const response = await fetch(image.url);
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      
      const link = document.createElement('a');
      link.href = url;
      link.download = `generated-${image.type}-${i + 1}.png`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      
      // 释放通过 createObjectURL 创建的 URL
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error(`图片下载失败: ${image.url}`, error);
      // 如果 fetch 失败，可以尝试回退到原始方法
      // window.open(image.url, `image-${i}`);
    }
  }
}

  /**
   * 记录用户反馈
   * @param {number} imageId 图片ID
   * @param {string} feedbackType 反馈类型
   * @param {Object} feedbackData 反馈数据
   */
  static async recordFeedback(imageId, feedbackType, feedbackData = {}) {
    try {
      // 这个接口需要在后端添加
      const response = await api.post('/record-feedback', {
        image_id: imageId,
        feedback_type: feedbackType,
        feedback_data: feedbackData
      })
      
      return response.data
    } catch (error) {
      console.warn('记录反馈失败:', error.message)
      // 反馈记录失败不应该影响主要功能
    }
  }

  /**
   * 保存生成历史记录
   * @param {Object} historyData 历史记录数据
   * @returns {Promise<Object>} 保存结果
   */
  static async saveGenerationHistory(historyData) {
    console.log('🟢 [1/3] saveGenerationHistory 开始执行')
    console.log('🟢 [2/3] historyData:', historyData)
    
    try {
      // 使用axios，它不受浏览器CORS限制影响
      console.log('🟢 [3/3] 调用axios.post /save-history')
      const response = await api.post('/save-history', historyData)
      console.log('✅ 保存历史记录成功:', response.data)
      return response.data
    } catch (error) {
      console.error('❌ saveGenerationHistory异常:', error)
      const message = error.response?.data?.error || error.message || '保存历史记录失败'
      throw new Error(message)
    }
  }

  /**
   * 获取生成历史记录列表
   * @param {Object} params 查询参数
   * @returns {Promise<Object>} 历史记录列表
   */
  static async getGenerationHistory(params = {}) {
    try {
      const queryParams = new URLSearchParams({
        page: params.page || 1,
        per_page: params.perPage || 20,
        ...(params.sessionId && { session_id: params.sessionId })
      })

      const response = await api.get(`/history?${queryParams}`)
      return response.data
    } catch (error) {
      const message = error.response?.data?.error || '获取历史记录失败'
      throw new Error(message)
    }
  }

  /**
   * 获取历史记录详情
   * @param {number} historyId 历史记录ID
   * @returns {Promise<Object>} 历史记录详情
   */
  static async getHistoryDetail(historyId) {
    try {
      const response = await api.get(`/history/${historyId}`)
      return response.data
    } catch (error) {
      const message = error.response?.data?.error || '获取历史记录详情失败'
      throw new Error(message)
    }
  }

  /**
   * 更新历史记录
   * @param {number} historyId 历史记录ID
   * @param {Object} updateData 更新数据
   * @returns {Promise<Object>} 更新结果
   */
  static async updateHistory(historyId, updateData) {
    try {
      const response = await api.put(`/history/${historyId}`, updateData)
      return response.data
    } catch (error) {
      const message = error.response?.data?.error || '更新历史记录失败'
      throw new Error(message)
    }
  }

  /**
   * 删除历史记录
   * @param {number} historyId 历史记录ID
   * @returns {Promise<Object>} 删除结果
   */
  static async deleteHistory(historyId) {
    try {
      const response = await api.delete(`/history/${historyId}`)
      return response.data
    } catch (error) {
      const message = error.response?.data?.error || '删除历史记录失败'
      throw new Error(message)
    }
  }

  // ============ 金币系统 ============

  /**
   * 获取当前用户金币余额
   * @returns {Promise<Object>} 金币信息
   */
  static async getUserCoins() {
    try {
      const response = await api.get('/user/coins')
      return response.data
    } catch (error) {
      const message = error.response?.data?.error || '获取金币失败'
      throw new Error(message)
    }
  }

  /**
   * 获取金币交易记录
   * @param {number} limit 记录数量
   * @returns {Promise<Object>} 交易记录
   */
  static async getCoinTransactions(limit = 50) {
    try {
      const response = await api.get(`/user/coin-transactions?limit=${limit}`)
      return response.data
    } catch (error) {
      const message = error.response?.data?.error || '获取交易记录失败'
      throw new Error(message)
    }
  }
}

export default AIGCService
