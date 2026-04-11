<template>
  <div class="login-container">
    <div class="login-card">
      <div class="logo-section">
        <el-icon class="logo-icon"><MagicStick /></el-icon>
        <h1>AIGC 图片生成助手</h1>
        <p class="subtitle">Amazon Listing 智能图片生成平台</p>
      </div>

      <el-tabs v-model="activeTab" class="login-tabs">
        <!-- 登录Tab -->
        <el-tab-pane label="登录" name="login">
          <el-form
            ref="loginFormRef"
            :model="loginForm"
            :rules="loginRules"
            class="login-form"
          >
            <el-form-item prop="username">
              <el-input
                v-model="loginForm.username"
                placeholder="用户名或邮箱"
                size="large"
                clearable
              >
                <template #prefix>
                  <el-icon><User /></el-icon>
                </template>
              </el-input>
            </el-form-item>

            <el-form-item prop="password">
              <el-input
                v-model="loginForm.password"
                type="password"
                placeholder="密码"
                size="large"
                show-password
                @keyup.enter="handleLogin"
              >
                <template #prefix>
                  <el-icon><Lock /></el-icon>
                </template>
              </el-input>
            </el-form-item>

            <el-button
              type="primary"
              size="large"
              :loading="logging"
              @click="handleLogin"
              class="submit-btn"
            >
              {{ logging ? '登录中...' : '登录' }}
            </el-button>
          </el-form>
        </el-tab-pane>

        <!-- 注册Tab -->
        <el-tab-pane label="注册" name="register">
          <el-form
            ref="registerFormRef"
            :model="registerForm"
            :rules="registerRules"
            class="login-form"
          >
            <el-form-item prop="phone">
              <el-input
                v-model="registerForm.phone"
                placeholder="手机号"
                size="large"
                clearable
              >
                <template #prefix>
                  <el-icon><Phone /></el-icon>
                </template>
              </el-input>
            </el-form-item>

            <el-form-item prop="email">
              <el-input
                v-model="registerForm.email"
                placeholder="邮箱"
                size="large"
                clearable
              >
                <template #prefix>
                  <el-icon><Message /></el-icon>
                </template>
              </el-input>
            </el-form-item>

            <el-form-item prop="username">
              <el-input
                v-model="registerForm.username"
                placeholder="用户名"
                size="large"
                clearable
              >
                <template #prefix>
                  <el-icon><User /></el-icon>
                </template>
              </el-input>
            </el-form-item>

            <el-form-item prop="password">
              <el-input
                v-model="registerForm.password"
                type="password"
                placeholder="密码"
                size="large"
                show-password
              >
                <template #prefix>
                  <el-icon><Lock /></el-icon>
                </template>
              </el-input>
            </el-form-item>

            <el-form-item prop="confirmPassword">
              <el-input
                v-model="registerForm.confirmPassword"
                type="password"
                placeholder="确认密码"
                size="large"
                show-password
              >
                <template #prefix>
                  <el-icon><Lock /></el-icon>
                </template>
              </el-input>
            </el-form-item>

            <el-form-item prop="inviteCode">
              <el-input
                v-model="registerForm.inviteCode"
                placeholder="邀请码"
                size="large"
                clearable
              >
                <template #prefix>
                  <el-icon><Ticket /></el-icon>
                </template>
              </el-input>
            </el-form-item>

            <el-button
              type="primary"
              size="large"
              :loading="registering"
              @click="handleRegister"
              class="submit-btn"
            >
              {{ registering ? '注册中...' : '注册' }}
            </el-button>
          </el-form>
        </el-tab-pane>
      </el-tabs>
    </div>
  </div>
</template>

<script>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User, Lock, Phone, Message, Ticket, MagicStick } from '@element-plus/icons-vue'
import authService from '../services/authService'

export default {
  name: 'Login',
  components: {
    User,
    Lock,
    Phone,
    Message,
    Ticket,
    MagicStick
  },
  setup() {
    const router = useRouter()
    const activeTab = ref('login')
    const logging = ref(false)
    const registering = ref(false)

    // 登录表单
    const loginFormRef = ref(null)
    const loginForm = reactive({
      username: '',
      password: ''
    })

    const validatePhone = (rule, value, callback) => {
      const phonePattern = /^1[3-9]\d{9}$/
      if (!value) {
        callback(new Error('请输入手机号'))
      } else if (!phonePattern.test(value)) {
        callback(new Error('手机号格式不正确'))
      } else {
        callback()
      }
    }

    const validateEmail = (rule, value, callback) => {
      const emailPattern = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/
      if (!value) {
        callback(new Error('请输入邮箱'))
      } else if (!emailPattern.test(value)) {
        callback(new Error('邮箱格式不正确'))
      } else {
        callback()
      }
    }

    const validatePassword = (rule, value, callback) => {
      if (!value) {
        callback(new Error('请输入密码'))
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
      } else if (value !== registerForm.password) {
        callback(new Error('两次密码输入不一致'))
      } else {
        callback()
      }
    }

    const loginRules = {
      username: [
        { required: true, message: '请输入用户名或邮箱', trigger: 'blur' }
      ],
      password: [
        { required: true, message: '请输入密码', trigger: 'blur' }
      ]
    }

    // 注册表单
    const registerFormRef = ref(null)
    const registerForm = reactive({
      phone: '',
      email: '',
      username: '',
      password: '',
      confirmPassword: '',
      inviteCode: ''
    })

    const registerRules = {
      phone: [
        { required: true, validator: validatePhone, trigger: 'blur' }
      ],
      email: [
        { required: true, validator: validateEmail, trigger: 'blur' }
      ],
      username: [
        { required: true, message: '请输入用户名', trigger: 'blur' },
        { min: 3, max: 20, message: '用户名长度在3-20个字符', trigger: 'blur' }
      ],
      password: [
        { required: true, validator: validatePassword, trigger: 'blur' }
      ],
      confirmPassword: [
        { required: true, validator: validateConfirmPassword, trigger: 'blur' }
      ],
      inviteCode: [
        { required: true, message: '请输入邀请码', trigger: 'blur' }
      ]
    }

    // 处理登录
    const handleLogin = async () => {
      if (!loginFormRef.value) return

      await loginFormRef.value.validate(async (valid) => {
        if (!valid) return

        logging.value = true
        try {
          const result = await authService.login(
            loginForm.username,
            loginForm.password
          )

          if (result.success) {
            ElMessage.success('登录成功')
            // 跳转到工作台
            router.push('/')
          } else {
            ElMessage.error(result.error || '登录失败')
          }
        } catch (error) {
          ElMessage.error('登录失败: ' + error.message)
        } finally {
          logging.value = false
        }
      })
    }

    // 处理注册
    const handleRegister = async () => {
      if (!registerFormRef.value) return

      await registerFormRef.value.validate(async (valid) => {
        if (!valid) return

        registering.value = true
        try {
          const result = await authService.register({
            phone: registerForm.phone,
            email: registerForm.email,
            username: registerForm.username,
            password: registerForm.password,
            inviteCode: registerForm.inviteCode
          })

          if (result.success) {
            ElMessage.success('注册成功，请登录')
            // 切换到登录Tab
            activeTab.value = 'login'
            // 清空注册表单
            registerFormRef.value.resetFields()
          } else {
            ElMessage.error(result.error || '注册失败')
          }
        } catch (error) {
          ElMessage.error('注册失败: ' + error.message)
        } finally {
          registering.value = false
        }
      })
    }

    return {
      activeTab,
      logging,
      registering,
      loginFormRef,
      loginForm,
      loginRules,
      registerFormRef,
      registerForm,
      registerRules,
      handleLogin,
      handleRegister
    }
  }
}
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.login-card {
  width: 100%;
  max-width: 450px;
  background: white;
  border-radius: 16px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  padding: 40px;
}

.logo-section {
  text-align: center;
  margin-bottom: 30px;
}

.logo-icon {
  font-size: 48px;
  color: #667eea;
  margin-bottom: 16px;
}

.logo-section h1 {
  margin: 0;
  font-size: 24px;
  color: #303133;
  font-weight: 600;
}

.subtitle {
  margin: 8px 0 0 0;
  font-size: 14px;
  color: #909399;
}

.login-tabs {
  margin-top: 20px;
}

.login-form {
  margin-top: 20px;
}

.submit-btn {
  width: 100%;
  margin-top: 10px;
  height: 44px;
  font-size: 16px;
  font-weight: 500;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
}

.submit-btn:hover {
  background: linear-gradient(135deg, #5568d3 0%, #6a4193 100%);
}

:deep(.el-tabs__item) {
  font-size: 16px;
  font-weight: 500;
}

:deep(.el-input__inner) {
  height: 44px;
}

:deep(.el-form-item) {
  margin-bottom: 20px;
}
</style>

