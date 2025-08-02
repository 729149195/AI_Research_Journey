<template>
    <div class="style-transfer">
        <!-- 动态背景元素 -->
        <div class="background-animations">
            <!-- 动态波浪 -->
            <div class="waves">
                <div class="wave wave1"></div>
                <div class="wave wave2"></div>
                <div class="wave wave3"></div>
            </div>

            <!-- 漂浮的气泡 -->
            <div class="bubbles">
                <div class="bubble bubble1" @click.stop="burstBubble"></div>
                <div class="bubble bubble2" @click.stop="burstBubble"></div>
                <div class="bubble bubble3" @click.stop="burstBubble"></div>
                <div class="bubble bubble4" @click.stop="burstBubble"></div>
                <div class="bubble bubble5" @click.stop="burstBubble"></div>
                <div class="bubble bubble6" @click.stop="burstBubble"></div>
                <div class="bubble bubble7" @click.stop="burstBubble"></div>
                <div class="bubble bubble8" @click.stop="burstBubble"></div>
                <div class="bubble bubble9" @click.stop="burstBubble"></div>
                <div class="bubble bubble10" @click.stop="burstBubble"></div>
            </div>
        </div>

        <!-- 头部标题 -->
        <div class="header">
            <!-- 背景装饰几何图形 -->
            <div class="header-decorations">
                <div class="decoration-circle circle-1"></div>
                <div class="decoration-circle circle-2"></div>
                <div class="decoration-triangle triangle-1"></div>
                <div class="decoration-triangle triangle-2"></div>
                <div class="decoration-star star-1">✦</div>
                <div class="decoration-star star-2">✧</div>
                <div class="decoration-star star-3">✦</div>
                <div class="decoration-star star-4">✧</div>
                <div class="decoration-star star-5">✦</div>
            </div>

            <!-- 主标题容器 -->
            <div class="title-container">
                <!-- 发光背景 -->
                <div class="title-glow"></div>

                <!-- 主标题 -->
                <h1 class="title">
                    <span class="title-icon">🖼️</span>
                    <span class="title-text">
                        <span class="title-char" style="--delay: 0s">风</span>
                        <span class="title-char" style="--delay: 0.1s">格</span>
                        <span class="title-char" style="--delay: 0.2s">迁</span>
                        <span class="title-char" style="--delay: 0.3s">移</span>
                    </span>
                </h1>

                <!-- 装饰线条 -->
                <div class="title-lines">
                    <div class="line line-left"></div>
                    <div class="line line-right"></div>
                </div>
            </div>

            <!-- 副标题容器 -->
            <div class="subtitle-container">
                <p class="subtitle">
                    <span class="subtitle-highlight">用AI转换图片风格，创造艺术奇迹</span>
                </p>
            </div>

            <!-- 光芒效果 -->
            <div class="light-rays">
                <div class="ray ray-1"></div>
                <div class="ray ray-2"></div>
                <div class="ray ray-3"></div>
                <div class="ray ray-4"></div>
                <div class="ray ray-5"></div>
                <div class="ray ray-6"></div>
            </div>
        </div>

        <div class="main-content">
            <!-- 左侧：输入图片 -->
            <div class="upload-section">
                <div class="section-title">
                    <h2>📤 输入图片</h2>
                </div>
                <el-upload class="image-uploader input-uploader" :show-file-list="false" :before-upload="handleImageUpload" accept=".jpg,.jpeg,.png" drag>
                    <div v-if="!inputPreview" class="upload-placeholder">
                        <el-icon class="upload-icon">
                            <Plus />
                        </el-icon>
                        <div class="upload-text">拖拽或点击上传图片</div>
                        <div class="upload-hint">支持JPG、PNG格式，小于10MB</div>
                    </div>
                    <div v-else class="image-preview">
                        <img :src="inputPreview" alt="输入图片" />
                        <div class="image-overlay">
                            <el-button type="danger" size="small" @click.stop="removeImage">
                                <el-icon>
                                    <Delete />
                                </el-icon>
                            </el-button>
                        </div>
                    </div>
                </el-upload>
            </div>

            <!-- 移动端风格选择控制面板 -->
            <div class="mobile-control-panel">
                <!-- 风格选择 -->
                <div class="style-select">
                    <label>请选择风格</label>
                    <div class="custom-select-wrapper">
                        <div 
                            class="custom-select" 
                            :class="{ 'is-open': isStyleSelectOpen }"
                            @click="toggleStyleSelect"
                        >
                            <div class="select-display">
                                {{ selectedStyle ? styleOptions.find(opt => opt.value === selectedStyle)?.label : '请选择图片风格' }}
                            </div>
                            <div class="select-arrow">
                                <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
                                    <path d="M7 10l5 5 5-5z"/>
                                </svg>
                            </div>
                        </div>
                        <div class="select-options" v-show="isStyleSelectOpen">
                            <div 
                                class="select-option"
                                :class="{ 'is-selected': selectedStyle === option.value }"
                                v-for="option in styleOptions" 
                                :key="option.value"
                                @click="selectStyle(option.value)"
                            >
                                {{ option.label }}
                            </div>
                        </div>
                    </div>
                </div>

                <div class="generate-btn-wrapper">
                    <el-button 
                        type="primary" 
                        size="large"
                        :disabled="!canGenerate" 
                        :loading="isGenerating" 
                        @click="generate"
                        class="generate-btn"
                    >
                        <el-icon>
                            <MagicStick />
                        </el-icon>
                        {{ isGenerating ? '生成中...' : '开始迁移' }}
                    </el-button>
                    <div v-if="isGenerating" class="progress-container">
                        <span v-if="statusText" class="status-text">{{ statusText }}</span>
                        <div v-if="progress > 0" class="custom-progress">
                            <div class="progress-bar" :style="{ width: progress + '%' }"></div>
                            <div class="progress-text">{{ progress }}%</div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- 右侧：输出图片 -->
            <div class="output-section">
                <div class="section-title">
                    <h2>🖼️ 输出图片</h2>
                </div>
                <div class="output-corner-actions" v-if="outputImage">
                    <div class="corner-button download-btn" @click="download" title="下载图片">
                        <el-icon>
                            <Download />
                        </el-icon>
                    </div>
                </div>
                <div class="image-container output-container">
                    <!-- 已生成的图片 -->
                    <div v-if="outputImage" class="preview-image">
                        <img :src="outputImage" alt="输出图片" @load="onImageLoad" @error="onImageError" />
                        <div class="image-actions">
                            <el-button size="small" type="warning" @click="regenerateImage" :loading="false">
                                <el-icon>
                                    <Refresh />
                                </el-icon>
                                {{ isRegenerating ? '中断重新生成' : '重新生成' }}
                            </el-button>
                        </div>
                    </div>
                    <!-- 生成失败显示 -->
                    <div v-else-if="imageStatus && imageStatus.includes('失败')" class="generating-failed">
                        <div class="failed-icon">❌</div>
                        <div class="failed-text">{{ imageStatus }}</div>
                        <div class="failed-actions">
                            <el-button size="small" type="warning" @click="regenerateImage" :loading="false">
                                <el-icon>
                                    <Refresh />
                                </el-icon>
                                重新生成
                            </el-button>
                        </div>
                    </div>
                    <!-- 预处理/排队阶段 - 旋转加载圆圈 -->
                    <div v-else-if="imageStatus && (imageStatus.includes('预处理') || imageStatus.includes('排队') || imageStatus.includes('处理中'))" class="generating-loading">
                        <div class="loading-container">
                            <div class="loading-spinner"></div>
                            <div class="loading-status">{{ imageStatus }}</div>
                            <div class="loading-actions">
                                <el-button size="small" type="warning" @click="regenerateImage" :loading="false">
                                    <el-icon>
                                        <Refresh />
                                    </el-icon>
                                    {{ isRegenerating ? '中断重新生成' : '重新生成' }}
                                </el-button>
                            </div>
                        </div>
                    </div>
                    <!-- 生成阶段 - 进度条显示 -->
                    <div v-else-if="imageStatus && imageStatus.includes('生成')" class="generating-progress">
                        <div class="progress-container">
                            <div class="progress-circle">
                                <svg class="progress-ring" width="120" height="120">
                                    <circle
                                        class="progress-ring-circle"
                                        stroke="#ff8c42"
                                        stroke-width="8"
                                        fill="transparent"
                                        r="52"
                                        cx="60"
                                        cy="60"
                                        :stroke-dasharray="`${2 * Math.PI * 52}`"
                                        :stroke-dashoffset="`${2 * Math.PI * 52 * (1 - Math.max(progress, 0) / 100)}`"
                                        style="--mobile-radius: 42"
                                    />
                                </svg>
                                <div class="progress-circle-text">{{ Math.round(Math.max(progress, 0)) }}%</div>
                            </div>
                            <div class="progress-status">{{ imageStatus || '生成中...' }}</div>
                            <div class="progress-actions">
                                <el-button size="small" type="warning" @click="regenerateImage" :loading="false">
                                    <el-icon>
                                        <Refresh />
                                    </el-icon>
                                    {{ isRegenerating ? '中断重新生成' : '重新生成' }}
                                </el-button>
                            </div>
                        </div>
                    </div>
                    <!-- 其他状态 - 旋转加载圆圈 -->
                    <div v-else-if="imageStatus" class="generating-loading">
                        <div class="loading-container">
                            <div class="loading-spinner"></div>
                            <div class="loading-status">{{ imageStatus }}</div>
                            <div class="loading-actions">
                                <el-button size="small" type="warning" @click="regenerateImage" :loading="false">
                                    <el-icon>
                                        <Refresh />
                                    </el-icon>
                                    {{ isRegenerating ? '中断重新生成' : '重新生成' }}
                                </el-button>
                            </div>
                        </div>
                    </div>
                    <!-- 等待生成 -->
                    <div v-else class="preview-placeholder">
                        <el-icon class="placeholder-icon">
                            <Picture />
                        </el-icon>
                        <div class="placeholder-text">生成后的图片将显示在此</div>
                    </div>
                </div>
            </div>
        </div>

        <!-- 底部控制面板 -->
        <div class="control-panel">
            <!-- 风格选择 -->
            <div class="style-select">
                <label>请选择风格</label>
                <div class="custom-select-wrapper">
                    <div 
                        class="custom-select" 
                        :class="{ 'is-open': isStyleSelectOpen }"
                        @click="toggleStyleSelect"
                    >
                        <div class="select-display">
                            {{ selectedStyle ? styleOptions.find(opt => opt.value === selectedStyle)?.label : '请选择图片风格' }}
                        </div>
                        <div class="select-arrow">
                            <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
                                <path d="M7 10l5 5 5-5z"/>
                            </svg>
                        </div>
                    </div>
                    <div class="select-options" v-show="isStyleSelectOpen">
                        <div 
                            class="select-option"
                            :class="{ 'is-selected': selectedStyle === option.value }"
                            v-for="option in styleOptions" 
                            :key="option.value"
                            @click="selectStyle(option.value)"
                        >
                            {{ option.label }}
                        </div>
                    </div>
                </div>
            </div>

            <div class="generate-btn-wrapper">
                <el-button 
                    type="primary" 
                    size="large"
                    :disabled="!canGenerate" 
                    :loading="isGenerating" 
                    @click="generate"
                    class="generate-btn"
                >
                    <el-icon>
                        <MagicStick />
                    </el-icon>
                    {{ isGenerating ? '生成中...' : '开始迁移' }}
                </el-button>
                <div v-if="isGenerating" class="progress-container">
                    <span v-if="statusText" class="status-text">{{ statusText }}</span>
                    <div v-if="progress > 0" class="custom-progress">
                        <div class="progress-bar" :style="{ width: progress + '%' }"></div>
                        <div class="progress-text">{{ progress }}%</div>
                    </div>
                </div>
            </div>
        </div>

        <!-- 原生消息提示容器 -->
        <div class="native-message-container">
            <div 
                v-for="message in messages" 
                :key="message.id"
                :class="[
                    'native-message', 
                    `native-message--${message.type}`,
                    { 'native-message--visible': message.visible }
                ]"
                @click="closeMessage(message.id)"
            >
                <div class="native-message__icon">
                    <span v-if="message.type === 'success'">✅</span>
                    <span v-else-if="message.type === 'error'">❌</span>
                    <span v-else-if="message.type === 'warning'">⚠️</span>
                    <span v-else>ℹ️</span>
                </div>
                <div class="native-message__content">{{ message.content }}</div>
                <div class="native-message__close">✕</div>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { Plus, Delete, MagicStick, Download, Picture, Refresh } from '@element-plus/icons-vue'

const API_BASE_URL = 'https://api.lingximoyu.com'
const API_KEY = 'sk-JdJqP2CyAUXtqGL36d25AaDa6e9b46868bF45d0a515d7882'

// 输入图片相关
const inputFile = ref(null)
const inputPreview = ref('')

// 输出图片
const outputImage = ref('')

// 图片状态和重新生成状态
const imageStatus = ref('')
const isRegenerating = ref(false)

// 用于中断请求的控制器
let currentAbortController = null

// 防抖控制
let lastGenerateTime = 0
let lastRegenerateTime = 0
const REGENERATE_DEBOUNCE_TIME = 1000 // 1秒内只能重新生成一次

// 风格选项
const styleOptions = [
    { label: '莫奈风', value: '莫奈风' },
    { label: '动画风', value: '动画风' },
    { label: '赛博朋克风', value: '赛博朋克风' },
    { label: '中国风', value: '中国风' },
    { label: '皮克斯风', value: '皮克斯风' },
    { label: '机甲风', value: '机甲风' },
]
const selectedStyle = ref('')

// 生成状态
const isGenerating = ref(false)
const progress = ref(0)
const statusText = ref('预处理中...')

// 自定义下拉菜单状态
const isStyleSelectOpen = ref(false)

// 原生消息提示系统
const messages = ref([])
let messageId = 0

const canGenerate = computed(() => inputFile.value && selectedStyle.value)

// 处理图片上传
const handleImageUpload = (file) => {
    if (!validateImage(file)) return false
    inputFile.value = file
    const reader = new FileReader()
    reader.onload = (e) => {
        inputPreview.value = e.target.result
    }
    reader.readAsDataURL(file)
    return false
}

const validateImage = (file) => {
    const isJPG = file.type === 'image/jpeg' || file.type === 'image/jpg'
    const isPNG = file.type === 'image/png'
    if (!isJPG && !isPNG) {
        NativeMessage.error('请上传JPG或PNG格式的图片！')
        return false
    }
    const isLt10M = file.size / 1024 / 1024 < 10
    if (!isLt10M) {
        NativeMessage.error('图片大小不能超过10MB！')
        return false
    }
    return true
}

const removeImage = () => {
    inputFile.value = null
    inputPreview.value = ''
    outputImage.value = ''
}

// 显示消息的方法
const showMessage = (content, type = 'info', duration = 3000) => {
    const id = ++messageId
    const message = {
        id,
        content,
        type, // success, error, warning, info
        visible: true
    }
    
    messages.value.push(message)
    
    // 自动隐藏
    setTimeout(() => {
        const index = messages.value.findIndex(m => m.id === id)
        if (index > -1) {
            messages.value[index].visible = false
            // 动画结束后移除
            setTimeout(() => {
                const removeIndex = messages.value.findIndex(m => m.id === id)
                if (removeIndex > -1) {
                    messages.value.splice(removeIndex, 1)
                }
            }, 300)
        }
    }, duration)
}

// 消息类型方法
const NativeMessage = {
    success: (content, duration) => showMessage(content, 'success', duration),
    error: (content, duration) => showMessage(content, 'error', duration),
    warning: (content, duration) => showMessage(content, 'warning', duration),
    info: (content, duration) => showMessage(content, 'info', duration)
}

// 手动关闭消息
const closeMessage = (id) => {
    const index = messages.value.findIndex(m => m.id === id)
    if (index > -1) {
        messages.value[index].visible = false
        setTimeout(() => {
            const removeIndex = messages.value.findIndex(m => m.id === id)
            if (removeIndex > -1) {
                messages.value.splice(removeIndex, 1)
            }
        }, 300)
    }
}

// 自定义下拉菜单方法
const toggleStyleSelect = () => {
    isStyleSelectOpen.value = !isStyleSelectOpen.value
}

const selectStyle = (value) => {
    selectedStyle.value = value
    isStyleSelectOpen.value = false
}

// 泡泡破裂效果
const burstBubble = (event) => {
    const bubble = event.target

    // 创建破裂动画
    bubble.style.animation = 'bubbleBurst 0.3s ease-out forwards'

    // 创建破裂粒子效果
    for (let i = 0; i < 6; i++) {
        const particle = document.createElement('div')
        particle.className = 'burst-particle'
        particle.style.left = bubble.offsetLeft + bubble.offsetWidth / 2 + 'px'
        particle.style.top = bubble.offsetTop + bubble.offsetHeight / 2 + 'px'
        particle.style.setProperty('--angle', Math.random() * 360 + 'deg')
        particle.style.setProperty('--distance', Math.random() * 50 + 20 + 'px')
        bubble.parentElement.appendChild(particle)

        // 移除粒子
        setTimeout(() => {
            if (particle.parentElement) {
                particle.parentElement.removeChild(particle)
            }
        }, 600)
    }

    // 重置泡泡
    setTimeout(() => {
        bubble.style.animation = ''
    }, 300)
}

// 点击外部关闭下拉菜单
const handleClickOutside = (event) => {
    const selectWrapper = event.target.closest('.custom-select-wrapper')
    if (!selectWrapper) {
        isStyleSelectOpen.value = false
    }
}

// 生成风格迁移结果
const generate = async () => {
    if (!canGenerate.value) return
    
    // 防抖检查
    const now = Date.now()
    if (now - lastGenerateTime < REGENERATE_DEBOUNCE_TIME) {
        console.log('生成过于频繁，忽略点击')
        return
    }
    lastGenerateTime = now
    
    isGenerating.value = true
    isRegenerating.value = false // 确保重新生成状态为false
    progress.value = 0
    statusText.value = '预处理中...'
    imageStatus.value = '预处理中...'
    outputImage.value = '' // 清空之前的图片
    
    // 中断之前的请求并等待一小段时间
    if (currentAbortController) {
        try {
            currentAbortController.abort()
        } catch (e) {
            console.warn('中断请求时出错:', e)
        }
        currentAbortController = null
        // 等待一小段时间确保请求完全中断
        await new Promise(resolve => setTimeout(resolve, 100))
    }
    
    try {
        // 将文件转为base64
        const { base64, width: imgW, height: imgH } = await compressImage(inputFile.value)
        const prompt = `将这张图片转换成${selectedStyle.value}，输出尺寸${imgW}x${imgH}`

        const body = {
            model: 'gpt-4o-image',
            stream: true,
            messages: [
                {
                    role: 'user',
                    content: [
                        { type: 'text', text: prompt },
                        { type: 'image_url', image_url: { url: base64 } },
                    ],
                },
            ],
        }

        // 创建新的 AbortController
        currentAbortController = new AbortController()

        const res = await fetch(`https://api.lingximoyu.com/v1/chat/completions`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                Authorization: `Bearer ${API_KEY}`,
            },
            body: JSON.stringify(body),
            signal: currentAbortController.signal
        })

        if (!res.ok || !res.body) {
            const txt = await res.text()
            throw new Error(txt || '接口请求失败')
        }

        const reader = res.body.getReader()
        const decoder = new TextDecoder('utf-8')
        let accumulated = ''
        let chunkCount = 0
        
        try {
            while (true) {
                const { done, value } = await reader.read()
                if (done) break
                const chunk = decoder.decode(value, { stream: true })
                const lines = chunk.split('\n')
                for (const line of lines) {
                    if (!line.startsWith('data:')) continue
                    const payload = line.replace(/^data:\s*/, '')
                    if (payload === '[DONE]') {
                        progress.value = 100
                        break
                    }
                    try {
                        const json = JSON.parse(payload)
                        const contentDelta = json.choices?.[0]?.delta?.content || ''
                        accumulated += contentDelta

                        // 队列/预处理提示
                        if (contentDelta.includes('任务正在队列中')) {
                            statusText.value = '排队中...'
                            imageStatus.value = '排队中...'
                        }

                        const pctMatch = contentDelta.match(/进度：([\d.]+)%/)
                        if (pctMatch) {
                            statusText.value = ''
                            imageStatus.value = '生成中...'
                            progress.value = Math.min(99, parseFloat(pctMatch[1]).toFixed(1))
                        }

                        if (contentDelta.includes('图片绘制成功')) {
                            statusText.value = '生成成功'
                            imageStatus.value = '生成成功'
                            NativeMessage.success('图片风格转换成功！')
                        }

                        // Fallback：仍然用 chunk 数来估算，避免长时间0%
                        if (!pctMatch) {
                            chunkCount++
                            if (chunkCount % 10 === 0 && progress.value < 90) {
                                progress.value += 1
                            }
                        }

                        // 尝试在增量中解析 URL
                        const urlMatch = accumulated.match(/https?:[^\s)]+/)
                        if (urlMatch) {
                            outputImage.value = urlMatch[0]
                            progress.value = 100
                            imageStatus.value = '图片已获取'
                        }
                    } catch (e) {
                        console.warn('解析流数据失败', e)
                    }
                }
            }
        } finally {
            // 确保reader被正确关闭
            try {
                reader.releaseLock()
            } catch (e) {
                console.warn('释放reader锁时出错:', e)
            }
        }
    } catch (err) {
        console.error(err)
        // 如果是用户主动中断，不显示错误消息
        if (err.name !== 'AbortError') {
            imageStatus.value = '生成失败'
            NativeMessage.error(err.message || '生成失败，请重试！')
        }
    } finally {
        isGenerating.value = false
        currentAbortController = null
        // 若未成功获取图片，则复位进度；成功则保持100%
        if (!outputImage.value) {
            progress.value = 0
            imageStatus.value = '生成失败'
        }
    }
}

const download = () => {
    if (!outputImage.value) return
    const link = document.createElement('a')
    link.href = outputImage.value
    link.download = 'style_transfer.png'
    link.click()
}

// 重新生成图片
const regenerateImage = async () => {
    console.log('重新生成按钮被点击', { isRegenerating: isRegenerating.value, inputFile: !!inputFile.value, selectedStyle: selectedStyle.value })
    
    // 检查基本条件
    if (!inputFile.value || !selectedStyle.value) {
        console.log('基本条件不满足', { inputFile: !!inputFile.value, selectedStyle: selectedStyle.value })
        NativeMessage.warning('请先上传图片并选择风格！')
        return
    }
    
    // 如果正在重新生成，则中断当前请求并立即开始新的重新生成
    if (isRegenerating.value) {
        console.log('正在重新生成，中断当前请求并开始新的重新生成')
        if (currentAbortController) {
            try {
                currentAbortController.abort()
            } catch (e) {
                console.warn('中断请求时出错:', e)
            }
            currentAbortController = null
        }
        // 立即开始新的重新生成，不等待防抖
        await startRegenerate()
        return
    }
    
    // 防抖检查（只在非重新生成状态下）
    const now = Date.now()
    if (now - lastRegenerateTime < REGENERATE_DEBOUNCE_TIME) {
        console.log('重新生成过于频繁，忽略点击')
        return
    }
    lastRegenerateTime = now
    
        // 开始重新生成
    await startRegenerate()
}

// 实际的重新生成逻辑
const startRegenerate = async () => {
    // 中断当前请求并等待一小段时间
    if (currentAbortController) {
        try {
            currentAbortController.abort()
        } catch (e) {
            console.warn('中断请求时出错:', e)
        }
        currentAbortController = null
        // 等待一小段时间确保请求完全中断
        await new Promise(resolve => setTimeout(resolve, 100))
    }

    console.log('开始重新生成')
    isRegenerating.value = true
    isGenerating.value = true // 设置主生成状态为true，让开始迁移按钮显示加载状态
    outputImage.value = '' // 清空当前图片
    progress.value = 0
    statusText.value = '预处理中...'
    imageStatus.value = '预处理中...'
    
    try {
        const { base64, width: imgW, height: imgH } = await compressImage(inputFile.value)
        const prompt = `将这张图片转换成${selectedStyle.value}，输出尺寸${imgW}x${imgH}`

        const body = {
            model: 'gpt-4o-image',
            stream: true,
            messages: [
                {
                    role: 'user',
                    content: [
                        { type: 'text', text: prompt },
                        { type: 'image_url', image_url: { url: base64 } },
                    ],
                },
            ],
        }

        // 创建新的 AbortController
        currentAbortController = new AbortController()

        const res = await fetch(`https://api.lingximoyu.com/v1/chat/completions`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                Authorization: `Bearer ${API_KEY}`,
            },
            body: JSON.stringify(body),
            signal: currentAbortController.signal
        })

        if (!res.ok || !res.body) {
            const txt = await res.text()
            throw new Error(txt || '接口请求失败')
        }

        const reader = res.body.getReader()
        const decoder = new TextDecoder('utf-8')
        let accumulated = ''
        let chunkCount = 0
        
        try {
            while (true) {
                const { done, value } = await reader.read()
                if (done) break
                const chunk = decoder.decode(value, { stream: true })
                const lines = chunk.split('\n')
                for (const line of lines) {
                    if (!line.startsWith('data:')) continue
                    const payload = line.replace(/^data:\s*/, '')
                    if (payload === '[DONE]') {
                        progress.value = 100
                        break
                    }
                    try {
                        const json = JSON.parse(payload)
                        const contentDelta = json.choices?.[0]?.delta?.content || ''
                        accumulated += contentDelta

                        // 队列/预处理提示
                        if (contentDelta.includes('任务正在队列中')) {
                            statusText.value = '排队中...'
                            imageStatus.value = '排队中...'
                        }

                        const pctMatch = contentDelta.match(/进度：([\d.]+)%/)
                        if (pctMatch) {
                            statusText.value = ''
                            imageStatus.value = '生成中...'
                            progress.value = Math.min(99, parseFloat(pctMatch[1]).toFixed(1))
                        }

                        if (contentDelta.includes('图片绘制成功')) {
                            statusText.value = '生成成功'
                            imageStatus.value = '生成成功'
                            NativeMessage.success('图片风格转换成功！')
                        }

                        // Fallback：仍然用 chunk 数来估算，避免长时间0%
                        if (!pctMatch && !contentDelta.includes('任务正在队列中')) {
                            chunkCount++
                            if (chunkCount % 10 === 0 && progress.value < 90) {
                                progress.value += 1
                            }
                        }

                        // 尝试在增量中解析 URL
                        const urlMatch = accumulated.match(/https?:[^\s)]+/)
                        if (urlMatch) {
                            outputImage.value = urlMatch[0]
                            progress.value = 100
                            imageStatus.value = '图片已获取'
                        }
                    } catch (e) {
                        console.warn('解析流数据失败', e)
                    }
                }
            }
        } finally {
            // 确保reader被正确关闭
            try {
                reader.releaseLock()
            } catch (e) {
                console.warn('释放reader锁时出错:', e)
            }
        }
    } catch (err) {
        console.error('重新生成失败:', err)
        // 如果是用户主动中断，不显示错误消息
        if (err.name !== 'AbortError') {
            imageStatus.value = '重新生成失败'
            NativeMessage.error(err.message || '重新生成失败，请重试！')
        }
    } finally {
        console.log('重新生成完成，重置状态')
        isRegenerating.value = false
        isGenerating.value = false // 确保主生成状态也被重置
        currentAbortController = null
        // 若未成功获取图片，则复位进度；成功则保持100%
        if (!outputImage.value) {
            progress.value = 0
            imageStatus.value = '重新生成失败'
        }
    }
}

// 图片加载成功
const onImageLoad = () => {
    imageStatus.value = '图片加载成功'
}

// 图片加载失败
const onImageError = () => {
    imageStatus.value = '图片加载失败'
}

// 将图片压缩到最长边 768px，并导出为 0.7 质量 JPEG
const compressImage = (file) => {
    return new Promise((resolve, reject) => {
        const img = new Image()
        img.onload = () => {
            const maxSide = 768
            let { width, height } = img
            if (width > height && width > maxSide) {
                height = (maxSide / width) * height
                width = maxSide
            } else if (height > maxSide) {
                width = (maxSide / height) * width
                height = maxSide
            }
            const canvas = document.createElement('canvas')
            canvas.width = width
            canvas.height = height
            const ctx = canvas.getContext('2d')
            ctx.drawImage(img, 0, 0, width, height)
            // 质量 0.7 可自行调整
            const dataUrl = canvas.toDataURL('image/jpeg', 0.7)
            resolve({ base64: dataUrl, width, height })
        }
        img.onerror = reject
        // File → blob → objectURL 避免 FileReader 额外内存
        img.src = URL.createObjectURL(file)
    })
}

// 组件挂载时初始化
onMounted(() => {
    document.addEventListener('click', handleClickOutside)
})

// 组件卸载时清理事件监听
onUnmounted(() => {
    document.removeEventListener('click', handleClickOutside)
    // 清理当前请求
    if (currentAbortController) {
        try {
            currentAbortController.abort()
        } catch (e) {
            console.warn('组件卸载时中断请求出错:', e)
        }
        currentAbortController = null
    }
})
</script>

<style scoped>
/* 全局字体设置 - 使用本地64_fonts.ttf字体适合6-12岁儿童 */
.style-transfer {
    min-height: 100vh;
    background: linear-gradient(135deg, #ffb347 0%, #ff8c42 100%);
    padding: 20px;
    position: relative;
    overflow-x: hidden;
    /* 统一使用本地可爱字体：64_fonts.ttf */
    font-family: 'CuteFont64', 'Comic Sans MS', 'Microsoft YaHei', '微软雅黑', cursive, sans-serif;
    font-size: 16px;
    line-height: 1.8;
    font-weight: 400;
}

/* 动态背景容器 */
.background-animations {
    position: fixed;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
    pointer-events: none;
    z-index: 0;
    overflow: hidden;
}

.waves {
    position: absolute;
    bottom: 0;
    left: 0;
    width: 100vw;
    height: 43vh;
    overflow: hidden;
}

.wave {
    position: absolute;
    bottom: 0;
    left: -50%;
    width: 200vw;
    height: 450px;
    background: linear-gradient(90deg,
        rgba(255, 255, 255, 0.1) 0%,
        rgba(255, 255, 255, 0.4) 25%,
        rgba(219, 219, 219, 0.6) 50%,
        rgba(255, 255, 255, 0.5) 75%,
        rgba(255, 255, 255, 0.1) 100%);
    border-radius: 50%;
    transform-origin: center bottom;
}

.wave1 {
    animation: waveMove 12s ease-in-out infinite;
    opacity: 0.4;
    height: 480px;
}

.wave2 {
    animation: waveMove 15s ease-in-out infinite reverse;
    opacity: 0.3;
    height: 440px;
    animation-delay: -3s;
}

.wave3 {
    animation: waveMove 18s ease-in-out infinite;
    opacity: 0.2;
    height: 400px;
    animation-delay: -6s;
}

@keyframes waveMove {
    0%, 100% {
        transform: translateX(0%) scaleY(0.8) rotate(-2deg);
    }
    25% {
        transform: translateX(5%) scaleY(1.1) rotate(1deg);
    }
    50% {
        transform: translateX(10%) scaleY(1.3) rotate(-1deg);
    }
    75% {
        transform: translateX(7%) scaleY(1.0) rotate(2deg);
    }
}

/* 气泡动画 - 增加更多泡泡 */
.bubbles {
    position: absolute;
    width: 100%;
    height: 100%;
    top: 0;
    left: 0;
}

.bubble {
    position: absolute;
    border-radius: 50%;
    background: linear-gradient(135deg, rgba(255, 255, 255, 0.4), rgba(255, 255, 255, 0.1));
    border: 2px solid rgba(255, 255, 255, 0.3);
    animation: bubbleFloat linear infinite;
    cursor: pointer;
    transition: all 0.1s ease;
    pointer-events: auto;
}

.bubble:hover {
    transform: scale(1.1);
    background: linear-gradient(135deg, rgba(255, 255, 255, 0.5), rgba(255, 255, 255, 0.2));
}

.bubble1 {
    width: 60px;
    height: 60px;
    left: 8%;
    animation: bubbleFloat 16s linear infinite;
}

.bubble2 {
    width: 40px;
    height: 40px;
    left: 18%;
    animation: bubbleFloat 20s linear infinite;
    animation-delay: -2s;
}

.bubble3 {
    width: 75px;
    height: 75px;
    left: 28%;
    animation: bubbleFloat 18s linear infinite;
    animation-delay: -4s;
}

.bubble4 {
    width: 35px;
    height: 35px;
    left: 38%;
    animation: bubbleFloat 14s linear infinite;
    animation-delay: -6s;
}

.bubble5 {
    width: 55px;
    height: 55px;
    left: 48%;
    animation: bubbleFloat 22s linear infinite;
    animation-delay: -8s;
}

.bubble6 {
    width: 45px;
    height: 45px;
    left: 58%;
    animation: bubbleFloat 17s linear infinite;
    animation-delay: -10s;
}

.bubble7 {
    width: 65px;
    height: 65px;
    left: 68%;
    animation: bubbleFloat 19s linear infinite;
    animation-delay: -12s;
}

.bubble8 {
    width: 30px;
    height: 30px;
    left: 78%;
    animation: bubbleFloat 15s linear infinite;
    animation-delay: -14s;
}

.bubble9 {
    width: 50px;
    height: 50px;
    left: 88%;
    animation: bubbleFloat 21s linear infinite;
    animation-delay: -16s;
}

.bubble10 {
    width: 70px;
    height: 70px;
    left: 12%;
    animation: bubbleFloat 23s linear infinite;
    animation-delay: -18s;
}

@keyframes bubbleFloat {
    0% {
        top: 110%;
        opacity: 0;
        transform: translateX(0) scale(0);
    }
    10% {
        opacity: 1;
        transform: translateX(0) scale(1);
    }
    90% {
        opacity: 1;
        transform: translateX(20px) scale(1);
    }
    100% {
        top: -10%;
        opacity: 0;
        transform: translateX(40px) scale(0);
    }
}

/* 泡泡破裂动画 */
@keyframes bubbleBurst {
    0% {
        transform: scale(1);
        opacity: 1;
    }
    50% {
        transform: scale(1.3);
        opacity: 0.7;
    }
    100% {
        transform: scale(0);
        opacity: 0;
    }
}

/* 破裂粒子效果 */
.burst-particle {
    position: absolute;
    width: 4px;
    height: 4px;
    background: rgba(255, 255, 255, 0.8);
    border-radius: 50%;
    pointer-events: none;
    animation: particleBurst 0.6s ease-out forwards;
}

@keyframes particleBurst {
    0% {
        opacity: 1;
        transform: translate(0, 0) scale(1);
    }
    100% {
        opacity: 0;
        transform: translate(calc(cos(var(--angle)) * var(--distance)),
            calc(sin(var(--angle)) * var(--distance))) scale(0);
    }
}

/* 确保内容在动画之上 */
.header,
.main-content {
    position: relative;
    z-index: 1;
}

/* 全局字体继承 */
.style-transfer *,
.style-transfer *::before,
.style-transfer *::after {
    font-family: inherit;
    font-weight: inherit;
}

.header {
    text-align: center;
    margin-bottom: 10px;
    position: relative;
    overflow: visible;
}

/* 背景装饰几何图形 */
.header-decorations {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    pointer-events: none;
    z-index: 1;
}

.decoration-circle {
    position: absolute;
    border-radius: 50%;
    background: linear-gradient(45deg, rgba(255, 215, 0, 0.4), rgba(255, 140, 66, 0.3));
    animation: decorationFloat 8s ease-in-out infinite;
}

.circle-1 {
    width: 80px;
    height: 80px;
    top: 10%;
    left: 5%;
    animation-delay: 0s;
}

.circle-2 {
    width: 60px;
    height: 60px;
    top: 20%;
    right: 8%;
    animation-delay: -2s;
}

.decoration-triangle {
    position: absolute;
    width: 0;
    height: 0;
    animation: decorationSpin 12s linear infinite;
}

.triangle-1 {
    border-left: 25px solid transparent;
    border-right: 25px solid transparent;
    border-bottom: 43px solid rgba(255, 99, 71, 0.4);
    top: 15%;
    left: 15%;
    animation-delay: -1s;
}

.triangle-2 {
    border-left: 20px solid transparent;
    border-right: 20px solid transparent;
    border-bottom: 35px solid rgba(255, 215, 0, 0.4);
    top: 25%;
    right: 20%;
    animation-delay: -3s;
}

.decoration-star {
    position: absolute;
    font-size: 1.5rem;
    color: rgba(255, 215, 0, 0.8);
    animation: starTwinkle 3s ease-in-out infinite;
    text-shadow: 0 0 10px rgba(255, 215, 0, 0.6);
}

.star-1 {
    top: 8%;
    left: 25%;
    animation-delay: 0s;
}

.star-2 {
    top: 12%;
    right: 15%;
    animation-delay: -0.5s;
}

.star-3 {
    top: 30%;
    left: 8%;
    animation-delay: -1s;
}

.star-4 {
    top: 35%;
    right: 25%;
    animation-delay: -1.5s;
}

.star-5 {
    top: 18%;
    left: 50%;
    animation-delay: -2s;
}

/* 主标题容器 */
.title-container {
    position: relative;
    z-index: 3;
    margin-bottom: -20px;
}

.title-glow {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    width: 400px;
    height: 100px;
    background: radial-gradient(ellipse, rgba(255, 215, 0, 0.4) 0%, transparent 70%);
    filter: blur(20px);
    animation: glowPulse 4s ease-in-out infinite;
}

.title {
    font-size: 3.5rem;
    font-family: 'CuteFont64', cursive;
    position: relative;
    z-index: 2;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 10px;
}

.title-icon {
    font-size: 3rem;
    filter: drop-shadow(0 0 15px rgba(255, 140, 66, 0.6));
    animation: iconBounce 3s ease-in-out infinite;
}

.title-text {
    color: #2c1810;
    text-shadow:
        3px 3px 0px #ffd700,
        6px 6px 0px #fff8dc,
        9px 9px 0px rgba(255, 99, 71, 0.3),
        0 0 20px rgba(255, 215, 0, 0.6);
    animation: textGlow 3s ease-in-out infinite;
}

.title-char {
    display: inline-block;
    animation: charFloat 3s ease-in-out infinite;
    animation-delay: var(--delay);
}

/* 装饰线条 */
.title-lines {
    position: absolute;
    top: 50%;
    left: 0;
    right: 0;
    transform: translateY(-50%);
    z-index: 1;
}

.line {
    position: absolute;
    height: 3px;
    background: linear-gradient(90deg, transparent, #ffd700, transparent);
    animation: lineExpand 4s ease-in-out infinite;
}

.line-left {
    left: 0;
    right: 60%;
    animation-delay: 0s;
}

.line-right {
    left: 60%;
    right: 0;
    animation-delay: -2s;
}

/* 副标题容器 */
.subtitle-container {
    position: relative;
    z-index: 3;
}

.subtitle {
    font-size: 1.5rem;
    margin: 0;
    font-family: 'CuteFont64', cursive;
    position: relative;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 6px;
    flex-wrap: wrap;
}

.subtitle-highlight {
    color: #8b0000;
    text-shadow:
        2px 2px 0px #ffd700,
        4px 4px 0px #fff8dc,
        0 0 10px rgba(255, 215, 0, 0.8);
    animation: highlightPulse 3s ease-in-out infinite;
}

/* 光芒效果 */
.light-rays {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    width: 400px;
    height: 400px;
    pointer-events: none;
    z-index: 0;
}

.ray {
    position: absolute;
    top: 50%;
    left: 50%;
    width: 1px;
    height: 100px;
    background: linear-gradient(to bottom,
        rgba(255, 215, 0, 0.6) 0%,
        rgba(255, 215, 0, 0.3) 50%,
        transparent 100%);
    transform-origin: bottom center;
    animation: rayRotate 20s linear infinite;
}

.ray-1 {
    transform: translate(-50%, -100%) rotate(0deg);
    animation-delay: 0s;
}

.ray-2 {
    transform: translate(-50%, -100%) rotate(60deg);
    animation-delay: -3.33s;
}

.ray-3 {
    transform: translate(-50%, -100%) rotate(120deg);
    animation-delay: -6.66s;
}

.ray-4 {
    transform: translate(-50%, -100%) rotate(180deg);
    animation-delay: -10s;
}

.ray-5 {
    transform: translate(-50%, -100%) rotate(240deg);
    animation-delay: -13.33s;
}

.ray-6 {
    transform: translate(-50%, -100%) rotate(300deg);
    animation-delay: -16.66s;
}

/* 头部动画关键帧 */
@keyframes decorationFloat {
    0%, 100% {
        transform: translateY(0px) rotate(0deg);
    }
    50% {
        transform: translateY(-10px) rotate(180deg);
    }
}

@keyframes decorationSpin {
    0% {
        transform: rotate(0deg);
    }
    100% {
        transform: rotate(360deg);
    }
}

@keyframes starTwinkle {
    0%, 100% {
        opacity: 0.8;
        transform: scale(1);
    }
    50% {
        opacity: 1;
        transform: scale(1.2);
    }
}

@keyframes glowPulse {
    0%, 100% {
        opacity: 0.4;
        transform: translate(-50%, -50%) scale(1);
    }
    50% {
        opacity: 0.8;
        transform: translate(-50%, -50%) scale(1.1);
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

@keyframes textGlow {
    0%, 100% {
        text-shadow:
            3px 3px 0px #ffd700,
            6px 6px 0px #fff8dc,
            9px 9px 0px rgba(255, 99, 71, 0.3),
            0 0 20px rgba(255, 215, 0, 0.6);
    }
    50% {
        text-shadow:
            3px 3px 0px #ffd700,
            6px 6px 0px #fff8dc,
            9px 9px 0px rgba(255, 99, 71, 0.5),
            0 0 30px rgba(255, 215, 0, 1);
    }
}

@keyframes charFloat {
    0%, 100% {
        transform: translateY(0px);
    }
    50% {
        transform: translateY(-8px);
    }
}

@keyframes lineExpand {
    0%, 100% {
        opacity: 0.3;
        transform: scaleX(0.5);
    }
    50% {
        opacity: 0.8;
        transform: scaleX(1);
    }
}

@keyframes highlightPulse {
    0%, 100% {
        text-shadow:
            2px 2px 0px #ffd700,
            4px 4px 0px #fff8dc,
            0 0 10px rgba(255, 215, 0, 0.8);
    }
    50% {
        text-shadow:
            2px 2px 0px #ffd700,
            4px 4px 0px #fff8dc,
            0 0 20px rgba(255, 215, 0, 1);
    }
}

@keyframes rayRotate {
    0% {
        transform: translate(-50%, -100%) rotate(var(--start-rotation, 0deg));
        opacity: 0.3;
    }
    50% {
        opacity: 0.7;
    }
    100% {
        transform: translate(-50%, -100%) rotate(calc(var(--start-rotation, 0deg) + 360deg));
        opacity: 0.3;
    }
}

.main-content {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 15px;
    max-width: 1000px;
    margin: 0 auto;
    position: relative;
    z-index: 2;
}

.section-title {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.section-title h2 {
    color: #8b4513;
    margin: 0;
    font-size: 1.8rem;
    text-shadow: 2px 2px 0px #ffd700;
    font-weight: 500;
    letter-spacing: 2px;
    font-family: 'CuteFont64', cursive;
}

.upload-section,
.output-section {
    background: #fff8dc;
    border-radius: 25px;
    padding: 25px;
    border: 6px solid #f7a985;
    box-shadow: 0px 10px #ff6347;
    display: flex;
    flex-direction: column;
    gap: 20px;
}

.output-section {
    position: relative;
}

/* 底部控制面板 */
.control-panel {
    background: #fff8dc;
    border-radius: 25px;
    padding: 25px;
    border: 6px solid #f7a985;
    box-shadow: 0px 10px #ff6347;
    margin-top: 20px;
    max-width: 1000px;
    margin-left: auto;
    margin-right: auto;
    position: relative;
    z-index: 2;
    display: flex;
    flex-direction: column;
    gap: 20px;
}

/* 移动端控制面板 */
.mobile-control-panel {
    background: #fff8dc;
    border-radius: 25px;
    padding: 25px;
    border: 6px solid #f7a985;
    box-shadow: 0px 10px #ff6347;
    display: none;
    flex-direction: column;
    gap: 20px;
}

/* 上传组件样式 */
.image-uploader {
    width: 100%;
}

.image-uploader :deep(.el-upload) {
    width: 100%;
}

.image-uploader :deep(.el-upload-dragger) {
    width: 100%;
    height: 100%;
    border: 4px dashed #ff8c42;
    border-radius: 20px;
    background: #fff8dc;
    transition: all 0.3s ease;
    box-shadow: inset 0px 4px 8px rgba(0, 0, 0, 0.1);
}

.image-uploader :deep(.el-upload-dragger:hover) {
    border-color: #ff6347;
    background: #fffacd;
    transform: translateY(-2px);
    box-shadow: 0px 6px 12px rgba(0, 0, 0, 0.2);
}

/* 输入上传器特殊样式 */
.input-uploader {
    position: relative;
    width: 100%;
    height: 500px;
    border-radius: 20px;
    overflow: hidden;
    background: #fffacd;
    display: flex;
    align-items: center;
    justify-content: center;
}

.input-uploader :deep(.el-upload) {
    width: 100%;
    height: 100%;
}

.input-uploader :deep(.el-upload-dragger) {
    width: 100%;
    height: 100%;
    border: 4px dashed #ff8c42;
    border-radius: 20px;
    background: #fff8dc;
    transition: all 0.3s ease;
    box-shadow: none;
    position: relative;
    display: flex;
    align-items: center;
    justify-content: center;
}

.input-uploader :deep(.el-upload-dragger:hover) {
    border-color: #ff6347;
    background: #fffacd;
    transform: translateY(-2px);
    box-shadow: 0px 6px 12px rgba(0, 0, 0, 0.2);
}

.upload-placeholder {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 100%;
    color: #8b4513;
    text-align: center;
}

.upload-icon {
    font-size: 2.5rem;
    color: #ff8c42;
    margin-bottom: 10px;
    text-shadow: 2px 2px 0px #ffd700;
}

.upload-text {
    font-size: 1.2rem;
    text-shadow: 1px 1px 0px #ffd700;
    text-align: center;
    margin-bottom: 5px;
}

.upload-hint {
    font-size: 1rem;
    color: #cd853f;
    text-align: center;
}

.image-preview {
    width: 90%;
    height: auto;
    display: flex;
    align-items: center;
    justify-content: center;
    position: relative;
}

.image-overlay {
    position: absolute;
    top: 5px;
    right: -10px;
    opacity: 1;
    transition: opacity 0.3s ease;
}

.image-preview:hover .image-overlay {
    opacity: 1;
}

/* 删除按钮样式 */
.image-overlay .el-button {
    font-size: 0.8rem;
    color: #fff;
    background-color: #ff6347;
    padding: 0.3em 0.6em;
    border-radius: 20px;
    border: 3px solid #f7a985;
    box-shadow: 0px 2px #8b0000;
    transition: all 0.1s ease;
}

.image-overlay .el-button:hover {
    background-color: #ff4500;
    transform: translateY(-1px);
    box-shadow: 0px 3px #8b0000;
}

.image-overlay .el-button:active {
    position: relative;
    top: 2px;
    border: 3px solid #cd5c5c;
    box-shadow: 0px 0px;
}

/* 风格选择 */
.style-select {
    display: flex;
    flex-direction: column;
    gap: 8px;
}

.style-select label {
    color: #8b4513;
    font-size: 1.2rem;
    text-shadow: 1px 1px 0px #ffd700;
    letter-spacing: 0.5px;
}

/* 自定义下拉菜单样式 */
.custom-select-wrapper {
    position: relative;
    width: 100%;
}

.custom-select {
    border: 4px solid #f7a985;
    border-radius: 20px;
    background: #fffacd;
    color: #8b4513;
    box-shadow: inset 0px 2px 4px rgba(0, 0, 0, 0.1);
    padding: 0.8em 1em;
    font-size: 1.1rem;
    width: 100%;
    transition: all 0.2s ease;
    cursor: pointer;
    letter-spacing: 0.5px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    min-height: 48px;
}

.custom-select:hover {
    background-color: #fff8dc;
    border-color: #ffb347;
    transform: translateY(-2px);
    box-shadow: 
        inset 0px 2px 4px rgba(0, 0, 0, 0.1), 
        0px 6px 12px rgba(255, 140, 66, 0.3),
        0px 2px 6px rgba(255, 215, 0, 0.4);
}

.custom-select.is-open {
    border-color: #ff8c42;
    box-shadow: 0 0 0 4px rgba(255, 179, 71, 0.4), 0 4px 12px rgba(255, 215, 0, 0.6);
    background-color: #fff8dc;
    transform: translateY(-1px);
}

.select-display {
    flex: 1;
    text-align: left;
}

.select-arrow {
    color: #ff8c42;
    transition: transform 0.2s ease;
    display: flex;
    align-items: center;
    justify-content: center;
    width: 24px;
    height: 24px;
}

.custom-select.is-open .select-arrow {
    transform: rotate(180deg);
}

.select-options {
    position: absolute;
    top: 100%;
    left: 0;
    right: 0;
    background: #fff8dc;
    border: 4px solid #ff8c42;
    border-top: none;
    border-radius: 0 0 20px 20px;
    box-shadow: 0px 8px 16px rgba(0, 0, 0, 0.2);
    z-index: 1000;
    max-height: 300px;
    overflow-y: auto;
    overflow-x: hidden;
}

.select-option {
    background: #fff8dc;
    color: #8b4513;
    font-size: 1.4rem;
    padding: 16px 20px;
    line-height: 1.8;
    border-bottom: 1px solid #f7a985;
    cursor: pointer;
    min-height: 55px;
    display: flex;
    align-items: center;
    transition: all 0.2s ease;
    letter-spacing: 0.5px;
    width: 100%;
    box-sizing: border-box;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.select-option:last-child {
    border-bottom: none;
    border-radius: 0 0 16px 16px;
}

.select-option:hover {
    background: #ffb347 !important;
    background-color: #ffb347 !important;
    color: #fff !important;
    font-weight: 800;
    text-shadow: 1px 1px 2px rgba(139, 69, 19, 0.5);
    transform: scale(1.02);
}

.select-option.is-selected {
    background: #ff8c42 !important;
    background-color: #ff8c42 !important;
    color: #fff !important;
    font-weight: 800;
    text-shadow: 1px 1px 2px rgba(139, 69, 19, 0.5);
    box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.2);
}

.select-option.is-selected:hover {
    background: #ff6347 !important;
    background-color: #ff6347 !important;
}

/* 自定义滚动条样式 */
.select-options::-webkit-scrollbar {
    width: 8px;
}

.select-options::-webkit-scrollbar-track {
    background: rgba(255, 215, 0, 0.2);
    border-radius: 4px;
}

.select-options::-webkit-scrollbar-thumb {
    background: linear-gradient(135deg, #ff8c42, #ffb347);
    border-radius: 4px;
    border: 1px solid #f7a985;
}

.select-options::-webkit-scrollbar-thumb:hover {
    background: linear-gradient(135deg, #ffb347, #ffd700);
}

/* 生成按钮样式 */
.generate-btn-wrapper {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 15px;
}

.generate-btn {
    height: 60px;
    cursor: pointer;
    font-size: 1.3rem;
    font-weight: 800;
    color: #8b4513;
    background-color: #ffffe3;
    padding: 0.8em 1.8em;
    border-radius: 50px;
    border: 6px solid rgb(247, 169, 133);
    box-shadow: 0px 8px #f32b11;
    transition: all 0.1s ease;
    letter-spacing: 1px;
}

.generate-btn:hover {
    background-color: #fff8dc;
    transform: translateY(-2px);
    box-shadow: 0px 10px #f32b11;
}

.generate-btn:active {
    position: relative;
    top: 8px;
    border: 6px solid #ffb764;
    box-shadow: 0px 0px;
}

.generate-btn:disabled {
    opacity: 0.6;
    cursor: not-allowed;
    background-color: #f5f5dc !important;
    border-color: #ddd !important;
    color: #999 !important;
}

.generate-btn:disabled:hover {
    transform: none !important;
    box-shadow: 0px 8px #f32b11 !important;
}

/* 自定义进度条样式 */
.progress-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 10px;
    width: 100%;
}

.status-text {
    color: #8b4513;
    font-size: 1rem;
    font-weight: 600;
    text-shadow: 1px 1px 0px #ffd700;
}

.custom-progress {
    position: relative;
    width: 200px;
    height: 20px;
    background: #fff8dc;
    border: 3px solid #f7a985;
    border-radius: 15px;
    overflow: hidden;
    box-shadow: inset 0px 2px 4px rgba(0, 0, 0, 0.1);
}

.progress-bar {
    height: 100%;
    background: linear-gradient(90deg, #ff8c42, #ffd700, #ffb347);
    border-radius: 12px;
    transition: width 0.3s ease;
    position: relative;
    overflow: hidden;
}

.progress-bar::after {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.6), transparent);
    animation: progressShine 2s ease-in-out infinite;
}

@keyframes progressShine {
    0% {
        left: -100%;
    }
    100% {
        left: 100%;
    }
}

.progress-text {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    color: #8b4513;
    font-size: 0.8rem;
    font-weight: 800;
    text-shadow: 1px 1px 0px rgba(255, 255, 255, 0.8);
}

/* 输出区域样式 */
.output-corner-actions {
    position: absolute;
    top: 25px;
    right: 35px;
    display: flex;
    gap: 12px;
    z-index: 999;
}

.corner-button {
    width: 55px;
    height: 55px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    box-shadow:
        0px 6px 12px rgba(255, 99, 71, 0.4),
        0px 3px 6px rgba(255, 140, 66, 0.3),
        inset 0px 2px 0px rgba(255, 255, 255, 0.3);
    transition: all 0.3s cubic-bezier(.4, 2, .6, 1);
    font-size: 1.4rem;
    position: relative;
    overflow: hidden;
    font-weight: 800;
}

.corner-button::before {
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

.corner-button:hover::before {
    width: 100%;
    height: 100%;
}

.corner-button:hover {
    box-shadow:
        0px 8px 16px rgba(255, 99, 71, 0.5),
        0px 4px 8px rgba(255, 140, 66, 0.4),
        inset 0px 2px 0px rgba(255, 255, 255, 0.4);
}

.corner-button:active {
    transform: translateY(-1px) scale(1.02);
    box-shadow:
        0px 4px 8px rgba(0, 0, 0, 0.2),
        0px 2px 4px rgba(0, 0, 0, 0.1);
}

.download-btn {
    background: linear-gradient(135deg, #ffb347, #ffd700);
    color: #8b4513;
    text-shadow: 1px 1px 0px rgba(255, 255, 255, 0.5);
    border: 4px solid #f7a985;
}

.download-btn:hover {
    background: linear-gradient(135deg, #ffd700, #ffb347);
    border-color: #ff8c42;
    transform: translateY(-5px) scale(1.15);
}

.corner-button .el-icon {
    font-size: 1.4rem;
    font-weight: 800;
    z-index: 1;
    position: relative;
    filter: drop-shadow(1px 1px 2px rgba(139, 69, 19, 0.4));
}

/* 图片容器样式 */
.image-container {
    position: relative;
    width: 100%;
    height: 500px;
    border-radius: 20px;
    overflow: hidden;
    background: #fffacd;
    border: 4px solid #f7a985;
    box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.2);
    display: flex;
    align-items: center;
    justify-content: center;
}

.input-container .image-uploader {
    width: 100%;
    height: 100%;
}

.input-container .image-uploader :deep(.el-upload) {
    width: 100%;
    height: 100%;
}

.preview-placeholder {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 100%;
    color: #8b4513;
    text-align: center;
}

.placeholder-icon {
    font-size: 2.5rem;
    margin-bottom: 8px;
    color: #ff8c42;
    text-shadow: 2px 2px 0px #ffd700;
}

.placeholder-text {
    font-size: 1.1rem;
    text-align: center;
    text-shadow: 1px 1px 0px #ffd700;
}

.preview-image {
    width: 100%;
    height: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
    position: relative;
}

.preview-image img {
    width: 90%;
    height: 90%;
    object-fit: cover;
    border-radius: 10px;
    border: 2px solid #f7a985;
}

.image-preview img {
    width: 90%;
    height: 90%;
    object-fit: cover;
    border-radius: 10px;
    border: 2px solid #f7a985;
}

/* 图片操作按钮样式 */
.image-actions {
    position: absolute;
    top: 10px;
    right: 10px;
    display: flex;
    gap: 8px;
    z-index: 10;
}

.image-actions .el-button {
    font-size: 0.8rem;
    color: #fff;
    background-color: #ff6347;
    padding: 0.3em 0.6em;
    border-radius: 20px;
    border: 3px solid #f7a985;
    box-shadow: 0px 2px #8b0000;
    transition: all 0.1s ease;
}

.image-actions .el-button:hover {
    background-color: #ff4500;
    transform: translateY(-1px);
    box-shadow: 0px 3px #8b0000;
}

.image-actions .el-button:active {
    position: relative;
    top: 2px;
    border: 3px solid #cd5c5c;
    box-shadow: 0px 0px;
}

.image-actions .el-button[type="warning"] {
    background-color: #ff8c42;
    color: #fff;
    border-color: #f7a985;
}

.image-actions .el-button[type="warning"]:hover {
    background-color: #ff6347;
    transform: translateY(-1px);
    box-shadow: 0px 3px #f32b11;
}

.image-actions .el-button[type="warning"]:active {
    position: relative;
    top: 2px;
    border: 3px solid #ffb764;
    box-shadow: 0px 0px;
}

/* 生成失败样式 */
.generating-failed {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 100%;
    color: #dc143c;
    text-shadow: 1px 1px 0px rgba(255, 255, 255, 0.5);
    font-size: 1.2rem;
    font-weight: 600;
    gap: 15px;
}

.failed-icon {
    font-size: 3rem;
    color: #dc143c;
    text-shadow: 1px 1px 0px rgba(255, 255, 255, 0.5);
    animation: shake 0.5s ease-in-out;
}

@keyframes shake {
    0%, 100% { transform: translateX(0); }
    25% { transform: translateX(-5px); }
    75% { transform: translateX(5px); }
}

.failed-text {
    text-align: center;
    color: #dc143c;
}

.failed-actions {
    display: flex;
    gap: 10px;
}

.failed-actions .el-button {
    font-size: 0.8rem;
    color: #fff;
    background-color: #ff8c42;
    padding: 0.3em 0.6em;
    border-radius: 20px;
    border: 3px solid #f7a985;
    box-shadow: 0px 2px #f32b11;
    transition: all 0.1s ease;
}

.failed-actions .el-button:hover {
    background-color: #ff6347;
    transform: translateY(-1px);
    box-shadow: 0px 3px #f32b11;
}

.failed-actions .el-button:active {
    position: relative;
    top: 2px;
    border: 3px solid #ffb764;
    box-shadow: 0px 0px;
}

/* 生成加载样式 */
.generating-loading {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 100%;
    color: #8b4513;
    text-shadow: 1px 1px 0px #ffd700;
    font-size: 1.2rem;
    font-weight: 600;
    gap: 15px;
}

.loading-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 15px;
}

.loading-spinner {
    width: 80px;
    height: 80px;
    border: 8px solid rgba(255, 140, 66, 0.2);
    border-top: 8px solid #ff8c42;
    border-radius: 50%;
    animation: spin 1s linear infinite;
    filter: drop-shadow(0 0 8px rgba(255, 140, 66, 0.4));
}

@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}

.loading-status {
    text-align: center;
    color: #8b4513;
    text-shadow: 1px 1px 0px #ffd700;
    animation: loadingPulse 1.5s ease-in-out infinite;
}

@keyframes loadingPulse {
    0%, 100% {
        opacity: 1;
        transform: scale(1);
    }
    50% {
        opacity: 0.8;
        transform: scale(1.02);
    }
}

.loading-actions {
    display: flex;
    gap: 10px;
}

.loading-actions .el-button {
    font-size: 0.8rem;
    color: #fff;
    background-color: #ff8c42;
    padding: 0.3em 0.6em;
    border-radius: 20px;
    border: 3px solid #f7a985;
    box-shadow: 0px 2px #f32b11;
    transition: all 0.1s ease;
}

.loading-actions .el-button:hover {
    background-color: #ff6347;
    transform: translateY(-1px);
    box-shadow: 0px 3px #f32b11;
}

.loading-actions .el-button:active {
    position: relative;
    top: 2px;
    border: 3px solid #ffb764;
    box-shadow: 0px 0px;
}

/* 生成进度样式 */
.generating-progress {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 100%;
    color: #8b4513;
    text-shadow: 1px 1px 0px #ffd700;
    font-size: 1.2rem;
    font-weight: 600;
    gap: 15px;
}

.progress-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 15px;
}

.progress-circle {
    position: relative;
    width: 120px;
    height: 120px;
    display: flex;
    align-items: center;
    justify-content: center;
}

.progress-ring {
    transform: rotate(-90deg);
    position: absolute;
    top: 0;
    left: 0;
}

.progress-ring-circle {
    transition: stroke-dashoffset 0.3s ease;
    stroke-linecap: round;
    filter: drop-shadow(0 0 8px rgba(255, 140, 66, 0.4));
}

.progress-circle-text {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    font-size: 1.4rem;
    font-weight: 800;
    color: #ff8c42;
    text-shadow: 1px 1px 0px #ffd700;
    animation: progressPulse 2s ease-in-out infinite;
    z-index: 2;
}

@keyframes progressPulse {
    0%, 100% {
        transform: translate(-50%, -50%) scale(1);
        opacity: 1;
    }
    50% {
        transform: translate(-50%, -50%) scale(1.05);
        opacity: 0.9;
    }
}

.progress-status {
    text-align: center;
    color: #8b4513;
    text-shadow: 1px 1px 0px #ffd700;
    animation: statusBlink 1.5s ease-in-out infinite;
}

@keyframes statusBlink {
    0%, 100% {
        opacity: 1;
    }
    50% {
        opacity: 0.7;
    }
}

.progress-actions {
    display: flex;
    gap: 10px;
}

.progress-actions .el-button {
    font-size: 0.8rem;
    color: #fff;
    background-color: #ff8c42;
    padding: 0.3em 0.6em;
    border-radius: 20px;
    border: 3px solid #f7a985;
    box-shadow: 0px 2px #f32b11;
    transition: all 0.1s ease;
}

.progress-actions .el-button:hover {
    background-color: #ff6347;
    transform: translateY(-1px);
    box-shadow: 0px 3px #f32b11;
}

.progress-actions .el-button:active {
    position: relative;
    top: 2px;
    border: 3px solid #ffb764;
    box-shadow: 0px 0px;
}

/* 原生消息提示容器 */
.native-message-container {
    position: fixed;
    top: 20px;
    right: 20px;
    z-index: 9999;
    max-width: 400px;
    pointer-events: none;
}

.native-message {
    background: linear-gradient(135deg, #fff8dc 0%, #fffacd 100%);
    border: 4px solid #f7a985;
    border-radius: 20px;
    padding: 15px 20px;
    margin-bottom: 15px;
    box-shadow: 
        0px 8px 16px rgba(255, 99, 71, 0.3),
        0px 4px 8px rgba(255, 140, 66, 0.2),
        inset 0px 2px 0px rgba(255, 255, 255, 0.5);
    display: flex;
    align-items: center;
    justify-content: space-between;
    transition: all 0.4s cubic-bezier(.4, 2, .6, 1);
    cursor: pointer;
    pointer-events: auto;
    font-family: 'CuteFont64', 'Comic Sans MS', cursive;
    font-size: 1rem;
    color: #8b4513;
    text-shadow: 1px 1px 0px rgba(255, 255, 255, 0.5);
    letter-spacing: 0.5px;
    opacity: 0;
    transform: translateX(100%) scale(0.8);
    position: relative;
    overflow: hidden;
}

.native-message::before {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.4), transparent);
    transition: left 0.6s ease;
}

.native-message:hover::before {
    left: 100%;
}

.native-message:hover {
    transform: translateY(-3px) scale(1.02);
    box-shadow: 
        0px 12px 24px rgba(255, 99, 71, 0.4),
        0px 6px 12px rgba(255, 140, 66, 0.3),
        inset 0px 2px 0px rgba(255, 255, 255, 0.6);
}

.native-message--visible {
    opacity: 1;
    transform: translateX(0) scale(1);
}

.native-message__icon {
    font-size: 1.8rem;
    margin-right: 15px;
    filter: drop-shadow(1px 1px 2px rgba(0, 0, 0, 0.1));
    animation: iconBounce 2s ease-in-out infinite;
}

.native-message__content {
    flex-grow: 1;
    line-height: 1.4;
    text-align: left;
}

.native-message__close {
    cursor: pointer;
    font-size: 1.2rem;
    margin-left: 15px;
    font-weight: 800;
    opacity: 0.7;
    transition: all 0.2s ease;
    color: #8b4513;
    text-shadow: 1px 1px 0px rgba(255, 255, 255, 0.5);
    padding: 5px;
    border-radius: 50%;
    background: rgba(255, 255, 255, 0.3);
    width: 24px;
    height: 24px;
    display: flex;
    align-items: center;
    justify-content: center;
    min-width: 24px;
}

.native-message__close:hover {
    opacity: 1;
    background: rgba(255, 99, 71, 0.2);
    transform: scale(1.1);
}

/* 不同类型的消息样式 */
.native-message--success {
    border-color: #90ee90;
    background: linear-gradient(135deg, #f0fff0 0%, #e6ffe6 100%);
    color: #2e8b57;
}

.native-message--success .native-message__icon {
    color: #2e8b57;
    animation: successPulse 2s ease-in-out infinite;
}

@keyframes successPulse {
    0%, 100% {
        transform: scale(1);
    }
    50% {
        transform: scale(1.1);
    }
}

.native-message--error {
    border-color: #ff6b6b;
    background: linear-gradient(135deg, #ffe6e6 0%, #ffcccc 100%);
    color: #dc143c;
}

.native-message--error .native-message__icon {
    color: #dc143c;
    animation: errorShake 0.5s ease-in-out;
}

@keyframes errorShake {
    0%, 100% {
        transform: translateX(0);
    }
    25% {
        transform: translateX(-3px);
    }
    75% {
        transform: translateX(3px);
    }
}

.native-message--warning {
    border-color: #ffa500;
    background: linear-gradient(135deg, #fffacd 0%, #fff8dc 100%);
    color: #b8860b;
}

.native-message--warning .native-message__icon {
    color: #ff8c00;
    animation: warningFlash 1s ease-in-out infinite;
}

@keyframes warningFlash {
    0%, 100% {
        opacity: 1;
    }
    50% {
        opacity: 0.6;
    }
}

.native-message--info {
    border-color: #87ceeb;
    background: linear-gradient(135deg, #f0f8ff 0%, #e6f3ff 100%);
    color: #4682b4;
}

.native-message--info .native-message__icon {
    color: #4682b4;
    animation: infoRotate 3s linear infinite;
}

@keyframes infoRotate {
    0% {
        transform: rotate(0deg);
    }
    100% {
        transform: rotate(360deg);
    }
}

/* 响应式设计 */
@media (max-width: 1200px) {
    .main-content {
        grid-template-columns: 1fr;
        gap: 20px;
        max-width: 100%;
    }
    
    .control-panel {
        max-width: 100%;
        margin-top: 15px;
    }
    
    .mobile-control-panel {
        display: flex;
    }
    
    .control-panel {
        display: none;
    }
}

@media (max-width: 768px) {
    .style-transfer {
        padding: 10px;
        font-size: 14px;
    }

    .header {
        padding: 15px 8px;
        margin-bottom: 20px;
    }

    .title {
        font-size: 2.5rem;
        letter-spacing: 3px;
        gap: 8px;
        flex-direction: column;
    }

    .title-icon {
        font-size: 2.2rem;
    }

    .subtitle {
        font-size: 1.2rem;
        letter-spacing: 1px;
        gap: 4px;
    }

    .section-title h2 {
        font-size: 1.5rem;
    }

    .image-container {
        height: 450px;
    }
    
    .input-uploader {
        height: 450px;
    }
    
    .control-panel {
        padding: 20px;
        gap: 15px;
    }

    .output-corner-actions {
        top: 12px;
        right: 12px;
        gap: 8px;
    }

    .corner-button {
        width: 42px;
        height: 42px;
        border-width: 2px;
    }

    .corner-button .el-icon {
        font-size: 1.1rem;
    }

    .native-message-container {
        top: 10px;
        right: 10px;
        left: 10px;
        max-width: none;
    }

    .native-message {
        padding: 12px 15px;
        font-size: 0.9rem;
        margin-bottom: 10px;
        border-width: 3px;
    }

    .native-message__icon {
        font-size: 1.5rem;
        margin-right: 10px;
    }

    .native-message__close {
        font-size: 1rem;
        width: 20px;
        height: 20px;
        min-width: 20px;
        margin-left: 10px;
    }

    /* 移动端加载圆圈优化 */
    .loading-spinner {
        width: 60px;
        height: 60px;
        border-width: 6px;
    }

    .loading-status {
        font-size: 0.9rem;
    }

    .progress-circle {
        width: 100px;
        height: 100px;
    }

    .progress-ring {
        width: 100px;
        height: 100px;
    }

    .progress-ring-circle {
        r: 42;
        cx: 50;
        cy: 50;
        stroke-width: 6;
    }

    .progress-circle-text {
        font-size: 1rem;
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
    }

    .progress-status {
        font-size: 0.9rem;
    }

    /* 移动端重新生成按钮优化 */
    .failed-actions .el-button,
    .loading-actions .el-button,
    .progress-actions .el-button {
        font-size: 0.7rem;
        padding: 0.4em 0.8em;
        min-width: 80px;
    }

    .image-actions .el-button {
        font-size: 0.7rem;
        padding: 0.3em 0.5em;
    }

    /* 移动端图片操作按钮布局优化 */
    .image-actions {
        flex-direction: column;
        gap: 3px;
    }

    .image-actions .el-button {
        min-width: 28px;
        height: 28px;
        padding: 0.2em 0.3em;
    }
}

@media (max-width: 480px) {
    .header {
        padding: 10px 5px;
    }

    .title {
        font-size: 2rem;
        letter-spacing: 1px;
    }

    .title-icon {
        font-size: 1.8rem;
    }

    .subtitle {
        font-size: 1rem;
        letter-spacing: 0.5px;
    }

    .title-glow {
        width: 250px;
        height: 60px;
    }

    .light-rays {
        width: 250px;
        height: 250px;
    }

    .ray {
        height: 60px;
    }

    .output-corner-actions {
        top: 10px;
        right: 10px;
        gap: 6px;
    }

    .corner-button {
        width: 36px;
        height: 36px;
        border-width: 2px;
    }

    .corner-button .el-icon {
        font-size: 1rem;
    }
    
    .image-container {
        height: 380px;
    }
    
    .input-uploader {
        height: 380px;
    }
    
    .control-panel,
    .mobile-control-panel {
        padding: 15px;
        gap: 12px;
    }

    /* 超小屏幕加载圆圈优化 */
    .loading-spinner {
        width: 50px;
        height: 50px;
        border-width: 5px;
    }

    .progress-circle {
        width: 80px;
        height: 80px;
    }

    .progress-ring {
        width: 80px;
        height: 80px;
    }

    .progress-ring-circle {
        r: 35;
        cx: 40;
        cy: 40;
        stroke-width: 5;
    }

    .progress-circle-text {
        font-size: 1rem;
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
    }

    .progress-status {
        font-size: 0.8rem;
    }

    /* 超小屏幕重新生成按钮优化 */
    .failed-actions .el-button,
    .loading-actions .el-button,
    .progress-actions .el-button {
        font-size: 0.6rem;
        padding: 0.3em 0.6em;
        min-width: 70px;
    }

    .image-actions .el-button {
        font-size: 0.6rem;
        padding: 0.2em 0.4em;
        min-width: 24px;
        height: 24px;
    }
}

/* 加载状态下的按钮样式 */
.image-actions .el-button.is-loading,
.failed-actions .el-button.is-loading,
.loading-actions .el-button.is-loading,
.progress-actions .el-button.is-loading {
    opacity: 0.8;
    cursor: not-allowed;
    pointer-events: none;
}

.image-actions .el-button.is-loading:hover,
.failed-actions .el-button.is-loading:hover,
.loading-actions .el-button.is-loading:hover,
.progress-actions .el-button.is-loading:hover {
    transform: none;
    box-shadow: 0px 2px #f32b11;
}

/* 确保加载状态下的按钮仍然可见 */
.el-button.is-loading .el-icon {
    animation: spin 1s linear infinite;
}

@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}
</style>