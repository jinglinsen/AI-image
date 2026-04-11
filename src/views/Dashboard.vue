<template>
  <div class="dashboard">
    <!-- 页面标题和统计卡片 -->
    <div class="page-header">
      <h1 class="page-title">
        <el-icon><Monitor /></el-icon>
        项目仪表盘
      </h1>
      <p class="page-description">管理您的亚马逊产品图片生成任务</p>
    </div>

    <!-- 统计卡片区域 -->
    <el-row :gutter="24" class="stats-cards">
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon total">
              <el-icon><DataBoard /></el-icon>
            </div>
            <div class="stat-info">
              <h3>{{ stats.totalTasks }}</h3>
              <p>总任务数</p>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon processing">
              <el-icon><Loading /></el-icon>
            </div>
            <div class="stat-info">
              <h3>{{ stats.processingTasks }}</h3>
              <p>进行中</p>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon completed">
              <el-icon><CircleCheck /></el-icon>
            </div>
            <div class="stat-info">
              <h3>{{ stats.completedTasks }}</h3>
              <p>已完成</p>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon images">
              <el-icon><Picture /></el-icon>
            </div>
            <div class="stat-info">
              <h3>{{ stats.generatedImages }}</h3>
              <p>生成图片</p>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 快速操作区域 -->
    <el-card class="quick-actions">
      <div class="section-title">
        <el-icon><Plus /></el-icon>
        快速开始
      </div>
      <div class="action-buttons">
        <el-button 
          type="primary" 
          size="large" 
          @click="createNewTask"
          class="create-task-btn"
        >
          <el-icon><Plus /></el-icon>
          创建新的图片生成任务
        </el-button>
        <el-button size="large" @click="showHelp">
          <el-icon><QuestionFilled /></el-icon>
          使用帮助
        </el-button>
      </div>
    </el-card>

    <!-- 最近任务列表 -->
    <el-card class="recent-tasks">
      <div class="section-title">
        <el-icon><Clock /></el-icon>
        最近任务
      </div>
      
      <el-table :data="recentTasks" style="width: 100%">
        <el-table-column prop="id" label="任务ID" width="120" />
        <el-table-column prop="productName" label="产品名称" min-width="200" />
        <el-table-column prop="targetMarket" label="目标市场" width="100">
          <template #default="scope">
            <el-tag>{{ scope.row.targetMarket }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="120">
          <template #default="scope">
            <el-tag 
              :type="getStatusType(scope.row.status)"
              effect="light"
            >
              {{ getStatusText(scope.row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="generatedCount" label="已生成图片" width="120">
          <template #default="scope">
            <span class="generated-count">{{ scope.row.generatedCount }} 张</span>
          </template>
        </el-table-column>
        <el-table-column prop="createTime" label="创建时间" width="160" />
        <el-table-column label="操作" width="200">
          <template #default="scope">
            <el-button 
              v-if="scope.row.status === 'draft'"
              type="primary" 
              size="small"
              @click="continueTask(scope.row)"
            >
              继续编辑
            </el-button>
            <el-button 
              v-else
              type="success" 
              size="small"
              @click="viewTask(scope.row)"
            >
              查看详情
            </el-button>
            <el-button 
              type="danger" 
              size="small"
              @click="deleteTask(scope.row)"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <div v-if="recentTasks.length === 0" class="empty-state">
        <el-icon class="empty-icon"><Document /></el-icon>
        <p>暂无任务记录</p>
        <p class="empty-tip">点击上方"创建新的图片生成任务"开始您的第一个项目</p>
      </div>
    </el-card>

    <!-- 帮助对话框 -->
    <el-dialog v-model="helpDialogVisible" title="使用帮助" width="600px">
      <div class="help-content">
        <h3>如何使用AIGC产品图生成助手？</h3>
        <ol>
          <li><strong>创建任务：</strong>点击"创建新的图片生成任务"开始</li>
          <li><strong>上传产品信息：</strong>添加产品图片、描述和竞品信息</li>
          <li><strong>选择图片类型：</strong>从7种类型中选择需要生成的图片</li>
          <li><strong>配置生成参数：</strong>调整场景、风格等参数</li>
          <li><strong>生成和调优：</strong>生成图片并根据需要进行调整</li>
        </ol>
        
        <h4>支持的图片类型：</h4>
        <ul>
          <li>产品主图 - 纯白背景产品图</li>
          <li>尺寸图 - 展示产品尺寸的参考图</li>
          <li>功能细节图 - 突出产品功能特性</li>
          <li>使用场景图 - 产品使用的生活场景</li>
          <li>多角度展示图 - 不同角度的产品图</li>
          <li>互动图 - 人宠互动的温馨场景</li>
          <li>产品多样性图 - 多颜色多款式展示</li>
        </ul>
      </div>
    </el-dialog>
  </div>
</template>

<script>
export default {
  name: 'Dashboard',
  data() {
    return {
      helpDialogVisible: false,
      stats: {
        totalTasks: 12,
        processingTasks: 3,
        completedTasks: 9,
        generatedImages: 84
      },
      recentTasks: [
        {
          id: 'T001',
          productName: '宠物狗狗磨牙玩具套装',
          targetMarket: '美国',
          status: 'completed',
          generatedCount: 7,
          createTime: '2024-01-15 14:30'
        },
        {
          id: 'T002',
          productName: '猫咪自动喂食器',
          targetMarket: '英国',
          status: 'processing',
          generatedCount: 4,
          createTime: '2024-01-15 10:20'
        },
        {
          id: 'T003',
          productName: '宠物牵引绳套装',
          targetMarket: '德国',
          status: 'draft',
          generatedCount: 0,
          createTime: '2024-01-14 16:45'
        }
      ]
    }
  },
  methods: {
    createNewTask() {
      this.$router.push('/create-task')
    },
    continueTask(task) {
      this.$router.push(`/create-task?taskId=${task.id}`)
    },
    viewTask(task) {
      this.$router.push(`/workbench/${task.id}`)
    },
    deleteTask(task) {
      this.$confirm(`确定要删除任务"${task.productName}"吗？`, '确认删除', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        const index = this.recentTasks.findIndex(t => t.id === task.id)
        if (index > -1) {
          this.recentTasks.splice(index, 1)
          this.$message.success('任务已删除')
        }
      }).catch(() => {
        this.$message.info('已取消删除')
      })
    },
    showHelp() {
      this.helpDialogVisible = true
    },
    getStatusType(status) {
      const statusMap = {
        'draft': 'info',
        'processing': 'warning',
        'completed': 'success',
        'failed': 'danger'
      }
      return statusMap[status] || 'info'
    },
    getStatusText(status) {
      const statusMap = {
        'draft': '草稿',
        'processing': '进行中',
        'completed': '已完成',
        'failed': '失败'
      }
      return statusMap[status] || '未知'
    }
  }
}
</script>

<style scoped>
.dashboard {
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 24px;
}

.page-title {
  font-size: 28px;
  font-weight: 600;
  color: #303133;
  display: flex;
  align-items: center;
  margin-bottom: 8px;
}

.page-title .el-icon {
  margin-right: 12px;
  color: #409eff;
}

.page-description {
  color: #606266;
  font-size: 14px;
}

.stats-cards {
  margin-bottom: 24px;
}

.stat-card {
  transition: transform 0.2s;
}

.stat-card:hover {
  transform: translateY(-2px);
}

.stat-content {
  display: flex;
  align-items: center;
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 16px;
  font-size: 24px;
  color: white;
}

.stat-icon.total {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.stat-icon.processing {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.stat-icon.completed {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}

.stat-icon.images {
  background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
}

.stat-info h3 {
  font-size: 24px;
  font-weight: 600;
  color: #303133;
  margin: 0;
}

.stat-info p {
  color: #909399;
  margin: 4px 0 0 0;
  font-size: 14px;
}

.quick-actions {
  margin-bottom: 24px;
}

.action-buttons {
  display: flex;
  gap: 16px;
  margin-top: 16px;
}

.create-task-btn {
  padding: 12px 24px;
  font-size: 16px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
}

.create-task-btn:hover {
  background: linear-gradient(135deg, #5a6fd8 0%, #6a4190 100%);
}

.recent-tasks {
  margin-bottom: 24px;
}

.generated-count {
  color: #67c23a;
  font-weight: 500;
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: #909399;
}

.empty-icon {
  font-size: 64px;
  color: #dcdfe6;
  margin-bottom: 16px;
}

.empty-state p {
  margin: 8px 0;
}

.empty-tip {
  font-size: 12px;
  color: #c0c4cc;
}

.help-content h3 {
  color: #303133;
  margin-bottom: 16px;
}

.help-content h4 {
  color: #606266;
  margin: 20px 0 12px 0;
}

.help-content ol {
  padding-left: 20px;
  margin-bottom: 20px;
}

.help-content ul {
  padding-left: 20px;
}

.help-content li {
  margin-bottom: 8px;
  line-height: 1.6;
}
</style>

