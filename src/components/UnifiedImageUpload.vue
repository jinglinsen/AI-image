<template>
  <div class="unified-image-upload">
    <!-- 上传区域 -->
    <div class="upload-zone" :class="{ 'dragover': dragover }" @dragover.prevent @drop.prevent="handleDrop">
      <el-upload
        ref="upload"
        v-model:file-list="fileList"
        :auto-upload="false"
        :show-file-list="false"
        :on-change="handleFileChange"
        :multiple="multiple"
        accept="image/*"
        drag
        class="upload-dragger"
      >
        <div class="upload-content">
          <el-icon class="upload-icon"><UploadFilled /></el-icon>
          <div class="upload-text">
            <p>拖拽图片到此处，或 <em>点击上传</em></p>
            <p class="upload-methods">
              支持：本地文件 | 
              <el-button type="text" @click.stop="handlePaste" class="method-btn">粘贴图片</el-button> | 
              <el-button type="text" @click.stop="showUrlInput = true" class="method-btn">输入URL</el-button>
            </p>
          </div>
        </div>
      </el-upload>
    </div>
    
    <!-- URL输入对话框 -->
    <el-dialog v-model="showUrlInput" title="添加图片URL" width="500px">
      <el-input
        v-model="urlInput"
        type="textarea"
        :rows="6"
        placeholder="请输入图片URL，每行一个：&#10;https://example.com/image1.jpg&#10;https://example.com/image2.png"
      />
      <template #footer>
        <el-button @click="showUrlInput = false">取消</el-button>
        <el-button type="primary" @click="addImagesFromUrls" :loading="loadingUrls">
          添加图片
        </el-button>
      </template>
    </el-dialog>
    
    <!-- 已上传图片列表 -->
    <div v-if="imageList.length > 0" class="uploaded-images">
      <div class="images-header">
        <span class="images-count">已添加 {{ imageList.length }} 张图片</span>
        <el-button size="small" text @click="clearAll">
          <el-icon><Delete /></el-icon>
          清空
        </el-button>
      </div>
      
      <div class="image-list">
        <div 
          v-for="(image, index) in imageList" 
          :key="index" 
          class="image-item"
        >
          <div class="image-preview">
            <el-image 
              :src="getImageUrl(image)" 
              :alt="image.name"
              :preview-src-list="[getImageUrl(image)]"
              fit="cover"
              class="preview-image"
              :preview-teleported="true"
            />
            <div class="image-overlay">
              <el-button size="small" circle @click="removeImage(index)">
                <el-icon><Close /></el-icon>
              </el-button>
            </div>
          </div>
          
          <div class="image-details">
            <div class="image-info">
              <span class="image-name">{{ image.name }}</span>
              <span v-if="image.size" class="image-size">{{ formatFileSize(image.size) }}</span>
            </div>
            
            <!-- 用途选择（仅在显示用途时） -->
            <el-select
              v-if="showPurpose"
              v-model="image.purpose"
              placeholder="选择用途"
              size="small"
              class="purpose-select"
            >
              <el-option label="构图参考" value="composition" />
              <el-option label="色彩参考" value="color" />
              <el-option label="光影参考" value="lighting" />
              <el-option label="风格参考" value="style" />
              <el-option label="材质参考" value="texture" />
              <el-option label="场景参考" value="scene" />
            </el-select>
            
            <!-- 描述输入 -->
            <el-input
              v-if="showDescription"
              v-model="image.description"
              type="textarea"
              :rows="2"
              :placeholder="descriptionPlaceholder || '添加图片描述...'"
              size="small"
              class="description-input"
            />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import AIGCService from '../services/aigcService.js'
import config from '../config/index.js'

export default {
  name: 'UnifiedImageUpload',
  props: {
    modelValue: {
      type: Array,
      default: () => []
    },
    multiple: {
      type: Boolean,
      default: false
    },
    showDescription: {
      type: Boolean,
      default: true
    },
    showPurpose: {
      type: Boolean,
      default: false
    },
    descriptionPlaceholder: {
      type: String,
      default: ''
    },
    uploadId: {
      type: String,
      default: 'default'
    }
  },
  emits: ['update:modelValue'],
  data() {
    return {
      fileList: [],
      imageList: [],
      dragover: false,
      showUrlInput: false,
      urlInput: '',
      loadingUrls: false
    }
  },
  watch: {
    modelValue: {
      handler(newValue) {
        if (JSON.stringify(newValue) !== JSON.stringify(this.imageList)) {
          // 保留现有图片的文件引用和缓存
          const updatedList = newValue.map(newImage => {
            console.log('newImage-------',newImage)
            const existingImage = this.imageList.find(img => img.id === newImage.id)
            if (existingImage && existingImage._fileRef && existingImage._cachedBlobUrl) {
              // 保留重要的引用
              return {
                ...newImage,
                _fileRef: existingImage._fileRef,
                _cachedBlobUrl: existingImage._cachedBlobUrl,
                raw: existingImage.raw
              }
            }
            return newImage
          })
          this.imageList = updatedList
        }
      },
      immediate: true
    },
    imageList: {
      handler(newValue) {
        if (JSON.stringify(newValue) !== JSON.stringify(this.modelValue)) {
          console.log('----',newValue)
          this.$emit('update:modelValue', [...newValue])
        }
      },
      deep: true
    }
  },
  mounted() {
    // 监听全局粘贴事件
    document.addEventListener('paste', this.handleGlobalPaste)
  },
  beforeUnmount() {
    document.removeEventListener('paste', this.handleGlobalPaste)
    // 清理所有缓存的blob URLs
    this.imageList.forEach(image => {
      if (image._cachedBlobUrl) {
        URL.revokeObjectURL(image._cachedBlobUrl)
      }
    })
  },
  methods: {
    updateModelValue() {
      console.log(`[${this.uploadId}] updateModelValue:`, this.imageList.length, '张图片')
      // 不需要手动emit，watch会自动处理
      // this.$emit('update:modelValue', [...this.imageList])
    },
    async handleFileChange(file, fileList) {
      // 创建稳定的文件引用
      const fileForUpload = new File([file.raw], file.name, { type: file.raw.type })
      
      // 预先创建blob URL
      const previewUrl = URL.createObjectURL(fileForUpload)
      
      const newImage = {
        id: Date.now() + Math.random(),
        name: fileForUpload.name,
        size: fileForUpload.size,
        raw: fileForUpload,
        description: '',
        status: 'uploading',
        _fileRef: fileForUpload,  // 保存额外的文件引用
        _cachedBlobUrl: previewUrl  // 预先创建的blob URL
      }
      
      if (this.showPurpose) {
        newImage.purpose = 'style'
      }
      
      if (this.multiple) {
        this.imageList.push(newImage)
      } else {
        this.imageList = [newImage]
      }
      
      // 清空上传组件的文件列表
      this.$refs.upload.clearFiles()
      
      // 上传到后端
      try {
        console.log('开始上传图片到后端:', file.name)
        const uploadResult = await AIGCService.uploadImage(fileForUpload)
        
        // 更新图片状态
        newImage.status = 'ready'
        newImage.filename = uploadResult.filename
        newImage.storage = uploadResult.storage
        
        // 构建完整的URL
        const fullUrl = uploadResult.url.startsWith('http') ? uploadResult.url : AIGCService.getImageUrl(uploadResult.url)
        newImage.url = fullUrl
        newImage.serverUrl = fullUrl  // 确保serverUrl也是完整URL
        
        console.log('🔍 图片上传URL调试:', {
          originalUrl: uploadResult.url,
          fullUrl: fullUrl,
          storage: uploadResult.storage,
          configBaseURL: config.api.baseURL,
          configImageBaseURL: config.api.imageBaseURL,
          isRelativePath: uploadResult.url.startsWith('/api/'),
          isHttpUrl: uploadResult.url.startsWith('http')
        })
        
        // 清除blob URL，因为现在有了服务器URL
        if (newImage._cachedBlobUrl) {
          URL.revokeObjectURL(newImage._cachedBlobUrl)
          newImage._cachedBlobUrl = null
        }
        
        // 获取所有可能的URL并测试
        const possibleUrls = AIGCService.getImageUrls(uploadResult.url)
        console.log('🔗 所有可能的图片URL:', possibleUrls)
        
        // 异步测试所有URL的可访问性
        this.testImageUrls(possibleUrls, newImage)
        
        console.log('图片上传成功:', uploadResult)
        this.$message.success(`图片 ${file.name} 上传成功`)
        
        // 强制触发响应式更新 - 确保父组件立即获取到OSS URL
        this.$emit('update:modelValue', [...this.imageList])
        
      } catch (error) {
        console.error('图片上传失败:', error)
        newImage.status = 'error'
        this.$message.error(`图片 ${file.name} 上传失败: ${error.message}`)
        
        // 即使失败也要触发更新，通知父组件状态变化
        this.$emit('update:modelValue', [...this.imageList])
      }
    },
    
    async handleDrop(event) {
      this.dragover = false
      const files = Array.from(event.dataTransfer.files).filter(file => 
        file.type.startsWith('image/')
      )
      
      if (files.length === 0) {
        this.$message.warning('请拖拽图片文件')
        return
      }
      
      for (const file of files) {
        // 创建稳定的文件引用
        const fileForUpload = new File([file], file.name, { type: file.type })
        
        // 预先创建blob URL
        const previewUrl = URL.createObjectURL(fileForUpload)
        
        const newImage = {
          id: Date.now() + Math.random(),
          name: fileForUpload.name,
          size: fileForUpload.size,
          raw: fileForUpload,
          description: '',
          status: 'uploading',
          _fileRef: fileForUpload,  // 保存额外的文件引用
          _cachedBlobUrl: previewUrl  // 预先创建的blob URL
        }
        
        if (this.showPurpose) {
          newImage.purpose = 'style'
        }
        
        if (this.multiple) {
          this.imageList.push(newImage)
        } else {
          this.imageList = [newImage]
        }
        
        // 上传到后端
        try {
          console.log('开始上传拖拽图片:', file.name)
          const uploadResult = await AIGCService.uploadImage(fileForUpload)
          
          newImage.status = 'ready'
          newImage.filename = uploadResult.filename
          // 构建完整的URL
          const fullUrl = uploadResult.url.startsWith('http') ? uploadResult.url : AIGCService.getImageUrl(uploadResult.url)
          newImage.url = fullUrl
          newImage.serverUrl = fullUrl  // 确保serverUrl也是完整URL
          
          // 清除blob URL，因为现在有了服务器URL
          if (newImage._cachedBlobUrl) {
            URL.revokeObjectURL(newImage._cachedBlobUrl)
            newImage._cachedBlobUrl = null
          }
          
          console.log('拖拽图片上传成功:', uploadResult)
          
          // 每张图片上传后立即触发更新
          this.$emit('update:modelValue', [...this.imageList])
          
        } catch (error) {
          console.error('拖拽图片上传失败:', error)
          newImage.status = 'error'
          this.$message.error(`图片 ${file.name} 上传失败`)
          
          // 即使失败也要触发更新，通知父组件状态变化
          this.$emit('update:modelValue', [...this.imageList])
        }
      }
      
      this.$message.success(`处理了 ${files.length} 张图片`)
    },
    
    async handlePaste() {
      console.log(`[${this.uploadId}] 手动粘贴按钮点击`)
      
      // 检查Clipboard API是否可用
      if (!navigator.clipboard || !navigator.clipboard.read) {
        console.warn(`[${this.uploadId}] Clipboard API不可用，可能是HTTP环境或浏览器不支持`)
        this.$message({
          message: '当前环境不支持点击粘贴功能，请使用 Ctrl+V 或 Cmd+V 快捷键直接粘贴图片',
          type: 'warning',
          duration: 4000
        })
        return
      }
      
      try {
        const items = await navigator.clipboard.read()
        console.log(`[${this.uploadId}] 剪贴板项目数量:`, items.length)
        
        let foundImage = false
        for (const item of items) {
          console.log(`[${this.uploadId}] 剪贴板项目类型:`, item.types)
          if (item.types.some(type => type.startsWith('image/'))) {
            foundImage = true
            const imageType = item.types.find(type => type.startsWith('image/'))
            const blob = await item.getType(imageType)
            const file = new File([blob], `pasted-image-${Date.now()}.png`, { type: blob.type })
            
            console.log(`[${this.uploadId}] 从剪贴板获取文件:`, file.name, file.size)
            
            // 创建稳定的文件引用
            const fileForUpload = new File([file], file.name, { type: file.type })
            
            // 预先创建blob URL
            const previewUrl = URL.createObjectURL(fileForUpload)
            
            const newImage = {
              id: Date.now() + Math.random(),
              name: fileForUpload.name,
              size: fileForUpload.size,
              raw: fileForUpload,
              description: '',
              status: 'uploading',
              _fileRef: fileForUpload,  // 保存额外的文件引用
              _cachedBlobUrl: previewUrl  // 预先创建的blob URL
            }
            
            if (this.showPurpose) {
              newImage.purpose = 'style'
            }
            
            if (this.multiple) {
              this.imageList.push(newImage)
            } else {
              this.imageList = [newImage]
            }
            try {
              console.log(`[${this.uploadId}] 开始上传手动粘贴的图片:`, newImage.name, fileForUpload)
              const uploadResult = await AIGCService.uploadImage(fileForUpload)
              
              newImage.status = 'ready'
              newImage.filename = uploadResult.filename
              // 构建完整的URL
              const fullUrl = uploadResult.url.startsWith('http') ? uploadResult.url : AIGCService.getImageUrl(uploadResult.url)
              newImage.url = fullUrl
              newImage.serverUrl = fullUrl  // 确保serverUrl也是完整URL
              
              // 清除blob URL，因为现在有了服务器URL
              if (newImage._cachedBlobUrl) {
                URL.revokeObjectURL(newImage._cachedBlobUrl)
                newImage._cachedBlobUrl = null
              }
              
              console.log(`[${this.uploadId}] 手动粘贴图片上传成功:`, uploadResult)
              this.$message.success('图片粘贴并上传成功')
              
              // 强制触发响应式更新 - 确保父组件立即获取到OSS URL
              this.$emit('update:modelValue', [...this.imageList])
              
            } catch (error) {
              console.error(`[${this.uploadId}] 手动粘贴图片上传失败:`, error)
              newImage.status = 'error'
              this.$message.error('图片粘贴上传失败: ' + error.message)
              
              // 即使失败也要触发更新，通知父组件状态变化
              this.$emit('update:modelValue', [...this.imageList])
            }
          }
        }
        
        if (!foundImage) {
          this.$message({
            message: '剪贴板中没有图片，请先复制图片后再点击粘贴',
            type: 'warning',
            duration: 3000
          })
        }
      } catch (error) {
        console.error(`[${this.uploadId}] 从剪贴板读取失败:`, error)
        this.$message({
          message: '读取剪贴板失败，请使用 Ctrl+V 或 Cmd+V 快捷键直接粘贴图片',
          type: 'warning',
          duration: 4000
        })
      }
    },
    
    async handleGlobalPaste(event) {
      // 更宽松的粘贴处理条件
      console.log(`[${this.uploadId}] 全局粘贴事件触发，activeElement:`, document.activeElement?.tagName, document.activeElement?.className)
      
      // 检查是否应该处理这个粘贴事件
      const shouldHandle = 
        this.$el.contains(document.activeElement) || 
        document.activeElement === document.body ||
        document.activeElement?.tagName === 'INPUT' ||
        document.activeElement?.tagName === 'TEXTAREA' ||
        !document.activeElement
      
      if (shouldHandle) {
        console.log(`[${this.uploadId}] UnifiedImageUpload 处理粘贴事件`)
        if (event.clipboardData?.items) {
          for (const item of event.clipboardData.items) {
            if (item.type.startsWith('image/')) {
              event.preventDefault()
              const file = item.getAsFile()
              console.log('获取到粘贴的文件:', file ? file.name : 'null', file ? file.size : 0)
              
              if (file) {
                // 创建稳定的文件引用
                const fileForUpload = new File([file], `pasted-image-${Date.now()}.png`, { type: file.type })
                
                // 预先创建blob URL
                const previewUrl = URL.createObjectURL(fileForUpload)
                
                const newImage = {
                  id: Date.now() + Math.random(),
                  name: fileForUpload.name,
                  size: fileForUpload.size,
                  raw: fileForUpload,  // 使用新创建的文件对象
                  description: '',
                  status: 'uploading',
                  _fileRef: fileForUpload,  // 保存额外的文件引用
                  _cachedBlobUrl: previewUrl  // 预先创建的blob URL
                }
                
                console.log('创建图片对象:', {
                  name: newImage.name,
                  size: newImage.size,
                  hasRaw: !!newImage.raw,
                  rawType: typeof newImage.raw,
                  status: newImage.status
                })
                
                if (this.showPurpose) {
                  newImage.purpose = 'style'
                }
                
                if (this.multiple) {
                  this.imageList.push(newImage)
                } else {
                  this.imageList = [newImage]
                }
                
                // 上传到后端
                try {
                  console.log('开始上传粘贴的图片:', newImage.name, fileForUpload)
                  const uploadResult = await AIGCService.uploadImage(fileForUpload)
                  
                  newImage.status = 'ready'
                  newImage.filename = uploadResult.filename
                  // 构建完整的URL
                  const fullUrl = uploadResult.url.startsWith('http') ? uploadResult.url : AIGCService.getImageUrl(uploadResult.url)
                  newImage.url = fullUrl
                  newImage.serverUrl = fullUrl  // 确保serverUrl也是完整URL
                  
                  // 清除blob URL，因为现在有了服务器URL
                  if (newImage._cachedBlobUrl) {
                    URL.revokeObjectURL(newImage._cachedBlobUrl)
                    newImage._cachedBlobUrl = null
                  }
                  
                  console.log('粘贴图片上传成功:', uploadResult)
                  console.log('更新后的图片对象:', newImage)
                  this.$message.success('图片粘贴并上传成功')
                  
                  // 强制触发响应式更新 - 确保父组件立即获取到OSS URL
                  this.$emit('update:modelValue', [...this.imageList])
                  
                } catch (error) {
                  console.error('粘贴图片上传失败:', error)
                  newImage.status = 'error'
                  this.$message.error('图片粘贴上传失败: ' + error.message)
                  
                  // 即使失败也要触发更新，通知父组件状态变化
                  this.$emit('update:modelValue', [...this.imageList])
                }
              } else {
                console.warn('未能获取到粘贴的文件对象')
              }
            }
          }
        } else {
          console.log('没有粘贴的剪贴板项目')
        }
      } else {
        console.log('UnifiedImageUpload 组件未聚焦，跳过粘贴处理')
      }
    },
    
    async addImagesFromUrls() {
      if (!this.urlInput.trim()) {
        this.$message.warning('请输入图片URL')
        return
      }
      
      this.loadingUrls = true
      const urls = this.urlInput.split('\n').filter(url => url.trim())
      
      try {
        for (const url of urls) {
          const trimmedUrl = url.trim()
          if (trimmedUrl) {
            const newImage = {
              name: trimmedUrl.split('/').pop() || `image-${Date.now()}.jpg`,
              url: trimmedUrl,
              description: '',
              status: 'ready'
            }
            
            if (this.showPurpose) {
              newImage.purpose = 'style'
            }
            
            if (this.multiple) {
              this.imageList.push(newImage)
            } else {
              this.imageList = [newImage]
            }
          }
        }
        
        this.urlInput = ''
        this.showUrlInput = false
        this.$message.success(`成功添加 ${urls.length} 张图片`)
        
        // 强制触发响应式更新
        this.$emit('update:modelValue', [...this.imageList])
      } catch (error) {
        this.$message.error('添加图片失败')
      } finally {
        this.loadingUrls = false
      }
    },
    
    removeImage(index) {
      this.imageList.splice(index, 1)
    },
    
    clearAll() {
      this.$confirm('确定要清空所有图片吗？', '确认操作', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        this.imageList = []
        this.$message.success('已清空所有图片')
      })
    },
    
    getImageUrl(image) {
      console.log(`[${this.uploadId}] getImageUrl调用，图片:`, {
        id: image.id,
        name: image.name,
        hasServerUrl: !!image.serverUrl,
        hasUrl: !!image.url,
        hasCachedBlobUrl: !!image._cachedBlobUrl,
        hasFileRef: !!image._fileRef,
        hasRaw: !!image.raw,
        status: image.status
      })
      
      // 最优先：使用完整的服务器URL（上传成功后）
      if (image.serverUrl && image.serverUrl.startsWith('http')) {
        console.log(`[${this.uploadId}] 使用完整serverUrl:`, image.serverUrl)
        return image.serverUrl
      }
      
      // 次优先：使用完整的URL
      if (image.url && image.url.startsWith('http')) {
        console.log(`[${this.uploadId}] 使用完整URL:`, image.url)
        return image.url
      }
      
      // 如果图片已上传且status为ready，但没有完整URL，尝试构建
      if (image.status === 'ready' && (image.serverUrl || image.url)) {
        const relativeUrl = image.serverUrl || image.url
        if (relativeUrl.startsWith('/api/')) {
          const fullUrl = AIGCService.getImageUrl(relativeUrl)
          console.log(`[${this.uploadId}] 构建完整服务器URL:`, fullUrl)
          return fullUrl
        }
      }
      
      // 对于正在上传或还未上传的图片，使用blob URL作为预览
      if (image.status === 'uploading' || !image.serverUrl) {
        // 检查是否已经有缓存的blob URL
        if (image._cachedBlobUrl) {
          console.log(`[${this.uploadId}] 使用缓存的blob URL:`, image._cachedBlobUrl.substring(0, 50))
          return image._cachedBlobUrl
        }
        
        // 尝试使用额外保存的文件引用
        if (image._fileRef && image._fileRef instanceof File) {
          try {
            const blobUrl = URL.createObjectURL(image._fileRef)
            image._cachedBlobUrl = blobUrl  // 缓存URL
            console.log(`[${this.uploadId}] 从_fileRef创建新的blob URL:`, blobUrl.substring(0, 50))
            return blobUrl
          } catch (error) {
            console.warn(`[${this.uploadId}] 无法从_fileRef创建blob URL:`, error)
          }
        }
        
        // 如果有File对象，创建blob URL
        if (image.raw && image.raw instanceof File) {
          try {
            const blobUrl = URL.createObjectURL(image.raw)
            image._cachedBlobUrl = blobUrl  // 缓存URL
            console.log(`[${this.uploadId}] 从raw创建新的blob URL:`, blobUrl.substring(0, 50))
            return blobUrl
          } catch (error) {
            console.warn(`[${this.uploadId}] 无法创建blob URL:`, error)
          }
        }
      }
      
      // 如果有相对URL，尝试构建完整URL
      if (image.url) {
        const fullUrl = image.url.startsWith('/') ? AIGCService.getImageUrl(image.url) : image.url
        console.log(`[${this.uploadId}] 使用构建的完整URL:`, fullUrl)
        return fullUrl
      }
      
      console.warn(`[${this.uploadId}] 无法获取图片URL，所有方法都失败`)
      return ''
    },
    
    async testImageUrls(urls, imageObject) {
      console.log('🧪 开始测试图片URL可访问性...')
      
      for (const url of urls) {
        try {
          const isAccessible = await AIGCService.testImageUrl(url)
          console.log(`${isAccessible ? '✅' : '❌'} ${url}`)
          
          if (isAccessible) {
            // 找到可访问的URL，更新图片对象
            imageObject.url = url
            imageObject.serverUrl = url
            
            // 清除blob URL，因为现在有了可访问的服务器URL
            if (imageObject._cachedBlobUrl) {
              URL.revokeObjectURL(imageObject._cachedBlobUrl)
              imageObject._cachedBlobUrl = null
            }
            
            console.log('🎉 找到可访问的URL:', url)
            break
          }
        } catch (error) {
          console.warn('URL测试失败:', url, error)
        }
      }
    },
    
    formatFileSize(size) {
      if (size < 1024) return size + ' B'
      if (size < 1024 * 1024) return (size / 1024).toFixed(1) + ' KB'
      return (size / (1024 * 1024)).toFixed(1) + ' MB'
    }
  }
}
</script>

<style scoped>
.unified-image-upload {
  width: 100%;
}

.upload-zone {
  border: 2px dashed var(--dark-border);
  border-radius: 8px;
  transition: border-color 0.3s;
  background: var(--dark-bg-primary);
}

/* 浅色主题上传区域 */
:deep(.light-theme) .upload-zone {
  border-color: var(--light-border);
  background: var(--light-bg-primary);
}

.upload-zone:hover,
.upload-zone.dragover {
  border-color: #409eff;
}

.upload-dragger {
  width: 100%;
}

.upload-content {
  padding: 40px 20px;
  text-align: center;
}

.upload-icon {
  font-size: 48px;
  color: #606266;
  margin-bottom: 16px;
}

.upload-text p {
  color: var(--dark-text-primary);
  margin: 8px 0;
}

:deep(.light-theme) .upload-text p {
  color: var(--light-text-primary);
}

.upload-text em {
  color: var(--primary-color);
  font-style: normal;
}

.upload-methods {
  font-size: 12px;
  color: var(--dark-text-tertiary);
  margin-top: 12px;
}

:deep(.light-theme) .upload-methods {
  color: var(--light-text-tertiary);
}

.method-btn {
  color: var(--primary-color);
  padding: 0;
  font-size: 12px;
}

.method-btn:hover {
  color: var(--primary-hover);
}

.uploaded-images {
  margin-top: 20px;
}

.images-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  padding-bottom: 8px;
  border-bottom: 1px solid var(--dark-border);
}

:deep(.light-theme) .images-header {
  border-bottom-color: var(--light-border);
}

.images-count {
  color: var(--dark-text-primary);
  font-weight: 500;
}

:deep(.light-theme) .images-count {
  color: var(--light-text-primary);
}

.image-list {
  display: grid;
  gap: 12px;
}

.image-item {
  display: flex;
  gap: 12px;
  background: var(--dark-bg-tertiary);
  border-radius: 8px;
  padding: 12px;
  border: 1px solid var(--dark-border);
  transition: all 0.3s;
}

:deep(.light-theme) .image-item {
  background: var(--light-bg-secondary);
  border-color: var(--light-border);
}

.image-item:hover {
  border-color: var(--primary-color);
  transform: translateY(-1px);
}

.image-preview {
  position: relative;
  width: 80px;
  height: 80px;
  border-radius: 4px;
  overflow: hidden;
  flex-shrink: 0;
}

.image-preview img,
.image-preview .preview-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.image-preview .preview-image :deep(.el-image__inner) {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.image-overlay {
  position: absolute;
  top: 4px;
  right: 4px;
  opacity: 0;
  transition: opacity 0.2s;
}

.image-item:hover .image-overlay {
  opacity: 1;
}

.image-details {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.image-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.image-name {
  color: var(--dark-text-primary);
  font-weight: 500;
  font-size: 14px;
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

:deep(.light-theme) .image-name {
  color: var(--light-text-primary);
}

.image-size {
  color: var(--dark-text-tertiary);
  font-size: 12px;
}

:deep(.light-theme) .image-size {
  color: var(--light-text-tertiary);
}

.purpose-select {
  width: 100%;
}

.description-input {
  width: 100%;
}

/* Element Plus 主题适配 */
:deep(.el-upload-dragger) {
  background: transparent;
  border: none;
  width: 100%;
}

:deep(.el-upload-dragger:hover) {
  background: transparent;
}

/* 深色主题输入框 */
:deep(.el-select .el-input__wrapper) {
  background: var(--dark-bg-tertiary);
  border-color: var(--dark-border);
}

:deep(.el-textarea__inner) {
  background: var(--dark-bg-tertiary);
  border-color: var(--dark-border);
  color: var(--dark-text-primary);
}

/* 浅色主题输入框 */
:deep(.light-theme .el-select .el-input__wrapper) {
  background: var(--light-bg-primary);
  border-color: var(--light-border);
}

:deep(.light-theme .el-textarea__inner) {
  background: var(--light-bg-primary);
  border-color: var(--light-border);
  color: var(--light-text-primary);
}
</style>
