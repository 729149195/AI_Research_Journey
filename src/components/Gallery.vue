<template>
  <div class="gallery">
    <div class="gallery-header">
      <h2>🎭 画廊</h2>
      <p>欣赏小朋友们创作的精彩故事图片！</p>
      <!-- 搜索框 -->
      <div class="search-box">
        <input 
          v-model="searchQuery" 
          type="text" 
          placeholder="搜索姓名或风格..." 
          class="search-input"
          @input="filterGallery"
        />
        <div class="search-icon">🔍</div>
      </div>
    </div>

    <!-- 加载状态 -->
    <div v-if="isLoading" class="loading-container">
      <el-skeleton :rows="3" animated />
    </div>

    <!-- 画廊内容 -->
    <div v-else class="gallery-waterfall">
      <div 
        v-for="(set, index) in filteredGallery" 
        :key="set.id"
        class="gallery-set"
      >
        <div class="set-info">
          <div class="set-meta">
            <h3>{{ set.userName }}的故事</h3>
            <span class="set-date">{{ set.createdAt }}</span>
          </div>
          <div class="set-style">{{ set.style }}</div>
        </div>
        <!-- 9宫格图片 -->
        <div class="images-grid-9">
          <div 
            v-for="(image, index) in set.images" 
            :key="index"
            class="image-item"
            @click="previewImage(image)"
          >
            <img :src="image" :alt="`图片${index + 1}`" />
            <div class="image-overlay">
              <el-icon class="preview-icon"><ZoomIn /></el-icon>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 空状态 -->
    <div v-if="!isLoading && filteredGallery.length === 0 && searchQuery" class="empty-state">
      <el-icon class="empty-icon"><Picture /></el-icon>
      <h3>没有找到相关内容</h3>
      <p>试试搜索其他关键词吧！</p>
    </div>
    
    <!-- 无数据状态 -->
    <div v-if="!isLoading && galleryImages.length === 0" class="empty-state">
      <el-icon class="empty-icon"><Picture /></el-icon>
      <h3>暂无故事</h3>
      <p>快来上面创作你的第一个故事吧！</p>
    </div>

    <!-- 自定义精致图片预览弹出框 -->
    <div v-if="isPreviewVisible" class="custom-preview-overlay" @click="closePreview">
      <div class="custom-preview-container" @click.stop>
        <!-- 装饰背景 -->
        <div class="preview-decorations">
          <div class="decoration-star star-1">✦</div>
          <div class="decoration-star star-2">✧</div>
          <div class="decoration-star star-3">✦</div>
          <div class="decoration-star star-4">✧</div>
          <div class="decoration-circle circle-1"></div>
          <div class="decoration-circle circle-2"></div>
          <div class="magic-sparkles">
            <div class="sparkle sparkle-1">✨</div>
            <div class="sparkle sparkle-2">✨</div>
            <div class="sparkle sparkle-3">✨</div>
            <div class="sparkle sparkle-4">✨</div>
            <div class="sparkle sparkle-5">✨</div>
          </div>
        </div>

        <!-- 关闭按钮 -->
        <div class="preview-close-btn" @click="closePreview">
          <el-icon>
            <Close />
          </el-icon>
        </div>

        <!-- 标题区域 -->
        <div class="preview-header">
          <h3 class="preview-title">
            <span class="title-icon">🖼️</span>
            <span class="title-text">图片预览</span>
          </h3>
        </div>

        <!-- 图片内容区域 -->
        <div class="preview-content">
          <div class="image-wrapper" v-if="selectedImage">
            <div class="image-glow"></div>
            <img :src="selectedImage" alt="预览" class="preview-main-image" />
            <div class="image-border-decoration">
              <div class="corner corner-tl"></div>
              <div class="corner corner-tr"></div>
              <div class="corner corner-bl"></div>
              <div class="corner corner-br"></div>
            </div>
          </div>
        </div>

        <!-- 底部操作区域 -->
        <div class="preview-actions">
          <button class="action-btn download-btn" @click="downloadCurrentImage">
            <el-icon><Download /></el-icon>
            <span>下载图片</span>
          </button>
          <button class="action-btn share-btn" @click="shareCurrentImage">
            <el-icon><Share /></el-icon>
            <span>分享图片</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { ZoomIn, Picture, Close, Download, Share } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

// 画廊图片数据
const galleryImages = ref([])
const filteredGallery = ref([])
const searchQuery = ref('')
const isLoading = ref(false)
const selectedImage = ref(null)
const isPreviewVisible = ref(false)

// 模拟历史数据
const mockHistoryData = [
  {
    id: 1,
    images: Array(9).fill(null).map((_, index) => 
      `https://picsum.photos/300/300?random=${1000 + index}`
    ),
    createdAt: '2024-01-15',
    userName: 'Alice',
    style: '卡通风格'
  },
  {
    id: 2,
    images: Array(9).fill(null).map((_, index) => 
      `https://picsum.photos/300/300?random=${2000 + index}`
    ),
    createdAt: '2024-01-14',
    userName: 'Bob',
    style: '动漫风格'
  },
  {
    id: 3,
    images: Array(9).fill(null).map((_, index) => 
      `https://picsum.photos/300/300?random=${3000 + index}`
    ),
    createdAt: '2024-01-13',
    userName: 'Charlie',
    style: '奇幻风格'
  },
  {
    id: 4,
    images: Array(9).fill(null).map((_, index) => 
      `https://picsum.photos/300/300?random=${4000 + index}`
    ),
    createdAt: '2024-01-12',
    userName: 'Daisy',
    style: '水彩风格'
  },
  {
    id: 5,
    images: Array(9).fill(null).map((_, index) => 
      `https://picsum.photos/300/300?random=${5000 + index}`
    ),
    createdAt: '2024-01-11',
    userName: 'Emma',
    style: '油画风格'
  },
  {
    id: 6,
    images: Array(9).fill(null).map((_, index) => 
      `https://picsum.photos/300/300?random=${6000 + index}`
    ),
    createdAt: '2024-01-10',
    userName: 'Frank',
    style: '卡通风格'
  },
  {
    id: 7,
    images: Array(9).fill(null).map((_, index) => 
      `https://picsum.photos/300/300?random=${7000 + index}`
    ),
    createdAt: '2024-01-09',
    userName: 'Grace',
    style: '写实风格'
  },
  {
    id: 8,
    images: Array(9).fill(null).map((_, index) => 
      `https://picsum.photos/300/300?random=${8000 + index}`
    ),
    createdAt: '2024-01-08',
    userName: 'Henry',
    style: '动漫风格'
  }
]

// 加载画廊数据
const loadGalleryData = async () => {
  isLoading.value = true
  try {
    // 模拟API调用
    await new Promise(resolve => setTimeout(resolve, 1000))
    galleryImages.value = mockHistoryData
    filteredGallery.value = galleryImages.value
  } catch (error) {
    console.error('加载画廊数据失败:', error)
  } finally {
    isLoading.value = false
  }
}

// 搜索过滤功能
const filterGallery = () => {
  if (!searchQuery.value.trim()) {
    filteredGallery.value = galleryImages.value
    return
  }
  
  const query = searchQuery.value.toLowerCase()
  filteredGallery.value = galleryImages.value.filter(item => 
    item.userName.toLowerCase().includes(query) || 
    item.style.toLowerCase().includes(query)
  )
}

// 预览图片
const previewImage = (image) => {
  selectedImage.value = image
  isPreviewVisible.value = true
}

// 下载图片集
const downloadImageSet = (images, setId) => {
  images.forEach((url, index) => {
    const link = document.createElement('a')
    link.href = url
    link.download = `画廊_${setId}_${index + 1}.jpg`
    link.click()
  })
}

// 关闭预览
const closePreview = () => {
  selectedImage.value = null
  isPreviewVisible.value = false
}

// ESC键关闭功能
const handleKeydown = (event) => {
  if (event.key === 'Escape' && isPreviewVisible.value) {
    closePreview()
  }
}

// 下载当前图片
const downloadCurrentImage = () => {
  if (selectedImage.value) {
    const link = document.createElement('a')
    link.href = selectedImage.value
    link.download = `画廊图片_${Date.now()}.jpg`
    link.click()
    
    // 提示用户
    ElMessage.success('图片下载开始！')
  }
}

// 分享当前图片
const shareCurrentImage = () => {
  if (selectedImage.value) {
    // 检查是否支持 Web Share API
    if (navigator.share) {
      navigator.share({
        title: '精彩的故事图片',
        text: '快来看看这张精彩的故事图片！',
        url: selectedImage.value
      }).catch((error) => {
        console.log('分享失败:', error)
        fallbackShare()
      })
    } else {
      fallbackShare()
    }
  }
}

// 备用分享方案
const fallbackShare = () => {
  // 复制链接到剪贴板
  if (navigator.clipboard && selectedImage.value) {
    navigator.clipboard.writeText(selectedImage.value).then(() => {
      ElMessage.success('图片链接已复制到剪贴板！')
    }).catch(() => {
      ElMessage.info('分享功能即将上线！')
    })
  } else {
    ElMessage.info('分享功能即将上线！')
  }
}

onMounted(() => {
  loadGalleryData()
  // 添加键盘事件监听
  document.addEventListener('keydown', handleKeydown)
})

// 组件卸载时清理事件监听
onUnmounted(() => {
  document.removeEventListener('keydown', handleKeydown)
})
</script>

<style scoped>
/* 全局字体设置 - 使用本地64_fonts.ttf字体与主页面保持一致 */
.gallery {
  background: #fff8dc;
  border-radius: 25px;
  padding: 30px;
  border: 6px solid #f7a985;
  box-shadow: 0px 10px #ff6347;
  max-width: 1800px;
  margin: 0 auto;
  position: relative;
  overflow: hidden;
  /* 统一使用本地可爱字体：64_fonts.ttf */
  font-family: 'CuteFont64', 'Comic Sans MS', 'Microsoft YaHei', '微软雅黑', cursive, sans-serif;
  font-size: 16px;
  line-height: 1.8;
  font-weight: 400;
}

/* Gallery 内部动态装饰 */
.gallery::before {
  content: '';
  position: absolute;
  top: -50px;
  right: -50px;
  width: 100px;
  height: 100px;
  background: radial-gradient(circle, rgba(255, 215, 0, 0.3) 0%, transparent 70%);
  border-radius: 50%;
  animation: galleryGlow 4s ease-in-out infinite alternate;
  pointer-events: none;
}

.gallery::after {
  content: '';
  position: absolute;
  bottom: -30px;
  left: -30px;
  width: 80px;
  height: 80px;
  background: radial-gradient(circle, rgba(255, 182, 193, 0.3) 0%, transparent 70%);
  border-radius: 50%;
  animation: galleryGlow 5s ease-in-out infinite alternate reverse;
  pointer-events: none;
}

@keyframes galleryGlow {
  0% {
    transform: scale(1) rotate(0deg);
    opacity: 0.3;
  }
  100% {
    transform: scale(1.5) rotate(180deg);
    opacity: 0.6;
  }
}

/* 全局字体继承 */
.gallery *,
.gallery *::before,
.gallery *::after {
  font-family: inherit;
  font-weight: inherit;
}

.gallery-header {
  text-align: center;
  margin-bottom: 20px;
}

.gallery-header h2 {
  color: #8b4513;
  font-size: 2.6rem;
  margin: 0 0 10px 0;
  font-weight: 400;
  text-shadow: 2px 2px 0px #ffd700;
  letter-spacing: 3px;
  font-family: 'CuteFont64', cursive;
}

.gallery-header p {
  color: #8b4513;
  font-size: 1.3rem;
  margin: 0 0 20px 0;
  font-weight: 500;
  text-shadow: 1px 1px 0px #ffd700;
  letter-spacing: 2px;
  font-family: 'CuteFont64', cursive;
}

/* 搜索框样式 */
.search-box {
  position: relative;
  max-width: 400px;
  margin: 0 auto;
}

.search-input {
  width: 100%;
  padding: 12px 50px 12px 20px;
  border: 4px solid #f7a985;
  border-radius: 25px;
  background: #fff8dc;
  color: #8b4513;
  font-size: 1.1rem;
  font-weight: 700;
  outline: none;
  transition: all 0.3s ease;
  letter-spacing: 0.5px;
  box-shadow: inset 0px 2px 4px rgba(0, 0, 0, 0.1);
}

.search-input:focus {
  border-color: #ffb347;
  background: #fffacd;
  box-shadow: 0 0 0 4px #ffe4b5, 0 2px 6px #ffd700;
}

.search-input::placeholder {
  color: #cd853f;
  font-weight: 600;
}

.search-icon {
  position: absolute;
  right: 15px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 1.2rem;
  color: #ff8c42;
  pointer-events: none;
}

.loading-container {
  padding: 20px 0;
}

.gallery-waterfall {
  column-count: 3;
  column-gap: 25px;
  column-fill: balance;
}

.gallery-set {
  border: 4px solid #f7a985;
  border-radius: 20px;
  padding: 20px;
  background: #fffacd;
  transition: all 0.3s cubic-bezier(.4,2,.6,1);
  box-shadow: 0px 6px #ff6347;
  margin-bottom: 25px;
  break-inside: avoid;
  page-break-inside: avoid;
  -webkit-column-break-inside: avoid;
  position: relative;
  animation: galleryCardFloat 6s ease-in-out infinite;
}

.gallery-set:nth-child(even) {
  animation-delay: -3s;
}

.gallery-set:nth-child(3n) {
  animation-delay: -1.5s;
}


.gallery-set:hover::before {
  opacity: 0.7;
}

@keyframes galleryCardFloat {
  0%, 100% {
    transform: translateY(0px) rotate(0deg);
  }
  25% {
    transform: translateY(-2px) rotate(0.5deg);
  }
  50% {
    transform: translateY(0px) rotate(0deg);
  }
  75% {
    transform: translateY(-1px) rotate(-0.5deg);
  }
}

@keyframes gradientShift {
  0% {
    background-position: 0% 50%;
  }
  50% {
    background-position: 100% 50%;
  }
  100% {
    background-position: 0% 50%;
  }
}

.set-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 15px;
}

.set-meta h3 {
  color: #8b4513;
  margin: 0 0 5px 0;
  font-size: 1.4rem;
  font-weight: 800;
  text-shadow: 1px 1px 0px #ffd700;
  letter-spacing: 0.5px;
}

.set-date {
  color: #cd853f;
  font-size: 1rem;
  font-weight: 700;
}

.set-style {
  background: #ff8c42;
  color: #fff;
  padding: 8px 16px;
  border-radius: 20px;
  font-size: 1rem;
  font-weight: 800;
  border: 3px solid #f7a985;
  box-shadow: 0px 3px #ff6347;
  text-shadow: 1px 1px 0px #d2691e;
  letter-spacing: 0.5px;
}

.images-grid-9 {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  grid-template-rows: repeat(3, 1fr);
  gap: 8px;
  margin-top: 10px;
}

.image-item {
  position: relative;
  aspect-ratio: 1;
  border-radius: 15px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.15s cubic-bezier(.4,2,.6,1);
  background: #fff;
  border: 3px solid #f7a985;
  box-shadow: 0px 3px #ff6347;
}

.image-item img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.image-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 140, 66, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.image-item:hover .image-overlay {
  opacity: 1;
}

.preview-icon {
  color: #fff;
  font-size: 2.2rem;
  filter: drop-shadow(0 2px 0 #ff6347);
  font-weight: 800;
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: #8b4513;
}

.empty-icon {
  font-size: 4.5rem;
  color: #ff8c42;
  margin-bottom: 20px;
  filter: drop-shadow(0 2px 0 #ffd700);
}

.empty-state h3 {
  font-size: 1.8rem;
  margin: 0 0 10px 0;
  font-weight: 800;
  text-shadow: 1px 1px 0px #ffd700;
  letter-spacing: 0.5px;
}

.empty-state p {
  font-size: 1.2rem;
  margin: 0;
  font-weight: 700;
  text-shadow: 1px 1px 0px #ffd700;
  letter-spacing: 0.5px;
}

/* ========== 自定义精致图片预览弹出框样式 ========== */

.custom-preview-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.85);
  backdrop-filter: blur(8px);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
  animation: overlayFadeIn 0.3s ease-out;
  cursor: pointer;
}

@keyframes overlayFadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

.custom-preview-container {
  background: linear-gradient(135deg, #fff8dc, #fffacd);
  border: 6px solid #f7a985;
  border-radius: 30px;
  padding: 35px;
  max-width: 90vw;
  max-height: 90vh;
  overflow: auto;
  position: relative;
  box-shadow: 
    0px 20px 40px rgba(255, 99, 71, 0.4),
    0px 10px 20px rgba(255, 140, 66, 0.3),
    inset 0px 2px 0px rgba(255, 255, 255, 0.6);
  animation: containerSlideIn 0.4s cubic-bezier(.4, 2, .6, 1);
  cursor: default;
  /* 统一使用本地可爱字体：64_fonts.ttf */
  font-family: 'CuteFont64', 'Comic Sans MS', 'Microsoft YaHei', '微软雅黑', cursive, sans-serif;
}

@keyframes containerSlideIn {
  from {
    opacity: 0;
    transform: scale(0.7) translateY(-50px);
  }
  to {
    opacity: 1;
    transform: scale(1) translateY(0);
  }
}

/* 装饰背景元素 */
.preview-decorations {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  overflow: hidden;
  border-radius: 24px;
}

.decoration-star {
  position: absolute;
  font-size: 1.5rem;
  color: rgba(255, 215, 0, 0.7);
  animation: starTwinkle 3s ease-in-out infinite;
  text-shadow: 0 0 10px rgba(255, 215, 0, 0.5);
}

.star-1 {
  top: 15%;
  left: 10%;
  animation-delay: 0s;
}

.star-2 {
  top: 20%;
  right: 15%;
  animation-delay: -1s;
}

.star-3 {
  bottom: 25%;
  left: 15%;
  animation-delay: -2s;
}

.star-4 {
  bottom: 15%;
  right: 10%;
  animation-delay: -0.5s;
}

.decoration-circle {
  position: absolute;
  border-radius: 50%;
  background: linear-gradient(45deg, rgba(255, 215, 0, 0.3), rgba(255, 140, 66, 0.2));
  animation: decorationFloat 6s ease-in-out infinite;
}

.circle-1 {
  width: 40px;
  height: 40px;
  top: 10%;
  left: 5%;
  animation-delay: 0s;
}

.circle-2 {
  width: 30px;
  height: 30px;
  bottom: 20%;
  right: 8%;
  animation-delay: -3s;
}

/* 闪烁星光效果 */
.magic-sparkles {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
}

.sparkle {
  position: absolute;
  font-size: 0.8rem;
  color: rgba(255, 215, 0, 0.6);
  animation: sparkleAnimation 4s ease-in-out infinite;
  text-shadow: 0 0 6px rgba(255, 215, 0, 0.4);
}

.sparkle-1 {
  top: 12%;
  left: 25%;
  animation-delay: 0s;
}

.sparkle-2 {
  top: 35%;
  right: 20%;
  animation-delay: -1s;
}

.sparkle-3 {
  bottom: 30%;
  left: 30%;
  animation-delay: -2s;
}

.sparkle-4 {
  bottom: 12%;
  right: 35%;
  animation-delay: -3s;
}

.sparkle-5 {
  top: 50%;
  left: 8%;
  animation-delay: -1.5s;
}

/* 动画关键帧 */
@keyframes starTwinkle {
  0%, 100% {
    opacity: 0.3;
    transform: scale(1) rotate(0deg);
  }
  50% {
    opacity: 1;
    transform: scale(1.2) rotate(180deg);
  }
}

@keyframes decorationFloat {
  0%, 100% {
    transform: translateY(0px) rotate(0deg);
  }
  50% {
    transform: translateY(-15px) rotate(180deg);
  }
}

@keyframes sparkleAnimation {
  0%, 100% {
    opacity: 0;
    transform: scale(0.5) rotate(0deg);
  }
  25% {
    opacity: 0.8;
    transform: scale(1.2) rotate(90deg);
  }
  50% {
    opacity: 1;
    transform: scale(1) rotate(180deg);
  }
  75% {
    opacity: 0.8;
    transform: scale(1.3) rotate(270deg);
  }
}

/* 关闭按钮 */
.preview-close-btn {
  position: absolute;
  top: 15px;
  right: 15px;
  width: 45px;
  height: 45px;
  background: linear-gradient(135deg, #ff6347, #ff8c42);
  border: 4px solid #f7a985;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: #fff;
  font-size: 1.2rem;
  font-weight: 800;
  box-shadow: 
    0px 6px 12px rgba(255, 99, 71, 0.4),
    0px 3px 6px rgba(255, 140, 66, 0.3),
    inset 0px 2px 0px rgba(255, 255, 255, 0.3);
  transition: all 0.3s cubic-bezier(.4, 2, .6, 1);
  z-index: 10;
}

.preview-close-btn:hover {
  background: linear-gradient(135deg, #ff4500, #ff6347);
  transform: translateY(-3px) scale(1.1);
  box-shadow: 
    0px 8px 16px rgba(255, 99, 71, 0.5),
    0px 4px 8px rgba(255, 140, 66, 0.4),
    inset 0px 2px 0px rgba(255, 255, 255, 0.4);
}

.preview-close-btn:active {
  transform: translateY(-1px) scale(1.05);
  box-shadow: 
    0px 4px 8px rgba(255, 99, 71, 0.3),
    inset 0px 1px 0px rgba(255, 255, 255, 0.2);
}

/* 标题区域 */
.preview-header {
  text-align: center;
  margin-bottom: 25px;
  position: relative;
  z-index: 2;
}

.preview-title {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  font-size: 2rem;
  font-weight: 800;
  color: #8b4513;
  text-shadow: 
    2px 2px 0px #ffd700,
    4px 4px 0px #fff8dc,
    0 0 15px rgba(255, 215, 0, 0.6);
  letter-spacing: 1px;
  margin: 0;
  animation: titleGlow 3s ease-in-out infinite;
}

.title-icon {
  font-size: 1.8rem;
  filter: drop-shadow(0 0 10px rgba(255, 140, 66, 0.6));
  animation: iconBounce 3s ease-in-out infinite;
}

.title-text {
  animation: textFloat 3s ease-in-out infinite;
}

@keyframes titleGlow {
  0%, 100% {
    text-shadow: 
      2px 2px 0px #ffd700,
      4px 4px 0px #fff8dc,
      0 0 15px rgba(255, 215, 0, 0.6);
  }
  50% {
    text-shadow: 
      2px 2px 0px #ffd700,
      4px 4px 0px #fff8dc,
      0 0 25px rgba(255, 215, 0, 1);
  }
}

@keyframes iconBounce {
  0%, 100% {
    transform: translateY(0px) rotate(0deg);
  }
  50% {
    transform: translateY(-5px) rotate(10deg);
  }
}

@keyframes textFloat {
  0%, 100% {
    transform: translateY(0px);
  }
  50% {
    transform: translateY(-3px);
  }
}

/* 图片内容区域 */
.preview-content {
  text-align: center;
  position: relative;
  z-index: 2;
  margin-bottom: 25px;
}

.image-wrapper {
  position: relative;
  display: inline-block;
  animation: imageAppear 0.5s ease-out 0.2s both;
}

@keyframes imageAppear {
  from {
    opacity: 0;
    transform: scale(0.8) translateY(20px);
  }
  to {
    opacity: 1;
    transform: scale(1) translateY(0);
  }
}

.image-glow {
  position: absolute;
  top: -10px;
  left: -10px;
  right: -10px;
  bottom: -10px;
  background: radial-gradient(ellipse, rgba(255, 215, 0, 0.4) 0%, transparent 70%);
  border-radius: 25px;
  animation: glowPulse 4s ease-in-out infinite;
  pointer-events: none;
}

@keyframes glowPulse {
  0%, 100% {
    opacity: 0.4;
    transform: scale(1);
  }
  50% {
    opacity: 0.8;
    transform: scale(1.05);
  }
}

.preview-main-image {
  max-width: 100%;
  max-height: 70vh;
  min-height: 200px;
  border-radius: 20px;
  border: 6px solid #f7a985;
  box-shadow: 
    0px 15px 30px rgba(255, 99, 71, 0.4),
    0px 8px 15px rgba(255, 140, 66, 0.3),
    inset 0px 2px 0px rgba(255, 255, 255, 0.3);
  transition: all 0.3s ease;
  object-fit: contain;
  background: #fff;
}

.preview-main-image:hover {
  transform: scale(1.02);
  box-shadow: 
    0px 20px 40px rgba(255, 99, 71, 0.5),
    0px 10px 20px rgba(255, 140, 66, 0.4),
    inset 0px 2px 0px rgba(255, 255, 255, 0.4);
}

/* 图片装饰边框 */
.image-border-decoration {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  border-radius: 20px;
  overflow: hidden;
}

.corner {
  position: absolute;
  width: 25px;
  height: 25px;
  background: rgba(255, 215, 0, 0.8);
  border-radius: 50%;
  animation: cornerSpin 6s linear infinite;
  box-shadow: 
    0 0 10px rgba(255, 215, 0, 0.6),
    inset 0 2px 0 rgba(255, 255, 255, 0.3);
}

.corner-tl {
  top: -12px;
  left: -12px;
  animation-delay: 0s;
}

.corner-tr {
  top: -12px;
  right: -12px;
  animation-delay: -1.5s;
}

.corner-bl {
  bottom: -12px;
  left: -12px;
  animation-delay: -3s;
}

.corner-br {
  bottom: -12px;
  right: -12px;
  animation-delay: -4.5s;
}

@keyframes cornerSpin {
  0% {
    transform: rotate(0deg) scale(1);
    opacity: 0.7;
  }
  50% {
    transform: rotate(180deg) scale(1.2);
    opacity: 1;
  }
  100% {
    transform: rotate(360deg) scale(1);
    opacity: 0.7;
  }
}

/* 底部操作区域 */
.preview-actions {
  text-align: center;
  margin-top: 25px;
  position: relative;
  z-index: 2;
  display: flex;
  justify-content: center;
  gap: 20px;
  flex-wrap: wrap;
}

.action-btn {
  background: linear-gradient(135deg, #ffb347, #ffd700);
  border: 4px solid #f7a985;
  border-radius: 25px;
  padding: 12px 24px;
  font-size: 1.1rem;
  font-weight: 800;
  color: #8b4513;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.3s cubic-bezier(.4, 2, .6, 1);
  box-shadow: 
    0px 6px 12px rgba(255, 179, 71, 0.4),
    0px 3px 6px rgba(255, 215, 0, 0.3),
    inset 0px 2px 0px rgba(255, 255, 255, 0.6);
  text-shadow: 1px 1px 0px rgba(255, 255, 255, 0.5);
  letter-spacing: 0.5px;
  position: relative;
  overflow: hidden;
  min-width: 140px;
  justify-content: center;
}

.action-btn::before {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  width: 0;
  height: 0;
  background: rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  transform: translate(-50%, -50%);
  transition: all 0.3s ease;
}

.action-btn:hover::before {
  width: 100%;
  height: 100%;
}

.action-btn:hover {
  background: linear-gradient(135deg, #ffd700, #ffb347);
  transform: translateY(-3px) scale(1.05);
  box-shadow: 
    0px 8px 16px rgba(255, 179, 71, 0.5),
    0px 4px 8px rgba(255, 215, 0, 0.4),
    inset 0px 2px 0px rgba(255, 255, 255, 0.7);
}

.action-btn:active {
  transform: translateY(-1px) scale(1.02);
  box-shadow: 
    0px 4px 8px rgba(255, 179, 71, 0.3),
    inset 0px 1px 0px rgba(255, 255, 255, 0.4);
}

.download-btn .el-icon {
  font-size: 1.2rem;
  color: #8b4513;
  filter: drop-shadow(1px 1px 2px rgba(139, 69, 19, 0.3));
}

.share-btn {
  background: linear-gradient(135deg, #ff8c42, #ff6347);
  color: #fff;
  text-shadow: 1px 1px 2px rgba(139, 69, 19, 0.5);
}

.share-btn:hover {
  background: linear-gradient(135deg, #ff6347, #ff8c42);
}

.share-btn .el-icon {
  font-size: 1.2rem;
  color: #fff;
  filter: drop-shadow(1px 1px 2px rgba(139, 69, 19, 0.5));
}

/* 响应式设计 */
@media (max-width: 768px) {
  .custom-preview-container {
    padding: 20px;
    margin: 10px;
    max-width: 95vw;
    max-height: 95vh;
  }

  .preview-title {
    font-size: 1.6rem;
    gap: 8px;
  }

  .title-icon {
    font-size: 1.4rem;
  }

  .preview-main-image {
    max-height: 60vh;
    min-height: 150px;
  }

  .preview-actions {
    flex-direction: column;
    align-items: center;
    gap: 15px;
  }

  .action-btn {
    font-size: 1rem;
    padding: 10px 20px;
    min-width: 120px;
  }

  .preview-close-btn {
    width: 40px;
    height: 40px;
    top: 10px;
    right: 10px;
    font-size: 1rem;
  }

  /* 移动端装饰元素优化 */
  .decoration-star {
    font-size: 1.2rem;
  }

  .decoration-circle {
    opacity: 0.7;
  }

  .circle-1 {
    width: 30px;
    height: 30px;
  }

  .circle-2 {
    width: 25px;
    height: 25px;
  }

  .sparkle {
    font-size: 0.6rem;
  }
}

@media (max-width: 480px) {
  .custom-preview-container {
    padding: 15px;
    border-width: 4px;
  }

  .preview-title {
    font-size: 1.4rem;
  }

  .title-icon {
    font-size: 1.2rem;
  }

  .preview-main-image {
    max-height: 50vh;
    border-width: 4px;
  }

  .action-btn {
    font-size: 0.9rem;
    padding: 8px 16px;
    border-width: 3px;
  }

  .preview-close-btn {
    width: 35px;
    height: 35px;
    border-width: 3px;
  }
}

@media (max-width: 1600px) {
  .gallery {
    max-width: 1400px;
  }
}

@media (max-width: 1400px) {
  .gallery {
    max-width: 1200px;
  }
}

@media (max-width: 1200px) {
  .gallery-waterfall {
    column-count: 2;
    column-gap: 20px;
  }
}

@media (max-width: 900px) {
  .gallery-waterfall {
    column-count: 1;
    column-gap: 0;
  }
  
  .search-box {
    max-width: 100%;
  }
}
@media (max-width: 600px) {
  .images-grid-9 {
    grid-template-columns: repeat(3, 1fr);
    grid-template-rows: repeat(3, 1fr);
    gap: 4px;
  }
  .gallery {
    padding: 20px;
    border-width: 4px;
    box-shadow: 0px 6px #ff6347;
    font-size: 14px;
  }
  .gallery-set {
    border-width: 3px;
    box-shadow: 0px 4px #ff6347;
  }
  .image-item {
    border-width: 2px;
    box-shadow: 0px 2px #ff6347;
  }
  .gallery-header h2 {
    font-size: 1.8rem;
  }
  .gallery-header p {
    font-size: 1.1rem;
  }
  .set-meta h3 {
    font-size: 1.2rem;
  }
}

/* Element Plus 组件字体统一覆盖 */
:deep(.el-skeleton) {
  font-weight: 700;
}

:deep(.el-dialog) {
  font-weight: 700;
}

:deep(.el-dialog__title) {
  font-size: 1.4rem;
  font-weight: 800;
  color: #8b4513;
  letter-spacing: 0.5px;
}

:deep(.el-icon) {
  font-weight: 800;
}
</style> 