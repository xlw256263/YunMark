<template>
  <div class="stats-view">
    <div class="stats-header">
      <h1>📊 数据中心</h1>
      <p class="subtitle">可视化分析您的收藏习惯</p>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading-container">
      <el-skeleton :rows="10" animated />
    </div>

    <!-- 主要内容 -->
    <div v-else class="stats-content">
      <!-- 概览卡片 -->
      <el-row :gutter="20" class="overview-cards">
        <el-col :xs="24" :sm="12" :md="6">
          <el-card class="stat-card" shadow="hover">
            <div class="stat-icon" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%)">
              <el-icon :size="32"><Collection /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ overview.total_bookmarks }}</div>
              <div class="stat-label">收藏总数</div>
            </div>
          </el-card>
        </el-col>

        <el-col :xs="24" :sm="12" :md="6">
          <el-card class="stat-card" shadow="hover">
            <div class="stat-icon" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%)">
              <el-icon :size="32"><FolderOpened /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ overview.total_categories }}</div>
              <div class="stat-label">分类数量</div>
            </div>
          </el-card>
        </el-col>

        <el-col :xs="24" :sm="12" :md="6">
          <el-card class="stat-card" shadow="hover">
            <div class="stat-icon" style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)">
              <el-icon :size="32"><PriceTag /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ overview.total_tags }}</div>
              <div class="stat-label">标签数量</div>
            </div>
          </el-card>
        </el-col>

        <el-col :xs="24" :sm="12" :md="6">
          <el-card class="stat-card" shadow="hover">
            <div class="stat-icon" style="background: linear-gradient(135deg, #fa709a 0%, #fee140 100%)">
              <el-icon :size="32"><TrendCharts /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ overview.new_this_week }}</div>
              <div class="stat-label">本周新增</div>
            </div>
          </el-card>
        </el-col>
      </el-row>

      <!-- 图表区域 -->
      <el-row :gutter="20" class="charts-section">
        <!-- 创建趋势图 -->
        <el-col :xs="24" :lg="16">
          <el-card class="chart-card" shadow="hover">
            <template #header>
              <div class="card-header">
                <span>📈 收藏趋势（最近30天）</span>
                <el-radio-group v-model="trendDays" size="small" @change="loadCreationTrend">
                  <el-radio-button :label="7">7天</el-radio-button>
                  <el-radio-button :label="15">15天</el-radio-button>
                  <el-radio-button :label="30">30天</el-radio-button>
                </el-radio-group>
              </div>
            </template>
            <v-chart :option="trendChartOption" class="chart" autoresize />
          </el-card>
        </el-col>

        <!-- 分类分布饼图 -->
        <el-col :xs="24" :lg="8">
          <el-card class="chart-card" shadow="hover">
            <template #header>
              <span>🥧 分类分布</span>
            </template>
            <v-chart :option="categoryPieOption" class="chart" autoresize />
          </el-card>
        </el-col>
      </el-row>

      <el-row :gutter="20" class="charts-section">
        <!-- 热门标签 -->
        <el-col :xs="24" :lg="12">
          <el-card class="chart-card" shadow="hover">
            <template #header>
              <span>🏷️ 热门标签 TOP 15</span>
            </template>
            <v-chart :option="tagBarOption" class="chart" autoresize />
          </el-card>
        </el-col>

        <!-- 热门书签排行 -->
        <el-col :xs="24" :lg="12">
          <el-card class="chart-card" shadow="hover">
            <template #header>
              <span>🔥 热门书签 TOP 10</span>
            </template>
            <div class="top-bookmarks-list">
              <div
                v-for="(bookmark, index) in topBookmarks"
                :key="bookmark.id"
                class="bookmark-item"
                @click="openBookmark(bookmark.url)"
              >
                <div class="rank-badge" :class="`rank-${index + 1}`">
                  {{ index + 1 }}
                </div>
                <div class="bookmark-info">
                  <div class="bookmark-title">{{ bookmark.title }}</div>
                  <div class="bookmark-url">{{ truncateUrl(bookmark.url) }}</div>
                </div>
                <div class="bookmark-clicks">
                  <el-icon><View /></el-icon>
                  {{ bookmark.click_count }}
                </div>
              </div>
              <el-empty v-if="topBookmarks.length === 0" description="暂无数据" />
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { LineChart, PieChart, BarChart } from 'echarts/charts'
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent
} from 'echarts/components'
import VChart from 'vue-echarts'
import { ElMessage } from 'element-plus'
import { Collection, FolderOpened, PriceTag, TrendCharts, View } from '@element-plus/icons-vue'
import {
  getStatisticsOverview,
  getCategoryDistribution,
  getTopBookmarks,
  getCreationTrend,
  getTagUsageStats
} from '@/api/statistics'
import type {
  StatsOverview,
  CategoryDistribution,
  TopBookmark,
  HeatmapData,
  TagUsageStat
} from '@/types'

// 注册 ECharts 组件
use([
  CanvasRenderer,
  LineChart,
  PieChart,
  BarChart,
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent
])

// 响应式数据
const loading = ref(true)
const overview = ref<StatsOverview>({
  total_bookmarks: 0,
  new_this_week: 0,
  total_clicks: 0,
  total_categories: 0,
  total_tags: 0
})
const categoryDist = ref<CategoryDistribution[]>([])
const topBookmarks = ref<TopBookmark[]>([])
const creationTrend = ref<HeatmapData[]>([])
const tagUsage = ref<TagUsageStat[]>([])
const trendDays = ref(30)

// 趋势图配置
const trendChartOption = computed(() => ({
  tooltip: {
    trigger: 'axis',
    backgroundColor: 'rgba(0, 0, 0, 0.8)',
    borderColor: '#667eea',
    textStyle: { color: '#fff' }
  },
  grid: {
    left: '3%',
    right: '4%',
    bottom: '3%',
    containLabel: true
  },
  xAxis: {
    type: 'category',
    boundaryGap: false,
    data: creationTrend.value.map(item => item.date.slice(5)),
    axisLine: { lineStyle: { color: '#e2e8f0' } },
    axisLabel: { color: '#64748b' }
  },
  yAxis: {
    type: 'value',
    axisLine: { lineStyle: { color: '#e2e8f0' } },
    axisLabel: { color: '#64748b' },
    splitLine: { lineStyle: { color: '#f1f5f9' } }
  },
  series: [{
    name: '新增收藏',
    type: 'line',
    smooth: true,
    symbol: 'circle',
    symbolSize: 8,
    sampling: 'average',
    itemStyle: {
      color: '#667eea'
    },
    areaStyle: {
      color: {
        type: 'linear',
        x: 0,
        y: 0,
        x2: 0,
        y2: 1,
        colorStops: [
          { offset: 0, color: 'rgba(102, 126, 234, 0.3)' },
          { offset: 1, color: 'rgba(102, 126, 234, 0.05)' }
        ]
      }
    },
    data: creationTrend.value.map(item => item.count)
  }]
}))

// 分类饼图配置
const categoryPieOption = computed(() => ({
  tooltip: {
    trigger: 'item',
    formatter: '{b}: {c} ({d}%)',
    backgroundColor: 'rgba(0, 0, 0, 0.8)',
    borderColor: '#667eea',
    textStyle: { color: '#fff' }
  },
  legend: {
    orient: 'vertical',
    right: 10,
    top: 'center',
    textStyle: { color: '#64748b' }
  },
  series: [{
    name: '分类分布',
    type: 'pie',
    radius: ['40%', '70%'],
    center: ['35%', '50%'],
    avoidLabelOverlap: false,
    itemStyle: {
      borderRadius: 10,
      borderColor: '#fff',
      borderWidth: 2
    },
    label: {
      show: false,
      position: 'center'
    },
    emphasis: {
      label: {
        show: true,
        fontSize: 18,
        fontWeight: 'bold',
        color: '#1e293b'
      }
    },
    labelLine: { show: false },
    data: categoryDist.value.map(item => ({
      name: item.category_name,
      value: item.count
    }))
  }]
}))

// 标签柱状图配置
const tagBarOption = computed(() => ({
  tooltip: {
    trigger: 'axis',
    axisPointer: { type: 'shadow' },
    backgroundColor: 'rgba(0, 0, 0, 0.8)',
    borderColor: '#667eea',
    textStyle: { color: '#fff' }
  },
  grid: {
    left: '3%',
    right: '4%',
    bottom: '3%',
    containLabel: true
  },
  xAxis: {
    type: 'value',
    axisLine: { lineStyle: { color: '#e2e8f0' } },
    axisLabel: { color: '#64748b' },
    splitLine: { lineStyle: { color: '#f1f5f9' } }
  },
  yAxis: {
    type: 'category',
    data: [...tagUsage.value].reverse().map(tag => tag.tag_name),
    axisLine: { lineStyle: { color: '#e2e8f0' } },
    axisLabel: { color: '#64748b' }
  },
  series: [{
    name: '使用次数',
    type: 'bar',
    data: [...tagUsage.value].reverse().map(tag => tag.usage_count),
    itemStyle: {
      color: {
        type: 'linear',
        x: 0,
        y: 0,
        x2: 1,
        y2: 0,
        colorStops: [
          { offset: 0, color: '#667eea' },
          { offset: 1, color: '#764ba2' }
        ]
      },
      borderRadius: [0, 4, 4, 0]
    }
  }]
}))

// 加载概览数据
const loadOverview = async () => {
  try {
    const data = await getStatisticsOverview()
    overview.value = data
  } catch (error) {
    console.error('加载概览数据失败:', error)
    ElMessage.error('加载概览数据失败')
  }
}

// 加载分类分布
const loadCategoryDistribution = async () => {
  try {
    const data = await getCategoryDistribution()
    categoryDist.value = data
  } catch (error) {
    console.error('加载分类分布失败:', error)
  }
}

// 加载热门书签
const loadTopBookmarks = async () => {
  try {
    const data = await getTopBookmarks(10)
    topBookmarks.value = data
  } catch (error) {
    console.error('加载热门书签失败:', error)
  }
}

// 加载创建趋势
const loadCreationTrend = async () => {
  try {
    const data = await getCreationTrend(trendDays.value)
    creationTrend.value = data
  } catch (error) {
    console.error('加载创建趋势失败:', error)
  }
}

// 加载标签统计
const loadTagUsage = async () => {
  try {
    const data = await getTagUsageStats(15)
    tagUsage.value = data
  } catch (error) {
    console.error('加载标签统计失败:', error)
  }
}

// 打开书签链接
const openBookmark = (url: string) => {
  window.open(url, '_blank')
}

// 截断URL显示
const truncateUrl = (url: string, maxLength: number = 40) => {
  if (url.length <= maxLength) return url
  return url.substring(0, maxLength) + '...'
}

// 初始化加载所有数据
const initStats = async () => {
  loading.value = true
  try {
    await Promise.all([
      loadOverview(),
      loadCategoryDistribution(),
      loadTopBookmarks(),
      loadCreationTrend(),
      loadTagUsage()
    ])
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  initStats()
})
</script>

<style scoped>
.stats-view {
  min-height: 100vh;
  padding: 20px;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
}

.stats-header {
  text-align: center;
  margin-bottom: 30px;
}

.stats-header h1 {
  font-size: 36px;
  color: #1e293b;
  margin: 0 0 10px 0;
  font-weight: 700;
}

.subtitle {
  font-size: 16px;
  color: #64748b;
  margin: 0;
}

.loading-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.stats-content {
  max-width: 1400px;
  margin: 0 auto;
}

/* 概览卡片 */
.overview-cards {
  margin-bottom: 20px;
}

.stat-card {
  display: flex;
  align-items: center;
  padding: 20px;
  border-radius: 12px;
  transition: all 0.3s ease;
  cursor: pointer;
}

.stat-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.15);
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  margin-right: 15px;
  flex-shrink: 0;
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: #1e293b;
  line-height: 1;
  margin-bottom: 5px;
}

.stat-label {
  font-size: 14px;
  color: #64748b;
}

/* 图表区域 */
.charts-section {
  margin-bottom: 20px;
}

.chart-card {
  border-radius: 12px;
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
  color: #1e293b;
}

.chart {
  height: 350px;
  width: 100%;
}

/* 热门书签列表 */
.top-bookmarks-list {
  max-height: 350px;
  overflow-y: auto;
}

.bookmark-item {
  display: flex;
  align-items: center;
  padding: 12px;
  margin-bottom: 8px;
  background: #f8fafc;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.bookmark-item:hover {
  background: #e2e8f0;
  transform: translateX(5px);
}

.rank-badge {
  width: 30px;
  height: 30px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 14px;
  margin-right: 12px;
  flex-shrink: 0;
  color: white;
}

.rank-1 {
  background: linear-gradient(135deg, #ffd700 0%, #ffed4e 100%);
  color: #856404;
}

.rank-2 {
  background: linear-gradient(135deg, #c0c0c0 0%, #e8e8e8 100%);
  color: #5a6268;
}

.rank-3 {
  background: linear-gradient(135deg, #cd7f32 0%, #daa520 100%);
  color: #5c3a1e;
}

.rank-4, .rank-5, .rank-6, .rank-7, .rank-8, .rank-9, .rank-10 {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.bookmark-info {
  flex: 1;
  min-width: 0;
}

.bookmark-title {
  font-size: 14px;
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 4px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.bookmark-url {
  font-size: 12px;
  color: #64748b;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.bookmark-clicks {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 14px;
  font-weight: 600;
  color: #667eea;
  margin-left: 10px;
  flex-shrink: 0;
}

/* 滚动条样式 */
.top-bookmarks-list::-webkit-scrollbar {
  width: 6px;
}

.top-bookmarks-list::-webkit-scrollbar-track {
  background: #f1f5f9;
  border-radius: 3px;
}

.top-bookmarks-list::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 3px;
}

.top-bookmarks-list::-webkit-scrollbar-thumb:hover {
  background: #94a3b8;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .stats-header h1 {
    font-size: 28px;
  }

  .stat-value {
    font-size: 24px;
  }

  .chart {
    height: 300px;
  }
}
</style>
