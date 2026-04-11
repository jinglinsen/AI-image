<template>
  <div class="aigc-workbench">
    <!-- KIMI风格布局 -->
    <el-container class="kimi-layout">
      <!-- 左侧边栏 -->
      <el-aside 
        :width="leftPanelCollapsed ? '0px' : '450px'" 
        class="kimi-sidebar"
        v-show="!leftPanelCollapsed"
      >
        <!-- 顶部 Logo 和折叠按钮 -->
        <div class="sidebar-header">
          <div class="app-logo">
            <el-icon class="logo-icon"><MagicStick /></el-icon>
            <span class="app-name">AIGC助手</span>
          </div>
          <div class="header-actions">
            <!-- 使用帮助按钮 -->
            <el-button 
              circle
              size="small"
              @click="helpDialogVisible = true"
              class="help-button-header"
              title="使用帮助"
            >
              <el-icon><InfoFilled /></el-icon>
            </el-button>
            
            <el-button 
              type="primary"
              size="small"
              @click="createNewTask"
              class="new-task-btn"
            >
              <el-icon><Plus /></el-icon>
              新任务
            </el-button>
          <el-button 
            text 
              @click="leftPanelCollapsed = true"
            class="collapse-btn"
          >
              <el-icon><Close /></el-icon>
          </el-button>
          </div>
        </div>
        
        <!-- 标签页导航 -->
        <div class="sidebar-tabs">
          <el-tabs v-model="activeTab" class="sidebar-tab-nav">
            <el-tab-pane label="产品配置" name="product">
            </el-tab-pane>
            <el-tab-pane label="历史记录" name="history">
            </el-tab-pane>
          </el-tabs>
        </div>

        <!-- 内容区域 -->
        <div class="sidebar-content">
          <!-- 产品配置面板 -->
          <div v-if="activeTab === 'product'" class="config-panel">
          <!-- 产品定义 -->
          <el-collapse v-model="activeCollapse" accordion>
            <el-collapse-item title="产品定义" name="product">
              <template #title>
                <div class="collapse-title">
                  <el-icon><Box /></el-icon>
                  <span>产品定义</span>
                </div>
              </template>
              
              <div class="form-section">
                <el-form :model="productForm" label-position="top">
                  <el-form-item label="目标亚马逊站点">
                    <el-select 
                      v-model="productForm.targetMarket" 
                      placeholder="选择目标市场"
                      style="width: 100%"
                    >
                      <template #prefix>
                        <el-icon><Location /></el-icon>
                      </template>
                      <el-option value="US">
                        <div class="market-option">
                          <div class="market-name">🇺🇸 美国 (Amazon.com)</div>
                          <div class="market-desc">北美最大市场，注重功能性和家庭场景</div>
                        </div>
                      </el-option>
                      <el-option value="UK">
                        <div class="market-option">
                          <div class="market-name">🇬🇧 英国 (Amazon.co.uk)</div>
                          <div class="market-desc">欧洲重要市场，偏好经典优雅风格</div>
                        </div>
                      </el-option>
                      <el-option value="DE">
                        <div class="market-option">
                          <div class="market-name">🇩🇪 德国 (Amazon.de)</div>
                          <div class="market-desc">注重品质和工艺，简约实用风格</div>
                        </div>
                      </el-option>
                      <el-option value="JP">
                        <div class="market-option">
                          <div class="market-name">🇯🇵 日本 (Amazon.co.jp)</div>
                          <div class="market-desc">精致简约，温馨整洁的日式美学</div>
                        </div>
                      </el-option>
                      <el-option value="IN">
                        <div class="market-option">
                          <div class="market-name">🇮🇳 印度 (Amazon.in)</div>
                          <div class="market-desc">新兴市场，重视性价比和实用性</div>
                        </div>
                      </el-option>
                    </el-select>
                  </el-form-item>
                  
                  <el-form-item label="产品标题">
                    <el-input 
                      v-model="productForm.title"
                      placeholder="例如：4件装 10英寸陶瓷餐盘套装"
                    />
                  </el-form-item>
                  
                  <el-form-item label="核心卖点">
                    <el-input
                      v-model="productForm.sellingPoints"
                      type="textarea"
                      :rows="4"
                      placeholder="请描述产品的核心卖点，例如：&#10;• 微波炉适用，耐高温安全&#10;• 易于清洗，防刮擦表面&#10;• 环保材质，食品级安全&#10;• 现代简约设计，适配多种装修风格"
                      style="width: 100%"
                    />
                  </el-form-item>
                  
                  <el-form-item label="产品尺寸">
                    <el-row :gutter="8">
                      <el-col :span="5">
                        <el-input 
                          v-model="productForm.dimensions.length"
                          placeholder="长"
                          type="number"
                        />
                      </el-col>
                      <el-col :span="5">
                        <el-input 
                          v-model="productForm.dimensions.width"
                          placeholder="宽"
                          type="number"
                        />
                      </el-col>
                      <el-col :span="5">
                        <el-input 
                          v-model="productForm.dimensions.height"
                          placeholder="高"
                          type="number"
                        />
                      </el-col>
                      <el-col :span="9">
                        <el-select v-model="productForm.dimensions.unit" style="width: 100%">
                          <el-option label="厘米 (cm)" value="cm" />
                          <el-option label="英寸 (inch)" value="inch" />
                          <el-option label="毫米 (mm)" value="mm" />
                        </el-select>
                      </el-col>
                    </el-row>
                  </el-form-item>
                  
                  <el-form-item label="原始产品图片">
                    <UnifiedImageUpload 
                      v-model="productImages"
                      :show-description="true"
                      description-placeholder="为这张图片添加详细说明，帮助AI理解图片内容和用途..."
                      multiple
                      upload-id="product-images"
                      @update:modelValue="onProductImagesUpdate"
                    />
                  </el-form-item>
                </el-form>
              </div>
            </el-collapse-item>
            
            <!-- 竞品分析 -->
            <el-collapse-item title="竞品分析" name="competitor">
              <template #title>
                <div class="collapse-title">
                  <el-icon><TrendCharts /></el-icon>
                  <span>竞品分析</span>
                  <el-tag v-if="competitors.length > 0" size="small" type="success">
                    {{ competitors.length }} 个竞品
                  </el-tag>
                </div>
              </template>
              
              <div class="form-section">
                <el-alert
                  title="竞品信息将帮助AI理解市场趋势和风格偏好"
                  description="添加竞品的标题和关键卖点信息，AI会据此生成更具竞争力的产品图片。注意：为控制输入图片数量，竞品分析不再支持图片上传。"
                  type="info"
                  :closable="false"
                  show-icon
                  style="margin-bottom: 16px;"
                />
                
                <el-button 
                  type="primary" 
                  @click="addCompetitor"
                  class="add-competitor-btn"
                >
                  <el-icon><Plus /></el-icon>
                  添加竞品信息
                </el-button>
                
                <div v-for="(competitor, index) in competitors" :key="index" class="competitor-card">
                  <div class="competitor-header">
                    <span class="competitor-title">竞品 {{ index + 1 }}</span>
                    <el-button 
                      type="danger" 
                      size="small" 
                      text
                      @click="removeCompetitor(index)"
                    >
                      <el-icon><Delete /></el-icon>
                    </el-button>
                  </div>
                  
                  <el-form :model="competitor" label-position="top">
                    <el-form-item label="竞品标题">
                      <el-input v-model="competitor.title" placeholder="输入竞品标题" />
                    </el-form-item>
                    
                    <el-form-item label="竞品卖点">
                      <el-input 
                        v-model="competitor.description"
                        type="textarea"
                        :rows="3"
                        placeholder="输入竞品的关键卖点和特色功能..."
                      />
                    </el-form-item>
                  </el-form>
                </div>
              </div>
            </el-collapse-item>
          </el-collapse>
          </div>

          <!-- 历史记录面板 -->
          <div v-if="activeTab === 'history'" class="history-panel">
            <div class="history-header">
              <h3>历史记录</h3>
              <el-button size="small" text @click="loadHistoryList">
                <el-icon><Refresh /></el-icon>
                刷新
              </el-button>
            </div>
            <div class="history-list" v-loading="historyLoading">
              <div v-if="historyList.length === 0" class="history-empty">
                <el-icon class="empty-icon"><Document /></el-icon>
                <p>暂无历史记录</p>
              </div>
              <div 
                v-for="item in historyList" 
                :key="item.id" 
                class="history-item"
                :class="{ 'is-pinned': item.is_pinned }"
              >
                <div class="history-content" @click="loadHistoryItem(item)">
                  <div class="history-title-row">
                    <el-icon v-if="item.is_pinned" class="pin-icon"><StarFilled /></el-icon>
                    <span class="history-title">{{ item.title || '未命名任务' }}</span>
                  </div>
                  <div class="history-meta">
                    {{ formatHistoryTime(item.created_at) }} · {{ item.generated_image_count || 0 }}张图片
                  </div>
                </div>
                <el-dropdown trigger="click" @click.stop placement="bottom-end">
                  <el-button text class="history-actions" @click.stop>
                    <el-icon><MoreFilled /></el-icon>
                  </el-button>
                  <template #dropdown>
                    <el-dropdown-menu>
                      <el-dropdown-item @click.stop="togglePinHistoryItem(item)">
                        <el-icon v-if="item.is_pinned"><Lock /></el-icon>
                        <el-icon v-else><Star /></el-icon>
                        {{ item.is_pinned ? '取消置顶' : '置顶' }}
                      </el-dropdown-item>
                      <el-dropdown-item @click.stop="renameHistoryItem(item)">
                        <el-icon><Edit /></el-icon>
                        重命名
                      </el-dropdown-item>
                      <el-dropdown-item @click.stop="deleteHistoryItem(item)" divided>
                        <el-icon><Delete /></el-icon>
                        删除
                      </el-dropdown-item>
                    </el-dropdown-menu>
                  </template>
                </el-dropdown>
              </div>
            </div>
          </div>
        </div>

        <!-- 底部用户区域 -->
        <div class="sidebar-footer">
          <div class="user-info">
            <div class="user-avatar">
              <el-icon><User /></el-icon>
            </div>
            <div class="user-details">
              <span class="username">{{ currentUsername }}</span>
              <div class="coin-display">
                <el-icon class="coin-icon"><Coin /></el-icon>
                <span class="coin-amount">{{ userCoins }}</span>
              </div>
            </div>
          </div>
          <el-dropdown trigger="click">
            <el-button text class="more-btn">
              <el-icon><MoreFilled /></el-icon>
            </el-button>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item @click="handleChangePassword">
                  <el-icon><Lock /></el-icon>
                  修改密码
                </el-dropdown-item>
                <el-dropdown-item @click="handleLogout" divided>
                  <el-icon><SwitchButton /></el-icon>
                  退出登录
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-aside>
      
      <!-- 中栏：主创作与预览区 -->
      <el-main class="center-panel" :class="{ 'has-results': hasGeneratedImages, 'with-mini-sidebar': leftPanelCollapsed }">
      <!-- 迷你侧边栏（折叠状态） -->
      <div v-if="leftPanelCollapsed" class="mini-sidebar">
        <div class="mini-sidebar-header">
          <el-button 
            circle 
            @click="leftPanelCollapsed = false"
            class="expand-btn"
            :title="'展开侧边栏'"
          >
            <el-icon class="logo-icon"><MagicStick /></el-icon>
          </el-button>
        </div>
        
        <div class="mini-sidebar-content">
          <el-button 
            type="primary"
            circle
            @click="createNewTask"
            class="mini-new-task-btn"
            :title="'新任务'"
          >
            <el-icon><Plus /></el-icon>
          </el-button>
          
          <el-button 
            circle 
            @click="leftPanelCollapsed = false"
            class="mini-expand-btn"
            :title="'展开菜单'"
          >
            <el-icon><Menu /></el-icon>
          </el-button>
        </div>
      </div>
        
        <!-- 提示词输入区 -->
        <div class="prompt-section" :class="{ 'centered': !hasGeneratedImages }">
          <div class="prompt-input-container">
          <el-input
            v-model="mainPrompt"
            type="textarea"
              :rows="3"
            placeholder="[选填] 描述展示环境和氛围，如：温馨的家居环境，柔和自然光... 留空时AI会自动选择最佳方式 💡点击右侧帮助了解更多"
            class="main-prompt"
          />
            
            <!-- 图片类型选择按钮组 -->
            <div class="image-type-buttons-inside">
              <div 
                v-for="type in imageTypes" 
                :key="type.key"
                class="type-button"
                :class="{ 'selected': selectedImageTypes.includes(type.key) }"
                @click="toggleImageType(type.key)"
                :title="type.description"
              >
                <span class="type-label">{{ type.label }}</span>
                <el-button 
                  v-if="selectedImageTypes.includes(type.key)"
                  size="small"
                  circle
                  class="reference-config-btn"
                  @click.stop="openReferenceConfigForType(type.key)"
                >
                  <el-icon><Setting /></el-icon>
                </el-button>
              </div>
            </div>
            
            <!-- 底部控制栏 -->
            <div class="prompt-footer">
              <!-- 左侧控制组 -->
              <div class="left-controls">
                <!-- 模型选择 -->
                <div class="dropdown-wrapper">
                  <span class="dropdown-label">{{ currentModelLabel }}</span>
                  <el-select 
                    v-model="selectedModel" 
                    class="minimal-select"
                    placeholder=""
                  >
                    <el-option value="dall-e-3" label="🎨 DALL-E 3" />
                    <el-option value="qwen-plus" label="☁️ Qwen Plus" />
                    <el-option value="qwen-vl-plus" label="👁️ Qwen VL Plus" />
                    <el-option value="gpt5" label="🤖 GPT-5" />
                  </el-select>
                </div>
                
                <!-- 图片比例 -->
                <div class="dropdown-wrapper">
                  <span class="dropdown-label">{{ currentRatioLabel }}</span>
                  <el-select 
                    v-model="selectedRatio" 
                    class="minimal-select"
                    placeholder=""
                  >
                    <el-option value="1:1" label="⬜ 1:1" />
                    <el-option value="3:4" label="📱 3:4" />
                    <el-option value="4:3" label="🖥️ 4:3" />
                    <el-option value="16:9" label="📺 16:9" />
                  </el-select>
                </div>
                
                <!-- 图片尺寸显示 -->
                <div class="size-display">
                  <span class="size-label">{{ currentSizeLabel }}</span>
                </div>
              </div>
              
              <!-- 右侧控制组 -->
              <div class="right-controls">
                <!-- 是否为图文开关 -->
                <div class="text-graphic-toggle">
                  <span class="toggle-label">是否为图文：</span>
                  <el-switch 
                    v-model="allowTextInImage"
                    :active-value="true"
                    :inactive-value="false"
                    active-color="#13ce66"
                    inactive-color="#ff4949"
                    style="margin-right: 16px;"
                  />
                </div>
                
                <el-button 
                  v-if="!generating && currentTaskId"
                  @click="startNewTask"
                  class="new-task-button"
                  round
                >
                  <el-icon><DocumentAdd /></el-icon>
                  新建任务
                </el-button>
                
                <el-button 
                  v-if="!generating"
                  type="primary" 
                  @click="generateImages"
                  :disabled="selectedImageTypes.length === 0"
                  class="generate-button"
                  round
                >
                  <el-icon><MagicStick /></el-icon>
                  {{ currentTaskId ? '继续生成' : '生成图片' }}
                </el-button>
                
                <el-button 
                  v-else
                  type="danger" 
                  @click="cancelGeneration"
                  :loading="cancelling"
                  class="cancel-button"
                  round
                >
                  <el-icon><Close /></el-icon>
                  {{ cancelling ? '终止中...' : '终止生成' }}
                </el-button>
              </div>
            </div>
          </div>
        </div>
        
        <!-- 参考图片配置区域 -->
        <div v-if="showReferenceUpload" class="reference-upload-section">
          <div class="reference-header">
            <span class="reference-title">添加参考图片</span>
            <el-button size="small" text @click="showReferenceUpload = false">
              <el-icon><Close /></el-icon>
            </el-button>
          </div>
          
          <div class="simple-reference-config">
            <div class="config-controls">
              <div class="control-group">
                <label class="control-label">图片类型</label>
                <el-select 
                  v-model="currentReferenceType" 
                  placeholder="选择要配置参考图的图片类型"
                  style="width: 200px;"
                  size="default"
                >
                  <el-option
                    v-for="imageType in selectedImageTypes"
                    :key="imageType"
                    :value="imageType"
                    :label="getImageTypeLabel(imageType)"
                  >
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                      <span>{{ getImageTypeLabel(imageType) }}</span>
                      <el-tag 
                        :type="referenceImagesByType[imageType]?.length > 0 ? 'success' : 'info'"
                        size="small"
                      >
                        {{ referenceImagesByType[imageType]?.length || 0 }}张
                      </el-tag>
                    </div>
                  </el-option>
                </el-select>
              </div>
              
              <div class="control-group" v-if="currentReferenceType">
                <el-button 
                  size="default"
                  type="danger"
                  text
                  @click="clearReferenceForType(currentReferenceType)"
                  v-if="referenceImagesByType[currentReferenceType]?.length > 0"
                >
                  <el-icon><Delete /></el-icon>
                  清空
                </el-button>
              </div>
            </div>
            
            <!-- 配置提示 -->
            <div class="config-tip" v-if="currentReferenceType">
              <el-icon><InfoFilled /></el-icon>
              <span>为 <strong>{{ getImageTypeLabel(currentReferenceType) }}</strong> 添加参考图片，帮助AI理解您期望的视觉风格</span>
            </div>
            
            <!-- 图片上传区域 -->
            <div class="upload-area" v-if="currentReferenceType">
              <UnifiedImageUpload 
                :model-value="referenceImagesByType[currentReferenceType] || []"
                @update:model-value="updateReferenceImagesForType(currentReferenceType, $event)"
                :show-description="true"
                :description-placeholder="`说明这张参考图的用途，如：构图参考、色彩风格、光影效果等...`"
                :show-purpose="true"
                multiple
              />
            </div>
            
            <!-- 未选择类型的提示 -->
            <div class="no-selection-tip" v-else>
              <el-icon><Picture /></el-icon>
              <span>请先从上方下拉框选择要配置参考图的图片类型</span>
            </div>
          </div>
        </div>
        
        <!-- 生成结果展示区 -->
        <div v-if="hasGeneratedImages || generating" class="generation-results">
          <div v-if="allGeneratedImages.length > 0" class="images-header">
            <h3 class="results-title">生成结果</h3>
            <div class="results-actions">
              <el-button 
                size="small" 
                type="primary"
                @click="toggleSelectAll"
              >
                <el-icon><Select /></el-icon>
                {{ isAllSelected ? '取消全选' : '全选' }}
              </el-button>
              <el-button 
                size="small" 
                type="success"
                @click="batchDownloadImages"
                :disabled="selectedImages.length === 0"
              >
                <el-icon><Download /></el-icon>
                下载选中 ({{ selectedImages.length }})
              </el-button>
              <el-button size="small" @click="downloadAllImages">
                <el-icon><Download /></el-icon>
                下载全部
              </el-button>
              <el-button size="small" @click="clearAllResults">
                <el-icon><Delete /></el-icon>
                清空结果
              </el-button>
            </div>
          </div>
          
          <div v-if="allGeneratedImages.length > 0" class="image-grid">
            <div 
              v-for="(image, index) in allGeneratedImages" 
              :key="index"
              class="generated-image-card"
              @mouseenter="hoveredImageIndex = index"
              @mouseleave="hoveredImageIndex = null"
            >
              <div class="image-container" :class="{ 'selected': isImageSelected(image) }">
                <!-- 生成中状态 -->
                <div v-if="image.status === 'generating'" class="generating-placeholder">
                  <div class="generating-content">
                    <el-icon class="rotating generating-icon"><Loading /></el-icon>
                    <div class="generating-text">正在生成中...</div>
                    <el-progress 
                      :percentage="image.progress" 
                      :show-text="false" 
                      stroke-width="4"
                      class="generating-progress"
                    />
                  </div>
                </div>
                
                <!-- 生成错误状态 -->
                <div v-else-if="image.status === 'error'" class="error-placeholder">
                  <div class="error-content">
                    <el-icon class="error-icon"><Warning /></el-icon>
                    <div class="error-text">生成失败</div>
                    <div class="error-message">{{ image.error }}</div>
                    <el-button size="small" type="primary" @click="retryGeneration(image)">
                      重新生成
                    </el-button>
                  </div>
                </div>
                
                <!-- 生成完成状态 -->
                <div v-else>
                  <el-image 
                    :key="image.key || image.id"
                    :src="image.url" 
                    :alt="image.type"
                    :preview-src-list="[image.url]"
                    fit="cover"
                    class="generated-image"
                    :preview-teleported="true"
                    crossorigin="anonymous"
                    lazy
                    @error="handleImageError(image, $event)"
                    @load="handleImageLoad(image, $event)"
                  />
                  
                  <!-- 悬浮操作按钮 -->
                  <div 
                    v-if="hoveredImageIndex === index"
                    class="image-actions"
                  >
                    <el-button size="small" circle @click="downloadImage(image)">
                      <el-icon><Download /></el-icon>
                    </el-button>
                    <el-button size="small" circle @click="deleteGeneratedImage(index)">
                      <el-icon><Delete /></el-icon>
                    </el-button>
                    <el-button 
                      size="small" 
                      circle
                      type="primary"
                      @click.stop="openReworkDialog(image)"
                      title="重新生成图片"
                    >
                      <el-icon><Refresh /></el-icon>
                    </el-button>
                  </div>
                </div>
                
                <!-- 图片类型标签 -->
                <div class="image-type-tag">
                  {{ getImageTypeLabel(image.type) }}
                </div>
              </div>
              
              <!-- 图片信息 - 可点击选择 -->
              <div 
                class="image-info"
                :class="{ 'selectable': image.status === 'completed', 'info-selected': isImageSelected(image) }"
                @click="image.status === 'completed' && toggleImageSelection(image)"
              >
                <div class="image-meta">
                  <div class="meta-left">
                    <span class="model-tag">{{ getModelLabel(image.model) }}</span>
                    <span class="size-tag">{{ image.size || actualImageSize }}</span>
                  </div>
                  <div v-if="image.status === 'completed'" class="select-indicator">
                    <el-icon v-if="isImageSelected(image)" class="selected-icon"><CircleCheckFilled /></el-icon>
                    <el-icon v-else class="unselected-icon"><CircleCheck /></el-icon>
                  </div>
                </div>
                <div class="generation-time">{{ image.createTime }}</div>
              </div>
            </div>
          </div>
          
          <!-- 空状态 -->
          <div v-else class="empty-results">
            <div class="empty-icon">
              <el-icon><Picture /></el-icon>
            </div>
            <h3 class="empty-title">还没有生成图片</h3>
            <p class="empty-description">选择图片类型，输入提示词，点击生成按钮开始创作</p>
          </div>
        </div>
      </el-main>
    </el-container>
    
    <!-- 再创作对话框 -->
    <el-dialog v-model="reworkDialogVisible" title="图片再创作" width="700px">
      <div class="rework-content">
        <div class="rework-original">
          <h4 class="section-title">原始图片</h4>
          <div class="original-image-card">
            <el-image 
              :key="reworkImage?.key || reworkImage?.id"
              :src="reworkImage?.url" 
              alt="原始图片"
              :preview-src-list="reworkImage?.url ? [reworkImage.url] : []"
              fit="cover"
              class="original-image"
              :preview-teleported="true"
              crossorigin="anonymous"
              lazy
              @error="handleImageError(reworkImage, $event)"
              @load="handleImageLoad(reworkImage, $event)"
            />
            <div class="original-info">
              <div class="original-type">{{ getImageTypeLabel(reworkImage?.type) }}</div>
              <div class="original-model">{{ getModelLabel(reworkImage?.model) }}</div>
            </div>
          </div>
        </div>
        
        <el-form label-position="top">
          <el-form-item label="修改提示词">
            <el-input
              v-model="reworkPrompt"
              type="textarea"
              :rows="4"
              placeholder="[选填] 修改或完善提示词以获得更好的效果... 留空时AI会使用默认最佳实践"
            />
          </el-form-item>
          
          <el-form-item label="补充参考图片">
            <UnifiedImageUpload 
              :model-value="reworkReferenceImages"
              @update:model-value="updateReworkReferenceImages"
              :show-description="true"
              description-placeholder="说明这张参考图的用途，如：构图参考、色彩风格、光影效果等..."
              :show-purpose="true"
              multiple
            />
          </el-form-item>
        </el-form>
      </div>
      
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="reworkDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="executeRework" :loading="reworking">
            <el-icon><Refresh /></el-icon>
            {{ reworking ? '重新生成中...' : '重新生成' }}
          </el-button>
        </div>
      </template>
    </el-dialog>
    
    <!-- 使用帮助对话框 -->
    <el-dialog 
      v-model="helpDialogVisible" 
      title="📖 Amazon Listing 图片生成 - 使用帮助" 
      width="900px"
      :close-on-click-modal="false"
    >
      <div class="help-dialog-content">
        <!-- 快速入门 -->
        <el-collapse v-model="activeHelpSection" accordion>
          <el-collapse-item name="quick-start">
            <template #title>
              <div class="help-section-title">
                <el-icon><MagicStick /></el-icon>
                <span>快速入门 - 3步开始</span>
              </div>
            </template>
            <div class="help-section-content">
              <div class="help-step">
                <div class="step-number">1</div>
                <div class="step-content">
                  <h4>上传产品原图</h4>
                  <p>在左侧"产品定义"区域上传产品图片（支持拖拽/粘贴）</p>
                  <el-tag type="info" size="small">这是AI复制的标准，产品外观100%来自这里</el-tag>
                </div>
              </div>
              <div class="help-step">
                <div class="step-number">2</div>
                <div class="step-content">
                  <h4>选择图片类型</h4>
                  <p>点击主图、场景图、细节图等类型按钮</p>
                  <el-tag type="success" size="small">可多选，一次生成多种类型</el-tag>
                </div>
              </div>
              <div class="help-step">
                <div class="step-number">3</div>
                <div class="step-content">
                  <h4>点击生成（主提示词可留空）</h4>
                  <p>主提示词选填，留空时AI自动使用最佳实践</p>
                  <el-tag type="warning" size="small">新手建议留空，AI会自动处理</el-tag>
                </div>
              </div>
            </div>
          </el-collapse-item>
          
          <!-- 核心原则 -->
          <el-collapse-item name="core-principle">
            <template #title>
              <div class="help-section-title">
                <el-icon><InfoFilled /></el-icon>
                <span>核心原则 - 产品保真，环境创作</span>
              </div>
            </template>
            <div class="help-section-content">
              <div class="principle-card">
                <div class="principle-formula">
                  <div class="formula-item">
                    <strong>产品外观</strong>
                    <span class="formula-equal">=</span>
                    <span class="formula-value">输入图片（100%还原）</span>
                  </div>
                  <div class="formula-item">
                    <strong>展示方式</strong>
                    <span class="formula-equal">=</span>
                    <span class="formula-value">主提示词（自由创作）</span>
                  </div>
                </div>
                <el-divider />
                <div class="principle-details">
                  <div class="principle-col">
                    <h5>✅ AI自动保持（不会改变）</h5>
                    <ul>
                      <li>产品颜色、材质、纹理</li>
                      <li>Logo、文字、图案</li>
                      <li>形状、尺寸、比例</li>
                      <li>所有细节特征</li>
                    </ul>
                  </div>
                  <div class="principle-col">
                    <h5>🎨 主提示词控制（可以改变）</h5>
                    <ul>
                      <li>背景和环境</li>
                      <li>灯光和氛围</li>
                      <li>构图和角度</li>
                      <li>场景和道具</li>
                    </ul>
                  </div>
                </div>
              </div>
            </div>
          </el-collapse-item>
          
          <!-- 各输入框说明 -->
          <el-collapse-item name="input-fields">
            <template #title>
              <div class="help-section-title">
                <el-icon><Edit /></el-icon>
                <span>各输入框详细说明</span>
              </div>
            </template>
            <div class="help-section-content">
              <div class="field-explanation">
                <div class="field-item">
                  <div class="field-header">
                    <el-tag type="primary">产品名称</el-tag>
                    <el-tag type="danger" size="small">必填</el-tag>
                  </div>
                  <p><strong>作用：</strong>告诉AI这是什么产品</p>
                  <div class="field-example">
                    <strong>示例：</strong>
                    <code>不锈钢保温杯</code>
                    <code>蓝牙无线耳机</code>
                    <code>瑜伽垫</code>
                  </div>
                </div>
                
                <div class="field-item">
                  <div class="field-header">
                    <el-tag type="primary">产品卖点</el-tag>
                    <el-tag type="success" size="small">选填</el-tag>
                  </div>
                  <p><strong>作用：</strong>强调产品优势（通过构图展示，不改变产品）</p>
                  <div class="field-example">
                    <strong>示例：</strong>
                    <code>防水防漏，24小时保温</code>
                    <code>主动降噪，长续航</code>
                  </div>
                </div>
                
                <div class="field-item">
                  <div class="field-header">
                    <el-tag type="primary">主提示词</el-tag>
                    <el-tag type="success" size="small">选填</el-tag>
                  </div>
                  <p><strong>作用：</strong>描述展示环境和视觉风格（只影响背景、灯光、氛围）</p>
                  <p><strong>留空时：</strong>AI自动使用该图片类型的最佳实践</p>
                  <div class="field-example">
                    <strong>✅ 正确示例（描述环境）：</strong>
                    <code>温馨的家居环境，柔和自然光</code>
                    <code>现代办公桌面，专业简洁</code>
                    <code>户外场景，明亮的阳光</code>
                  </div>
                  <div class="field-example warning">
                    <strong>❌ 错误示例（试图改变产品）：</strong>
                    <code>把产品改成蓝色</code>
                    <code>增加一个按钮</code>
                    <code>让产品更大</code>
                    <el-alert type="warning" :closable="false" show-icon>
                      AI不会执行这些指令，产品外观已由输入图片固定
                    </el-alert>
                  </div>
                </div>
                
                <div class="field-item">
                  <div class="field-header">
                    <el-tag type="primary">参考图片</el-tag>
                    <el-tag type="success" size="small">选填</el-tag>
                  </div>
                  <p><strong>作用：</strong>提供风格、构图、灯光的参考</p>
                  <p><strong>注意：</strong>AI学习参考图的展示方式，不会复制里面的产品</p>
                  <el-alert type="info" :closable="false" show-icon>
                    为不同图片类型配置专属参考图，效果更精准
                  </el-alert>
                </div>
              </div>
            </div>
          </el-collapse-item>
          
          <!-- 提示词示例 -->
          <el-collapse-item name="prompt-examples">
            <template #title>
              <div class="help-section-title">
                <el-icon><Document /></el-icon>
                <span>提示词示例大全</span>
              </div>
            </template>
            <div class="help-section-content">
              <!-- 主题式提示词（适用于一次性生成多种图片） -->
              <div class="prompt-section">
                <h3 class="section-title">🎨 主题式提示词（一次性生成多种图片）</h3>
                <el-alert type="info" :closable="false" show-icon style="margin-bottom: 16px;">
                  当您选择同时生成多种图片类型时，使用主题式提示词可以确保整套图片风格统一、视觉连贯
                </el-alert>
                
                <div class="theme-prompts">
                  <div class="theme-item">
                    <div class="theme-header">
                      <h4>🔲 现代极简科技风</h4>
                      <span class="theme-tags">
                        <el-tag size="small" type="primary">电子产品</el-tag>
                        <el-tag size="small" type="primary">智能家居</el-tag>
                        <el-tag size="small" type="primary">办公用品</el-tag>
                      </span>
                    </div>
                    <div class="theme-content" @click="copyPrompt('为整个产品系列设定一个现代、干净、极简的视觉基调。强调产品的科技感和精密设计。使用中性色调（如白、灰、黑）和简洁的背景。光线要均匀、明亮，如同在专业摄影棚中拍摄。确保所有图片风格高度统一，营造出高端、专业的品牌形象。')">
                      <code>为整个产品系列设定一个现代、干净、极简的视觉基调。强调产品的科技感和精密设计。使用中性色调（如白、灰、黑）和简洁的背景。光线要均匀、明亮，如同在专业摄影棚中拍摄。确保所有图片风格高度统一，营造出高端、专业的品牌形象。</code>
                      <el-button text type="primary" size="small">复制</el-button>
                    </div>
                  </div>
                  
                  <div class="theme-item">
                    <div class="theme-header">
                      <h4>🏡 温暖自然居家风</h4>
                      <span class="theme-tags">
                        <el-tag size="small" type="success">家居用品</el-tag>
                        <el-tag size="small" type="success">宠物用品</el-tag>
                        <el-tag size="small" type="success">母婴产品</el-tag>
                      </span>
                    </div>
                    <div class="theme-content" @click="copyPrompt('为所有图片设定一个温暖、自然、充满生活气息的视觉风格。大量使用自然光和温暖的色调（如米白、原木色、浅黄）。场景优先选择舒适的家庭环境，多使用天然材质的道具（如木头、棉麻、绿植）。目标是让顾客感觉到产品的亲切、舒适和有机。')">
                      <code>为所有图片设定一个温暖、自然、充满生活气息的视觉风格。大量使用自然光和温暖的色调（如米白、原木色、浅黄）。场景优先选择舒适的家庭环境，多使用天然材质的道具（如木头、棉麻、绿植）。目标是让顾客感觉到产品的亲切、舒适和有机。</code>
                      <el-button text type="primary" size="small">复制</el-button>
                    </div>
                  </div>
                  
                  <div class="theme-item">
                    <div class="theme-header">
                      <h4>🏃 活力动感户外风</h4>
                      <span class="theme-tags">
                        <el-tag size="small" type="warning">运动装备</el-tag>
                        <el-tag size="small" type="warning">户外用品</el-tag>
                        <el-tag size="small" type="warning">儿童玩具</el-tag>
                      </span>
                    </div>
                    <div class="theme-content" @click="copyPrompt('贯穿所有图片的视觉主题是活力、动感和户外探险。使用高对比度、色彩鲜艳的调色板。光线要像户外阳光一样明亮、强烈。即使是信息图或细节图，也可以在背景中加入微妙的户外元素（如模糊的山脉、水花）。旨在传达产品的坚固、耐用和充满乐趣的特性。')">
                      <code>贯穿所有图片的视觉主题是活力、动感和户外探险。使用高对比度、色彩鲜艳的调色板。光线要像户外阳光一样明亮、强烈。即使是信息图或细节图，也可以在背景中加入微妙的户外元素（如模糊的山脉、水花）。旨在传达产品的坚固、耐用和充满乐趣的特性。</code>
                      <el-button text type="primary" size="small">复制</el-button>
                    </div>
                  </div>
                  
                  <div class="theme-item">
                    <div class="theme-header">
                      <h4>💎 优雅奢华高端风</h4>
                      <span class="theme-tags">
                        <el-tag size="small" type="danger">珠宝首饰</el-tag>
                        <el-tag size="small" type="danger">高端化妆品</el-tag>
                        <el-tag size="small" type="danger">皮具名品</el-tag>
                      </span>
                    </div>
                    <div class="theme-content" @click="copyPrompt('为整个系列定义一种优雅、奢华的视觉语言。主色调采用深色系（如深灰、海军蓝）或经典的黑白色，并用金色或银色作为点缀。光线要有戏剧性，多用侧光和轮廓光来雕刻产品的质感。所有背景和道具都要体现出品味和高级感。')">
                      <code>为整个系列定义一种优雅、奢华的视觉语言。主色调采用深色系（如深灰、海军蓝）或经典的黑白色，并用金色或银色作为点缀。光线要有戏剧性，多用侧光和轮廓光来雕刻产品的质感。所有背景和道具都要体现出品味和高级感。</code>
                      <el-button text type="primary" size="small">复制</el-button>
                    </div>
                  </div>
                  
                  <div class="theme-item">
                    <div class="theme-header">
                      <h4>🎨 有趣多彩创意风</h4>
                      <span class="theme-tags">
                        <el-tag size="small" type="info">儿童玩具</el-tag>
                        <el-tag size="small" type="info">宠物玩具</el-tag>
                        <el-tag size="small" type="info">创意礼品</el-tag>
                      </span>
                    </div>
                    <div class="theme-content" @click="copyPrompt('为所有图片注入一种有趣、好玩、充满想象力的视觉能量。大胆使用明亮、饱和的撞色搭配。背景可以是纯色的彩色背景，或者带有波点、条纹等有趣的几何图案。整体风格要活泼、俏皮，能立刻抓住眼球，让人感到快乐。')">
                      <code>为所有图片注入一种有趣、好玩、充满想象力的视觉能量。大胆使用明亮、饱和的撞色搭配。背景可以是纯色的彩色背景，或者带有波点、条纹等有趣的几何图案。整体风格要活泼、俏皮，能立刻抓住眼球，让人感到快乐。</code>
                      <el-button text type="primary" size="small">复制</el-button>
                    </div>
                  </div>
                  
                  <div class="theme-item">
                    <div class="theme-header">
                      <h4>🔬 纯净科学医疗风</h4>
                      <span class="theme-tags">
                        <el-tag size="small">母婴用品</el-tag>
                        <el-tag size="small">护肤品</el-tag>
                        <el-tag size="small">医疗器械</el-tag>
                      </span>
                    </div>
                    <div class="theme-content" @click="copyPrompt('建立一个极其干净、纯粹、充满科学信任感的视觉体系。主色调为白色、淡蓝色和浅绿色。背景通常是纯白或带有微妙科技感的浅灰色背景。光线要非常明亮、均匀，无阴影。所有元素都要显得一尘不染，突出产品的安全、纯净和经过科学验证的特性。')">
                      <code>建立一个极其干净、纯粹、充满科学信任感的视觉体系。主色调为白色、淡蓝色和浅绿色。背景通常是纯白或带有微妙科技感的浅灰色背景。光线要非常明亮、均匀，无阴影。所有元素都要显得一尘不染，突出产品的安全、纯净和经过科学验证的特性。</code>
                      <el-button text type="primary" size="small">复制</el-button>
                    </div>
                  </div>
                </div>
              </div>

              <el-divider />
              
              <!-- 按图片类型分类的提示词 -->
              <div class="prompt-section">
                <h3 class="section-title">📋 按图片类型分类的提示词</h3>
                <el-alert type="success" :closable="false" show-icon style="margin-bottom: 16px;">
                  只生成单一图片类型时，使用更具体的提示词可以获得更精准的效果
                </el-alert>
              
                <div class="example-category">
                  <h4>📸 主图（Main）- 纯白背景</h4>
                  <div class="example-list">
                    <div class="example-item" @click="copyPrompt('专业产品摄影，纯白背景，柔和工作室灯光')">
                      <code>专业产品摄影，纯白背景，柔和工作室灯光</code>
                      <el-button text size="small">复制</el-button>
                    </div>
                    <div class="example-item" @click="copyPrompt('干净简洁，白色背景，商业摄影，轻微底部阴影')">
                      <code>干净简洁，白色背景，商业摄影，轻微底部阴影</code>
                      <el-button text size="small">复制</el-button>
                    </div>
                    <div class="example-item recommended" @click="copyPrompt('')">
                      <code>留空（推荐）</code>
                      <el-button text type="success" size="small">推荐</el-button>
                    </div>
                  </div>
                </div>
                
                <div class="example-category">
                  <h4>🏠 生活方式图（Lifestyle）</h4>
                  <el-tabs type="border-card">
                    <el-tab-pane label="居家场景">
                      <div class="example-list">
                        <div class="example-item" @click="copyPrompt('在一个明亮、整洁的现代家居环境中展示产品。一个或多个人正在自然地与产品互动，表情轻松愉快。焦点清晰地对准产品，背景略微虚化，营造出温暖、舒适的家庭氛围。')">
                          <code>在一个明亮、整洁的现代家居环境中展示产品。一个或多个人正在自然地与产品互动，表情轻松愉快。焦点清晰地对准产品，背景略微虚化，营造出温暖、舒适的家庭氛围。</code>
                          <el-button text size="small">复制</el-button>
                        </div>
                        <div class="example-item" @click="copyPrompt('温馨的家居环境，木质茶几上，早晨阳光从窗户照进来，背景有绿色植物')">
                          <code>温馨的家居环境，木质茶几上，早晨阳光从窗户照进来，背景有绿色植物</code>
                          <el-button text size="small">复制</el-button>
                        </div>
                      </div>
                    </el-tab-pane>
                    <el-tab-pane label="户外场景">
                      <div class="example-list">
                        <div class="example-item" @click="copyPrompt('在一个阳光明媚的户外场景中（如公园草地、徒步小径或海滩）展示产品。人物充满活力地使用着产品，展现其在运动或休闲活动中的实用性。画面色彩鲜艳，充满动感。')">
                          <code>在一个阳光明媚的户外场景中（如公园草地、徒步小径或海滩）展示产品。人物充满活力地使用着产品，展现其在运动或休闲活动中的实用性。画面色彩鲜艳，充满动感。</code>
                          <el-button text size="small">复制</el-button>
                        </div>
                        <div class="example-item" @click="copyPrompt('户外场景，公园长椅上，明亮的阳光，清新自然')">
                          <code>户外场景，公园长椅上，明亮的阳光，清新自然</code>
                          <el-button text size="small">复制</el-button>
                        </div>
                      </div>
                    </el-tab-pane>
                    <el-tab-pane label="办公场景">
                      <div class="example-list">
                        <div class="example-item" @click="copyPrompt('在一个专业的办公或工作室环境中展示产品。场景可以是整洁的办公桌、明亮的工作室或会议室。突出产品在提升工作效率或创造力方面的作用。光线均匀，风格现代简约。')">
                          <code>在一个专业的办公或工作室环境中展示产品。场景可以是整洁的办公桌、明亮的工作室或会议室。突出产品在提升工作效率或创造力方面的作用。光线均匀，风格现代简约。</code>
                          <el-button text size="small">复制</el-button>
                        </div>
                        <div class="example-item" @click="copyPrompt('现代办公桌面，笔记本电脑旁边，专业商务氛围，自然光')">
                          <code>现代办公桌面，笔记本电脑旁边，专业商务氛围，自然光</code>
                          <el-button text size="small">复制</el-button>
                        </div>
                      </div>
                    </el-tab-pane>
                    <el-tab-pane label="宠物互动">
                      <div class="example-list">
                        <div class="example-item" @click="copyPrompt('在一个阳光明媚、温馨舒适的客厅里，一位面带微笑的主人正在与一只看起来非常享受的宠物（可以是金毛犬或长毛猫）互动使用产品。焦点在人与宠物互动的愉快瞬间。')">
                          <code>在一个阳光明媚、温馨舒适的客厅里，一位面带微笑的主人正在与一只看起来非常享受的宠物（可以是金毛犬或长毛猫）互动使用产品。焦点在人与宠物互动的愉快瞬间。</code>
                          <el-button text size="small">复制</el-button>
                        </div>
                      </div>
                    </el-tab-pane>
                  </el-tabs>
                </div>
                
                <div class="example-category">
                  <h4>🔍 细节图（Detail）- 质量特写</h4>
                  <div class="example-list">
                    <div class="example-item" @click="copyPrompt('对产品的表面材质进行一次极致的微距特写。光线从侧面以低角度照射，以最大程度地突显其纹理、光泽和精湛的工艺细节（如缝线、金属拉丝、木材质感）。')">
                      <code>对产品的表面材质进行一次极致的微距特写。光线从侧面以低角度照射，以最大程度地突显其纹理、光泽和精湛的工艺细节（如缝线、金属拉丝、木材质感）。</code>
                      <el-button text size="small">复制</el-button>
                    </div>
                    <div class="example-item" @click="copyPrompt('微距特写，清晰展示材质纹理，侧光突出质感')">
                      <code>微距特写，清晰展示材质纹理，侧光突出质感</code>
                      <el-button text size="small">复制</el-button>
                    </div>
                    <div class="example-item" @click="copyPrompt('专业摄影棚灯光，锐利焦点，表面细节清晰')">
                      <code>专业摄影棚灯光，锐利焦点，表面细节清晰</code>
                      <el-button text size="small">复制</el-button>
                    </div>
                    <div class="example-item" @click="copyPrompt('浅景深，背景虚化，重点突出关键细节')">
                      <code>浅景深，背景虚化，重点突出关键细节</code>
                      <el-button text size="small">复制</el-button>
                    </div>
                  </div>
                </div>
                
                <div class="example-category">
                  <h4>📊 信息图（Infographic）- 特点展示</h4>
                  <div class="example-list">
                    <div class="example-item" @click="copyPrompt('将产品以最佳角度展示在画面中央。从产品的三个关键部位引出线条，连接到三个简洁的圆形放大镜区域。每个放大镜区域内特写展示一个核心细节。整体布局干净、对称，有科技感。')">
                      <code>将产品以最佳角度展示在画面中央。从产品的三个关键部位引出线条，连接到三个简洁的圆形放大镜区域。每个放大镜区域内特写展示一个核心细节。整体布局干净、对称，有科技感。</code>
                      <el-button text size="small">复制</el-button>
                    </div>
                    <div class="example-item" @click="copyPrompt('采用左图右文（或上图下文）的布局。产品清晰地展示在一侧，另一侧用3-4个统一风格的简约图标，垂直排列，每个图标代表一个核心优势。')">
                      <code>采用左图右文（或上图下文）的布局。产品清晰地展示在一侧，另一侧用3-4个统一风格的简约图标，垂直排列，每个图标代表一个核心优势。</code>
                      <el-button text size="small">复制</el-button>
                    </div>
                    <div class="example-item" @click="copyPrompt('现代简约设计，蓝白配色，图标和图形元素，清晰的视觉层次')">
                      <code>现代简约设计，蓝白配色，图标和图形元素，清晰的视觉层次</code>
                      <el-button text size="small">复制</el-button>
                    </div>
                    <div class="example-item" @click="copyPrompt('专业信息图表风格，特点围绕产品展示，科技感')">
                      <code>专业信息图表风格，特点围绕产品展示，科技感</code>
                      <el-button text size="small">复制</el-button>
                    </div>
                  </div>
                </div>
                
                <div class="example-category">
                  <h4>📏 尺寸图（Size）- 尺寸展示</h4>
                  <div class="example-list">
                    <div class="example-item" @click="copyPrompt('将产品放置在一个中性、干净的背景上。在产品旁边放置一个常见的、尺寸标准的参照物（如一部智能手机、一只手或一个咖啡杯），以直观地展示其真实大小。')">
                      <code>将产品放置在一个中性、干净的背景上。在产品旁边放置一个常见的、尺寸标准的参照物（如一部智能手机、一只手或一个咖啡杯），以直观地展示其真实大小。</code>
                      <el-button text size="small">复制</el-button>
                    </div>
                    <div class="example-item" @click="copyPrompt('白色背景，清晰的尺寸标注线，放置尺子或手作为参照物')">
                      <code>白色背景，清晰的尺寸标注线，放置尺子或手作为参照物</code>
                      <el-button text size="small">复制</el-button>
                    </div>
                    <div class="example-item" @click="copyPrompt('技术图风格，专业测量指示，明确的尺寸对比')">
                      <code>技术图风格，专业测量指示，明确的尺寸对比</code>
                      <el-button text size="small">复制</el-button>
                    </div>
                  </div>
                </div>
                
                <div class="example-category">
                  <h4>📐 多角度图（Angle）</h4>
                  <div class="example-list">
                    <div class="example-item" @click="copyPrompt('在一个统一的浅灰色背景上，以2x2的网格布局展示产品的四个不同视角：正面视图、45度角视图、侧面视图和背面视图。确保所有视图的光照和风格完全一致。')">
                      <code>在一个统一的浅灰色背景上，以2x2的网格布局展示产品的四个不同视角：正面视图、45度角视图、侧面视图和背面视图。确保所有视图的光照和风格完全一致。</code>
                      <el-button text size="small">复制</el-button>
                    </div>
                  </div>
                </div>
              </div>
              
              <el-alert type="success" :closable="false" show-icon style="margin-top: 16px;">
                <template #title>
                  💡 提示：点击任意提示词可一键复制到剪贴板，然后粘贴到主提示词输入框中使用
                </template>
              </el-alert>
            </div>
          </el-collapse-item>
          
          <!-- 常见问题 -->
          <el-collapse-item name="faq">
            <template #title>
              <div class="help-section-title">
                <el-icon><QuestionFilled /></el-icon>
                <span>常见问题 Q&A</span>
              </div>
            </template>
            <div class="help-section-content">
              <div class="faq-list">
                <div class="faq-item">
                  <h5>Q1: 我想改变产品颜色怎么办？</h5>
                  <p><strong>A:</strong> 请重新上传不同颜色的产品图片。主提示词无法改变产品外观，产品外观100%来自输入图片。</p>
                </div>
                
                <div class="faq-item">
                  <h5>Q2: 主提示词可以留空吗？</h5>
                  <p><strong>A:</strong> 可以！留空时AI会使用该图片类型的默认最佳实践。新手推荐留空。</p>
                </div>
                
                <div class="faq-item">
                  <h5>Q3: "是否为图文"开关是什么意思？</h5>
                  <p><strong>A:</strong> 关闭时，AI不会添加任何新文字（但会保留产品原有Logo/包装文字）。适合需要后期添加文字的场景。</p>
                </div>
                
                <div class="faq-item">
                  <h5>Q4: 参考图和主提示词冲突怎么办？</h5>
                  <p><strong>A:</strong> 参考图优先级更高。如果有参考图，主提示词可以简化或留空。</p>
                </div>
                
                <div class="faq-item">
                  <h5>Q5: 为什么生成的产品和我上传的不一样？</h5>
                  <p><strong>A:</strong> 请检查：1）是否上传了清晰的产品图片，2）产品图片是否正确保存（查看控制台日志），3）如果使用OSS，检查网络连接。</p>
                </div>
                
                <div class="faq-item">
                  <h5>Q6: 参考图会丢失吗？</h5>
                  <p><strong>A:</strong> 不会，参考图已自动保存到本地浏览器。刷新页面后会自动恢复。只有创建新任务时才会清空。</p>
                </div>
              </div>
            </div>
          </el-collapse-item>
        </el-collapse>
      </div>
      
      <template #footer>
        <div class="dialog-footer">
          <el-button type="primary" @click="helpDialogVisible = false">我知道了</el-button>
        </div>
      </template>
    </el-dialog>
    
    
    <!-- 参考图片配置弹窗 -->
    <el-dialog 
      v-model="referenceConfigVisible" 
      :title="`为 ${getImageTypeLabel(currentConfigType)} 配置参考图片`"
      width="800px"
      :close-on-click-modal="false"
    >
      <div class="reference-config-dialog" v-if="currentConfigType">
        <div class="config-tip">
          <el-icon><InfoFilled /></el-icon>
          <span>为 <strong>{{ getImageTypeLabel(currentConfigType) }}</strong> 添加参考图片，帮助AI理解您期望的视觉风格</span>
        </div>
        <UnifiedImageUpload 
          :model-value="referenceImagesByType[currentConfigType] || []"
          @update:model-value="updateReferenceImagesForType(currentConfigType, $event)"
          :show-description="true"
          :description-placeholder="`说明这张参考图的用途，如：构图参考、色彩风格、光影效果等...`"
          :show-purpose="true"
          multiple
        />
      </div>
      
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="referenceConfigVisible = false">完成</el-button>
          <el-button 
            type="danger" 
            @click="clearReferenceForType(currentConfigType)"
            v-if="referenceImagesByType[currentConfigType]?.length > 0"
          >
            清空参考图
          </el-button>
        </div>
      </template>
    </el-dialog>
    
    <!-- 系统设置弹窗 -->
    <el-dialog 
      v-model="showSystemSettings" 
      title="系统设置"
      width="600px"
      :close-on-click-modal="false"
    >
      <div class="system-settings">
        <el-form label-position="top">
          <el-form-item label="主题设置">
            <el-radio-group>
              <el-radio label="dark">深色主题</el-radio>
              <el-radio label="light">浅色主题</el-radio>
            </el-radio-group>
          </el-form-item>
          
          <el-form-item label="语言设置">
            <el-select placeholder="选择语言">
              <el-option label="简体中文" value="zh-CN" />
              <el-option label="English" value="en-US" />
            </el-select>
          </el-form-item>
          
          <el-form-item label="API配置">
            <el-input placeholder="OpenAI API Key" type="password" show-password />
          </el-form-item>
        </el-form>
      </div>
      
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="showSystemSettings = false">取消</el-button>
          <el-button type="primary">保存设置</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import UnifiedImageUpload from '../components/UnifiedImageUpload.vue'
import AIGCService from '../services/aigcService.js'
import authService from '../services/authService.js'
import config from '../config'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Setting,
  InfoFilled,
  MagicStick,
  Picture,
  FullScreen,
  Crop,
  Brush,
  Close,
  Delete,
  Download,
  Refresh,
  User,
  MoreFilled,
  Menu,
  Plus,
  Loading,
  Warning,
  Edit,
  Document,
  QuestionFilled,
  Lock,
  SwitchButton,
  StarFilled,
  Star,
  Coin,
  DocumentAdd,
  CircleCheck,
  CircleCheckFilled
} from '@element-plus/icons-vue'

export default {
  name: 'AIGCWorkbench',
  components: {
    UnifiedImageUpload,
    Setting,
    InfoFilled,
    MagicStick,
    Picture,
    FullScreen,
    Crop,
    Brush,
    Close,
    Delete,
    Download,
    Refresh,
    User,
    MoreFilled,
    Menu,
    Plus,
    Loading,
    Warning,
    Edit,
    Document,
    QuestionFilled,
    Lock,
    SwitchButton
  },
  data() {
    return {
      // 面板折叠状态
      leftPanelCollapsed: false,
      rightPanelCollapsed: false,
      
      // 左栏数据
      activeCollapse: 'product',
      productForm: {
        targetMarket: 'US', // 默认美国市场
        title: '',
        sellingPoints: '', // 改为文本域输入
        dimensions: {
          length: '',
          width: '',
          height: '',
          unit: 'cm'
        }
      },
      productImages: [],
      competitors: [],
      
      // 中栏数据
      selectedModel: 'qwen-plus',
      mainPrompt: '',
      showReferenceUpload: false,
      referenceImages: [], // 保留兼容性
      referenceImagesByType: {}, // 按图片类型分组的参考图
      currentReferenceType: null, // 当前选中配置的图片类型
      generating: false,
      generationProgress: 0, // 生成进度
      cancelling: false, // 终止生成状态
      allowTextInImage: false, // 是否允许图片中包含文字
      
      // 任务管理
      currentTask: null,
      taskPollingTimer: null,
      
      // 图片尺寸设置 (根据比例动态计算)
      selectedSize: '1:1',
      selectedRatio: '1:1',
      selectedImageTypes: ['main'], // 默认只选中主图
      
      // 生成的图片列表（统一管理）
      allGeneratedImages: [],
      selectedImages: [], // 🆕 选中的图片ID列表
      hoveredImageIndex: null,
      imageTypes: config.generation.supportedImageTypes,
      
      
      // 右栏数据
      rightActiveTab: 'history',
      taskHistory: [],
      apiKeys: {
        nanoBanana: '',
        seedream: '',
        gpt5: ''
      },
      
      // 对话框数据
      reworkDialogVisible: false,
      reworkImage: null,
      reworkPrompt: '',
      reworkReferenceImages: [],
      reworking: false,
      helpDialogVisible: false, // 帮助对话框
      activeHelpSection: 'quick-start', // 默认展开快速入门
      
      
      // UI 状态
      showTypeTooltip: null,
      referenceConfigVisible: false,
      currentConfigType: null,
      activeTab: 'product', // 左侧栏当前激活的标签页
      showSystemSettings: false, // 系统设置弹窗
      currentUsername: '用户', // 当前用户名
      userCoins: 0, // 用户金币余额
      showChangePasswordDialog: false, // 修改密码对话框
      changePasswordForm: {
        oldPassword: '',
        newPassword: '',
        confirmPassword: ''
      },
      
      // 历史记录
      historyList: [],
      historyLoading: false,
      currentTaskId: null, // 当前任务ID
      currentHistoryId: null // 当前历史记录ID
    }
  },
  computed: {
    currentModelLabel() {
      const modelMap = {
        'qwen-plus': '☁️ Qwen Plus',
        'qwen-vl-plus': '👁️ Qwen VL Plus',
        'gpt5': '🤖 GPT-5'
      }
      return modelMap[this.selectedModel] || '🍌 Nano Banana'
    },
    
    currentRatioLabel() {
      const ratioMap = {
        '1:1': '⬜ 1:1',
        '3:4': '📱 3:4',
        '4:3': '🖥️ 4:3',
        '16:9': '📺 16:9'
      }
      return ratioMap[this.selectedRatio] || '⬜ 1:1'
    },
    
    currentSizeLabel() {
      const sizeMap = {
        '1:1': '📐 1024×1024',
        '3:4': '📐 864×1184',
        '4:3': '📐 1184×864',
        '16:9': '📐 1344×768'
      }
      return sizeMap[this.selectedRatio] || '📐 1024×1024'
    },
    
    actualImageSize() {
      const sizeMap = {
        '1:1': '1024x1024',
        '3:4': '864x1184',
        '4:3': '1184x864',
        '16:9': '1344x768'
      }
      return sizeMap[this.selectedRatio] || '1024x1024'
    },
    
    hasGeneratedImages() {
      return this.allGeneratedImages && this.allGeneratedImages.length > 0
    },
    
    // 🆕 是否全选
    isAllSelected() {
      const completedImages = this.allGeneratedImages.filter(img => img.status === 'completed')
      return completedImages.length > 0 && this.selectedImages.length === completedImages.length
    }
  },
  
  watch: {
    selectedImageTypes: {
      handler() {
        this.onImageTypesChange()
      },
      deep: true
    },
    
    // 监听比例变化，自动更新尺寸选择
    selectedRatio: {
      // handler(newRatio) {
      //   // 当比例变化时，自动更新selectedSize为对应的比例值
      //   this.selectedSize = newRatio
      // }
    },
    
    // 监听尺寸变化，自动更新比例选择
    selectedSize: {
      // handler(newSize) {
      //   // 当尺寸变化时，自动更新selectedRatio为对应的比例值
      //   this.selectedRatio = newSize
      // }
    }
  },
  
  async mounted() {
    this.loadApiKeys()
    this.loadTaskHistory()
    this.loadReferenceImages() // 加载保存的参考图
    this.loadUserInfo() // 加载用户信息和金币
    
    // 粘贴事件由 UnifiedImageUpload 组件统一处理
    // document.addEventListener('paste', this.handlePaste)
    
    // 检查后端服务连接
    try {
      await AIGCService.healthCheck()
      console.log('后端服务连接正常')
    } catch (error) {
      console.error('后端服务连接失败:', error.message)
      this.$message.warning('后端服务未启动，请检查服务状态')
    }
  },
  
  beforeUnmount() {
    // document.removeEventListener('paste', this.handlePaste)
    
    // 清理任务轮询定时器
    if (this.taskPollingTimer) {
      clearTimeout(this.taskPollingTimer)
    }
  },
  mounted() {
    // 加载用户信息
    this.loadUserInfo()
    // 加载历史记录
    this.loadHistoryList()
  },
  methods: {
    // 加载用户信息
    async loadUserInfo() {
      const user = authService.getUser()
      if (user && user.username) {
        this.currentUsername = user.username
      }
      
      // 加载金币余额
      await this.refreshUserCoins()
    },
    
    // 刷新金币余额（单独提取方便复用）
    async refreshUserCoins() {
      try {
        const result = await AIGCService.getUserCoins()
        if (result && result.coins !== undefined) {
          this.userCoins = result.coins
          console.log('💰 金币余额已更新:', this.userCoins)
        }
      } catch (error) {
        console.error('刷新金币余额失败:', error)
      }
    },
    
    // 修改密码
    async handleChangePassword() {
      this.$prompt('请输入新密码（至少6位，包含字母和数字）', '修改密码', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        inputType: 'password',
        inputPattern: /^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{6,}$/,
        inputErrorMessage: '密码至少6位，必须包含字母和数字'
      }).then(async ({ value: newPassword }) => {
        // 再次确认
        this.$prompt('请再次输入新密码', '确认新密码', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          inputType: 'password'
        }).then(async ({ value: confirmPassword }) => {
          if (newPassword !== confirmPassword) {
            ElMessage.error('两次密码输入不一致')
            return
          }
          
          // 获取旧密码
          this.$prompt('请输入当前密码', '验证身份', {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            inputType: 'password'
          }).then(async ({ value: oldPassword }) => {
            const result = await authService.changePassword(oldPassword, newPassword)
            if (result.success) {
              ElMessage.success('密码修改成功，请重新登录')
              setTimeout(() => {
                this.handleLogout()
              }, 1500)
            } else {
              ElMessage.error(result.error || '修改密码失败')
            }
          }).catch(() => {})
        }).catch(() => {})
      }).catch(() => {})
    },
    
    // 退出登录
    async handleLogout() {
      try {
        await ElMessageBox.confirm('确定要退出登录吗？', '提示', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        })
        
        authService.logout()
        ElMessage.success('已退出登录')
        this.$router.push('/login')
      } catch (error) {
        // 用户取消
      }
    },
    
    // ============ 历史记录相关方法 ============
    
    // 加载历史记录列表
    async loadHistoryList() {
      this.historyLoading = true
      try {
        const response = await AIGCService.getGenerationHistory({ 
          page: 1, 
          per_page: 50 
        })
        this.historyList = response.history || []
        console.log('历史记录加载成功:', this.historyList.length, '条')
      } catch (error) {
        console.error('加载历史记录失败:', error)
        this.$message.error('加载历史记录失败')
      } finally {
        this.historyLoading = false
      }
    },
    
    // 保存当前任务到历史记录
    async saveCurrentHistory(result, showMessage = true) {
      // 防止重复保存
      if (this._savingHistory) {
        console.warn('⚠️ 正在保存历史记录，跳过重复请求')
        return
      }
      
      this._savingHistory = true
      
      try {
        // 检查task_id是否存在（应该在生成时由后端创建并返回）
        if (!this.currentTaskId) {
          console.warn('⚠️ 没有task_id，无法保存历史记录')
          return
        }
        
        console.log('准备保存历史记录:', {
          taskId: this.currentTaskId,
          productTitle: this.productForm.title,
          imageTypes: this.selectedImageTypes,
          result: result
        })
        
        // 准备历史记录数据
        console.log('📝 当前表单数据:', {
          productForm: this.productForm,
          productImages: this.productImages,
          selectedImageTypes: this.selectedImageTypes
        })
        
        const historyData = {
          taskId: this.currentTaskId,
          historyId: this.currentHistoryId, // 如果存在，则更新现有记录
          generationParams: {
            productForm: this.productForm,
            selectedImageTypes: this.selectedImageTypes,
            mainPrompt: this.mainPrompt,
            productImages: (this.productImages || []).map(img => ({
              url: img?.url || '',
              filename: img?.filename || ''
            })),
            referenceImagesByType: this.referenceImagesByType || {},
            competitors: this.competitors || [],
            selectedSize: this.selectedSize,
            selectedRatio: this.selectedRatio,
            selectedModel: this.selectedModel
          },
          generatedImageCount: result?.generated_count || this.selectedImageTypes?.length || 0,
          successCount: result?.success_count || this.selectedImageTypes?.length || 0
        }
        
        console.log('📤 发送历史记录数据:', JSON.stringify(historyData, null, 2))
        
        const response = await AIGCService.saveGenerationHistory(historyData)
        
        console.log('保存历史记录响应:', response)
        
        if (response.success) {
          this.currentHistoryId = response.history_id
          console.log('✅ 历史记录保存成功，ID:', this.currentHistoryId)
          
          // 重新加载历史记录列表
          await this.loadHistoryList()
          
          // 显示成功提示
          if (showMessage) {
            this.$message.success('任务已保存到历史记录')
          }
        } else {
          console.error('❌ 历史记录保存失败:', response)
        }
      } catch (error) {
        console.error('❌ 保存历史记录异常:', error)
        console.error('错误详情:', {
          message: error.message,
          response: error.response,
          stack: error.stack
        })
        
        // 尝试获取详细错误信息
        let errorMsg = error.message
        if (error.response) {
          errorMsg = error.response.data?.error || error.response.statusText || error.message
        }
        
        // 显示错误提示，方便调试
        if (showMessage) {
          this.$message.error(`保存历史记录失败: ${errorMsg}`)
        }
      } finally {
        // 释放锁
        this._savingHistory = false
      }
    },
    
    // 点击历史记录项
    async loadHistoryItem(historyItem) {
      try {
        const response = await AIGCService.getHistoryDetail(historyItem.id)
        if (response.success) {
          const history = response.history
          
          // 恢复任务参数
          const params = history.generation_params || {}
          
          if (params.productForm) {
            this.productForm = params.productForm
          }
          if (params.selectedImageTypes) {
            this.selectedImageTypes = params.selectedImageTypes
          }
          if (params.mainPrompt !== undefined) {
            this.mainPrompt = params.mainPrompt
          }
          if (params.selectedSize) {
            this.selectedSize = params.selectedSize
          }
          if (params.selectedRatio) {
            this.selectedRatio = params.selectedRatio
          }
          if (params.selectedModel) {
            this.selectedModel = params.selectedModel
          }
          if (params.productImages) {
            this.productImages = params.productImages
          }
          if (params.referenceImagesByType) {
            this.referenceImagesByType = params.referenceImagesByType
          }
          if (params.competitors) {
            this.competitors = params.competitors
          }
          
          // 设置当前任务ID和历史记录ID
          this.currentTaskId = history.task_id
          this.currentHistoryId = history.id
          
          // 恢复生成的图片
          if (history.generated_images && history.generated_images.length > 0) {
            console.log('📸 恢复历史生成图片:', history.generated_images.length, '张')
            
            // 转换图片格式以匹配前端显示格式
            this.allGeneratedImages = history.generated_images.map(img => {
              // 构建完整的图片URL
              let imageUrl = img.image_url || img.url
              if (!imageUrl || !imageUrl.startsWith('http')) {
                // 如果没有完整URL，使用filename构建
                const filename = img.filename
                imageUrl = AIGCService.getImageUrl(filename)
              }
              // 添加时间戳避免缓存
              imageUrl = imageUrl + (imageUrl.includes('?') ? '&' : '?') + `t=${Date.now()}`
              
              return {
                id: img.id,
                url: imageUrl,
                type: img.image_type,
                status: 'completed',
                progress: 100,
                model: img.model_used || this.selectedModel,
                size: this.selectedSize,
                ratio: this.selectedRatio,
                createTime: new Date(img.created_at).toLocaleString(),
                filename: img.filename,
                key: `img-${img.id}-${Date.now()}`
              }
            })
            
            console.log('✅ 已恢复图片到右侧面板:', this.allGeneratedImages.length, '张')
          } else {
            // 如果没有生成图片，清空图片列表
            this.allGeneratedImages = []
            console.log('⚠️ 该历史记录没有生成图片')
          }
          
          // 切换到产品配置标签
          this.activeTab = 'product'
          
          this.$message.success(`历史记录加载成功${history.generated_images?.length ? `，已恢复 ${history.generated_images.length} 张图片` : ''}`)
        }
      } catch (error) {
        console.error('加载历史记录详情失败:', error)
        this.$message.error('加载历史记录详情失败')
      }
    },
    
    // 重命名历史记录
    async renameHistoryItem(historyItem) {
      try {
        const { value: newTitle } = await ElMessageBox.prompt('请输入新标题', '重命名', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          inputValue: historyItem.title,
          inputValidator: (value) => {
            if (!value || value.trim() === '') {
              return '标题不能为空'
            }
            return true
          }
        })
        
        if (newTitle) {
          await AIGCService.updateHistory(historyItem.id, { title: newTitle.trim() })
          this.$message.success('重命名成功')
          await this.loadHistoryList()
        }
      } catch (error) {
        if (error !== 'cancel') {
          console.error('重命名失败:', error)
          this.$message.error('重命名失败')
        }
      }
    },
    
    // 切换置顶状态
    async togglePinHistoryItem(historyItem) {
      try {
        await AIGCService.updateHistory(historyItem.id, { 
          isPinned: !historyItem.is_pinned 
        })
        this.$message.success(historyItem.is_pinned ? '取消置顶' : '置顶成功')
        await this.loadHistoryList()
      } catch (error) {
        console.error('切换置顶状态失败:', error)
        this.$message.error('操作失败')
      }
    },
    
    // 删除历史记录
    async deleteHistoryItem(historyItem) {
      try {
        await ElMessageBox.confirm('确定要删除这条历史记录吗？', '确认删除', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        })
        
        await AIGCService.deleteHistory(historyItem.id)
        this.$message.success('删除成功')
        await this.loadHistoryList()
      } catch (error) {
        if (error !== 'cancel') {
          console.error('删除失败:', error)
          this.$message.error('删除失败')
        }
      }
    },
    
    // 格式化时间
    formatHistoryTime(timestamp) {
      if (!timestamp) return ''
      
      const date = new Date(timestamp)
      const year = date.getFullYear()
      const month = String(date.getMonth() + 1).padStart(2, '0')
      const day = String(date.getDate()).padStart(2, '0')
      const hours = String(date.getHours()).padStart(2, '0')
      const minutes = String(date.getMinutes()).padStart(2, '0')
      
      // 判断是否是今天
      const now = new Date()
      const isToday = date.toDateString() === now.toDateString()
      
      if (isToday) {
        // 今天只显示时间
        return `今天 ${hours}:${minutes}`
      } else {
        // 其他日期显示完整日期时间
        return `${year}-${month}-${day} ${hours}:${minutes}`
      }
    },
    
    // 图片加载和错误处理方法
    handleImageError(image, event) {
      console.error('图片加载失败:', {
        url: image.url,
        type: image.type,
        filename: image.filename,
        storage: image.storage,
        error: event,
        image: image
      })
      
      // 尝试显示更详细的错误信息
      const errorMsg = `图片加载失败 [${image.type || 'unknown'}]: ${image.url || 'URL为空'}`
      this.$message.error(errorMsg)
      
      // 如果是OSS图片失败，尝试使用本地路径
      if (image.storage === 'oss' && image.filename) {
        console.warn('OSS图片加载失败，尝试使用本地路径:', image.filename)
        const localUrl = `/api/image/${image.filename}`
        if (image.url !== localUrl) {
          console.log('更新图片URL为本地路径:', localUrl)
          image.url = localUrl
          this.$forceUpdate()
        }
      }
    },
    
    handleImageLoad(image, event) {
      console.log('图片加载成功:', {
        url: image.url,
        type: image.type,
        size: event.target.naturalWidth + 'x' + event.target.naturalHeight,
        image: image
      })
    },
    
    // 图片类型相关方法
    toggleImageType(typeKey) {
      const index = this.selectedImageTypes.indexOf(typeKey)
      if (index > -1) {
        this.selectedImageTypes.splice(index, 1)
      } else {
        this.selectedImageTypes.push(typeKey)
      }
    },
    
    getTypeIcon(typeKey) {
      const iconMap = {
        'main': '📸',
        'infographic': '📊', 
        'lifestyle': '🏠',
        'size': '📏',
        'detail': '🔍',
        'angle': '🔄',
        'instruction': '📋',
        'comparison': '⚖️',
        'packaging': '📦'
      }
      return iconMap[typeKey] || '🖼️'
    },
    
    openReferenceConfigForType(typeKey) {
      this.currentConfigType = typeKey
      this.referenceConfigVisible = true
    },
    
    clearReferenceForType(typeKey) {
      this.$confirm('确定要清空此类型的所有参考图片吗？', '确认清空', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        this.referenceImagesByType[typeKey] = []
        this.$message.success('参考图片已清空')
      })
    },
    
    // 产品定义相关
    onProductImagesUpdate(newImages) {
      console.log('产品图片更新事件:', newImages)
      this.productImages = newImages
    },
    
    onReferenceImagesUpdate(newImages) {
      console.log('参考图片更新事件:', newImages)
      this.referenceImages = newImages
    },
    
    updateReferenceImagesForType(imageType, newImages) {
      console.log(`${imageType}类型参考图更新-------------------------:`, newImages)
      // Vue 3 响应式更新
      this.referenceImagesByType[imageType] = newImages
      // 确保响应式更新
      this.$forceUpdate()
      // 保存到localStorage
      this.saveReferenceImages()
    },
    
    // 重新生成弹窗中的参考图片更新
    updateReworkReferenceImages(newImages) {
      console.log('重新生成弹窗参考图片更新:', newImages)
      this.reworkReferenceImages = newImages
      // 确保响应式更新
      this.$forceUpdate()
    },
    
    // 图片类型选择已通过下拉框处理，移除旧的选择方法
    
    clearReferenceForType(imageType) {
      this.$confirm(`确定要清空 ${this.getImageTypeLabel(imageType)} 的所有参考图吗？`, '确认操作', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        this.referenceImagesByType[imageType] = []
        this.$forceUpdate()
        this.saveReferenceImages() // 保存变更
        this.$message.success('已清空参考图')
      }).catch(() => {
        // 用户取消
      })
    },
    
    openReferenceConfig() {
      this.showReferenceUpload = true
      // 如果还没有选择类型，且有可选类型，自动选择第一个
      if (!this.currentReferenceType && this.selectedImageTypes.length > 0) {
        this.currentReferenceType = this.selectedImageTypes[0]
      }
    },
    
    handleImageChange(file, fileList) {
      // 为新上传的图片添加描述字段
      fileList.forEach(item => {
        if (!item.description) {
          item.description = ''
        }
      })
    },
    
    // 手动粘贴功能（备用）
    async pasteFromClipboard() {
      try {
        const items = await navigator.clipboard.read()
        for (const item of items) {
          if (item.types.includes('image/png') || item.types.includes('image/jpeg')) {
            const blob = await item.getType(item.types.find(type => type.startsWith('image/')))
            const file = new File([blob], `pasted-image-${Date.now()}.png`, { type: blob.type })
            
            const newImage = {
              id: Date.now() + Math.random(),
              name: file.name,
              size: file.size,
              raw: file,
              description: '',
              status: 'uploading'
            }
            
            // 先添加到列表
            this.productImages.push(newImage)
            
            // 立即上传
            try {
              const uploadResult = await AIGCService.uploadImage(file)
              newImage.status = 'ready'
              newImage.serverUrl = uploadResult.url
              newImage.filename = uploadResult.filename
              newImage.url = uploadResult.url
              newImage.storage = uploadResult.storage
              this.$message.success('图片粘贴并上传成功')
            } catch (error) {
              newImage.status = 'error'
              this.$message.error('图片粘贴上传失败: ' + error.message)
            }
          }
        }
      } catch (error) {
        this.$message.error('粘贴失败，请确保剪贴板中有图片')
      }
    },
    
    async addImagesFromUrls() {
      if (!this.imageUrlInput.trim()) {
        this.$message.warning('请输入图片URL')
        return
      }
      
      this.loadingUrls = true
      const urls = this.imageUrlInput.split('\n').filter(url => url.trim())
      
      try {
        for (const url of urls) {
          const trimmedUrl = url.trim()
          if (trimmedUrl) {
            // 模拟从URL加载图片
            const mockFileObj = {
              name: trimmedUrl.split('/').pop() || `image-${Date.now()}.jpg`,
              url: trimmedUrl,
              description: '',
              status: 'ready'
            }
            
            this.productImages.push(mockFileObj)
          }
        }
        
        this.imageUrlInput = ''
        this.$message.success(`成功添加 ${urls.length} 张图片`)
      } catch (error) {
        this.$message.error('添加图片失败')
      } finally {
        this.loadingUrls = false
      }
    },
    
    removeImage(index) {
      this.productImages.splice(index, 1)
    },
    
    clearAllImages() {
      this.$confirm('确定要清空所有图片吗？', '确认操作', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        this.productImages = []
        this.$message.success('已清空所有图片')
      })
    },
    
    formatFileSize(size) {
      if (size < 1024) return size + ' B'
      if (size < 1024 * 1024) return (size / 1024).toFixed(1) + ' KB'
      return (size / (1024 * 1024)).toFixed(1) + ' MB'
    },
    
    // 粘贴事件处理
    async handlePaste(event) {
      // 只在特定区域或全局粘贴时处理
      if (event.clipboardData?.items) {
        for (const item of event.clipboardData.items) {
          if (item.type.startsWith('image/')) {
            event.preventDefault()
            const file = item.getAsFile()
            if (file) {
              const newImage = {
                id: Date.now() + Math.random(),
                name: `pasted-image-${Date.now()}.png`,
                size: file.size,
                raw: file,
                description: '',
                status: 'uploading'
              }
              
              // 先添加到列表显示上传状态
              this.productImages.push(newImage)
              
              // 立即上传到后端
              try {
                console.log('开始上传粘贴的图片:', newImage.name)
                const uploadResult = await AIGCService.uploadImage(file)
                
                // 更新图片状态
                newImage.status = 'ready'
                newImage.serverUrl = uploadResult.url
                newImage.filename = uploadResult.filename
                newImage.url = uploadResult.url  // 确保url字段存在
                newImage.storage = uploadResult.storage // local | oss
                
                console.log('粘贴图片上传成功:', uploadResult)
                this.$message.success('图片粘贴并上传成功')
                
              } catch (error) {
                console.error('粘贴图片上传失败:', error)
                newImage.status = 'error'
                this.$message.error('图片粘贴上传失败: ' + error.message)
              }
            }
          }
        }
      }
    },
    
    // 参考图片相关
    handleReferenceChange(file, fileList) {
      fileList.forEach(item => {
        if (!item.description) {
          item.description = ''
        }
        if (!item.purpose) {
          item.purpose = 'style'
        }
      })
    },
    
    removeReferenceImage(index) {
      this.referenceImages.splice(index, 1)
    },
    
    // 图片类型选择
    selectAllImageTypes() {
      this.selectedImageTypes = this.imageTypes.map(type => type.key)
    },
    
    clearAllImageTypes() {
      this.selectedImageTypes = []
      // 清空参考图选择
      this.currentReferenceType = null
    },
    
    // 监听图片类型变化
    onImageTypesChange() {
      // 如果当前选中的参考图类型不在新的选择中，清空选择
      if (this.currentReferenceType && !this.selectedImageTypes.includes(this.currentReferenceType)) {
        this.currentReferenceType = null
      }
      // 如果只有一个类型且还没选择，自动选中
      if (this.selectedImageTypes.length === 1 && !this.currentReferenceType) {
        this.currentReferenceType = this.selectedImageTypes[0]
      }
    },
    
    // 竞品分析相关
    addCompetitor() {
      this.competitors.push({
        title: '',
        description: ''
      })
    },
    
    removeCompetitor(index) {
      this.competitors.splice(index, 1)
    },
    
    // 开始新任务
    startNewTask() {
      this.$confirm('开始新任务将清空当前工作区的内容（不影响已保存的历史记录），是否继续？', '新建任务', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'info'
      }).then(() => {
        // 清空当前任务ID
        this.currentTaskId = null
        this.currentHistoryId = null
        
        // 清空生成的图片
        this.allGeneratedImages = []
        
        // 可选：清空表单（根据需求）
        // this.productForm = { ... }
        // this.mainPrompt = ''
        // this.selectedImageTypes = []
        
        this.$message.success('已开始新任务')
      }).catch(() => {
        // 用户取消
      })
    },
    
    // 流式图片生成
    async generateImages() {
      // 验证输入
      // 主提示词改为选填，留空时AI会使用默认最佳实践
      
      if (!this.selectedImageTypes || this.selectedImageTypes.length === 0) {
        this.$message.warning('请选择至少一种图片类型')
        return
      }
      
      if (!this.productForm.title.trim()) {
        this.$message.warning('请填写产品标题')
        return
      }
      
      // 检查金币余额
      const requiredCoins = this.selectedImageTypes.length
      if (this.userCoins < requiredCoins) {
        ElMessageBox.alert(
          `金币不足！生成 ${requiredCoins} 张图片需要 ${requiredCoins} 金币，当前余额仅有 ${this.userCoins} 金币。请联系管理员充值。`,
          '金币不足',
          {
            confirmButtonText: '知道了',
            type: 'warning'
          }
        )
        return
      }
      
      this.generating = true
      this.generationProgress = 0
      
      // 在生成前先保存/更新历史记录（不显示提示）
      console.log('📝 生成前保存历史记录...')
      await this.saveCurrentHistory(null, false)
      
      // 为每个图片类型创建占位符
      this.selectedImageTypes.forEach(imageType => {
        const placeholderImage = {
          id: `placeholder-${imageType}-${Date.now()}`,
          type: imageType,
          status: 'generating', // 生成中状态
          progress: 0,
          createTime: new Date().toLocaleString(),
          model: this.selectedModel,
          size: this.actualImageSize,
          url: null // 暂时没有URL
        }
        this.allGeneratedImages.unshift(placeholderImage)
      })
      
      try {
        // 准备生成参数
        const params = {
          taskId: this.currentTaskId || null, // 🆕 传递当前task_id（如果有）
          productForm: {
            targetMarket: this.productForm.targetMarket,
            title: this.productForm.title,
            sellingPoints: this.productForm.sellingPoints,
            dimensions: this.productForm.dimensions
          },
          selectedImageTypes: this.selectedImageTypes,
          mainPrompt: this.mainPrompt,
          productImages: this.productImages,
          referenceImagesByType: this.referenceImagesByType,
          competitors: this.competitors,
          selectedSize: this.actualImageSize,
          selectedRatio: this.selectedRatio,
          selectedModel: this.selectedModel,
          allowTextInImage: this.allowTextInImage
        }
        
        // 如果有task_id，说明是在同一任务下继续生成
        if (this.currentTaskId) {
          console.log('🔄 在现有任务下继续生成，task_id:', this.currentTaskId)
        } else {
          console.log('🆕 开始新任务生成')
        }
        
        console.log('开始流式生成图片:', params)
        
        // 在前端控制台输出详细的生成参数
        console.log('\n' + '='.repeat(80))
        console.log('🎯 前端生成参数 (Frontend Generation Parameters)')
        console.log('='.repeat(80))
        console.log('📝 产品信息:', params.productForm)
        console.log('🖼️ 选择的图片类型:', params.selectedImageTypes)
        console.log('✍️ 主要提示词:', params.mainPrompt)
        console.log('📸 产品图片数量:', params.productImages?.length || 0)
        console.log('🔍 参考图片:', params.referenceImagesByType)
        console.log('⚙️ 模型设置:', {
          model: params.selectedModel,
          size: params.selectedSize,
          ratio: params.selectedRatio
        })
        console.log('📝 文字生成设置:', this.allowTextInImage ? '允许文字' : '禁止文字')
        console.log('='.repeat(80))
        
        // 使用流式生成
        const result = await AIGCService.generateImagesStream(
          params,
          // 进度回调
          (progressData) => {
            this.generationProgress = progressData.progress
            console.log(`生成进度: ${progressData.progress}% - 当前类型: ${progressData.current_type}`)
            
            // 更新对应占位符的进度
            const placeholderIndex = this.allGeneratedImages.findIndex(
              img => img.type === progressData.current_type && img.status === 'generating'
            )
            if (placeholderIndex !== -1) {
              this.allGeneratedImages[placeholderIndex].progress = 50 // 表示正在生成
            }
          },
          // 单张图片完成回调
          (imageData) => {
            console.log('图片生成完成:', imageData)
            
            // 找到对应的占位符并替换
            const placeholderIndex = this.allGeneratedImages.findIndex(
              img => img.type === imageData.image.image_type && img.status === 'generating'
            )
            console.log('🔍 占位符索引:', placeholderIndex);
            
            if (placeholderIndex !== -1) {
              // 构建完整的图片对象
              // 构建完整URL，添加时间戳避免缓存
              let finalUrl = imageData.image.url
              if (!finalUrl || !finalUrl.startsWith('http')) {
                // 如果没有完整URL，使用filename构建
                const filename = imageData.image.filename || imageData.image.url?.split('/').pop()
                finalUrl = AIGCService.getImageUrl(filename)
              }
              // 添加时间戳避免缓存问题
              finalUrl = finalUrl + (finalUrl.includes('?') ? '&' : '?') + `t=${Date.now()}`
              
              const completeImage = {
                id: imageData.image.id,
                url: finalUrl,
                type: imageData.image.image_type,
                status: 'completed',
                progress: 100,
                model: imageData.image.model,
                size: this.actualImageSize,
                ratio: this.selectedRatio,
                createTime: new Date(imageData.image.created_at).toLocaleString(),
                filename: imageData.image.filename,
                key: `img-${imageData.image.id}-${Date.now()}` // 添加唯一key强制刷新
              }
              
              console.log('🔍 图片完成回调 - URL调试:', {
                originalUrl: imageData.image.url,
                finalUrl: completeImage.url,
                isOSSUrl: imageData.image.url?.startsWith('https://'),
                imageType: imageData.image.type
              })
              
              // 替换占位符
              this.allGeneratedImages.splice(placeholderIndex, 1, completeImage)
              
              this.$message.success(`${this.getImageTypeLabel(imageData.image.type)} 生成完成！`)
              
              // 每张图片生成完成后立即更新金币余额
              this.refreshUserCoins()
            }
          },
          // 错误回调
          (errorData) => {
            console.error('单张图片生成失败:', errorData)
            
            // 找到对应的占位符并标记为错误
            const placeholderIndex = this.allGeneratedImages.findIndex(
              img => img.type === errorData.image_type && img.status === 'generating'
            )
            
            if (placeholderIndex !== -1) {
              this.allGeneratedImages[placeholderIndex].status = 'error'
              this.allGeneratedImages[placeholderIndex].error = errorData.error
            }
            
            this.$message.error(`${this.getImageTypeLabel(errorData.image_type)} 生成失败`)
          },
          // 🆕 任务开始回调 - 接收后端返回的task_id
          (taskId) => {
            console.log('🆔 接收到后端task_id:', taskId)
            this.currentTaskId = taskId
          }
        )
        
        console.log('流式生成完成:', result)
        this.$message.success(`所有图片生成完成！共生成 ${result?.generated_count || this.selectedImageTypes.length} 张图片`)
        
        // 刷新金币余额（最后再刷新一次确保准确）
        await this.refreshUserCoins()
        
        // 自动保存历史记录（使用nextTick确保DOM更新完成）
        console.log('🔄 开始自动保存历史记录...')
        this.$nextTick(async () => {
          try {
            await this.saveCurrentHistory(result)
            console.log('✅ 历史记录保存流程完成')
          } catch (err) {
            console.error('❌ 历史记录保存流程出错:', err)
          }
        })
        
      } catch (error) {
        console.error('流式生成失败:', error)
        
        // 如果是网络连接错误，提供更好的错误信息
        if (error.message.includes('Failed to fetch') || error.message.includes('fetch')) {
          this.$message.error('无法连接到后端服务，请确保后端服务正在运行 (http://localhost:5000)')
          
          // 可选：为演示目的添加mock数据
          console.log('添加演示数据用于测试界面...')
          this.addMockGeneratedImages()
        } else {
        this.$message.error(`图片生成失败: ${error.message}`)
        }
        
        // 清理所有生成中的占位符
        this.allGeneratedImages = this.allGeneratedImages.filter(img => img.status !== 'generating')
        
      } finally {
        this.generating = false
        this.generationProgress = 0
        this.cancelling = false
      }
    },
    
    // 终止生成
    async cancelGeneration() {
      this.$confirm('确定要终止当前生成任务吗？已生成的图片将保留。', '确认终止', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }).then(async () => {
        this.cancelling = true
        
        try {
          // 如果有当前任务ID，调用API终止
          if (this.currentTask && this.currentTask.task_id) {
            await AIGCService.cancelTask(this.currentTask.task_id)
            this.$message.info('生成任务已终止')
          }
          
          // 清理任务轮询定时器
          if (this.taskPollingTimer) {
            clearTimeout(this.taskPollingTimer)
            this.taskPollingTimer = null
          }
          
          // 移除所有生成中的占位符
          this.allGeneratedImages = this.allGeneratedImages.filter(img => img.status !== 'generating')
          
          // 重置状态
          this.generating = false
          this.generationProgress = 0
          this.currentTask = null
          
        } catch (error) {
          console.error('终止生成失败:', error)
          this.$message.error('终止生成失败，请稍后重试')
        } finally {
          this.cancelling = false
        }
      }).catch(() => {
        // 用户取消
      })
    },
    
    // 重试生成失败的图片
    retryGeneration(image) {
      console.log('重试生成图片:', image)
      // 这里可以实现单独重试某个类型的图片
      this.$message.info('重试功能正在开发中...')
    },
    
    // 开始任务状态轮询
    startTaskPolling(taskId) {
      const pollStatus = async () => {
        try {
          const status = await AIGCService.getTaskStatus(taskId)
          console.log('任务状态更新:', status)
          
          // 更新当前任务信息
          this.currentTask = { ...this.currentTask, ...status }
          
          // 更新生成的图片列表
          if (status.images && status.images.length > 0) {
            // 将后端返回的图片格式转换为前端格式
            const newImages = status.images.map(img => {
              // 后端直接返回完整的URL，不需要再构建
                const imageUrl = img.url?.startsWith('http') ? img.url : AIGCService.getImageUrl(img.filename || img.url?.split('/').pop())
              
              return {
                id: img.id,
                url: imageUrl,
                type: img.type,
                prompt: img.prompt_used,
                model: img.model,
                size: this.actualImageSize,
                ratio: this.selectedRatio,
                createTime: new Date(img.created_at).toLocaleString(),
                filename: img.filename
              }
            })
            
            // 更新图片列表（避免重复）
            const existingIds = this.allGeneratedImages.map(img => img.id)
            const filteredNewImages = newImages.filter(img => !existingIds.includes(img.id))
            
            if (filteredNewImages.length > 0) {
              this.allGeneratedImages.unshift(...filteredNewImages)
            }
          }
          
          // 检查任务是否完成
          if (status.status === 'completed') {
            this.generating = false
            this.$message.success(`图片生成完成！共生成 ${status?.generated_count || status?.images?.length || this.selectedImageTypes.length} 张图片`)
            
            // 记录成功任务到历史
            this.saveCurrentTask()
            
          } else if (status.status === 'failed') {
            this.generating = false
            this.$message.error(`图片生成失败: ${status.error_message || '未知错误'}`)
            
          } else {
            // 继续轮询
            this.taskPollingTimer = setTimeout(pollStatus, config.generation.pollInterval)
          }
          
        } catch (error) {
          console.error('轮询任务状态失败:', error)
          this.generating = false
          this.$message.error('无法获取生成状态，请检查网络连接')
        }
      }
      
      // 开始轮询
      pollStatus()
    },
    
    // 新的辅助方法
    getImageTypeLabel(typeKey) {
      const type = this.imageTypes.find(t => t.key === typeKey)
      return type ? type.label : typeKey
    },
    
    getModelLabel(modelKey) {
      const modelLabels = {
        'qwen-plus': 'Qwen Plus',
        'qwen-vl-plus': 'Qwen VL Plus',
        'seedream-4': 'SeeDream 4.0',
        'flux-kontext': 'Flux Kontext'
      }
      return modelLabels[modelKey] || modelKey
    },
    
    // 帮助对话框 - 复制提示词
    copyPrompt(text) {
      if (text === '留空') {
        this.mainPrompt = ''
        this.$message.success('已清空主提示词（推荐让AI自动处理）')
      } else {
        // 复制到剪贴板
        navigator.clipboard.writeText(text).then(() => {
          this.$message.success('提示词已复制到剪贴板')
          // 同时填充到主提示词输入框
          this.mainPrompt = text
        }).catch(() => {
          // 降级方案
          this.mainPrompt = text
          this.$message.success('提示词已填充到输入框')
        })
      }
      // 不关闭对话框，方便用户继续浏览
    },
    
    // 图片操作方法
    async deleteGeneratedImage(index) {
      this.$confirm('确定要删除这张图片吗？', '确认删除', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(async () => {
        this.allGeneratedImages.splice(index, 1)
        this.$message.success('图片已删除')
        
        // 删除图片后自动更新历史记录
        if (this.currentHistoryId) {
          console.log('🗑️ 删除图片后更新历史记录...')
          await this.saveCurrentHistory(null, false)
        }
      })
    },
    
    downloadAllImages() {
      if (this.allGeneratedImages.length === 0) {
        this.$message.warning('没有可下载的图片')
        return
      }
      
      // 使用API服务的批量下载功能
      AIGCService.downloadImages(this.allGeneratedImages)
      this.$message.success(`已开始下载 ${this.allGeneratedImages.length} 张图片`)
    },
    
    // 🆕 切换图片选择
    toggleImageSelection(image) {
      const imageId = image.id
      const index = this.selectedImages.indexOf(imageId)
      
      if (index > -1) {
        // 已选中，取消选中
        this.selectedImages.splice(index, 1)
      } else {
        // 未选中，添加选中
        this.selectedImages.push(imageId)
      }
    },
    
    // 🆕 判断图片是否被选中
    isImageSelected(image) {
      return this.selectedImages.includes(image.id)
    },
    
    // 🆕 全选/取消全选
    toggleSelectAll() {
      const completedImages = this.allGeneratedImages.filter(img => img.status === 'completed')
      
      if (this.selectedImages.length === completedImages.length) {
        // 当前已全选，取消全选
        this.selectedImages = []
      } else {
        // 全选所有已完成的图片
        this.selectedImages = completedImages.map(img => img.id)
      }
    },
    
    // 🆕 批量下载选中的图片
    async batchDownloadImages() {
      if (this.selectedImages.length === 0) {
        this.$message.warning('请先选择要下载的图片')
        return
      }
      
      // 筛选出选中的图片
      const imagesToDownload = this.allGeneratedImages.filter(img => 
        this.selectedImages.includes(img.id)
      )
      
      // 使用API服务的批量下载功能
      AIGCService.downloadImages(imagesToDownload)
      this.$message.success(`已开始下载 ${imagesToDownload.length} 张图片`)
      
      // 下载后可选择清空选择
      // this.selectedImages = []
    },
    
    clearAllResults() {
      this.$confirm('确定要清空所有生成结果吗？', '确认操作', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        this.allGeneratedImages = []
        this.$message.success('已清空所有结果')
      })
    },
    
    // 再创作功能
    openReworkDialog(image) {
      console.log('开启重新生成对话框:', image)
      this.reworkImage = { ...image }
      this.reworkPrompt = image.prompt || this.mainPrompt || ''
      
      // 自动填充该图片类型的参考图片
      const imageType = image.type
      const originalReferences = this.referenceImagesByType[imageType] || []
      
      console.log(`为图片类型 ${imageType} 自动填充参考图片:`, originalReferences)
      
      // 将上一张生成的图片作为可移除的参考图片预填充到列表中
      const previousImageReference = {
        id: image.id,
        name: image.filename || `prev-${image.id}`,
        url: image.url,
        serverUrl: image.url,
        purpose: 'style',
        description: '上一次生成的图片 - 可选参考（可移除）'
      }
      
      // 将原有的参考图片和上一张生成的图片一起填充到重新生成的参考图片区域
      this.reworkReferenceImages = [previousImageReference, ...originalReferences]
      
      console.log('重新生成对话框参考图片列表:', this.reworkReferenceImages)
      
      this.reworkDialogVisible = true
    },
    
    // 图片操作相关
    showImageActions(type, index) {
      this.hoveredImage = { type, index }
    },
    
    hideImageActions() {
      this.hoveredImage = { type: null, index: null }
    },
    
    downloadImage(image) {
      // 使用API服务下载单张图片
      AIGCService.downloadImages([image])
      
      // 记录下载反馈
      AIGCService.recordFeedback(image.id, 'download', {
        image_type: image.type,
        download_time: new Date().toISOString()
      })
    },
    
    
    deleteImage(type, index) {
      this.$confirm('确定要删除这张图片吗？', '确认删除', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        this.generatedImages[type].splice(index, 1)
        this.$message.success('图片已删除')
      })
    },
    
    reworkImage(image) {
      this.reworkImage = image
      this.reworkPrompt = image.prompt
      this.reworkReferenceImages = []
      this.reworkDialogVisible = true
    },
    
    async executeRework() {
      // 修改提示词改为选填，留空时AI会使用默认最佳实践
      
      this.reworking = true
      
      try {
        const imageType = this.reworkImage.type
        
        // 构造完整的生成参数，包含左侧面板的所有参数
        const reworkParams = {
          // 左侧面板参数
          productForm: this.productForm,
          productImages: this.productImages,
          competitors: this.competitors,
          selectedImageTypes: [imageType], // 只生成当前图片类型
          selectedSize: this.selectedSize,
          selectedRatio: this.selectedRatio,
          selectedModel: this.selectedModel,
          mainPrompt: this.reworkPrompt, // 使用修改后的提示词
          allowTextInImage: this.allowTextInImage, // 文字生成设置
          
          // 参考图片（原有 + 新增）
          referenceImagesByType: {
            [imageType]: this.reworkReferenceImages
          },
          
          // 重新生成特有参数
          isRework: true,
          originalImage: {
            id: this.reworkImage.id,
            type: this.reworkImage.type,
            url: this.reworkImage.url,
            prompt: this.reworkImage.prompt,
            model: this.reworkImage.model
          }
        }
        
        console.log('开始重新生成图片，使用完整参数:', {
          imageType,
          originalImageId: this.reworkImage.id,
          params: reworkParams
        })
        
        // 关闭对话框
        this.reworkDialogVisible = false
        
        // 为重新生成创建占位符图片
        const placeholderImage = {
          id: `rework-placeholder-${imageType}-${Date.now()}`,
          type: imageType,
          status: 'generating', // 生成中状态
          progress: 0,
          createTime: new Date().toLocaleString(),
          model: this.selectedModel,
          size: this.selectedSize,
          ratio: this.selectedRatio,
          url: null, // 暂时没有URL
          isRework: true,
          originalId: this.reworkImage.id
        }
        
        // 添加占位符到图片列表开头
        this.allGeneratedImages.unshift(placeholderImage)
        
        // 使用流式生成接口重新生成
        const result = await AIGCService.generateImagesStream(
          reworkParams,
          // 进度回调
          (progressData) => {
            console.log(`重新生成进度: ${progressData.progress}% - 当前类型: ${progressData.current_type}`)
            
            // 更新对应占位符的进度
            const placeholderIndex = this.allGeneratedImages.findIndex(
              img => img.type === progressData.current_type && img.status === 'generating' && img.isRework
            )
            if (placeholderIndex !== -1) {
              this.allGeneratedImages[placeholderIndex].progress = 50 // 表示正在生成
            }
          },
          // 图片完成回调
          (imageData) => {
            console.log('重新生成图片完成:', imageData)
            
            // 找到对应的占位符并替换
            const placeholderIndex = this.allGeneratedImages.findIndex(
              img => img.type === (imageData.image?.image_type || imageData.type) && img.status === 'generating' && img.isRework
            )
            
            if (placeholderIndex !== -1) {
              // 构建完整的图片对象
              const processedImage = {
                id: imageData.image?.id || imageData.id,
                url: (imageData.image?.url || imageData.url)?.startsWith('http') ? 
                     (imageData.image?.url || imageData.url) : 
                     AIGCService.getImageUrl(imageData.image?.filename || imageData.filename || (imageData.image?.url || imageData.url)?.split('/').pop()),
                type: imageData.image?.image_type || imageData.type,
                status: 'completed',
                progress: 100,
                prompt: imageData.image?.prompt_used || imageData.prompt_used,
                model: imageData.image?.model_used || imageData.model_used,
                size: this.selectedSize,
                ratio: this.selectedRatio,
                createTime: new Date(imageData.image?.created_at || imageData.created_at).toLocaleString(),
                filename: imageData.image?.filename || imageData.filename,
                isRework: true,
                originalId: this.reworkImage.id
              }
              
              // 替换占位符
              this.allGeneratedImages.splice(placeholderIndex, 1, processedImage)
              this.$message.success('图片重新生成完成！')
            } else {
              // 如果没找到占位符，直接添加到开头（兜底处理）
              const processedImage = {
                id: imageData.image?.id || imageData.id,
                url: (imageData.image?.url || imageData.url)?.startsWith('http') ? 
                     (imageData.image?.url || imageData.url) : 
                     AIGCService.getImageUrl(imageData.image?.filename || imageData.filename || (imageData.image?.url || imageData.url)?.split('/').pop()),
                type: imageData.image?.image_type || imageData.type,
                status: 'completed',
                progress: 100,
                prompt: imageData.image?.prompt_used || imageData.prompt_used,
                model: imageData.image?.model_used || imageData.model_used,
                size: this.selectedSize,
                ratio: this.selectedRatio,
                createTime: new Date(imageData.image?.created_at || imageData.created_at).toLocaleString(),
                filename: imageData.image?.filename || imageData.filename,
                isRework: true,
                originalId: this.reworkImage.id
              }
              
              this.allGeneratedImages.unshift(processedImage)
              this.$message.success('图片重新生成完成！')
            }
          }
        )
        
        console.log('重新生成任务创建成功')
        this.$message.success('重新生成任务已启动')
        
      } catch (error) {
        console.error('重新生成失败:', error)
        this.$message.error(`重新生成失败: ${error.message}`)
      } finally {
        this.reworking = false
      }
    },
    
    
    // 任务管理相关
    loadTask(task) {
      // 加载历史任务数据
      this.$message.success(`已加载任务：${task.name}`)
    },
    
    saveCurrentTask() {
      const task = {
        id: Date.now(),
        name: this.productForm.title || `任务-${Date.now()}`,
        productForm: { ...this.productForm },
        competitors: [...this.competitors],
        generatedImages: { ...this.generatedImages },
        createTime: new Date().toLocaleString()
      }
      
      this.taskHistory.unshift(task)
      localStorage.setItem('aigc_task_history', JSON.stringify(this.taskHistory))
    },
    
    loadTaskHistory() {
      const history = localStorage.getItem('aigc_task_history')
      if (history) {
        this.taskHistory = JSON.parse(history)
      }
    },
    
    // 参考图持久化
    saveReferenceImages() {
      try {
        localStorage.setItem('aigc_reference_images', JSON.stringify(this.referenceImagesByType))
        console.log('参考图已保存到localStorage')
      } catch (error) {
        console.error('保存参考图失败:', error)
      }
    },
    
    loadReferenceImages() {
      try {
        const saved = localStorage.getItem('aigc_reference_images')
        if (saved) {
          this.referenceImagesByType = JSON.parse(saved)
          console.log('已从localStorage恢复参考图:', this.referenceImagesByType)
        }
      } catch (error) {
        console.error('加载参考图失败:', error)
        this.referenceImagesByType = {}
      }
    },
    
    // API配置相关
    saveApiKeys() {
      localStorage.setItem('aigc_api_keys', JSON.stringify(this.apiKeys))
      this.$message.success('API配置已保存')
    },
    
    loadApiKeys() {
      const keys = localStorage.getItem('aigc_api_keys')
      if (keys) {
        this.apiKeys = { ...this.apiKeys, ...JSON.parse(keys) }
      }
    },
    
    // 创建新任务
    createNewTask() {
      // 确认清除当前内容
      this.$confirm('创建新任务将清除当前所有内容，确认继续？', '确认', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }).then(() => {
        // 重置所有表单数据
        this.productForm = {
          targetMarket: 'US',
          title: '',
          sellingPoints: '',
          dimensions: {
            length: '',
            width: '',
            height: '',
            unit: 'cm'
          }
        }
        this.productImages = []
        this.competitors = []
        this.mainPrompt = ''
        this.selectedImageTypes = ['main']
        this.referenceImagesByType = {}
        this.allGeneratedImages = []
        this.generating = false
        this.generationProgress = 0
        this.allowTextInImage = false // 重置文字生成开关
        
        // 清理localStorage中的参考图
        localStorage.removeItem('aigc_reference_images')
        
        // 切换到产品配置页签
        this.activeTab = 'product'
        
        this.$message.success('新任务已创建，可以开始配置产品信息')
      }).catch(() => {
        // 用户取消
      })
    },
    
    // 添加演示数据用于测试界面
    addMockGeneratedImages() {
      const mockImages = this.selectedImageTypes.map((type, index) => ({
        id: `mock-${type}-${Date.now()}-${index}`,
        url: `https://picsum.photos/1024/1024?random=${Date.now() + index}`, // 使用Lorem Picsum作为占位图
        type: type,
        status: 'completed',
        progress: 100,
        model: this.selectedModel,
        size: this.actualImageSize,
        ratio: this.selectedRatio,
        createTime: new Date().toLocaleString(),
        filename: `mock_${type}_${Date.now()}.jpg`,
        prompt: this.mainPrompt || '演示图片',
        isMock: true // 标记为演示数据
      }))
      
      // 添加到图片列表
      this.allGeneratedImages.unshift(...mockImages)
      this.$message.info(`已添加 ${mockImages.length} 张演示图片用于界面测试`)
    }
  },
  
  // 自动保存当前任务
  watch: {
    productForm: {
      handler() {
        // 防抖保存
        clearTimeout(this.saveTimer)
        this.saveTimer = setTimeout(() => {
          this.saveCurrentTask()
        }, 1000)
      },
      deep: true
    }
  }
}
</script>

<style scoped>
.aigc-workbench {
  height: 100vh;
  background: var(--bg-primary);
  color: var(--text-primary);
  display: flex;
  flex-direction: column;
}

/* 浅色主题 */
.app-header {
  background: var(--bg-secondary);
  padding: 12px 24px;
  border-bottom: 1px solid var(--border-color);
  z-index: 1000;
}

.logo-section {
  display: flex;
  align-items: center;
  gap: 12px;
}

.logo-icon {
  width: 40px;
  height: 40px;
  background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  color: #000000;
  font-weight: bold;
}

.app-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.app-title {
  font-size: 18px;
  font-weight: 600;
  margin: 0;
  color: var(--text-primary);
}

.app-subtitle {
  font-size: 12px;
  color: var(--text-tertiary);
  margin: 0;
}

.workbench-container {
  height: calc(100vh - 65px);
}

/* 面板通用样式 */
.left-panel,
.right-panel {
  background: var(--bg-secondary);
  border-right: 1px solid var(--border-color);
  transition: width 0.3s ease;
  overflow: hidden;
}

.right-panel {
  border-right: none;
  border-left: 1px solid var(--border-color);
}

.panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px;
  border-bottom: 1px solid var(--border-color);
  background: var(--bg-tertiary);
}

.panel-title {
  display: flex;
  align-items: center;
  font-weight: 600;
  color: var(--text-primary);
}

.panel-title .el-icon {
  margin-right: 8px;
  color: #409eff;
}

.collapse-btn {
  color: var(--text-tertiary);
}

.panel-content {
  padding: 16px;
  height: calc(100vh - 60px);
  overflow-y: auto;
}

/* 左栏样式 */
.collapse-title {
  display: flex;
  align-items: center;
  color: var(--text-primary);
}

.collapse-title .el-icon {
  margin-right: 8px;
  color: #409eff;
}

.form-section {
  padding: 16px 0;
}

.image-upload-section {
  margin-bottom: 16px;
}

/* 新的图片上传样式 */
.upload-methods {
  margin-bottom: 16px;
}

.upload-method-group {
  width: 100%;
}

.upload-method-group .el-button {
  flex: 1;
}

.upload-area,
.paste-area,
.url-input-area {
  margin: 16px 0;
  padding: 16px;
  border: 2px dashed var(--border-color);
  border-radius: 8px;
  transition: border-color 0.3s;
}

.upload-area:hover,
.paste-area:hover {
  border-color: #409eff;
}

.upload-dragger {
  text-align: center;
  padding: 40px 20px;
}

.upload-icon {
  font-size: 48px;
  color: #606266;
  margin-bottom: 16px;
}

.upload-text {
  color: var(--text-primary);
  font-size: 16px;
  margin-bottom: 8px;
}

.upload-text em {
  color: #409eff;
  font-style: normal;
}

.upload-tip {
  color: var(--text-tertiary);
  font-size: 12px;
}

.paste-zone {
  text-align: center;
  padding: 40px 20px;
  cursor: pointer;
  transition: background 0.3s;
}

.paste-zone:hover {
  background: var(--bg-tertiary);
}

.paste-icon {
  font-size: 48px;
  color: #606266;
  margin-bottom: 16px;
}

.paste-text {
  color: var(--text-primary);
  font-size: 16px;
  margin-bottom: 8px;
}

.paste-tip {
  color: var(--text-tertiary);
  font-size: 12px;
}

.url-textarea {
  margin-bottom: 12px;
}

.add-urls-btn {
  width: 100%;
}

.uploaded-images {
  margin-top: 24px;
}

.images-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding-bottom: 8px;
  border-bottom: 1px solid var(--border-color);
}

.images-count {
  color: var(--text-primary);
  font-weight: 500;
}

.image-cards {
  display: grid;
  gap: 16px;
}

.image-card {
  background: var(--bg-tertiary);
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid var(--border-color);
  transition: transform 0.2s, box-shadow 0.2s;
}

.image-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
}

.image-preview {
  position: relative;
  height: 120px;
  overflow: hidden;
}

.image-preview img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.image-overlay {
  position: absolute;
  top: 8px;
  right: 8px;
  opacity: 0;
  transition: opacity 0.2s;
  display: flex;
  flex-direction: column;
  gap: 6px;
  z-index: 10;
}

.image-card:hover .image-overlay {
  opacity: 1;
}

.image-overlay .el-button {
  width: 36px;
  height: 36px;
  padding: 0;
  min-height: 36px;
  border-radius: 6px;
  background: rgba(0, 0, 0, 0.7);
  border: 1px solid rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(8px);
}

.image-overlay .el-button:hover {
  background: rgba(0, 0, 0, 0.8);
  border-color: rgba(255, 255, 255, 0.2);
}

.image-details {
  padding: 12px;
}

.image-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.image-name {
  font-size: 12px;
  color: var(--text-primary);
  font-weight: 500;
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.image-size {
  font-size: 11px;
  color: var(--text-tertiary);
  margin-left: 8px;
}

.image-description-input {
  margin-top: 8px;
}

.add-competitor-btn {
  width: 100%;
  margin-bottom: 16px;
}

.competitor-card {
  margin-bottom: 16px;
  padding: 16px;
  background: var(--bg-tertiary);
  border-radius: 8px;
}

.competitor-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.competitor-title {
  font-weight: 600;
  color: var(--text-primary);
}

.url-input {
  margin-top: 8px;
}

/* 中栏样式 */
.center-panel {
  background: var(--bg-primary);
  padding: 24px;
}

.prompt-section {
  margin-bottom: 20px;
}

.main-prompt {
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  transition: border-color 0.3s;
  font-size: 16px;
  color: var(--text-primary);
}

.main-prompt:focus {
  border-color: #FFD700;
  box-shadow: 0 0 0 2px rgba(255, 215, 0, 0.2);
}

.reference-upload-section {
  background: var(--bg-secondary);
  border-radius: 8px;
  border: 1px solid var(--border-color);
  padding: 16px;
  margin-bottom: 20px;
}

.reference-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.reference-title {
  color: var(--text-primary);
  font-weight: 600;
}

.generation-controls {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  align-items: center;
  margin-bottom: 24px;
  padding: 20px;
  background: var(--bg-secondary);
  border-radius: 12px;
  border: 1px solid var(--border-color);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
}

.control-item {
  flex: 0 0 auto;
}

.model-selector,
.type-selector,
.size-selector,
.ratio-selector {
  min-width: 180px;
  height: 48px;
}

/* 特殊的选择器样式优化 */
.model-selector .el-input__wrapper,
.type-selector .el-input__wrapper,
.size-selector .el-input__wrapper,
.ratio-selector .el-input__wrapper {
  background: var(--bg-tertiary);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  height: 48px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 
    0 2px 8px rgba(0, 0, 0, 0.15),
    inset 0 1px 2px rgba(255, 255, 255, 0.05);
  position: relative;
  overflow: hidden;
}

.model-selector .el-input__wrapper::before,
.type-selector .el-input__wrapper::before,
.size-selector .el-input__wrapper::before,
.ratio-selector .el-input__wrapper::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.08) 0%, rgba(139, 92, 246, 0.08) 100%);
  opacity: 0;
  transition: opacity 0.3s ease;
  pointer-events: none;
}

.model-selector .el-input__wrapper:hover,
.type-selector .el-input__wrapper:hover,
.size-selector .el-input__wrapper:hover,
.ratio-selector .el-input__wrapper:hover {
  border-color: #6366f1;
  box-shadow: 
    0 4px 16px rgba(99, 102, 241, 0.25),
    inset 0 1px 2px rgba(255, 255, 255, 0.08);
  transform: translateY(-3px);
}

.model-selector .el-input__wrapper:hover::before,
.type-selector .el-input__wrapper:hover::before,
.size-selector .el-input__wrapper:hover::before,
.ratio-selector .el-input__wrapper:hover::before {
  opacity: 1;
}

.model-selector .el-input__wrapper.is-focus,
.type-selector .el-input__wrapper.is-focus,
.size-selector .el-input__wrapper.is-focus,
.ratio-selector .el-input__wrapper.is-focus {
  border-color: #6366f1;
  box-shadow: 
    0 0 0 4px rgba(99, 102, 241, 0.25),
    0 8px 24px rgba(99, 102, 241, 0.2);
  transform: translateY(-3px);
}

.model-selector .el-input__wrapper.is-focus::before,
.type-selector .el-input__wrapper.is-focus::before,
.size-selector .el-input__wrapper.is-focus::before,
.ratio-selector .el-input__wrapper.is-focus::before {
  opacity: 1;
}

/* 输入文字样式 */
.model-selector .el-input__inner,
.type-selector .el-input__inner,
.size-selector .el-input__inner,
.ratio-selector .el-input__inner {
  color: var(--text-primary);
  font-weight: 500;
  font-size: 14px;
  height: 46px;
  line-height: 46px;
}

.model-option,
.type-option {
  display: flex !important;
  flex-direction: column !important;
  gap: 6px !important;
  padding: 4px 0 !important;
  min-height: 60px !important;
  width: 100% !important;
  box-sizing: border-box !important;
}

.model-name,
.type-name {
  font-weight: 600 !important;
  color: var(--text-primary) !important;
  font-size: 14px !important;
  margin: 0 !important;
  padding: 0 !important;
  line-height: 1.2 !important;
  display: block !important;
}

.model-desc,
.type-desc {
  font-size: 12px !important;
  color: #cccccc !important;
  line-height: 1.4 !important;
  opacity: 1 !important;
  max-width: 100% !important;
  word-wrap: break-word !important;
  white-space: normal !important;
  margin: 0 !important;
  padding: 0 !important;
  display: block !important;
  overflow: visible !important;
}

.add-reference-btn {
  flex: 0 0 auto;
  background: linear-gradient(135deg, var(--bg-tertiary), #444444);
  border: 1px solid #FFD700;
  color: #FFD700;
}

.add-reference-btn:hover {
  background: linear-gradient(135deg, #FFD700, #FFA500);
  color: #000000;
  border-color: #FFA500;
}

.prompt-section {
  flex: 1;
}

.main-prompt {
  background: var(--bg-primary);
  border: 2px solid var(--border-color);
  border-radius: 8px;
  transition: border-color 0.3s;
}

.main-prompt:focus {
  border-color: #409eff;
}

.reference-upload-section {
  background: var(--bg-primary);
  border-radius: 8px;
  border: 1px solid var(--border-color);
  padding: 16px;
}

.reference-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.reference-title {
  color: var(--text-primary);
  font-weight: 600;
}

.reference-upload {
  display: flex;
  gap: 16px;
  align-items: flex-start;
}

.reference-images {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  margin-top: 12px;
}

.reference-card {
  background: var(--bg-tertiary);
  border-radius: 8px;
  overflow: hidden;
  width: 150px;
  border: 1px solid var(--border-color);
}

.reference-preview {
  position: relative;
  height: 100px;
  overflow: hidden;
}

.reference-preview img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.reference-overlay {
  position: absolute;
  top: 4px;
  right: 4px;
  opacity: 0;
  transition: opacity 0.2s;
}

.reference-card:hover .reference-overlay {
  opacity: 1;
}

.reference-description {
  padding: 8px;
}

.control-buttons {
  display: flex;
  gap: 12px;
  align-items: center;
  justify-content: flex-end;
}

.generate-btn {
  background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%);
  border: none;
  padding: 12px 24px;
  font-size: 16px;
  font-weight: 600;
  color: #000000;
}

.generate-btn:hover {
  background: linear-gradient(135deg, #FFC107 0%, #FF8F00 100%);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(255, 193, 7, 0.3);
}

/* 生成结果样式 */
.generation-results {
  background: var(--bg-secondary);
  border-radius: 12px;
  padding: 20px;
  border: 1px solid var(--border-color);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
}

.images-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 12px;
  border-bottom: 1px solid var(--border-color);
}

.results-title {
  color: var(--text-primary);
  font-size: 18px;
  font-weight: 600;
  margin: 0;
}

.results-actions {
  display: flex;
  gap: 8px;
}

.image-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 20px;
}

.generated-image-card {
  background: var(--bg-primary);
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid var(--border-color);
  transition: all 0.3s;
}

.generated-image-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);
  border-color: #409eff;
}

.image-container {
  position: relative;
  aspect-ratio: 1;
  overflow: hidden;
}

.image-container.selected {
  outline: 3px solid #409eff;
  outline-offset: -3px;
}

.image-container img,
.image-container .generated-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.image-container .generated-image :deep(.el-image__inner) {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.image-type-tag {
  position: absolute;
  top: 8px;
  left: 8px;
  background: linear-gradient(135deg, #FFD700, #FFA500);
  color: #000000;
  font-weight: 600;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
}

.image-actions {
  position: absolute;
  top: 8px;
  right: 8px;
  display: flex;
  flex-direction: column;
  gap: 6px;
  opacity: 0;
  transition: opacity 0.3s;
  z-index: 20;
}

.generated-image-card:hover .image-actions {
  opacity: 1;
}

.image-actions .el-button {
  width: 32px;
  height: 32px;
  padding: 0;
  background: rgba(0, 0, 0, 0.8);
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: var(--text-primary);
  backdrop-filter: blur(4px);
}

.image-actions .el-button:hover {
  background: rgba(255, 215, 0, 0.9);
  border-color: #FFD700;
  color: #000000;
  transform: scale(1.05);
}

.image-actions .el-button--primary {
  background: linear-gradient(135deg, #FFD700, #FFA500);
  border-color: #FFD700;
  color: #000000;
}

.image-actions .el-button--primary:hover {
  background: linear-gradient(135deg, #FFC107, #FF8F00);
  transform: scale(1.05);
}

.image-info {
  padding: 12px;
  transition: all 0.3s;
}

/* 可选择的图片信息区域 */
.image-info.selectable {
  cursor: pointer;
  user-select: none;
}

.image-info.selectable:hover {
  background: rgba(64, 158, 255, 0.1);
}

.image-info.info-selected {
  background: rgba(64, 158, 255, 0.2);
  border-top: 2px solid #409eff;
}

.image-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.meta-left {
  display: flex;
  gap: 8px;
}

.select-indicator {
  display: flex;
  align-items: center;
  font-size: 20px;
  transition: all 0.3s;
}

.selected-icon {
  color: #409eff;
}

.unselected-icon {
  color: var(--text-tertiary);
}

.image-info.selectable:hover .unselected-icon {
  color: #409eff;
}

.model-tag,
.size-tag {
  background: linear-gradient(135deg, var(--bg-tertiary), #444444);
  color: #FFD700;
  padding: 2px 6px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 500;
  border: 1px solid #555555;
}

.generation-time {
  color: var(--text-tertiary);
  font-size: 12px;
}

/* 空状态样式 */
.empty-results {
  text-align: center;
  padding: 60px 20px;
  color: var(--text-tertiary);
}

.empty-icon {
  font-size: 64px;
  color: #606266;
  margin-bottom: 16px;
}

.empty-title {
  color: var(--text-primary);
  font-size: 18px;
  font-weight: 500;
  margin: 0 0 8px 0;
}

.empty-description {
  color: var(--text-tertiary);
  font-size: 14px;
  margin: 0;
}

/* 图片类型选择样式 */
.image-type-section {
  background: var(--bg-secondary);
  border-radius: 12px;
  padding: 20px;
  border: 1px solid var(--border-color);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
}

.image-type-selector {
  margin-bottom: 20px;
}

.selector-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding-bottom: 8px;
  border-bottom: 1px solid var(--border-color);
}

.selector-title {
  color: var(--text-primary);
  font-weight: 600;
  font-size: 16px;
}

.selector-actions {
  display: flex;
  gap: 8px;
}

.image-type-checkboxes {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 12px;
}

.image-type-checkbox {
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  padding: 12px;
  transition: all 0.3s;
}

.image-type-checkbox:hover {
  border-color: #409eff;
  background: var(--bg-hover);
}

.checkbox-content {
  display: flex;
  flex-direction: column;
  gap: 4px;
  margin-left: 8px;
}

.type-name {
  color: var(--text-primary);
  font-weight: 500;
  font-size: 14px;
}

.type-description {
  color: var(--text-tertiary);
  font-size: 12px;
  line-height: 1.4;
}

.image-type-tabs {
  background: var(--bg-secondary);
  border-radius: 8px;
  padding: 20px;
}

.generation-results {
  min-height: 400px;
}

.image-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 16px;
}

.image-card {
  position: relative;
  border-radius: 8px;
  overflow: hidden;
  background: var(--bg-tertiary);
  transition: transform 0.2s;
}

.image-card:hover {
  transform: translateY(-2px);
}

.image-card img {
  width: 100%;
  height: 200px;
  object-fit: cover;
}

.empty-results {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 300px;
  color: var(--text-tertiary);
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 16px;
  color: #606266;
}

.empty-tip {
  font-size: 12px;
  margin-top: 8px;
}

/* 右栏样式 */
.right-tabs {
  height: 100%;
}

.history-list {
  max-height: 400px;
  overflow-y: auto;
}

.history-item {
  padding: 12px;
  margin-bottom: 8px;
  background: var(--bg-tertiary);
  border-radius: 4px;
  cursor: pointer;
  transition: background 0.2s;
}

.history-item:hover {
  background: var(--border-color);
}

.task-name {
  font-weight: 500;
  color: var(--text-primary);
  margin-bottom: 4px;
}

.task-time {
  font-size: 12px;
  color: var(--text-tertiary);
}

.empty-history {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 40px 20px;
  color: var(--text-tertiary);
}

.settings-section h4 {
  color: var(--text-primary);
  margin-bottom: 16px;
}

/* 再创作对话框样式 */
.rework-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.rework-original {
  text-align: center;
}

.section-title {
  color: #303133;
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 12px;
}

.original-image-card {
  display: inline-block;
  background: #f5f5f5;
  border-radius: 8px;
  padding: 12px;
  border: 1px solid #e0e0e0;
}

.original-image-card img,
.original-image-card .original-image {
  width: 150px;
  height: 150px;
  object-fit: cover;
  border-radius: 4px;
  margin-bottom: 8px;
}

.original-image-card .original-image :deep(.el-image__inner) {
  width: 150px;
  height: 150px;
  object-fit: cover;
  border-radius: 4px;
}

.original-info {
  display: flex;
  gap: 8px;
  justify-content: center;
}

.original-type,
.original-model {
  background: #e3f2fd;
  color: #1976d2;
  padding: 2px 6px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 500;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

/* Element Plus 深色主题覆盖 */
:deep(.el-collapse) {
  background: transparent;
  border: none;
}

:deep(.el-collapse-item__header) {
  background: linear-gradient(135deg, #2d2d30 0%, #1e1e20 100%);
  color: var(--text-primary);
  border: 1px solid #3c3c41;
  border-radius: 8px;
  margin-bottom: 8px;
  padding: 14px 18px;
  transition: all 0.3s ease;
}

:deep(.el-collapse-item__header:hover) {
  background: linear-gradient(135deg, #333336 0%, #242426 100%);
  border-color: #5c5c61;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

:deep(.el-collapse-item__wrap) {
  background: transparent;
  border: none;
}

:deep(.el-collapse-item__content) {
  background: linear-gradient(145deg, #1f1f23 0%, #1a1a1e 100%);
  border-radius: 8px;
  padding: 20px;
  border: 1px solid #2d2d32;
  box-shadow: inset 0 2px 8px rgba(0, 0, 0, 0.1);
}

:deep(.el-form-item__label) {
  color: var(--text-secondary);
  font-weight: 500;
}

:deep(.el-input__wrapper) {
  background: linear-gradient(145deg, #242428 0%, #1e1e22 100%);
  border: 1px solid #3a3a3f;
  border-radius: 8px;
  transition: all 0.3s ease;
  box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.1);
}

:deep(.el-input__wrapper:hover) {
  border-color: #6366f1;
  box-shadow: 0 0 0 1px rgba(99, 102, 241, 0.3), inset 0 2px 4px rgba(0, 0, 0, 0.1);
  transform: translateY(-1px);
}

:deep(.el-input__wrapper.is-focus) {
  border-color: #6366f1;
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.2), inset 0 2px 4px rgba(0, 0, 0, 0.1);
  transform: translateY(-1px);
}

:deep(.el-input__inner) {
  color: var(--text-primary);
  background: transparent;
  font-weight: 400;
}

:deep(.el-select .el-input__inner) {
  color: var(--text-primary);
  background: transparent;
  font-weight: 500;
}

:deep(.el-textarea__inner) {
  background: linear-gradient(145deg, #242428 0%, #1e1e22 100%);
  border: 1px solid #3a3a3f;
  color: var(--text-primary);
  border-radius: 8px;
  transition: all 0.3s ease;
  box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.1);
}

:deep(.el-textarea__inner:hover) {
  border-color: #6366f1;
  box-shadow: 0 0 0 1px rgba(99, 102, 241, 0.3), inset 0 2px 4px rgba(0, 0, 0, 0.1);
  transform: translateY(-1px);
}

:deep(.el-textarea__inner:focus) {
  border-color: #6366f1;
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.2), inset 0 2px 4px rgba(0, 0, 0, 0.1);
  transform: translateY(-1px);
}

/* 优化后的下拉框样式 - 完全去除白色背景 */
:deep(.el-select .el-input__wrapper) {
  background: linear-gradient(145deg, #1a1a1e 0%, #0f0f13 100%);
  border: 1px solid #2d2d32;
  border-radius: 12px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 
    0 4px 12px rgba(0, 0, 0, 0.25),
    inset 0 1px 2px rgba(99, 102, 241, 0.08);
  position: relative;
  overflow: hidden;
}

:deep(.el-select .el-input__wrapper::before) {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.1) 0%, rgba(139, 92, 246, 0.1) 100%);
  opacity: 0;
  transition: opacity 0.3s ease;
  pointer-events: none;
}

:deep(.el-select .el-input__wrapper:hover) {
  border-color: #FFD700;
  background: linear-gradient(145deg, #1f1f23 0%, #141418 100%);
  box-shadow: 
    0 6px 20px rgba(255, 215, 0, 0.15),
    0 0 0 1px rgba(255, 215, 0, 0.3),
    inset 0 1px 2px rgba(255, 215, 0, 0.1);
  transform: translateY(-3px);
}

:deep(.el-select .el-input__wrapper:hover::before) {
  opacity: 1;
}

:deep(.el-select .el-input__wrapper.is-focus) {
  border-color: #FFD700;
  background: linear-gradient(145deg, #1f1f23 0%, #141418 100%);
  box-shadow: 
    0 0 0 4px rgba(255, 215, 0, 0.3),
    0 8px 28px rgba(255, 215, 0, 0.2),
    inset 0 1px 2px rgba(255, 215, 0, 0.15);
  transform: translateY(-3px);
}

:deep(.el-select .el-input__wrapper.is-focus::before) {
  opacity: 1;
}

/* 现代化的下拉菜单 - 深色主题优化 */
:deep(.el-select-dropdown) {
  background: rgba(15, 15, 19, 0.98);
  backdrop-filter: blur(24px) saturate(180%);
  border: 1px solid rgba(255, 215, 0, 0.2);
  border-radius: 16px;
  box-shadow: 
    0 32px 64px -16px rgba(0, 0, 0, 0.8),
    0 0 0 1px rgba(255, 215, 0, 0.1),
    inset 0 1px 0 rgba(255, 215, 0, 0.05);
  padding: 12px;
  margin-top: 6px;
  overflow: hidden;
  animation: dropdownSlide 0.25s cubic-bezier(0.34, 1.56, 0.64, 1);
}

@keyframes dropdownSlide {
  from {
    opacity: 0;
    transform: translateY(-8px) scale(0.95);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

/* 现代化的下拉选项 - 深色主题优化 */
:deep(.el-select-dropdown__item) {
  background: transparent;
  color: #f1f1f3;
  border-radius: 12px;
  margin: 3px 0;
  padding: 16px 18px;
  height: auto !important;
  min-height: 64px !important;
  line-height: normal !important;
  white-space: normal !important;
  overflow: visible !important;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  border: 1px solid transparent;
  cursor: pointer;
}

:deep(.el-select-dropdown__item::before) {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.1) 0%, rgba(139, 92, 246, 0.1) 100%);
  border-radius: 8px;
  opacity: 0;
  transition: opacity 0.25s ease;
  pointer-events: none;
}

:deep(.el-select-dropdown__item:hover) {
  background: linear-gradient(135deg, rgba(255, 215, 0, 0.12) 0%, rgba(255, 165, 0, 0.08) 100%);
  border-color: rgba(255, 215, 0, 0.4);
  transform: translateX(6px) scale(1.02);
  box-shadow: 
    0 6px 16px rgba(255, 215, 0, 0.15),
    inset 0 1px 0 rgba(255, 215, 0, 0.1);
}

:deep(.el-select-dropdown__item:hover::before) {
  opacity: 1;
}

:deep(.el-select-dropdown__item.selected) {
  background: linear-gradient(135deg, rgba(255, 215, 0, 0.2) 0%, rgba(255, 165, 0, 0.15) 100%);
  border: 1px solid #FFD700;
  color: #FFF8DC;
  font-weight: 600;
  transform: translateX(8px) scale(1.03);
  box-shadow: 
    0 8px 20px rgba(255, 215, 0, 0.25),
    inset 0 1px 0 rgba(255, 215, 0, 0.2),
    0 0 0 1px rgba(255, 215, 0, 0.3);
}

:deep(.el-select-dropdown__item.selected::before) {
  opacity: 1;
}

/* 优化的选项内容布局 */
:deep(.el-select-dropdown__item .model-option),
:deep(.el-select-dropdown__item .type-option),
:deep(.el-select-dropdown__item .market-option) {
  width: 100% !important;
  display: flex !important;
  flex-direction: column !important;
  gap: 8px !important;
  padding: 0 !important;
  margin: 0 !important;
  box-sizing: border-box !important;
}

:deep(.el-select-dropdown__item .model-name),
:deep(.el-select-dropdown__item .type-name),
:deep(.el-select-dropdown__item .market-name) {
  font-weight: 600 !important;
  color: var(--text-primary) !important;
  font-size: 15px !important;
  margin: 0 !important;
  padding: 0 !important;
  line-height: 1.3 !important;
  display: flex !important;
  align-items: center !important;
  letter-spacing: 0.2px !important;
}

:deep(.el-select-dropdown__item .model-desc),
:deep(.el-select-dropdown__item .type-desc),
:deep(.el-select-dropdown__item .market-desc) {
  font-size: 12px !important;
  color: #a1a1aa !important;
  line-height: 1.5 !important;
  opacity: 0.9 !important;
  white-space: normal !important;
  word-wrap: break-word !important;
  margin: 0 !important;
  padding: 0 !important;
  display: block !important;
  max-width: 100% !important;
  overflow: visible !important;
  font-weight: 400 !important;
}

/* 悬浮状态高级样式 - 金色主题 */
:deep(.el-select-dropdown__item:hover .model-name),
:deep(.el-select-dropdown__item:hover .type-name),
:deep(.el-select-dropdown__item:hover .market-name) {
  color: #FFF8DC !important;
  text-shadow: 0 0 8px rgba(255, 215, 0, 0.6) !important;
}

:deep(.el-select-dropdown__item:hover .model-desc),
:deep(.el-select-dropdown__item:hover .type-desc),
:deep(.el-select-dropdown__item:hover .market-desc) {
  color: #F0E68C !important;
  opacity: 1 !important;
}

/* 选中状态高级样式 - 金色主题 */
:deep(.el-select-dropdown__item.selected .model-name),
:deep(.el-select-dropdown__item.selected .type-name),
:deep(.el-select-dropdown__item.selected .market-name) {
  color: #FFFACD !important;
  text-shadow: 0 0 12px rgba(255, 215, 0, 0.8) !important;
}

:deep(.el-select-dropdown__item.selected .model-desc),
:deep(.el-select-dropdown__item.selected .type-desc),
:deep(.el-select-dropdown__item.selected .market-desc) {
  color: #F5DEB3 !important;
  opacity: 0.95 !important;
}

/* 确保下拉框容器优化 */
:deep(.el-select-dropdown) {
  max-height: 420px !important;
}

:deep(.el-select-dropdown__wrap) {
  max-height: 420px !important;
}

:deep(.el-scrollbar__view) {
  padding: 4px 0 !important;
}

/* 滚动条美化 */
:deep(.el-scrollbar__bar.is-vertical .el-scrollbar__thumb) {
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  border-radius: 8px;
  opacity: 0.7;
}

:deep(.el-scrollbar__bar.is-vertical) {
  width: 6px;
  right: 2px;
}

/* Prefix 图标样式优化 - 金色主题 */
:deep(.el-input__prefix) {
  color: #FFD700;
  font-size: 16px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  filter: drop-shadow(0 0 4px rgba(255, 215, 0, 0.3));
}

:deep(.el-select .el-input__wrapper:hover .el-input__prefix) {
  color: #FFA500;
  transform: scale(1.15) rotate(5deg);
  filter: drop-shadow(0 0 8px rgba(255, 165, 0, 0.5));
}

:deep(.el-select .el-input__wrapper.is-focus .el-input__prefix) {
  color: #FFFF00;
  transform: scale(1.2) rotate(-3deg);
  filter: drop-shadow(0 0 12px rgba(255, 255, 0, 0.6));
}

/* 多选标签样式优化 - 类似"添加参考图"按钮的配色 */
:deep(.el-tag) {
  background: linear-gradient(135deg, var(--bg-primary) 0%, #0f0f0f 100%);
  border: 1px solid #FFD700;
  color: #FFD700;
  border-radius: 8px;
  padding: 4px 12px;
  font-weight: 500;
  margin: 2px;
  box-shadow: 0 2px 8px rgba(255, 215, 0, 0.15);
  transition: all 0.3s ease;
}

:deep(.el-tag:hover) {
  background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%);
  border-color: #FFA500;
  color: #000000;
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(255, 215, 0, 0.3);
}

:deep(.el-tag .el-tag__close) {
  color: #FFD700;
  background: rgba(255, 215, 0, 0.1);
  border-radius: 50%;
  width: 18px;
  height: 18px;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid rgba(255, 215, 0, 0.3);
}

:deep(.el-tag .el-tag__close:hover) {
  background: #ef4444;
  color: var(--text-primary);
  transform: scale(1.15) rotate(90deg);
  box-shadow: 0 2px 8px rgba(239, 68, 68, 0.4);
  border-color: #ef4444;
}

/* 标签悬停时关闭按钮的样式 */
:deep(.el-tag:hover .el-tag__close) {
  color: #000000;
  background: rgba(0, 0, 0, 0.1);
  border-color: rgba(0, 0, 0, 0.2);
}

:deep(.el-tag:hover .el-tag__close:hover) {
  background: #ef4444 !important;
  color: var(--text-primary) !important;
  border-color: #ef4444 !important;
}

/* 确保描述文本完整显示 */
:deep(.el-select-dropdown__item .model-desc),
:deep(.el-select-dropdown__item .type-desc) {
  display: block !important;
  visibility: visible !important;
  min-height: 24px !important;
  white-space: normal !important;
}

.my-select-dropdown .el-select-dropdown__item {
  height: 80px !important;
  min-height: 80px !important;
}
:deep(.el-tabs__header) {
  background: var(--bg-tertiary);
  border-radius: 4px;
  margin-bottom: 16px;
}

:deep(.el-tabs__nav-wrap::after) {
  display: none;
}

:deep(.el-tabs__item) {
  color: var(--text-tertiary);
}

:deep(.el-tabs__item.is-active) {
  color: #409eff;
}

:deep(.el-upload--picture-card) {
  background: var(--bg-tertiary);
  border: 1px dashed var(--border-color);
}

:deep(.el-upload--picture-card:hover) {
  border-color: #409eff;
}
/* 简化的参考图片配置样式 */
.simple-reference-config {
  padding: 16px 0;
}

.config-controls {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 16px;
}

.control-group {
  display: flex;
  align-items: center;
  gap: 8px;
}

.control-label {
  font-size: 14px;
  color: #606266;
  font-weight: 500;
  white-space: nowrap;
}

.config-tip {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
  border-left: 4px solid #409eff;
  border-radius: 4px;
  margin-bottom: 16px;
  font-size: 14px;
  color: #1f2937;
}

.config-tip .el-icon {
  color: #409eff;
  font-size: 16px;
}

.upload-area {
  margin-top: 8px;
}

.no-selection-tip {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 40px 20px;
  color: var(--text-tertiary);
  font-size: 14px;
  text-align: center;
}

.no-selection-tip .el-icon {
  font-size: 24px;
  color: #c0c4cc;
}

/* 暗色主题适配 */
@media (prefers-color-scheme: dark) {
  .control-label {
    color: #a8abb2;
  }
  
  .config-tip {
    background: linear-gradient(135deg, #1e3a5f 0%, #1a365d 100%);
    color: #e2e8f0;
  }
  
  .no-selection-tip {
    color: #6b7280;
  }
}
/* 生成状态样式 */
.generating-placeholder,
.error-placeholder {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(145deg, #1a1a1e 0%, #0f0f13 100%);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1;
}

.generating-content,
.error-content {
  text-align: center;
  padding: 20px;
}

.generating-icon {
  font-size: 32px;
  color: #D4AF37;
  margin-bottom: 12px;
}

.error-icon {
  font-size: 32px;
  color: #ef4444;
  margin-bottom: 12px;
}

.generating-text,
.error-text {
  color: #E5E7EB;
  font-size: 16px;
  font-weight: 500;
  margin-bottom: 15px;
}

.error-message {
  color: #9CA3AF;
  font-size: 12px;
  margin-bottom: 15px;
  word-break: break-word;
}

.generating-progress {
  margin-top: 10px;
  width: 150px;
}

:deep(.generating-progress .el-progress-bar__outer) {
  background-color: rgba(212, 175, 55, 0.2);
}

:deep(.generating-progress .el-progress-bar__inner) {
  background: linear-gradient(90deg, #D4AF37 0%, #F1C40F 100%);
}

/* 旋转动画 */
@keyframes rotate {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

.rotating {
  animation: rotate 2s linear infinite;
}

.image-container {
  position: relative;
}

/* ========================================
   浅色主题适配 - 完整样式覆盖
======================================== */
/* ========================================
   更多浅色主题背景修复
======================================== */

/* 输入框和下拉框的浅色主题 */
/* ========================================
   KIMI风格布局样式
======================================== */

/* 主布局 */
.kimi-layout {
  height: 100vh;
}

/* KIMI风格侧边栏 */
.kimi-sidebar {
  background: var(--bg-secondary);
  border-right: 1px solid var(--border-color);
  display: flex;
  flex-direction: column;
  transition: all 0.3s ease;
}

/* 侧边栏头部 */
.sidebar-header {
  padding: 20px 16px;
  border-bottom: 1px solid var(--border-color);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.app-logo {
  display: flex;
  align-items: center;
  gap: 12px;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.new-task-btn {
  background: linear-gradient(135deg, #FFD700, #FFA500);
  border: none;
  color: #000;
  font-weight: 500;
}

.new-task-btn:hover {
  background: linear-gradient(135deg, #FFC107, #FF8F00);
  transform: translateY(-1px);
}

.logo-icon {
  width: 32px;
  height: 32px;
  background: linear-gradient(135deg, #FFD700, #FFA500);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #000;
  font-size: 16px;
}

.app-name {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
}

/* 导航切换 */
.sidebar-nav {
  padding: 16px 8px;
  border-bottom: 1px solid var(--border-color);
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
  color: var(--text-secondary);
  margin-bottom: 4px;
}

.nav-item:hover {
  background: rgba(255, 215, 0, 0.1);
  color: var(--text-primary);
}

.nav-item.active {
  background: rgba(255, 215, 0, 0.15);
  color: #FFD700;
  font-weight: 500;
}

.nav-item .el-icon {
  font-size: 16px;
}

/* 侧边栏内容 */
.sidebar-content {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
}

.config-panel, .history-panel {
  height: 100%;
}

/* 历史记录面板 */
.history-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.history-header h3 {
  margin: 0;
  font-size: 16px;
  color: var(--text-primary);
}

.history-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.history-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  background: var(--bg-tertiary);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.history-item.is-pinned {
  background: rgba(255, 215, 0, 0.05);
  border-left: 3px solid #ffd700;
}

.history-item:hover {
  background: rgba(255, 215, 0, 0.1);
  transform: translateX(2px);
}

.history-content {
  flex: 1;
  min-width: 0;
}

.history-title-row {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 4px;
}

.pin-icon {
  color: #ffd700;
  font-size: 14px;
  flex-shrink: 0;
}

.history-title {
  font-size: 14px;
  color: var(--text-primary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.history-meta {
  font-size: 12px;
  color: var(--text-tertiary);
}

.history-actions {
  opacity: 0;
  transition: opacity 0.2s;
  flex-shrink: 0;
}

.history-item:hover .history-actions {
  opacity: 1;
}

.history-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  color: var(--text-tertiary);
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 12px;
  opacity: 0.5;
}

/* 侧边栏底部 */
.sidebar-footer {
  padding: 16px;
  border-top: 1px solid var(--border-color);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.user-avatar {
  width: 32px;
  height: 32px;
  background: var(--bg-tertiary);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-secondary);
  flex-shrink: 0;
}

.user-details {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.coin-display {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 13px;
  color: #f59e0b;
  font-weight: 500;
}

.coin-icon {
  font-size: 16px;
  color: #f59e0b;
}

.coin-amount {
  color: #f59e0b;
}

.username {
  font-size: 14px;
  color: var(--text-primary);
}

.more-btn {
  color: var(--text-secondary);
}

/* 迷你侧边栏 */
.mini-sidebar {
  position: fixed;
  left: 0;
  top: 0;
  width: 64px;
  height: 100vh;
  background: var(--bg-secondary);
  border-right: 1px solid var(--border-color);
  display: flex;
  flex-direction: column;
  z-index: 1000;
  padding: 16px 8px;
}

.mini-sidebar-header {
  display: flex;
  justify-content: center;
  margin-bottom: 20px;
}

.expand-btn {
  width: 48px;
  height: 48px;
  background: linear-gradient(135deg, #FFD700, #FFA500);
  border: none;
  color: #000;
}

.expand-btn:hover {
  background: linear-gradient(135deg, #FFC107, #FF8F00);
  transform: scale(1.05);
}

.mini-sidebar-content {
  display: flex;
  flex-direction: column;
  gap: 12px;
  align-items: center;
}

.mini-new-task-btn {
  width: 48px;
  height: 48px;
  background: linear-gradient(135deg, #FFD700, #FFA500);
  border: none;
  color: #000;
}

.mini-new-task-btn:hover {
  background: linear-gradient(135deg, #FFC107, #FF8F00);
  transform: scale(1.05);
}

.mini-expand-btn {
  width: 48px;
  height: 48px;
  background: var(--bg-tertiary);
  border: 1px solid var(--border-color);
  color: var(--text-primary);
}

.mini-expand-btn:hover {
  background: var(--bg-primary);
  border-color: #FFD700;
  color: #FFD700;
}

/* 标签页样式 */
.sidebar-tabs {
  border-bottom: 1px solid var(--border-color);
}

.sidebar-tab-nav {
  padding: 0 16px;
}

:deep(.sidebar-tab-nav .el-tabs__header) {
  margin: 0;
}

:deep(.sidebar-tab-nav .el-tabs__nav-wrap) {
  padding: 0;
}

/* 提示词区域居中 */
.prompt-section.centered {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  min-height: 60vh;
}

/* 生成后布局调整 */
.center-panel {
  display: flex;
  flex-direction: column;
  transition: all 0.3s ease;
}

/* 当侧边栏折叠时，给中栏添加左边距 */
.center-panel.with-mini-sidebar {
  margin-left: 64px;
}

/* 当有生成结果时的布局 */
.center-panel.has-results {
  flex-direction: column-reverse;
}

.center-panel.has-results .prompt-section {
  min-height: auto;
  padding: 20px 0;
}

.center-panel.has-results .generation-results {
  flex: 1;
  overflow-y: auto;
}

/* 内部图片类型按钮 */
.image-type-buttons-inside {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  padding: 12px 16px;
  border-top: 1px solid var(--border-color);
  background: var(--bg-tertiary);
}

/* ========================================
   新的UI布局样式 - KIMI风格
======================================== */

/* 提示词输入容器 */
.prompt-input-container {
  max-width: 1000px;
  margin: 0 auto;
  background: var(--bg-secondary);
  border-radius: 16px;
  border: 1px solid var(--border-color);
  overflow: hidden;
  transition: all 0.3s ease;
}

.prompt-input-container:focus-within {
  border-color: #FFD700;
  box-shadow: 0 0 0 2px rgba(255, 215, 0, 0.1);
}

/* 主提示词输入框 */
.main-prompt {
  border: none !important;
  background: transparent !important;
}

:deep(.main-prompt .el-textarea__inner) {
  border: none !important;
  background: transparent !important;
  resize: none;
  padding: 16px 20px 8px 20px;
  font-size: 16px;
  line-height: 1.5;
  color: var(--text-primary);
}

/* 底部控制栏 */
.prompt-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 20px;
  border-top: 1px solid var(--border-color);
  background: var(--bg-tertiary);
}

/* 左侧控制组 */
.left-controls {
  display: flex;
  align-items: center;
  gap: 16px;
}

/* 下拉框包装器 */
.dropdown-wrapper {
  position: relative;
  display: flex;
  align-items: center;
  cursor: pointer;
  padding: 6px 8px;
  border-radius: 8px;
  transition: all 0.2s ease;
}

.dropdown-wrapper:hover {
  background: rgba(255, 215, 0, 0.1);
}

/* 下拉框标签 */
.dropdown-label {
  font-size: 14px;
  color: var(--text-secondary);
  pointer-events: none;
  display: flex;
  align-items: center;
  gap: 4px;
}

/* 隐藏的下拉框 */
.minimal-select {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  opacity: 0;
  cursor: pointer;
}

:deep(.minimal-select .el-input__wrapper) {
  background: transparent !important;
  border: none !important;
  box-shadow: none !important;
  padding: 0 !important;
}

:deep(.minimal-select .el-input__inner) {
  opacity: 0;
}

/* 添加下拉箭头 */
.dropdown-wrapper::after {
  content: '▼';
  font-size: 10px;
  color: var(--text-tertiary);
  margin-left: 4px;
  transition: transform 0.2s ease;
}

.dropdown-wrapper:hover::after {
  transform: translateY(-1px);
}

/* 尺寸显示 */
.size-display {
  padding: 6px 8px;
  border-radius: 8px;
  background: rgba(255, 215, 0, 0.05);
}

.size-label {
  font-size: 14px;
  color: var(--text-secondary);
}

/* 右侧控制组 */
.right-controls {
  display: flex;
  align-items: center;
  gap: 16px;
}

/* 文字图文开关样式 */
.text-graphic-toggle {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 0px 12px;
  background: var(--bg-tertiary);
  border-radius: 8px;
  border: 1px solid var(--border-color);
}

.toggle-label {
  color: var(--text-primary);
  font-size: 14px;
  font-weight: 500;
  white-space: nowrap;
}

.debug-text {
  color: #cccccc;
  font-size: 12px;
  white-space: nowrap;
}

/* 确保el-switch可见 */
:deep(.text-graphic-toggle .el-switch) {
  min-width: 60px;
}

:deep(.text-graphic-toggle .el-switch__label) {
  color: var(--text-primary) !important;
  font-size: 12px !important;
}

/* 浅色主题适配 */
/* 生成按钮 */
.generate-button {
  padding: 8px 20px;
  font-size: 14px;
  font-weight: 500;
  background: linear-gradient(135deg, #FFD700, #FFA500);
  border: none;
  color: #000;
  transition: all 0.2s ease;
}

.generate-button:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(255, 215, 0, 0.3);
}

.generate-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* 终止按钮 */
.cancel-button {
  padding: 8px 20px;
  font-size: 14px;
  font-weight: 500;
  background: linear-gradient(135deg, #ff4757, #ff3742);
  border: none;
  color: #fff;
  transition: all 0.2s ease;
}

.cancel-button:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(255, 71, 87, 0.3);
  background: linear-gradient(135deg, #ff3742, #ff2f3a);
}

.cancel-button:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

/* 图片类型按钮组 */
.image-type-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 16px;
  max-width: 1000px;
  margin-left: auto;
  margin-right: auto;
  justify-content: center;
}

.type-button {
  position: relative;
  padding: 6px 12px;
  background: var(--bg-tertiary);
  border: 1px solid var(--border-color);
  border-radius: 20px;
  cursor: pointer;
  transition: all 0.2s ease;
  font-size: 12px;
  display: flex;
  align-items: center;
  gap: 4px;
  white-space: nowrap;
}

.type-button:hover {
  border-color: #FFD700;
  background: rgba(255, 215, 0, 0.1);
}

.type-button.selected {
  border-color: #FFD700;
  background: rgba(255, 215, 0, 0.15);
  color: #FFD700;
  font-weight: 500;
}

.type-label {
  font-size: 12px;
  color: var(--text-primary);
}

.type-button.selected .type-label {
  color: #FFD700;
}

.reference-config-btn {
  width: 16px;
  height: 16px;
  background: #FFD700;
  color: #000;
  border: none;
  padding: 0;
  display: flex;
  align-items: center;
  justify-content: center;
}

.reference-config-btn .el-icon {
  font-size: 10px;
}

.reference-config-btn:hover {
  background: #FFA500;
}

/* 生成按钮区域 */
.generation-section {
  text-align: center;
  margin: 24px 0;
}

.generate-btn {
  padding: 16px 48px;
  font-size: 18px;
  font-weight: 600;
  background: linear-gradient(135deg, #FFD700, #FFA500);
  border: none;
  color: #000;
  border-radius: 24px;
  transition: all 0.3s ease;
}

.generate-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(255, 215, 0, 0.4);
}

.generate-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* 参考图片配置弹窗 */
.reference-config-dialog {
  padding: 16px 0;
}

.config-tip {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  background: rgba(255, 215, 0, 0.1);
  border: 1px solid rgba(255, 215, 0, 0.3);
  border-radius: 8px;
  margin-bottom: 20px;
  color: var(--text-primary);
}

/* 比例选项样式 */
.ratio-option {
  display: flex;
  align-items: center;
  gap: 8px;
}

.ratio-icon {
  font-size: 16px;
}

/* 折叠面板的浅色主题 */
/* 标签的浅色主题 */
/* Tab选项卡的浅色主题 */
/* 上传组件的浅色主题 */
/* Header帮助按钮样式 */
.help-button-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
  border: none !important;
  color: white !important;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
  transition: all 0.3s ease;
}

.help-button-header:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(102, 126, 234, 0.6) !important;
  background: linear-gradient(135deg, #764ba2 0%, #667eea 100%) !important;
}

/* 帮助对话框样式 */
.help-dialog-content {
  max-height: 70vh;
  overflow-y: auto;
  background: var(--text-primary);
  padding: 16px;
  border-radius: 8px;
}

.help-section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 600;
  color: #e2e2e2 !important;
}

.help-section-title .el-icon {
  font-size: 20px;
  color: #409eff;
}

.help-section-content {
  padding: 20px;
  line-height: 1.8;
  color: #606266;
}

/* 快速入门步骤 */
.help-step {
  display: flex;
  gap: 16px;
  margin-bottom: 24px;
  padding: 16px;
  background: var(--bg-secondary);
  border-radius: 8px;
  border-left: 4px solid #409eff;
}

.step-number {
  flex-shrink: 0;
  width: 40px;
  height: 40px;
  background: #409eff;
  color: white !important;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  font-weight: bold;
}

.step-content h4 {
  margin: 0 0 8px 0;
  color: #303133 !important;
  font-size: 16px;
}

.step-content p {
  margin: 0 0 8px 0;
  color: #606266 !important;
}

/* 核心原则卡片 */
.principle-card {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 24px;
  border-radius: 12px;
  color: white;
}

.principle-formula {
  margin-bottom: 16px;
}

.formula-item {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
  font-size: 16px;
}

.formula-equal {
  font-size: 24px;
  font-weight: bold;
}

.formula-value {
  background: rgba(255, 255, 255, 0.2);
  padding: 8px 16px;
  border-radius: 6px;
  font-weight: 500;
}

.principle-details {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
}

.principle-col h5 {
  margin: 0 0 12px 0;
  font-size: 15px;
}

.principle-col ul {
  margin: 0;
  padding-left: 20px;
  list-style: none;
}

.principle-col li {
  margin-bottom: 8px;
  position: relative;
  padding-left: 12px;
}

.principle-col li:before {
  content: "•";
  position: absolute;
  left: 0;
  color: rgba(255, 255, 255, 0.8);
}

/* 输入框说明 */
.field-explanation {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.field-item {
  padding: 16px;
  background: var(--bg-secondary);
  border-radius: 8px;
  border: 1px solid #e4e7ed;
}

.field-item p {
  color: #606266 !important;
}

.field-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
}

.field-example {
  margin-top: 12px;
  padding: 12px;
  background: white;
  border-radius: 6px;
  border-left: 3px solid #409eff;
}

.field-example.warning {
  border-left-color: #e6a23c;
  background: #fef7f0;
}

.field-example strong {
  display: block;
  margin-bottom: 8px;
  color: #303133 !important;
}

.field-example code {
  display: inline-block;
  margin: 4px 8px 4px 0;
  padding: 4px 12px;
  background: #ecf5ff;
  color: #409eff !important;
  border-radius: 4px;
  font-family: 'Consolas', 'Monaco', monospace;
  font-size: 13px;
}

.field-example.warning code {
  background: #fdf6ec;
  color: #e6a23c !important;
}

/* 提示词示例 */
.prompt-section {
  margin-bottom: 24px;
}

.section-title {
  margin: 0 0 16px 0;
  padding-bottom: 8px;
  font-size: 16px;
  font-weight: 600;
  color: #cfcfcf !important;
  border-bottom: 2px solid #409eff;
}

/* 主题式提示词 */
.theme-prompts {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.theme-item {
  background: linear-gradient(135deg, var(--bg-secondary) 0%, var(--text-primary) 100%);
  border: 1px solid #e4e7ed;
  border-radius: 12px;
  padding: 16px;
  transition: all 0.3s ease;
}

.theme-item:hover {
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.1);
  border-color: #409eff;
  transform: translateY(-2px);
}

.theme-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
  flex-wrap: wrap;
  gap: 8px;
}

.theme-header h4 {
  margin: 0;
  font-size: 15px;
  font-weight: 600;
  color: #303133 !important;
}

.theme-tags {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.theme-content {
  cursor: pointer;
  padding: 12px;
  background: var(--text-primary);
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  transition: all 0.2s ease;
}

.theme-content:hover {
  background: #ecf5ff;
  border-color: #409eff;
}

.theme-content code {
  flex: 1;
  font-family: 'Consolas', 'Monaco', monospace;
  font-size: 13px;
  color: #606266 !important;
  line-height: 1.6;
  display: block;
}

.theme-content .el-button {
  flex-shrink: 0;
}

/* 按类型分类的提示词 */
.example-category {
  margin-bottom: 32px;
}

.example-category h4 {
  margin: 0 0 16px 0;
  padding-bottom: 8px;
  border-bottom: 2px solid #409eff;
  color: #cacaca !important;
  font-size: 15px;
}

.example-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.example-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  background: var(--bg-secondary);
  border-radius: 6px;
  border: 1px solid #e4e7ed;
  cursor: pointer;
  transition: all 0.2s ease;
}

.example-item:hover {
  background: #ecf5ff;
  border-color: #409eff;
  transform: translateX(4px);
}

.example-item code {
  flex: 1;
  font-family: 'Consolas', 'Monaco', monospace;
  font-size: 13px;
  color: #303133 !important;
}

.example-item .el-button {
  flex-shrink: 0;
  color: #409eff !important;
}

.example-item.recommended {
  background: linear-gradient(135deg, #f0f9ff 0%, #e6f7ff 100%);
  border: 2px solid #67c23a;
}

.example-item.recommended:hover {
  background: linear-gradient(135deg, #d9f7be 0%, #b7eb8f 100%);
  border-color: #52c41a;
}

/* 常见问题 */
.faq-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.faq-item {
  padding: 16px;
  background: var(--bg-secondary);
  border-radius: 8px;
  border-left: 4px solid #409eff;
}

.faq-item h5 {
  margin: 0 0 12px 0;
  color: #409eff !important;
  font-size: 15px;
  font-weight: 600;
}

.faq-item p {
  margin: 0;
  color: #606266 !important;
  line-height: 1.8;
}

.faq-item strong {
  color: #303133 !important;
}

/* 对话框footer */
.help-dialog-content + .dialog-footer {
  padding-top: 16px;
  border-top: 1px solid #e4e7ed;
}

/* 滚动条样式 */
.help-dialog-content::-webkit-scrollbar {
  width: 8px;
}

.help-dialog-content::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 4px;
}

.help-dialog-content::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 4px;
}

.help-dialog-content::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

/* 历史记录样式 */
.history-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px;
  margin-bottom: 8px;
  border-radius: 8px;
  background: var(--bg-tertiary);
  border: 1px solid transparent;
  transition: all 0.3s ease;
  cursor: pointer;
}

.history-item:hover {
  background: var(--bg-hover);
  border-color: #409eff;
  transform: translateX(4px);
}

.history-item.is-pinned {
  background: linear-gradient(135deg, rgba(255, 215, 0, 0.1) 0%, rgba(255, 165, 0, 0.1) 100%);
  border-color: #FFD700;
}

.history-content {
  flex: 1;
  min-width: 0;
  cursor: pointer;
}

.history-title-row {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 6px;
}

.pin-icon {
  color: #FFD700;
  font-size: 14px;
}

.history-title {
  font-weight: 500;
  color: var(--text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.history-meta {
  font-size: 12px;
  color: var(--text-tertiary);
}

.history-actions {
  opacity: 1 !important; /* 始终显示 */
  color: var(--text-secondary);
  padding: 4px;
  margin-left: 8px;
  flex-shrink: 0;
}

.history-item:hover .history-actions {
  color: #409eff;
}

.history-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  color: var(--text-tertiary);
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 16px;
  color: var(--text-tertiary);
}

</style>
