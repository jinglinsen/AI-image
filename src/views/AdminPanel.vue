<template>
  <div class="admin-panel">
    <el-page-header @back="$router.push('/')">
      <template #content>
        <span class="admin-title">
          <el-icon><Setting /></el-icon>
          管理员后台
        </span>
      </template>
    </el-page-header>

    <el-tabs v-model="activeTab" class="admin-tabs">
      <!-- 用户管理Tab -->
      <el-tab-pane label="用户管理" name="users">
        <div class="tab-content">
          <!-- 用户列表 -->
          <el-table 
            :data="users" 
            v-loading="loading" 
            stripe
            @selection-change="handleUserSelectionChange"
          >
            <el-table-column type="selection" width="55" />
            <el-table-column prop="id" label="ID" width="80" />
            <el-table-column prop="username" label="用户名" width="150" />
            <el-table-column prop="email" label="邮箱" width="200" />
            <el-table-column prop="phone" label="手机号" width="150" />
            <el-table-column label="角色" width="100">
              <template #default="{ row }">
                <el-tag :type="row.is_admin ? 'danger' : 'info'">
                  {{ row.is_admin ? '管理员' : '普通用户' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="row.status === 'active' ? 'success' : 'danger'">
                  {{ row.status === 'active' ? '正常' : '停用' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="金币余额" width="120">
              <template #default="{ row }">
                <el-tag type="warning">
                  <el-icon><Coin /></el-icon>
                  {{ row.coins || 0 }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="created_at" label="注册时间" width="180">
              <template #default="{ row }">
                {{ formatDate(row.created_at) }}
              </template>
            </el-table-column>
            <el-table-column prop="last_login_at" label="最后登录" width="180">
              <template #default="{ row }">
                {{ row.last_login_at ? formatDate(row.last_login_at) : '从未登录' }}
              </template>
            </el-table-column>
            <el-table-column label="操作" fixed="right" width="350">
              <template #default="{ row }">
                <el-button type="primary" size="small" @click="viewUserStats(row)">
                  统计
                </el-button>
                <el-button type="success" size="small" @click="rechargeCoins(row)">
                  <el-icon><Coin /></el-icon>
                  充值
                </el-button>
                <el-button type="warning" size="small" @click="resetPassword(row)">
                  重置密码
                </el-button>
                <el-button 
                  type="danger" 
                  size="small" 
                  @click="deleteUser(row)"
                  :disabled="row.is_admin"
                >
                  删除
                </el-button>
              </template>
            </el-table-column>
          </el-table>

          <!-- 批量操作 -->
          <div class="batch-actions" style="margin-top: 16px;">
            <el-button 
              type="success" 
              @click="batchRechargeDialog = true"
              :disabled="selectedUsers.length === 0"
            >
              <el-icon><Coin /></el-icon>
              批量充值 ({{ selectedUsers.length }})
            </el-button>
          </div>

          <!-- 分页 -->
          <el-pagination
            v-model:current-page="pagination.page"
            v-model:page-size="pagination.perPage"
            :total="pagination.total"
            :page-sizes="[10, 20, 50, 100]"
            layout="total, sizes, prev, pager, next"
            @size-change="loadUsers"
            @current-change="loadUsers"
            class="pagination"
          />
        </div>
      </el-tab-pane>

      <!-- 邀请码管理Tab -->
      <el-tab-pane label="邀请码管理" name="inviteCodes">
        <div class="tab-content">
          <!-- 操作按钮 -->
          <div class="actions">
            <el-button type="primary" @click="generateInviteCodes">
              <el-icon><Plus /></el-icon>
              生成邀请码
            </el-button>
            <el-button @click="loadInviteCodes">
              <el-icon><Refresh /></el-icon>
              刷新
            </el-button>
            <el-button 
              type="success" 
              @click="copySelectedCodes"
              :disabled="selectedInviteCodes.length === 0"
            >
              <el-icon><CopyDocument /></el-icon>
              批量复制 ({{ selectedInviteCodes.length }})
            </el-button>
            
            <!-- 统计信息 -->
            <div class="stats">
              <el-tag type="success">
                未使用: {{ inviteCodeStats.unused || 0 }}
              </el-tag>
              <el-tag type="info">
                已使用: {{ inviteCodeStats.used || 0 }}
              </el-tag>
              <el-tag>
                总计: {{ inviteCodeStats.total || 0 }}
              </el-tag>
            </div>
          </div>

          <!-- 邀请码列表 -->
          <div class="table-container">
            <el-table 
              :data="inviteCodes" 
              v-loading="loading" 
              stripe
              @selection-change="handleSelectionChange"
            >
            <el-table-column type="selection" width="55" />
            <el-table-column prop="id" label="ID" width="80" />
            <el-table-column label="邀请码" width="200">
              <template #default="{ row }">
                <el-tag class="code-tag" @click="copyCode(row.code)">
                  {{ row.code }}
                  <el-icon><CopyDocument /></el-icon>
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="row.status === 'unused' ? 'success' : 'info'">
                  {{ row.status === 'unused' ? '未使用' : '已使用' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="created_at" label="创建时间" width="180">
              <template #default="{ row }">
                {{ formatDate(row.created_at) }}
              </template>
            </el-table-column>
            <el-table-column prop="used_by" label="使用者ID" width="100">
              <template #default="{ row }">
                {{ row.used_by || '-' }}
              </template>
            </el-table-column>
            <el-table-column prop="used_at" label="使用时间" width="180">
              <template #default="{ row }">
                {{ row.used_at ? formatDate(row.used_at) : '-' }}
              </template>
            </el-table-column>
            <el-table-column label="操作" fixed="right" width="100">
              <template #default="{ row }">
                <el-button 
                  type="danger" 
                  size="small" 
                  @click="deleteInviteCode(row)"
                  :disabled="row.status === 'used'"
                >
                  删除
                </el-button>
              </template>
            </el-table-column>
          </el-table>
          </div>

          <!-- 分页 -->
          <div class="pagination-container">
            <el-pagination
              v-model:current-page="inviteCodePagination.page"
              v-model:page-size="inviteCodePagination.perPage"
              :total="inviteCodePagination.total"
              :page-sizes="[20, 50, 100]"
              layout="total, sizes, prev, pager, next, jumper"
              @size-change="loadInviteCodes"
              @current-change="loadInviteCodes"
            />
          </div>
        </div>
      </el-tab-pane>

      <!-- 系统设置Tab -->
      <el-tab-pane label="系统设置" name="settings">
        <div class="tab-content">
          <el-card header="金币系统设置">
            <el-form :model="coinSettings" label-width="150px" style="max-width: 600px;">
              <el-form-item label="金币模式">
                <el-radio-group v-model="coinSettings.mode">
                  <el-radio label="fixed">固定初始金币</el-radio>
                  <el-radio label="daily">每日重置</el-radio>
                </el-radio-group>
                <div class="form-tip">
                  <p v-if="coinSettings.mode === 'fixed'">
                    新用户注册时获得固定数量的金币，用完为止
                  </p>
                  <p v-else>
                    每天凌晨00:00自动将所有用户的金币重置为设定值
                  </p>
                </div>
              </el-form-item>

              <el-form-item 
                label="新用户初始金币" 
                v-if="coinSettings.mode === 'fixed'"
              >
                <el-input-number 
                  v-model="coinSettings.init_amount" 
                  :min="0" 
                  :step="10"
                  style="width: 200px;"
                />
                <span class="form-tip">用户注册时获得的金币数</span>
              </el-form-item>

              <el-form-item 
                label="每日重置金币" 
                v-if="coinSettings.mode === 'daily'"
              >
                <el-input-number 
                  v-model="coinSettings.daily_amount" 
                  :min="0" 
                  :step="10"
                  style="width: 200px;"
                />
                <span class="form-tip">每天凌晨重置为此金币数</span>
              </el-form-item>

              <el-form-item label="每张图片消耗">
                <el-input-number 
                  v-model="coinSettings.per_image" 
                  :min="1" 
                  :max="100"
                  style="width: 200px;"
                />
                <span class="form-tip">生成一张图片消耗的金币数</span>
              </el-form-item>

              <el-form-item>
                <el-button 
                  type="primary" 
                  @click="saveCoinSettings"
                  :loading="coinSettingsLoading"
                >
                  保存设置
                </el-button>
                <el-button @click="loadCoinSettings">重置</el-button>
              </el-form-item>
            </el-form>

            <!-- 说明信息 -->
            <el-alert 
              title="说明" 
              type="info" 
              :closable="false"
              style="margin-top: 20px;"
            >
              <template #default>
                <ul style="margin: 0; padding-left: 20px;">
                  <li>金币用于控制用户的图片生成次数</li>
                  <li>每成功生成一张图片，自动扣除相应金币</li>
                  <li>金币不足时，用户无法生成图片</li>
                  <li>管理员可以在用户列表中给用户充值金币</li>
                </ul>
              </template>
            </el-alert>
          </el-card>
        </div>
      </el-tab-pane>
    </el-tabs>

    <!-- 用户统计弹窗 -->
    <el-dialog
      v-model="userStatsDialogVisible"
      title="用户统计信息"
      width="600px"
    >
      <el-descriptions :column="1" border v-if="selectedUserStats">
        <el-descriptions-item label="用户名">
          {{ selectedUserStats.username }}
        </el-descriptions-item>
        <el-descriptions-item label="总任务数">
          {{ selectedUserStats.total_tasks || 0 }}
        </el-descriptions-item>
        <el-descriptions-item label="总生成图片数">
          {{ selectedUserStats.total_images || 0 }}
        </el-descriptions-item>
        <el-descriptions-item label="API调用次数">
          {{ selectedUserStats.total_api_calls || 0 }}
        </el-descriptions-item>
        <el-descriptions-item label="成功率">
          {{ selectedUserStats.success_rate || '0%' }}
        </el-descriptions-item>
        <el-descriptions-item label="注册时间">
          {{ formatDate(selectedUserStats.created_at) }}
        </el-descriptions-item>
        <el-descriptions-item label="最后登录">
          {{ selectedUserStats.last_login_at ? formatDate(selectedUserStats.last_login_at) : '从未登录' }}
        </el-descriptions-item>
      </el-descriptions>
    </el-dialog>

    <!-- 生成邀请码弹窗 -->
    <el-dialog
      v-model="generateCodesDialogVisible"
      title="生成邀请码"
      width="400px"
    >
      <el-form>
        <el-form-item label="生成数量">
          <el-input-number 
            v-model="generateCount" 
            :min="1" 
            :max="100" 
            :step="1"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="generateCodesDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmGenerateCodes" :loading="generating">
          生成
        </el-button>
      </template>
    </el-dialog>

    <!-- 充值金币弹窗 -->
    <el-dialog
      v-model="rechargeDialogVisible"
      title="充值金币"
      width="400px"
    >
      <el-form label-width="100px">
        <el-form-item label="用户">
          <el-input :value="selectedUser?.username" disabled />
        </el-form-item>
        <el-form-item label="当前金币">
          <el-tag type="warning">
            <el-icon><Coin /></el-icon>
            {{ selectedUser?.coins || 0 }}
          </el-tag>
        </el-form-item>
        <el-form-item label="充值数量">
          <el-input-number 
            v-model="rechargeAmount" 
            :min="1" 
            :max="10000" 
            :step="10"
          />
        </el-form-item>
        <el-form-item label="充值后">
          <el-tag type="success">
            <el-icon><Coin /></el-icon>
            {{ (selectedUser?.coins || 0) + rechargeAmount }}
          </el-tag>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="rechargeDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmRecharge" :loading="recharging">
          确认充值
        </el-button>
      </template>
    </el-dialog>

    <!-- 批量充值弹窗 -->
    <el-dialog
      v-model="batchRechargeDialog"
      title="批量充值金币"
      width="500px"
    >
      <el-form label-width="100px">
        <el-form-item label="选中用户">
          <el-tag type="info">{{ selectedUsers.length }} 个用户</el-tag>
        </el-form-item>
        <el-form-item label="充值数量">
          <el-input-number 
            v-model="batchRechargeAmount" 
            :min="1" 
            :max="10000" 
            :step="10"
          />
        </el-form-item>
        <el-alert 
          :title="`将为 ${selectedUsers.length} 个用户每人充值 ${batchRechargeAmount} 金币`"
          type="warning"
          :closable="false"
          style="margin-top: 10px;"
        />
      </el-form>
      <template #footer>
        <el-button @click="batchRechargeDialog = false">取消</el-button>
        <el-button 
          type="primary" 
          @click="confirmBatchRecharge" 
          :loading="batchRecharging"
        >
          确认批量充值
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Setting, Plus, Refresh, CopyDocument, Coin } from '@element-plus/icons-vue'
import config from '../config'
import authService from '../services/authService'
import adminService from '../services/adminService'

export default {
  name: 'AdminPanel',
  components: {
    Setting,
    Plus,
    Refresh,
    CopyDocument,
    Coin
  },
  setup() {
    const activeTab = ref('users')
    const loading = ref(false)
    const generating = ref(false)

    // 用户管理
    const users = ref([])
    const pagination = reactive({
      page: 1,
      perPage: 20,
      total: 0
    })

    // 邀请码管理
    const inviteCodes = ref([])
    const inviteCodeStats = ref({})
    const inviteCodePagination = reactive({
      page: 1,
      perPage: 20,
      total: 0
    })
    const selectedInviteCodes = ref([])

    // 弹窗相关
    const userStatsDialogVisible = ref(false)
    const selectedUserStats = ref(null)
    const generateCodesDialogVisible = ref(false)
    const generateCount = ref(10)

    // 金币系统
    const coinSettings = reactive({
      mode: 'fixed',
      init_amount: 100,
      daily_amount: 10,
      per_image: 1
    })
    const coinSettingsLoading = ref(false)
    const selectedUsers = ref([])
    const selectedUser = ref(null)
    const rechargeDialogVisible = ref(false)
    const rechargeAmount = ref(50)
    const recharging = ref(false)
    const batchRechargeDialog = ref(false)
    const batchRechargeAmount = ref(100)
    const batchRecharging = ref(false)

    // 加载用户列表
    const loadUsers = async () => {
      loading.value = true
      try {
        const response = await fetch(
          `${config.api.baseURL}/admin/users?page=${pagination.page}&per_page=${pagination.perPage}`,
          {
            headers: authService.getAuthHeader()
          }
        )
        const data = await response.json()
        
        if (response.ok) {
          users.value = data.users
          pagination.total = data.pagination.total
        } else {
          ElMessage.error(data.error || '加载用户列表失败')
        }
      } catch (error) {
        ElMessage.error('加载用户列表失败: ' + error.message)
      } finally {
        loading.value = false
      }
    }

    // 查看用户统计
    const viewUserStats = async (user) => {
      try {
        const response = await fetch(
          `${config.api.baseURL}/admin/users/${user.id}/stats`,
          {
            headers: authService.getAuthHeader()
          }
        )
        const data = await response.json()
        
        if (response.ok) {
          selectedUserStats.value = { ...user, ...data.stats }
          userStatsDialogVisible.value = true
        } else {
          ElMessage.error(data.error || '获取用户统计失败')
        }
      } catch (error) {
        ElMessage.error('获取用户统计失败: ' + error.message)
      }
    }

    // 重置密码
    const resetPassword = async (user) => {
      try {
        const { value: newPassword } = await ElMessageBox.prompt(
          `请输入${user.username}的新密码`,
          '重置密码',
          {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            inputPattern: /^.{6,}$/,
            inputErrorMessage: '密码至少6位'
          }
        )

        const response = await fetch(
          `${config.api.baseURL}/admin/users/${user.id}/reset-password`,
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
        
        if (response.ok) {
          ElMessage.success(data.message)
        } else {
          ElMessage.error(data.error || '重置密码失败')
        }
      } catch (error) {
        if (error !== 'cancel') {
          ElMessage.error('重置密码失败: ' + error.message)
        }
      }
    }

    // 删除用户
    const deleteUser = async (user) => {
      try {
        await ElMessageBox.confirm(
          `确定要删除用户 ${user.username} 吗？此操作不可恢复！`,
          '警告',
          {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning'
          }
        )

        const response = await fetch(
          `${config.api.baseURL}/admin/users/${user.id}`,
          {
            method: 'DELETE',
            headers: authService.getAuthHeader()
          }
        )
        const data = await response.json()
        
        if (response.ok) {
          ElMessage.success(data.message)
          loadUsers()
        } else {
          ElMessage.error(data.error || '删除用户失败')
        }
      } catch (error) {
        if (error !== 'cancel') {
          ElMessage.error('删除用户失败: ' + error.message)
        }
      }
    }

    // 加载邀请码列表
    const loadInviteCodes = async () => {
      loading.value = true
      try {
        const response = await fetch(
          `${config.api.baseURL}/admin/invite-codes?page=${inviteCodePagination.page}&per_page=${inviteCodePagination.perPage}`,
          {
            headers: authService.getAuthHeader()
          }
        )
        const data = await response.json()
        
        if (response.ok) {
          inviteCodes.value = data.invite_codes
          inviteCodePagination.total = data.pagination.total
        } else {
          ElMessage.error(data.error || '加载邀请码失败')
        }
      } catch (error) {
        ElMessage.error('加载邀请码失败: ' + error.message)
      } finally {
        loading.value = false
      }
    }

    // 加载邀请码统计
    const loadInviteCodeStats = async () => {
      try {
        const response = await fetch(
          `${config.api.baseURL}/admin/invite-codes/stats`,
          {
            headers: authService.getAuthHeader()
          }
        )
        const data = await response.json()
        
        if (response.ok) {
          inviteCodeStats.value = data.stats
        }
      } catch (error) {
        console.error('加载邀请码统计失败:', error)
      }
    }

    // 生成邀请码
    const generateInviteCodes = () => {
      generateCodesDialogVisible.value = true
    }

    const confirmGenerateCodes = async () => {
      generating.value = true
      try {
        const response = await fetch(
          `${config.api.baseURL}/admin/invite-codes/generate`,
          {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              ...authService.getAuthHeader()
            },
            body: JSON.stringify({ count: generateCount.value })
          }
        )
        const data = await response.json()
        
        if (response.ok) {
          ElMessage.success(`成功生成 ${data.count} 个邀请码`)
          generateCodesDialogVisible.value = false
          loadInviteCodes()
          loadInviteCodeStats()
        } else {
          ElMessage.error(data.error || '生成邀请码失败')
        }
      } catch (error) {
        ElMessage.error('生成邀请码失败: ' + error.message)
      } finally {
        generating.value = false
      }
    }

    // 复制单个邀请码
    const copyCode = async (code) => {
      try {
        await navigator.clipboard.writeText(code)
        ElMessage.success('邀请码已复制到剪贴板')
      } catch (error) {
        ElMessage.error('复制失败，请手动复制')
      }
    }

    // 选择变化处理
    const handleSelectionChange = (selection) => {
      selectedInviteCodes.value = selection
    }

    // 批量复制邀请码
    const copySelectedCodes = async () => {
      if (selectedInviteCodes.value.length === 0) {
        ElMessage.warning('请先选择要复制的邀请码')
        return
      }

      try {
        // 提取所有选中的邀请码
        const codes = selectedInviteCodes.value.map(item => item.code)
        // 每行一个邀请码
        const text = codes.join('\n')
        
        await navigator.clipboard.writeText(text)
        ElMessage.success(`已复制 ${codes.length} 个邀请码到剪贴板（每行一个）`)
      } catch (error) {
        // 如果换行格式失败，尝试逗号分隔
        try {
          const codes = selectedInviteCodes.value.map(item => item.code)
          const text = codes.join(',')
          await navigator.clipboard.writeText(text)
          ElMessage.success(`已复制 ${codes.length} 个邀请码到剪贴板（逗号分隔）`)
        } catch (err) {
          ElMessage.error('复制失败，请手动复制')
        }
      }
    }

    // 删除邀请码
    const deleteInviteCode = async (inviteCode) => {
      if (inviteCode.status === 'used') {
        ElMessage.warning('已使用的邀请码不能删除')
        return
      }

      try {
        await ElMessageBox.confirm(
          `确定要删除邀请码 ${inviteCode.code} 吗？`,
          '警告',
          {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning'
          }
        )

        const response = await fetch(
          `${config.api.baseURL}/admin/invite-codes/${inviteCode.id}`,
          {
            method: 'DELETE',
            headers: authService.getAuthHeader()
          }
        )
        const data = await response.json()
        
        if (response.ok) {
          ElMessage.success('删除成功')
          loadInviteCodes()
          loadInviteCodeStats()
        } else {
          ElMessage.error(data.error || '删除失败')
        }
      } catch (error) {
        if (error !== 'cancel') {
          ElMessage.error('删除失败: ' + error.message)
        }
      }
    }

    // 格式化日期
    const formatDate = (dateStr) => {
      if (!dateStr) return '-'
      const date = new Date(dateStr)
      return date.toLocaleString('zh-CN')
    }

    // ============ 金币系统方法 ============

    // 加载金币设置
    const loadCoinSettings = async () => {
      try {
        const result = await adminService.getCoinSettings()
        if (result.success) {
          Object.assign(coinSettings, result.data)
        }
      } catch (error) {
        ElMessage.error('加载金币设置失败: ' + error.message)
      }
    }

    // 保存金币设置
    const saveCoinSettings = async () => {
      coinSettingsLoading.value = true
      try {
        const result = await adminService.updateCoinSettings(coinSettings)
        if (result.success) {
          ElMessage.success('金币设置保存成功')
        } else {
          ElMessage.error(result.error || '保存失败')
        }
      } catch (error) {
        ElMessage.error('保存金币设置失败: ' + error.message)
      } finally {
        coinSettingsLoading.value = false
      }
    }

    // 用户选择改变
    const handleUserSelectionChange = (selection) => {
      selectedUsers.value = selection
    }

    // 打开充值对话框
    const rechargeCoins = (user) => {
      selectedUser.value = user
      rechargeAmount.value = 50
      rechargeDialogVisible.value = true
    }

    // 确认充值
    const confirmRecharge = async () => {
      if (!selectedUser.value) return
      
      recharging.value = true
      try {
        const result = await adminService.rechargeCoins(
          selectedUser.value.id,
          rechargeAmount.value
        )
        
        if (result.success) {
          ElMessage.success(result.message)
          rechargeDialogVisible.value = false
          // 更新用户列表中的金币数
          const userIndex = users.value.findIndex(u => u.id === selectedUser.value.id)
          if (userIndex !== -1 && result.user) {
            users.value[userIndex].coins = result.user.coins
          }
        } else {
          ElMessage.error(result.error || '充值失败')
        }
      } catch (error) {
        ElMessage.error('充值失败: ' + error.message)
      } finally {
        recharging.value = false
      }
    }

    // 确认批量充值
    const confirmBatchRecharge = async () => {
      if (selectedUsers.value.length === 0) return
      
      batchRecharging.value = true
      try {
        const userIds = selectedUsers.value.map(u => u.id)
        const result = await adminService.batchRechargeCoins(userIds, batchRechargeAmount.value)
        
        if (result.success) {
          ElMessage.success(result.message)
          batchRechargeDialog.value = false
          // 重新加载用户列表
          await loadUsers()
        } else {
          ElMessage.error(result.error || '批量充值失败')
        }
      } catch (error) {
        ElMessage.error('批量充值失败: ' + error.message)
      } finally {
        batchRecharging.value = false
      }
    }

    onMounted(() => {
      loadUsers()
      loadInviteCodes()
      loadInviteCodeStats()
      loadCoinSettings()
    })

    return {
      activeTab,
      loading,
      generating,
      users,
      pagination,
      inviteCodes,
      inviteCodeStats,
      inviteCodePagination,
      selectedInviteCodes,
      userStatsDialogVisible,
      selectedUserStats,
      generateCodesDialogVisible,
      generateCount,
      // 金币系统
      coinSettings,
      coinSettingsLoading,
      selectedUsers,
      selectedUser,
      rechargeDialogVisible,
      rechargeAmount,
      recharging,
      batchRechargeDialog,
      batchRechargeAmount,
      batchRecharging,
      // 方法
      loadUsers,
      viewUserStats,
      resetPassword,
      deleteUser,
      loadInviteCodes,
      generateInviteCodes,
      confirmGenerateCodes,
      copyCode,
      handleSelectionChange,
      copySelectedCodes,
      deleteInviteCode,
      formatDate,
      // 金币系统方法
      loadCoinSettings,
      saveCoinSettings,
      handleUserSelectionChange,
      rechargeCoins,
      confirmRecharge,
      confirmBatchRecharge
    }
  }
}
</script>

<style scoped>
.admin-panel {
  padding: 24px;
  min-height: 100vh;
  background: #f5f7fa;
  color: #303133;
}

.admin-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 18px;
  font-weight: 600;
}

.admin-tabs {
  margin-top: 24px;
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.tab-content {
  padding: 16px 0;
}

.actions {
  display: flex;
  gap: 12px;
  align-items: center;
  margin-bottom: 16px;
}

.stats {
  margin-left: auto;
  display: flex;
  gap: 8px;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}

/* 表格容器 - 限制高度并添加滚动 */
.table-container {
  max-height: calc(100vh - 400px);
  overflow-y: auto;
  margin-bottom: 20px;
}

.pagination-container {
  margin-top: 20px;
  padding: 10px 0;
  display: flex;
  justify-content: center;
  background: white;
}

.code-tag {
  cursor: pointer;
  user-select: all;
}

.code-tag:hover {
  opacity: 0.8;
}

:deep(.el-table) {
  font-size: 14px;
}

:deep(.el-page-header) {
  margin-bottom: 20px;
}

.form-tip {
  color: #909399;
  font-size: 13px;
  margin-top: 5px;
  margin-left: 10px;
}

.batch-actions {
  display: flex;
  gap: 12px;
}
</style>

