<template>
  <div class="home-view">
    <!-- Hero 区域 -->
    <section class="hero">
      <h1>收藏不止于链接，更有洞察</h1>
      <p class="subtitle">发现、整理、分享你喜爱的网址</p>

      <div class="tag-cloud">
        <el-tag v-for="tag in popularTags" :key="tag" class="tag-item">
          # {{ tag }}
        </el-tag>
      </div>
    </section>

    <!-- 功能特性 -->
    <div class="features">
      <el-card class="feature-card" shadow="hover">
        <el-icon :size="48" color="#6366f1"><Collection /></el-icon>
        <h3>智能收藏</h3>
        <p>高效管理你的网址收藏，支持分类和标签</p>
      </el-card>

      <el-card class="feature-card" shadow="hover">
        <el-icon :size="48" color="#818cf8"><Share /></el-icon>
        <h3>社区分享</h3>
        <p>发现和分享优质内容，与志同道合的人交流</p>
      </el-card>

      <el-card class="feature-card" shadow="hover">
        <el-icon :size="48" color="#a78bfa"><DataAnalysis /></el-icon>
        <h3>数据洞察</h3>
        <p>可视化分析收藏习惯，了解你的兴趣偏好</p>
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import {
  Collection,
  Share,
  DataAnalysis,
} from '@element-plus/icons-vue'

// 热门标签（示例数据，后续可从 API 获取）
const popularTags = ref([
  '技术',
  '设计',
  '效率工具',
  'AI',
  '阅读',
  '前端',
  '后端',
  '开源',
  '产品',
  '学习',
])
</script>

<style scoped>
.home-view {
  min-height: calc(100vh - 73px);
}

/* ========== Hero 区域 ========== */
.hero {
  text-align: center;
  padding: 80px 40px 60px;
  background: linear-gradient(180deg, rgba(99, 102, 241, 0.1) 0%, transparent 100%);
}

.hero h1 {
  font-size: 48px;
  font-weight: 700;
  margin-bottom: 12px;
  background: linear-gradient(135deg, #818cf8, #a78bfa, #c084fc);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.subtitle {
  font-size: 20px;
  color: #94a3b8;
  margin-bottom: 32px;
}

.tag-cloud {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 8px;
  max-width: 800px;
  margin: 0 auto;
}

.tag-item {
  cursor: pointer;
  padding: 6px 16px;
  font-size: 14px;
  background: rgba(99, 102, 241, 0.15);
  border: 1px solid rgba(99, 102, 241, 0.3);
  color: #818cf8;
  transition: all 0.2s;
}

.tag-item:hover {
  background: rgba(99, 102, 241, 0.3);
  transform: translateY(-2px);
}

/* ========== 功能特性 ========== */
.features {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 24px;
  padding: 0 40px 60px;
  max-width: 1200px;
  margin: 0 auto;
}

.feature-card {
  text-align: center;
  padding: 40px 24px;
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(12px);
  transition: all 0.3s;
}

.feature-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.3);
  border-color: rgba(99, 102, 241, 0.3);
}

.feature-card h3 {
  font-size: 22px;
  margin: 20px 0 12px;
  color: #e2e8f0;
}

.feature-card p {
  font-size: 15px;
  color: #94a3b8;
  line-height: 1.6;
}

/* ========== 响应式 ========== */
@media (max-width: 768px) {
  .hero {
    padding: 60px 20px 40px;
  }

  .hero h1 {
    font-size: 32px;
  }

  .subtitle {
    font-size: 16px;
  }

  .features {
    grid-template-columns: 1fr;
    padding: 0 20px 40px;
  }
}
</style>
