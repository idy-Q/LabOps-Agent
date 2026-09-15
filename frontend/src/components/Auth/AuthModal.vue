<template>
  <div
    v-if="modelValue"
    @keydown.esc.window="closeModal"
    class="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-4 bg-black/75 backdrop-blur-md animate-fade-in"
    @click.self="closeModal"
  >
    <div
      class="w-full max-w-xl rounded-2xl glass-card border border-white/[0.14] p-5 sm:p-6 shadow-2xl flex flex-col max-h-[90vh] backdrop-blur-2xl overflow-y-auto text-zinc-100"
    >
      <!-- 弹窗顶栏 -->
      <div class="flex items-center justify-between border-b border-white/[0.08] pb-3.5 mb-4 shrink-0">
        <div class="flex items-center space-x-2.5">
          <span class="p-2 rounded-xl bg-indigo-500/15 border border-indigo-500/30 text-indigo-300">
            <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
            </svg>
          </span>
          <div>
            <h3 class="font-medium text-zinc-100 text-sm sm:text-base glass-text flex items-center gap-2">
              身份鉴权与权限切换中心
              <span
                class="text-[10px] px-2 py-0.5 rounded-full font-mono border"
                :class="rolePillClass(currentUser?.role)"
              >
                当前: {{ currentUser?.real_name || '未登录' }} [{{ currentUser?.role || '游客' }}]
              </span>
            </h3>
          </div>
        </div>

        <button
          @click="closeModal"
          class="text-zinc-500 hover:text-zinc-300 p-1.5 rounded-lg hover:bg-zinc-800 transition-colors"
          title="关闭"
        >
          <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      <!-- Tab 切换按钮栏 -->
      <div class="flex items-center space-x-2 bg-zinc-900/80 p-1 rounded-xl border border-white/[0.08] mb-4 text-xs shrink-0">
        <button
          @click="switchTab('login')"
          :class="[
            'flex-1 py-1.5 rounded-lg font-medium transition-all text-center flex items-center justify-center space-x-1.5',
            activeTab === 'login'
              ? 'bg-zinc-800 text-white shadow-sm border border-white/[0.08]'
              : 'text-zinc-400 hover:text-zinc-200'
          ]"
        >
          <svg class="w-3.5 h-3.5 text-indigo-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 16l-4-4m0 0l4-4m-4 4h14m-5 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h7a3 3 0 013 3v1" />
          </svg>
          <span>登录</span>
        </button>

        <button
          @click="switchTab('register')"
          :class="[
            'flex-1 py-1.5 rounded-lg font-medium transition-all text-center flex items-center justify-center space-x-1.5',
            activeTab === 'register'
              ? 'bg-zinc-800 text-white shadow-sm border border-white/[0.08]'
              : 'text-zinc-400 hover:text-zinc-200'
          ]"
        >
          <svg class="w-3.5 h-3.5 text-cyan-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z" />
          </svg>
          <span>新用户注册</span>
        </button>
      </div>

      <!-- 错误提示横幅 -->
      <div
        v-if="errorMessage"
        class="mb-3.5 p-2.5 rounded-xl bg-rose-500/15 border border-rose-500/30 text-rose-300 text-xs flex items-center space-x-2 animate-fade-in"
      >
        <svg class="w-4 h-4 shrink-0 text-rose-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <span>{{ errorMessage }}</span>
      </div>

      <!-- 成功提示横幅 -->
      <div
        v-if="successMessage"
        class="mb-3.5 p-2.5 rounded-xl bg-emerald-500/15 border border-emerald-500/30 text-emerald-300 text-xs flex items-center space-x-2 animate-fade-in"
      >
        <svg class="w-4 h-4 shrink-0 text-emerald-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
        </svg>
        <span>{{ successMessage }}</span>
      </div>

      <!-- Tab 1: 登录 / 快捷演示登入 -->
      <div v-if="activeTab === 'login'" class="space-y-4">
        <form @submit.prevent="handleLogin" class="space-y-3">
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div>
              <label class="block text-[11px] text-zinc-400 mb-1">工号 / 学号</label>
              <input
                v-model="loginForm.username"
                type="text"
                placeholder="例如: admin / teacher_li"
                class="w-full bg-black/30 backdrop-blur-sm border border-white/[0.08] focus:border-indigo-500/60 rounded-lg px-3 py-1.5 text-xs text-zinc-100 placeholder-zinc-500 focus:outline-none transition-colors"
                required
              />
            </div>
            <div>
              <label class="block text-[11px] text-zinc-400 mb-1">登录密码</label>
              <input
                v-model="loginForm.password"
                type="password"
                placeholder="请输入密码"
                class="w-full bg-black/30 backdrop-blur-sm border border-white/[0.08] focus:border-indigo-500/60 rounded-lg px-3 py-1.5 text-xs text-zinc-100 placeholder-zinc-500 focus:outline-none transition-colors"
                required
              />
            </div>
          </div>

          <div class="flex justify-end pt-1">
            <button
              type="submit"
              :disabled="isLoading || !loginForm.username || !loginForm.password"
              class="w-full sm:w-auto px-5 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white font-medium text-xs disabled:opacity-40 transition-all shadow-md active:scale-95 flex items-center justify-center space-x-1.5"
            >
              <span v-if="isLoading" class="w-3.5 h-3.5 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
              <span>{{ isLoading ? '验证登入中...' : '登入系统' }}</span>
            </button>
          </div>
        </form>

        <!-- 演示账号折叠下拉切换栏 (默认收敛，点击展开) -->
        <div class="pt-3 border-t border-white/[0.08]">
          <div
            @click="isDemoAccountsOpen = !isDemoAccountsOpen"
            @keydown.enter.prevent="isDemoAccountsOpen = !isDemoAccountsOpen"
            @keydown.space.prevent="isDemoAccountsOpen = !isDemoAccountsOpen"
            tabindex="0"
            role="button"
            :aria-expanded="isDemoAccountsOpen"
            class="flex items-center justify-between py-1.5 px-2.5 rounded-xl bg-zinc-900/50 hover:bg-zinc-800/60 border border-white/[0.06] hover:border-white/[0.12] cursor-pointer transition-all select-none group focus:outline-none focus:ring-1 focus:ring-indigo-500/50"
            :class="{ 'mb-3': isDemoAccountsOpen }"
          >
            <span class="text-xs font-medium text-zinc-300 flex items-center gap-1.5 group-hover:text-zinc-100">
              <svg class="w-3.5 h-3.5 text-amber-400 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
              <span>演示账号</span>
            </span>

            <!-- 下拉折叠交互按钮 -->
            <button
              type="button"
              tabindex="-1"
              class="px-2 py-0.5 rounded-md bg-zinc-800/90 group-hover:bg-zinc-700/90 text-[11px] font-medium text-indigo-300 group-hover:text-indigo-200 border border-white/[0.08] flex items-center gap-1 transition-all pointer-events-none"
            >
              <span>{{ isDemoAccountsOpen ? '收起' : '展开快捷切换' }}</span>
              <svg
                class="w-3 h-3 transition-transform duration-200"
                :class="{ 'rotate-180': isDemoAccountsOpen }"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
              </svg>
            </button>
          </div>

          <!-- 4 张典型预置用户卡片 (默认折叠收敛，仅展开时平滑展示) -->
          <transition
            enter-active-class="transition-all duration-200 ease-out"
            enter-from-class="opacity-0 -translate-y-2"
            enter-to-class="opacity-100 translate-y-0"
            leave-active-class="transition-all duration-150 ease-in"
            leave-from-class="opacity-100 translate-y-0"
            leave-to-class="opacity-0 -translate-y-2"
          >
            <div v-show="isDemoAccountsOpen" class="grid grid-cols-1 sm:grid-cols-2 gap-2.5 pt-0.5">
              <div
                v-for="u in demoUsers"
                :key="u.username"
                @click="quickSelectDemoUser(u)"
                class="p-3 rounded-xl border transition-all cursor-pointer group flex flex-col justify-between"
                :class="[
                  currentUser?.username === u.username
                    ? 'bg-indigo-950/40 border-indigo-500/50 ring-1 ring-indigo-500/40'
                    : 'bg-black/25 hover:bg-white/[0.06] border-white/[0.06] hover:border-white/[0.14]'
                ]"
              >
                <div class="flex items-start justify-between">
                  <div>
                    <div class="font-medium text-zinc-200 text-xs flex items-center gap-1.5">
                      {{ u.real_name }}
                      <span class="font-mono text-[10px] text-zinc-500">({{ u.username }})</span>
                    </div>
                    <div class="text-[10px] text-zinc-400 mt-0.5 truncate">{{ u.department }}</div>
                  </div>
                  <span
                    class="px-1.5 py-0.5 rounded text-[10px] font-mono shrink-0 border"
                    :class="rolePillClass(u.role)"
                  >
                    {{ u.role_label }}
                  </span>
                </div>

                <div class="flex items-center justify-between mt-2 pt-2 border-t border-white/[0.04] text-[10px]">
                  <span class="font-mono text-zinc-500">密码: {{ u.default_password }}</span>
                  <span
                    class="text-indigo-400 group-hover:text-indigo-300 font-medium flex items-center gap-0.5 transition-colors"
                  >
                    {{ currentUser?.username === u.username ? '当前使用中' : '一键登入 →' }}
                  </span>
                </div>
              </div>
            </div>
          </transition>
        </div>
      </div>

      <!-- Tab 2: 新用户注册 -->
      <div v-if="activeTab === 'register'" class="space-y-4">
        <form @submit.prevent="handleRegister" class="space-y-3">
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div>
              <label class="block text-[11px] text-zinc-400 mb-1">
                工号 / 学号 <span class="text-rose-400">*</span>
              </label>
              <input
                v-model="registerForm.username"
                type="text"
                placeholder="例如: teacher_zhou / 20260901"
                class="w-full bg-black/30 backdrop-blur-sm border border-white/[0.08] focus:border-cyan-500/60 rounded-lg px-3 py-1.5 text-xs text-zinc-100 placeholder-zinc-500 focus:outline-none transition-colors"
                required
                minlength="2"
              />
            </div>

            <div>
              <label class="block text-[11px] text-zinc-400 mb-1">
                真实姓名 <span class="text-rose-400">*</span>
              </label>
              <input
                v-model="registerForm.real_name"
                type="text"
                placeholder="例如: 周老师 / 赵同学"
                class="w-full bg-black/30 backdrop-blur-sm border border-white/[0.08] focus:border-cyan-500/60 rounded-lg px-3 py-1.5 text-xs text-zinc-100 placeholder-zinc-500 focus:outline-none transition-colors"
                required
              />
            </div>

            <div>
              <label class="block text-[11px] text-zinc-400 mb-1">
                登录密码 <span class="text-rose-400">* (至少6位)</span>
              </label>
              <input
                v-model="registerForm.password"
                type="password"
                placeholder="设置 6 位以上密码"
                class="w-full bg-black/30 backdrop-blur-sm border border-white/[0.08] focus:border-cyan-500/60 rounded-lg px-3 py-1.5 text-xs text-zinc-100 placeholder-zinc-500 focus:outline-none transition-colors"
                required
                minlength="6"
              />
            </div>

            <div>
              <label class="block text-[11px] text-zinc-400 mb-1">
                所属教研室 / 班级 / 部门 <span class="text-rose-400">*</span>
              </label>
              <input
                v-model="registerForm.department"
                type="text"
                placeholder="例如: 数据科学教研室 / 计科2203班"
                class="w-full bg-black/30 backdrop-blur-sm border border-white/[0.08] focus:border-cyan-500/60 rounded-lg px-3 py-1.5 text-xs text-zinc-100 placeholder-zinc-500 focus:outline-none transition-colors"
                required
              />
            </div>

            <div class="sm:col-span-2">
              <label class="block text-[11px] text-zinc-400 mb-1">联系电话 (可选)</label>
              <input
                v-model="registerForm.phone"
                type="tel"
                placeholder="例如: 13800000000"
                class="w-full bg-black/30 backdrop-blur-sm border border-white/[0.08] focus:border-cyan-500/60 rounded-lg px-3 py-1.5 text-xs text-zinc-100 placeholder-zinc-500 focus:outline-none transition-colors"
              />
            </div>
          </div>

          <!-- 申请角色选择 -->
          <div>
            <label class="block text-[11px] text-zinc-400 mb-1.5">
              申请身份角色 <span class="text-rose-400">*</span>
            </label>
            <div class="grid grid-cols-3 gap-2">
              <button
                type="button"
                @click="registerForm.role = 'TEACHER'"
                :class="[
                  'py-2 px-3 rounded-lg border text-xs font-medium flex flex-col items-center gap-1 transition-all',
                  registerForm.role === 'TEACHER'
                    ? 'bg-indigo-950/60 border-indigo-500/60 text-indigo-200 shadow-sm ring-1 ring-indigo-500/30'
                    : 'bg-black/20 hover:bg-white/[0.05] border-white/[0.06] text-zinc-400'
                ]"
              >
                <span>高校专业教师</span>
                <span class="text-[10px] text-zinc-500 font-mono">TEACHER</span>
              </button>

              <button
                type="button"
                @click="registerForm.role = 'STUDENT'"
                :class="[
                  'py-2 px-3 rounded-lg border text-xs font-medium flex flex-col items-center gap-1 transition-all',
                  registerForm.role === 'STUDENT'
                    ? 'bg-emerald-950/60 border-emerald-500/60 text-emerald-200 shadow-sm ring-1 ring-emerald-500/30'
                    : 'bg-black/20 hover:bg-white/[0.05] border-white/[0.06] text-zinc-400'
                ]"
              >
                <span>实训在读学生</span>
                <span class="text-[10px] text-zinc-500 font-mono">STUDENT</span>
              </button>

              <button
                type="button"
                @click="registerForm.role = 'ADMIN'"
                :class="[
                  'py-2 px-3 rounded-lg border text-xs font-medium flex flex-col items-center gap-1 transition-all',
                  registerForm.role === 'ADMIN'
                    ? 'bg-rose-950/60 border-rose-500/60 text-rose-200 shadow-sm ring-1 ring-rose-500/30'
                    : 'bg-black/20 hover:bg-white/[0.05] border-white/[0.06] text-zinc-400'
                ]"
              >
                <span>系统超级管理员</span>
                <span class="text-[10px] text-zinc-500 font-mono">ADMIN</span>
              </button>
            </div>
          </div>

          <!-- 选管理员时动态弹出激活码输入框 -->
          <div
            v-if="registerForm.role === 'ADMIN'"
            class="p-3 rounded-xl bg-rose-950/30 border border-rose-500/30 space-y-1.5 animate-fade-in"
          >
            <div class="flex items-center justify-between">
              <label class="block text-[11px] font-medium text-rose-300 flex items-center gap-1">
                <svg class="w-3.5 h-3.5 text-rose-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                </svg>
                管理员专属安全激活口令 <span class="text-rose-400">*</span>
              </label>
              <span class="text-[10px] text-rose-400/80 font-mono">提权防护</span>
            </div>
            <input
              v-model="registerForm.admin_code"
              type="password"
              placeholder="请输入专属安全激活口令 (初始为 admin666)"
              class="w-full bg-black/40 border border-rose-500/40 focus:border-rose-400 rounded-lg px-3 py-1.5 text-xs text-rose-100 placeholder-rose-300/40 focus:outline-none transition-colors"
              required
            />
            <p class="text-[10px] text-rose-300/70">
              面向高校实验室的轻量化智能自治运维系统超级管理员拥有工单办结、规约修改与资产调度最高权限，申请必须输入口令 <code class="px-1 py-0.5 rounded bg-black/50 text-rose-300 font-mono">admin666</code>。
            </p>
          </div>

          <div class="flex justify-end pt-2">
            <button
              type="submit"
              :disabled="isLoading"
              class="w-full sm:w-auto px-6 py-2 rounded-lg bg-cyan-600 hover:bg-cyan-500 text-white font-medium text-xs disabled:opacity-40 transition-all shadow-md active:scale-95 flex items-center justify-center space-x-1.5"
            >
              <span v-if="isLoading" class="w-3.5 h-3.5 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
              <span>{{ isLoading ? '提交注册中...' : '立即注册并登入' }}</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, watch } from 'vue'
import { api } from '../../api/client'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false,
  },
  currentUser: {
    type: Object,
    default: null,
  },
})

const emit = defineEmits(['update:modelValue', 'loginSuccess'])

const activeTab = ref('login')
const isLoading = ref(false)
const errorMessage = ref('')
const successMessage = ref('')
const isDemoAccountsOpen = ref(false)

// 弹窗开启状态监听：每次重新打开弹窗时，严格重置演示账号下拉栏为收敛状态并清空提示
watch(
  () => props.modelValue,
  (val) => {
    if (val) {
      isDemoAccountsOpen.value = false
      errorMessage.value = ''
      successMessage.value = ''
    }
  }
)

const loginForm = reactive({
  username: '',
  password: '',
})

const registerForm = reactive({
  username: '',
  password: '',
  real_name: '',
  role: 'TEACHER',
  department: '',
  phone: '',
  admin_code: '',
})

// 典型演示用户列表 (从后端 GET /api/auth/demo-users 拉取)
const demoUsers = ref([
  {
    username: 'admin',
    real_name: '王主管',
    role: 'ADMIN',
    role_label: '超级管理员',
    department: '网络中心运维部',
    phone: '13800000001',
    default_password: 'admin666',
  },
  {
    username: 'teacher_li',
    real_name: '李老师',
    role: 'TEACHER',
    role_label: '专业课教师',
    department: '物联网工程教研室',
    phone: '13900000002',
    default_password: '123456',
  },
  {
    username: 'teacher_zhang',
    real_name: '张老师',
    role: 'TEACHER',
    role_label: '实训指导教师',
    department: '网络安全教研室',
    phone: '13900000003',
    default_password: '123456',
  },
  {
    username: 'student_chen',
    real_name: '陈同学',
    role: 'STUDENT',
    role_label: '实训在读学生',
    department: '计科2201班',
    phone: '13700000004',
    default_password: '123456',
  },
])

onMounted(async () => {
  try {
    const list = await api.getDemoUsers()
    if (Array.isArray(list) && list.length > 0) {
      demoUsers.value = list
    }
  } catch (e) {
    console.warn('拉取典型演示账号列表失败，使用本地预置备份', e)
  }
})

function switchTab(tab) {
  activeTab.value = tab
  errorMessage.value = ''
  successMessage.value = ''
}

function closeModal() {
  errorMessage.value = ''
  successMessage.value = ''
  isDemoAccountsOpen.value = false
  emit('update:modelValue', false)
}

function rolePillClass(role) {
  switch (role) {
    case 'ADMIN':
      return 'bg-rose-500/15 border-rose-500/30 text-rose-300'
    case 'TEACHER':
      return 'bg-indigo-500/15 border-indigo-500/30 text-indigo-300'
    case 'STUDENT':
      return 'bg-emerald-500/15 border-emerald-500/30 text-emerald-300'
    default:
      return 'bg-zinc-800 border-white/[0.08] text-zinc-400'
  }
}

async function quickSelectDemoUser(u) {
  loginForm.username = u.username
  loginForm.password = u.default_password
  await handleLogin()
}

async function handleLogin() {
  errorMessage.value = ''
  successMessage.value = ''
  isLoading.value = true

  try {
    const user = await api.login({
      username: loginForm.username.trim(),
      password: loginForm.password,
    })

    successMessage.value = `登录成功！欢迎 ${user.real_name} (${user.role})`
    loginForm.password = ''
    emit('loginSuccess', user)
    setTimeout(() => {
      closeModal()
    }, 600)
  } catch (err) {
    errorMessage.value = err.message || '登录失败，请检查工号与密码'
  } finally {
    isLoading.value = false
  }
}

async function handleRegister() {
  errorMessage.value = ''
  successMessage.value = ''
  isLoading.value = true

  const payload = {
    username: registerForm.username.trim(),
    password: registerForm.password,
    real_name: registerForm.real_name.trim(),
    role: registerForm.role,
    department: registerForm.department.trim(),
    phone: registerForm.phone?.trim() || null,
  }

  if (registerForm.role === 'ADMIN') {
    payload.admin_code = registerForm.admin_code?.trim() || ''
  }

  try {
    const registeredUser = await api.register(payload)
    successMessage.value = `注册成功！已为 ${registeredUser.real_name} 开通 ${registeredUser.role} 角色`
    registerForm.username = ''
    registerForm.password = ''
    registerForm.real_name = ''
    registerForm.department = ''
    registerForm.phone = ''
    registerForm.admin_code = ''
    registerForm.role = 'TEACHER'
    emit('loginSuccess', registeredUser)
    setTimeout(() => {
      closeModal()
    }, 800)
  } catch (err) {
    errorMessage.value = err.message || '注册失败，请检查填写内容'
  } finally {
    isLoading.value = false
  }
}
</script>
