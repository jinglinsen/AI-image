<template>
  <el-dialog
    v-model="visible"
    title="系统设置"
    width="500px"
    @close="handleClose"
  >
    <el-tabs v-model="activeTab">
      <!-- 账号设置Tab -->
      <el-tab-pane label="账号设置" name="account">
        <div class="settings-section">
          <h4>用户信息</h4>
          <el-descriptions :column="1" border>
            <el-descriptions-item label="用户名">
              {{ userInfo.username || '-' }}
            </el-descriptions-item>
            <el-descriptions-item label="邮箱">
              {{ userInfo.email || '-' }}
            </el-descriptions-item>
            <el-descriptions-item label="手机号">
              {{ userInfo.phone || '-' }}
            </el-descriptions-item>
            <el-descriptions-item label="角色">
              <el-tag :type="userInfo.is_admin ? 'danger' : 'info'">
                {{ userInfo.is_admin ? '管理员' : '普通用户' }}
              </el-tag>
            </el-descriptions-item>
          </el-descriptions>
        </div>

        <div class="settings-section">
          <h4>修改密码</h4>
          <el-form
            ref="passwordFormRef"
            :model="passwordForm"
            :rules="passwordRules"
            label-width="90px"
          >
            <el-form-item label="原密码" prop="oldPassword">
              <el-input
                v-model="passwordForm.oldPassword"
                type="password"
                placeholder="请输入原密码"
                show-password
              />
            </el-form-item>
            <el-form-item label="新密码" prop="newPassword">
              <el-input
                v-model="passwordForm.newPassword"
                type="password"
                placeholder="请输入新密码（至少6位，包含字母和数字）"
                show-password
              />
            </el-form-item>
            <el-form-item label="确认密码" prop="confirmPassword">
              <el-input
                v-model="passwordForm.confirmPassword"
                type="password"
                placeholder="请再次输入新密码"
                show-password
              />
            </el-form-item>
            <el-form-item>
              <el-button
                type="primary"
                @click="handleChangePassword"
                :loading="changingPassword"
              >
                {{ changingPassword ? '修改中...' : '修改密码' }}
              </el-button>
            </el-form-item>
          </el-form>
        </div>
      </el-tab-pane>

      <!-- 管理后台Tab（仅管理员可见） -->
      <el-tab-pane
        v-if="userInfo.is_admin"
        label="管理后台"
        name="admin"
      >
        <div class="settings-section">
          <el-button type="primary" @click="goToAdmin">
            <el-icon><Setting /></el-icon>
            进入管理后台
          </el-button>
        </div>
      </el-tab-pane>
    </el-tabs>

    <template #footer>
      <div class="dialog-footer">
        <el-button @click="handleLogout" type="danger">
          <el-icon><SwitchButton /></el-icon>
          退出登录
        </el-button>
        <el-button @click="handleClose">关闭</el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script>
import { ref, reactive, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Setting, SwitchButton } from '@element-plus/icons-vue'
import authService from '../services/authService'

export default {
  name: 'SystemSettings',
  components: {
    Setting,
    SwitchButton
  },
  props: {
    modelValue: {
      type: Boolean,
      default: false
    }
  },
  emits: ['update:modelValue'],
  setup(props, { emit }) {
    const router = useRouter()
    const activeTab = ref('account')
    const changingPassword = ref(false)

    // 控制对话框显示
    const visible = computed({
      get: () => props.modelValue,
      set: (val) => emit('update:modelValue', val)
    })

    // 用户信息
    const userInfo = reactive({
      username: '',
      email: '',
      phone: '',
      is_admin: false
    })

    // 加载用户信息
    const loadUserInfo = async () => {
      const result = await authService.getUserInfo()
      if (result.success) {
        Object.assign(userInfo, result.user)
      }
    }

    // 监听对话框打开
    watch(visible, (newVal) => {
      if (newVal) {
        loadUserInfo()
        resetPasswordForm()
      }
    })

    // 修改密码表单
    const passwordFormRef = ref(null)
    const passwordForm = reactive({
      oldPassword: '',
      newPassword: '',
      confirmPassword: ''
    })

    const validatePassword = (rule, value, callback) => {
      if (!value) {
        callback(new Error('请输入新密码'))
      } else if (value.length < 6) {
        callback(new Error('密码至少6位'))
      } else if (!/[a-zA-Z]/.test(value)) {
        callback(new Error('密码必须包含字母'))
      } else if (!/\d/.test(value)) {
        callback(new Error('密码必须包含数字'))
      } else {
        callback()
      }
    }

    const validateConfirmPassword = (rule, value, callback) => {
      if (!value) {
        callback(new Error('请确认密码'))
      } else if (value !== passwordForm.newPassword) {
        callback(new Error('两次密码输入不一致'))
      } else {
        callback()
      }
    }

    const passwordRules = {
      oldPassword: [
        { required: true, message: '请输入原密码', trigger: 'blur' }
      ],
      newPassword: [
        { required: true, validator: validatePassword, trigger: 'blur' }
      ],
      confirmPassword: [
        { required: true, validator: validateConfirmPassword, trigger: 'blur' }
      ]
    }

    // 重置密码表单
    const resetPasswordForm = () => {
      if (passwordFormRef.value) {
        passwordFormRef.value.resetFields()
      }
      passwordForm.oldPassword = ''
      passwordForm.newPassword = ''
      passwordForm.confirmPassword = ''
    }

    // 修改密码
    const handleChangePassword = async () => {
      if (!passwordFormRef.value) return

      await passwordFormRef.value.validate(async (valid) => {
        if (!valid) return

        changingPassword.value = true
        try {
          const result = await authService.changePassword(
            passwordForm.oldPassword,
            passwordForm.newPassword
          )

          if (result.success) {
            ElMessage.success('密码修改成功，请重新登录')
            // 修改密码后需要重新登录
            setTimeout(() => {
              handleLogout()
            }, 1500)
          } else {
            ElMessage.error(result.error || '修改密码失败')
          }
        } catch (error) {
          ElMessage.error('修改密码失败: ' + error.message)
        } finally {
          changingPassword.value = false
        }
      })
    }

    // 退出登录
    const handleLogout = async () => {
      try {
        await ElMessageBox.confirm(
          '确定要退出登录吗？',
          '提示',
          {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning'
          }
        )

        authService.logout()
        ElMessage.success('已退出登录')
        router.push('/login')
      } catch (error) {
        // 用户取消
      }
    }

    // 进入管理后台
    const goToAdmin = () => {
      router.push('/admin')
      handleClose()
    }

    // 关闭对话框
    const handleClose = () => {
      visible.value = false
      resetPasswordForm()
    }

    return {
      visible,
      activeTab,
      userInfo,
      passwordFormRef,
      passwordForm,
      passwordRules,
      changingPassword,
      handleChangePassword,
      handleLogout,
      goToAdmin,
      handleClose
    }
  }
}
</script>

<style scoped>
.settings-section {
  margin-bottom: 24px;
}

.settings-section h4 {
  margin: 0 0 16px 0;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.dialog-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

:deep(.el-descriptions) {
  margin-bottom: 0;
}

:deep(.el-form-item:last-child) {
  margin-bottom: 0;
}
</style>

