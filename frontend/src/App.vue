<template>
  <div class="min-h-screen bg-slate-900 text-slate-100 p-6">
    <div class="max-w-6xl mx-auto">
      <header class="mb-8">
        <div class="flex items-center justify-between">
          <div>
            <h1 class="text-3xl font-bold text-white flex items-center gap-3">
              <span class="text-4xl">⚠️</span>
              有毒气体监控系统
            </h1>
            <p class="text-slate-400 mt-1">一氧化碳 (CO) 浓度实时监控与风机联动控制</p>
          </div>
          <div class="flex items-center gap-6">
            <div
              class="flex items-center gap-3 px-4 py-2.5 rounded-xl border transition-all duration-300"
              :class="fanStatus?.is_running
                ? 'bg-green-500/10 border-green-500/40 shadow-lg shadow-green-500/10'
                : 'bg-slate-800 border-slate-700'"
            >
              <div class="relative">
                <svg
                  class="w-8 h-8 transition-all duration-500"
                  :class="fanStatus?.is_running ? 'text-green-400 fan-spinning' : 'text-slate-500'"
                  viewBox="0 0 24 24"
                  fill="currentColor"
                >
                  <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.42 0-8-3.58-8-8s3.58-8 8-8 8 3.58 8 8-3.58 8-8 8z"/>
                  <path d="M12 6c-1.1 0-2 .9-2 2s.9 2 2 2 2-.9 2-2-.9-2-2-2zm-4 4c-1.1 0-2 .9-2 2s.9 2 2 2 2-.9 2-2-.9-2-2-2zm4 4c-1.1 0-2 .9-2 2s.9 2 2 2 2-.9 2-2-.9-2-2-2zm4-4c-1.1 0-2 .9-2 2s.9 2 2 2 2-.9 2-2-.9-2-2-2z"/>
                </svg>
                <svg
                  v-if="fanStatus?.is_running"
                  class="absolute inset-0 w-8 h-8 text-green-400 fan-spinning"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="1.5"
                >
                  <path d="M12 3C12 3 8 7 8 12C8 17 12 21 12 21" stroke-linecap="round"/>
                  <path d="M12 3C12 3 16 7 16 12C16 17 12 21 12 21" stroke-linecap="round"/>
                  <circle cx="12" cy="12" r="2.5"/>
                </svg>
              </div>
              <div class="flex flex-col">
                <span
                  class="text-sm font-bold transition-colors duration-300"
                  :class="fanStatus?.is_running ? 'text-green-400' : 'text-slate-500'"
                >
                  {{ fanStatus?.is_running ? '风机运行中' : '风机已停止' }}
                </span>
                <span class="text-xs text-slate-500">
                  {{ fanStatus?.device_code || 'FAN-001' }}
                </span>
              </div>
            </div>
            <div class="flex items-center gap-2">
              <span class="w-3 h-3 bg-green-500 rounded-full animate-pulse"></span>
              <span class="text-sm text-slate-400">系统运行中</span>
            </div>
          </div>
        </div>
      </header>

      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div class="lg:col-span-2 space-y-6">
          <div class="bg-slate-800 rounded-xl p-6 shadow-lg border border-slate-700">
            <div class="flex items-center justify-between mb-4">
              <h2 class="text-xl font-semibold text-white">CO 浓度趋势</h2>
              <div class="flex items-center gap-3">
                <span class="text-sm text-slate-400 flex items-center gap-2">
                  <span
                    class="w-2 h-2 rounded-full"
                    :class="isRefreshing ? 'bg-primary-400 animate-ping' : 'bg-green-500'"
                  ></span>
                  {{ isRefreshing ? '刷新中...' : '实时同步' }}
                </span>
                <span class="text-sm text-slate-500">最近 10 条数据</span>
              </div>
            </div>
            <div class="h-72">
              <Line :key="chartUpdateKey" :data="chartData" :options="chartOptions" />
            </div>
            <div class="mt-3 text-right text-xs text-slate-500">
              最后更新: {{ lastUpdateTime }}
            </div>
          </div>

          <div class="bg-slate-800 rounded-xl p-6 shadow-lg border border-slate-700">
            <h2 class="text-xl font-semibold text-white mb-4">历史数据</h2>
            <div class="overflow-x-auto">
              <table class="w-full text-sm">
                <thead>
                  <tr class="text-slate-400 border-b border-slate-700">
                    <th class="text-left py-2 px-3">序号</th>
                    <th class="text-left py-2 px-3">时间</th>
                    <th class="text-right py-2 px-3">浓度 (ppm)</th>
                    <th class="text-right py-2 px-3">状态</th>
                  </tr>
                </thead>
                <tbody>
                  <tr
                    v-for="(reading, index) in readings"
                    :key="reading.id"
                    class="border-b border-slate-700/50 hover:bg-slate-700/30"
                  >
                    <td class="py-2 px-3 text-slate-400">{{ readings.length - index }}</td>
                    <td class="py-2 px-3 text-slate-300">{{ formatTime(reading.timestamp) }}</td>
                    <td class="py-2 px-3 text-right font-mono" :class="getConcentrationClass(reading.co_ppm)">
                      {{ reading.co_ppm.toFixed(2) }}
                    </td>
                    <td class="py-2 px-3 text-right">
                      <span
                        class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium"
                        :class="getStatusBadgeClass(reading.co_ppm)"
                      >
                        {{ getStatusText(reading.co_ppm) }}
                      </span>
                    </td>
                  </tr>
                  <tr v-if="readings.length === 0">
                    <td colspan="4" class="py-8 text-center text-slate-500">暂无数据</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <div class="space-y-6">
          <div class="bg-slate-800 rounded-xl p-6 shadow-lg border border-slate-700">
            <h2 class="text-lg font-semibold text-white mb-4">当前浓度</h2>
            <div class="text-center">
              <div
                class="text-6xl font-bold mb-2 transition-colors duration-300"
                :class="getConcentrationClass(currentReading?.co_ppm || 0)"
              >
                {{ currentReading ? currentReading.co_ppm.toFixed(2) : '--' }}
              </div>
              <div class="text-slate-400 text-lg">ppm</div>
              <div class="mt-4">
                <span
                  class="inline-flex items-center px-4 py-2 rounded-full text-sm font-medium"
                  :class="getStatusBadgeClass(currentReading?.co_ppm || 0)"
                >
                  <span class="w-2 h-2 rounded-full mr-2" :class="getStatusDotClass(currentReading?.co_ppm || 0)"></span>
                  {{ getStatusText(currentReading?.co_ppm || 0) }}
                </span>
              </div>
              <div class="mt-4 text-xs text-slate-500">
                采样时间: {{ currentReading ? formatTime(currentReading.timestamp) : '--' }}
              </div>
            </div>
          </div>

          <div class="bg-slate-800 rounded-xl p-6 shadow-lg border border-slate-700">
            <div class="flex items-center justify-between mb-4">
              <h2 class="text-lg font-semibold text-white">风机控制</h2>
              <div
                class="w-4 h-4 rounded-full"
                :class="fanStatus?.is_running ? 'bg-green-500 animate-pulse' : 'bg-slate-500'"
              ></div>
            </div>

            <div class="mb-4 p-3 bg-slate-700/50 rounded-lg">
              <div class="flex items-center justify-between text-sm">
                <span class="text-slate-400">设备名称</span>
                <span class="text-slate-200 font-medium">{{ fanStatus?.name || '--' }}</span>
              </div>
              <div class="flex items-center justify-between text-sm mt-1.5">
                <span class="text-slate-400">设备编号</span>
                <span class="text-slate-300 font-mono text-xs">{{ fanStatus?.device_code || '--' }}</span>
              </div>
              <div class="flex items-center justify-between text-sm mt-1.5">
                <span class="text-slate-400">安装位置</span>
                <span class="text-slate-300">{{ fanStatus?.location || '--' }}</span>
              </div>
            </div>

            <div class="mb-6">
              <div class="flex items-center justify-between mb-2">
                <span class="text-slate-400">风机状态</span>
                <span
                  class="font-semibold"
                  :class="fanStatus?.is_running ? 'text-green-400' : 'text-slate-400'"
                >
                  {{ fanStatus?.is_running ? '运行中' : '已停止' }}
                </span>
              </div>
              <div class="h-3 bg-slate-700 rounded-full overflow-hidden">
                <div
                  class="h-full transition-all duration-500 rounded-full"
                  :class="fanStatus?.is_running ? 'bg-green-500 w-full' : 'bg-slate-600 w-0'"
                ></div>
              </div>
            </div>

            <div class="mb-6">
              <label class="flex items-center justify-between cursor-pointer">
                <span class="text-slate-300">自动模式</span>
                <div
                  class="relative w-14 h-7 rounded-full transition-colors duration-300"
                  :class="fanStatus?.auto_mode ? 'bg-primary-600' : 'bg-slate-600'"
                  @click="toggleAutoMode"
                >
                  <div
                    class="absolute top-1 w-5 h-5 bg-white rounded-full transition-transform duration-300 shadow-md"
                    :class="fanStatus?.auto_mode ? 'translate-x-8' : 'translate-x-1'"
                  ></div>
                </div>
              </label>
              <p class="text-xs text-slate-500 mt-2">
                {{ fanStatus?.auto_mode ? '超过阈值自动启动风机' : '手动控制风机状态' }}
              </p>
            </div>

            <div v-if="fanStatus?.auto_mode" class="mb-6">
              <label class="block text-slate-300 mb-2">
                报警阈值: <span class="text-warning-400 font-semibold">{{ fanStatus.threshold_ppm }} ppm</span>
              </label>
              <input
                type="range"
                :value="fanStatus.threshold_ppm"
                @input="updateThreshold($event.target.value)"
                min="10"
                max="150"
                step="5"
                class="w-full h-2 bg-slate-700 rounded-lg appearance-none cursor-pointer accent-warning-500"
              />
              <div class="flex justify-between text-xs text-slate-500 mt-1">
                <span>10</span>
                <span>150</span>
              </div>
            </div>

            <button
              v-if="!fanStatus?.auto_mode"
              @click="toggleFan"
              class="w-full py-3 px-4 rounded-lg font-semibold transition-all duration-200 transform hover:scale-[1.02] active:scale-[0.98]"
              :class="fanStatus?.is_running
                ? 'bg-danger-600 hover:bg-danger-700 text-white'
                : 'bg-success-600 hover:bg-success-700 text-white'"
            >
              {{ fanStatus?.is_running ? '停止风机' : '启动风机' }}
            </button>

            <div class="mt-4 pt-4 border-t border-slate-700">
              <p class="text-xs text-slate-500">
                最后更新: {{ fanStatus ? formatTime(fanStatus.updated_at) : '--' }}
              </p>
            </div>
          </div>

          <div class="bg-slate-800 rounded-xl p-6 shadow-lg border border-slate-700">
            <h2 class="text-lg font-semibold text-white mb-4">安全提示</h2>
            <div class="space-y-3 text-sm">
              <div class="flex items-start gap-3">
                <span class="text-green-400">●</span>
                <span class="text-slate-400">0-35 ppm: 正常范围，安全</span>
              </div>
              <div class="flex items-start gap-3">
                <span class="text-yellow-400">●</span>
                <span class="text-slate-400">35-100 ppm: 轻微超标，注意通风</span>
              </div>
              <div class="flex items-start gap-3">
                <span class="text-red-400">●</span>
                <span class="text-slate-400">100+ ppm: 严重超标，立即撤离</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <footer class="mt-8 text-center text-slate-500 text-sm">
        <p>有毒气体监控系统 v1.0 | 数据每 3 秒自动刷新 | 下次刷新倒计时: {{ countdown }}s</p>
      </footer>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { Line } from 'vue-chartjs'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js'

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
)

const readings = ref([])
const currentReading = ref(null)
const fanStatus = ref(null)
const chartUpdateKey = ref(0)
const isRefreshing = ref(false)
const lastUpdateTime = ref('--')
const countdown = ref(3)
let refreshInterval = null
let countdownInterval = null

const chartData = computed(() => {
  const labels = readings.value.map(r => formatTime(r.timestamp))
  const data = readings.value.map(r => r.co_ppm)

  return {
    labels,
    datasets: [
      {
        label: 'CO 浓度 (ppm)',
        data,
        borderColor: '#3b82f6',
        backgroundColor: 'rgba(59, 130, 246, 0.1)',
        borderWidth: 2,
        tension: 0.4,
        fill: true,
        pointBackgroundColor: '#3b82f6',
        pointBorderColor: '#fff',
        pointBorderWidth: 2,
        pointRadius: 4,
        pointHoverRadius: 6
      }
    ]
  }
})

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      display: false
    },
    tooltip: {
      backgroundColor: 'rgba(15, 23, 42, 0.9)',
      titleColor: '#fff',
      bodyColor: '#94a3b8',
      borderColor: '#334155',
      borderWidth: 1,
      padding: 12,
      cornerRadius: 8
    }
  },
  scales: {
    x: {
      grid: {
        color: 'rgba(51, 65, 85, 0.5)'
      },
      ticks: {
        color: '#64748b',
        font: {
          size: 11
        }
      }
    },
    y: {
      grid: {
        color: 'rgba(51, 65, 85, 0.5)'
      },
      ticks: {
        color: '#64748b',
        font: {
          size: 11
        }
      },
      beginAtZero: true,
      suggestedMax: 100
    }
  }
}

function formatTime(timestamp) {
  if (!timestamp) return '--'
  const date = new Date(timestamp)
  return date.toLocaleTimeString('zh-CN', {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

function getConcentrationClass(ppm) {
  if (ppm <= 35) return 'text-green-400'
  if (ppm <= 100) return 'text-yellow-400'
  return 'text-red-400'
}

function getStatusText(ppm) {
  if (ppm <= 35) return '正常'
  if (ppm <= 100) return '超标'
  return '危险'
}

function getStatusBadgeClass(ppm) {
  if (ppm <= 35) return 'bg-green-500/20 text-green-400'
  if (ppm <= 100) return 'bg-yellow-500/20 text-yellow-400'
  return 'bg-red-500/20 text-red-400'
}

function getStatusDotClass(ppm) {
  if (ppm <= 35) return 'bg-green-400'
  if (ppm <= 100) return 'bg-yellow-400'
  return 'bg-red-400'
}

async function fetchReadings() {
  try {
    const response = await fetch('/api/readings/latest')
    const data = await response.json()
    readings.value = data
    if (data.length > 0) {
      currentReading.value = data[data.length - 1]
    }
  } catch (error) {
    console.error('获取数据失败:', error)
  }
}

async function fetchFanStatus() {
  try {
    const response = await fetch('/api/fan')
    const data = await response.json()
    fanStatus.value = data
  } catch (error) {
    console.error('获取风机状态失败:', error)
  }
}

async function toggleFan() {
  if (!fanStatus.value) return
  try {
    const response = await fetch('/api/fan', {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        is_running: !fanStatus.value.is_running
      })
    })
    const data = await response.json()
    fanStatus.value = data
  } catch (error) {
    console.error('切换风机状态失败:', error)
  }
}

async function toggleAutoMode() {
  if (!fanStatus.value) return
  try {
    const response = await fetch('/api/fan', {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        auto_mode: !fanStatus.value.auto_mode
      })
    })
    const data = await response.json()
    fanStatus.value = data
  } catch (error) {
    console.error('切换自动模式失败:', error)
  }
}

async function updateThreshold(value) {
  if (!fanStatus.value) return
  try {
    const response = await fetch('/api/fan', {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        threshold_ppm: parseFloat(value)
      })
    })
    const data = await response.json()
    fanStatus.value = data
  } catch (error) {
    console.error('更新阈值失败:', error)
  }
}

async function refreshData() {
  isRefreshing.value = true
  try {
    await Promise.all([fetchReadings(), fetchFanStatus()])
    chartUpdateKey.value++
    lastUpdateTime.value = formatDateTime(new Date())
  } catch (error) {
    console.error('刷新数据失败:', error)
  } finally {
    setTimeout(() => {
      isRefreshing.value = false
    }, 300)
  }
}

function formatDateTime(date) {
  return date.toLocaleTimeString('zh-CN', {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

onMounted(() => {
  refreshData()
  countdown.value = 3

  refreshInterval = setInterval(() => {
    refreshData()
    countdown.value = 3
  }, 3000)

  countdownInterval = setInterval(() => {
    if (countdown.value > 0) {
      countdown.value--
    }
  }, 1000)
})

onUnmounted(() => {
  if (refreshInterval) {
    clearInterval(refreshInterval)
  }
  if (countdownInterval) {
    clearInterval(countdownInterval)
  }
})
</script>

<style scoped>
@keyframes fan-spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

.fan-spinning {
  animation: fan-spin 0.8s linear infinite;
}
</style>
