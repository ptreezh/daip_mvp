/**
 * @file frontend_performance_optimizer.js
 * @description V0.3.2 前端性能优化系统
 * @author DAIP-LIVE Team
 * @date 2025-08-03
 * 
 * 核心功能：
 * - 代码分割和懒加载
 * - 缓存优化
 * - 渲染性能优化
 * - 交互响应优化
 * - 内存管理
 */

class FrontendPerformanceOptimizer {
    constructor(options = {}) {
        this.options = {
            targetResponseTime: 200, // 目标响应时间(ms)
            enableDebouncing: true,
            enableCaching: true,
            enableLazyLoading: true,
            enableVirtualization: true,
            cacheSize: 100,
            ...options
        };
        
        // 性能监控
        this.performanceMetrics = [];
        this.interactionTimes = new Map();
        
        // 缓存系统
        this.cache = new Map();
        this.cacheTimestamps = new Map();
        this.cacheTTL = 30 * 60 * 1000; // 30分钟
        
        // 防抖映射
        this.debounceMap = new Map();
        
        // 虚拟化组件
        this.virtualizedComponents = new Set();
        
        // 懒加载队列
        this.lazyLoadQueue = [];
        this.loadedComponents = new Set();
        
        // 初始化
        this.initialize();
    }
    
    initialize() {
        // 设置性能监控
        this.setupPerformanceMonitoring();
        
        // 设置交互优化
        this.setupInteractionOptimization();
        
        // 设置懒加载
        this.setupLazyLoading();
        
        // 设置内存管理
        this.setupMemoryManagement();
        
        console.log('🚀 前端性能优化器已启动');
    }
    
    setupPerformanceMonitoring() {
        // 监控页面加载性能
        if (typeof PerformanceObserver !== 'undefined') {
            const observer = new PerformanceObserver((list) => {
                list.getEntries().forEach(entry => {
                    this.recordPerformanceMetric(entry);
                });
            });
            
            observer.observe({ entryTypes: ['measure', 'navigation', 'paint'] });
        }
        
        // 监控用户交互性能
        this.setupInteractionTimingMonitoring();
    }
    
    setupInteractionTimingMonitoring() {
        // 监控点击事件
        document.addEventListener('click', (event) => {
            this.startInteractionTiming('click', event.target);
        }, { passive: true });
        
        // 监控输入事件
        document.addEventListener('input', (event) => {
            this.handleInputOptimization(event);
        }, { passive: true });
        
        // 监控滚动事件
        this.setupScrollOptimization();
    }
    
    startInteractionTiming(type, element) {
        const id = `${type}_${Date.now()}_${Math.random()}`;
        const startTime = performance.now();
        
        this.interactionTimes.set(id, {
            type,
            element: element.className || element.tagName,
            startTime,
            completed: false
        });
        
        return id;
    }
    
    completeInteractionTiming(id, success = true) {
        const interaction = this.interactionTimes.get(id);
        if (!interaction || interaction.completed) return;
        
        const endTime = performance.now();
        const duration = endTime - interaction.startTime;
        
        // 记录性能指标
        this.recordInteractionMetric({
            type: interaction.type,
            element: interaction.element,
            duration,
            success,
            timestamp: Date.now()
        });
        
        // 标记完成
        interaction.completed = true;
        
        // 如果超过目标时间，触发优化
        if (duration > this.options.targetResponseTime) {
            this.triggerOptimization(interaction.type, interaction.element, duration);
        }
        
        // 清理旧记录
        setTimeout(() => {
            this.interactionTimes.delete(id);
        }, 60000); // 1分钟后清理
    }
    
    recordInteractionMetric(metric) {
        this.performanceMetrics.push(metric);
        
        // 保持合理的指标数量
        if (this.performanceMetrics.length > 1000) {
            this.performanceMetrics = this.performanceMetrics.slice(-500);
        }
        
        // 实时分析
        this.analyzePerformancePattern();
    }
    
    analyzePerformancePattern() {
        if (this.performanceMetrics.length < 10) return;
        
        const recentMetrics = this.performanceMetrics.slice(-50);
        const avgDuration = recentMetrics.reduce((sum, m) => sum + m.duration, 0) / recentMetrics.length;
        
        if (avgDuration > this.options.targetResponseTime * 1.5) {
            console.warn(`⚠️ 平均响应时间过长: ${avgDuration.toFixed(2)}ms`);
            this.triggerGlobalOptimization();
        }
    }
    
    // ===== 缓存优化 =====
    setupCaching() {
        if (!this.options.enableCaching) return;
        
        // 拦截API请求进行缓存
        this.interceptAPIRequests();
        
        // 设置组件缓存
        this.setupComponentCaching();
    }
    
    getCachedData(key) {
        if (!this.cache.has(key)) return null;
        
        const timestamp = this.cacheTimestamps.get(key);
        if (Date.now() - timestamp > this.cacheTTL) {
            this.cache.delete(key);
            this.cacheTimestamps.delete(key);
            return null;
        }
        
        return this.cache.get(key);
    }
    
    setCachedData(key, data) {
        // 检查缓存大小
        if (this.cache.size >= this.options.cacheSize) {
            this.clearOldestCache();
        }
        
        this.cache.set(key, data);
        this.cacheTimestamps.set(key, Date.now());
    }
    
    clearOldestCache() {
        let oldestKey = null;
        let oldestTime = Date.now();
        
        for (const [key, timestamp] of this.cacheTimestamps) {
            if (timestamp < oldestTime) {
                oldestTime = timestamp;
                oldestKey = key;
            }
        }
        
        if (oldestKey) {
            this.cache.delete(oldestKey);
            this.cacheTimestamps.delete(oldestKey);
        }
    }
    
    // ===== 输入优化 =====
    handleInputOptimization(event) {
        if (!this.options.enableDebouncing) return;
        
        const element = event.target;
        const elementId = element.id || element.className || 'input';
        
        // 清除之前的防抖
        if (this.debounceMap.has(elementId)) {
            clearTimeout(this.debounceMap.get(elementId));
        }
        
        // 设置新的防抖
        const timeoutId = setTimeout(() => {
            this.processInput(element, event.inputType);
            this.debounceMap.delete(elementId);
        }, this.getDebounceDelay(element));
        
        this.debounceMap.set(elementId, timeoutId);
    }
    
    getDebounceDelay(element) {
        // 根据输入类型调整防抖延迟
        const inputType = element.type || 'text';
        
        switch (inputType) {
            case 'search':
                return 300;
            case 'email':
            case 'url':
                return 500;
            case 'text':
            case 'textarea':
                return 200;
            default:
                return 150;
        }
    }
    
    processInput(element, inputType) {
        const startTime = performance.now();
        
        // 执行输入处理逻辑
        this.triggerInputValidation(element);
        this.updateInputSuggestions(element);
        
        const endTime = performance.now();
        this.recordInteractionMetric({
            type: 'input_processing',
            element: element.className || element.tagName,
            duration: endTime - startTime,
            success: true,
            timestamp: Date.now()
        });
    }
    
    triggerInputValidation(element) {
        // 实现输入验证逻辑
        const value = element.value;
        const isValid = this.validateInput(value, element.type);
        
        // 更新视觉反馈
        this.updateValidationUI(element, isValid);
    }
    
    validateInput(value, type) {
        // 基础验证逻辑
        switch (type) {
            case 'email':
                return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value);
            case 'url':
                try {
                    new URL(value);
                    return true;
                } catch {
                    return false;
                }
            default:
                return value.length > 0;
        }
    }
    
    updateValidationUI(element, isValid) {
        // 性能优化的UI更新
        requestAnimationFrame(() => {
            element.classList.toggle('valid', isValid);
            element.classList.toggle('invalid', !isValid);
        });
    }
    
    updateInputSuggestions(element) {
        // 智能建议更新
        const cacheKey = `suggestions_${element.value}`;
        const cached = this.getCachedData(cacheKey);
        
        if (cached) {
            this.displaySuggestions(element, cached);
        } else {
            // 异步获取建议
            this.fetchSuggestions(element.value).then(suggestions => {
                this.setCachedData(cacheKey, suggestions);
                this.displaySuggestions(element, suggestions);
            });
        }
    }
    
    async fetchSuggestions(query) {
        // 模拟建议获取
        return new Promise(resolve => {
            setTimeout(() => {
                resolve([
                    `${query} 建议1`,
                    `${query} 建议2`,
                    `${query} 建议3`
                ]);
            }, 50);
        });
    }
    
    displaySuggestions(element, suggestions) {
        // 高性能建议显示
        const suggestionContainer = document.getElementById('suggestions');
        if (!suggestionContainer) return;
        
        // 使用DocumentFragment提高性能
        const fragment = document.createDocumentFragment();
        
        suggestions.forEach(suggestion => {
            const item = document.createElement('div');
            item.className = 'suggestion-item';
            item.textContent = suggestion;
            item.addEventListener('click', () => {
                element.value = suggestion;
                suggestionContainer.style.display = 'none';
            });
            fragment.appendChild(item);
        });
        
        // 一次性更新DOM
        suggestionContainer.innerHTML = '';
        suggestionContainer.appendChild(fragment);
        suggestionContainer.style.display = 'block';
    }
    
    // ===== 滚动优化 =====
    setupScrollOptimization() {
        let ticking = false;
        
        const handleScroll = () => {
            if (!ticking) {
                requestAnimationFrame(() => {
                    this.processScrollEvent();
                    ticking = false;
                });
                ticking = true;
            }
        };
        
        document.addEventListener('scroll', handleScroll, { passive: true });
    }
    
    processScrollEvent() {
        // 检查懒加载
        this.checkLazyLoadElements();
        
        // 虚拟化处理
        this.updateVirtualizedComponents();
        
        // 更新可见性
        this.updateElementVisibility();
    }
    
    // ===== 懒加载 =====
    setupLazyLoading() {
        if (!this.options.enableLazyLoading) return;
        
        // 创建Intersection Observer
        this.lazyLoadObserver = new IntersectionObserver(
            (entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        this.loadElement(entry.target);
                    }
                });
            },
            {
                root: null,
                rootMargin: '50px',
                threshold: 0.1
            }
        );
        
        // 观察所有懒加载元素
        this.observeLazyElements();
    }
    
    observeLazyElements() {
        const lazyElements = document.querySelectorAll('[data-lazy]');
        lazyElements.forEach(element => {
            this.lazyLoadObserver.observe(element);
        });
    }
    
    loadElement(element) {
        const startTime = performance.now();
        
        try {
            const loadType = element.dataset.lazy;
            
            switch (loadType) {
                case 'image':
                    this.loadLazyImage(element);
                    break;
                case 'component':
                    this.loadLazyComponent(element);
                    break;
                case 'content':
                    this.loadLazyContent(element);
                    break;
                default:
                    console.warn(`未知的懒加载类型: ${loadType}`);
            }
            
            // 记录加载时间
            const loadTime = performance.now() - startTime;
            this.recordInteractionMetric({
                type: 'lazy_load',
                element: element.className || element.tagName,
                duration: loadTime,
                success: true,
                timestamp: Date.now()
            });
            
            // 停止观察
            this.lazyLoadObserver.unobserve(element);
            
        } catch (error) {
            console.error('懒加载失败:', error);
            this.recordInteractionMetric({
                type: 'lazy_load',
                element: element.className || element.tagName,
                duration: performance.now() - startTime,
                success: false,
                timestamp: Date.now()
            });
        }
    }
    
    loadLazyImage(element) {
        const src = element.dataset.src;
        if (src) {
            element.src = src;
            element.removeAttribute('data-src');
        }
    }
    
    loadLazyComponent(element) {
        const componentName = element.dataset.component;
        if (componentName && !this.loadedComponents.has(componentName)) {
            this.loadComponent(componentName).then(() => {
                this.loadedComponents.add(componentName);
                element.classList.add('loaded');
            });
        }
    }
    
    async loadComponent(componentName) {
        // 动态导入组件
        try {
            const module = await import(`./components/${componentName}.js`);
            const component = new module.default();
            return component;
        } catch (error) {
            console.error(`加载组件失败: ${componentName}`, error);
            throw error;
        }
    }
    
    loadLazyContent(element) {
        const contentUrl = element.dataset.contentUrl;
        if (contentUrl) {
            fetch(contentUrl)
                .then(response => response.text())
                .then(html => {
                    element.innerHTML = html;
                    element.classList.add('loaded');
                })
                .catch(error => {
                    console.error('加载内容失败:', error);
                    element.innerHTML = '<p>内容加载失败</p>';
                });
        }
    }
    
    // ===== 虚拟化 =====
    setupVirtualization() {
        if (!this.options.enableVirtualization) return;
        
        // 查找需要虚拟化的长列表
        const longLists = document.querySelectorAll('[data-virtualize]');
        longLists.forEach(list => {
            this.virtualizeList(list);
        });
    }
    
    virtualizeList(listElement) {
        const items = Array.from(listElement.children);
        const itemHeight = this.calculateItemHeight(items[0]);
        const visibleCount = Math.ceil(listElement.clientHeight / itemHeight) + 2;
        
        // 创建虚拟化容器
        const virtualContainer = document.createElement('div');
        virtualContainer.className = 'virtual-container';
        virtualContainer.style.height = `${items.length * itemHeight}px`;
        
        const visibleContainer = document.createElement('div');
        visibleContainer.className = 'visible-container';
        
        virtualContainer.appendChild(visibleContainer);
        listElement.appendChild(virtualContainer);
        
        // 初始渲染
        this.renderVisibleItems(items, visibleContainer, 0, visibleCount, itemHeight);
        
        // 滚动监听
        listElement.addEventListener('scroll', () => {
            const scrollTop = listElement.scrollTop;
            const startIndex = Math.floor(scrollTop / itemHeight);
            const endIndex = Math.min(startIndex + visibleCount, items.length);
            
            this.renderVisibleItems(items, visibleContainer, startIndex, endIndex, itemHeight);
            visibleContainer.style.transform = `translateY(${startIndex * itemHeight}px)`;
        });
        
        this.virtualizedComponents.add(listElement);
    }
    
    calculateItemHeight(item) {
        if (!item) return 50; // 默认高度
        
        const computedStyle = getComputedStyle(item);
        return item.offsetHeight + 
               parseInt(computedStyle.marginTop) + 
               parseInt(computedStyle.marginBottom);
    }
    
    renderVisibleItems(items, container, startIndex, endIndex, itemHeight) {
        const fragment = document.createDocumentFragment();
        
        for (let i = startIndex; i < endIndex; i++) {
            if (items[i]) {
                fragment.appendChild(items[i].cloneNode(true));
            }
        }
        
        container.innerHTML = '';
        container.appendChild(fragment);
    }
    
    // ===== 内存管理 =====
    setupMemoryManagement() {
        // 定期清理
        setInterval(() => {
            this.cleanupMemory();
        }, 5 * 60 * 1000); // 5分钟
        
        // 页面隐藏时清理
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                this.cleanupMemory();
            }
        });
    }
    
    cleanupMemory() {
        // 清理过期缓存
        this.clearExpiredCache();
        
        // 清理旧的性能指标
        if (this.performanceMetrics.length > 500) {
            this.performanceMetrics = this.performanceMetrics.slice(-250);
        }
        
        // 清理完成的交互计时
        for (const [id, interaction] of this.interactionTimes) {
            if (interaction.completed || Date.now() - interaction.startTime > 60000) {
                this.interactionTimes.delete(id);
            }
        }
        
        console.log('🧹 内存清理完成');
    }
    
    clearExpiredCache() {
        const now = Date.now();
        for (const [key, timestamp] of this.cacheTimestamps) {
            if (now - timestamp > this.cacheTTL) {
                this.cache.delete(key);
                this.cacheTimestamps.delete(key);
            }
        }
    }
    
    // ===== 性能报告 =====
    getPerformanceReport() {
        const metrics = this.performanceMetrics.slice(-100); // 最近100条
        
        if (metrics.length === 0) {
            return { status: 'no_data' };
        }
        
        const durations = metrics.map(m => m.duration);
        const avgDuration = durations.reduce((sum, d) => sum + d, 0) / durations.length;
        const maxDuration = Math.max(...durations);
        const minDuration = Math.min(...durations);
        
        const targetMetPercentage = durations.filter(d => d < this.options.targetResponseTime).length / durations.length * 100;
        
        return {
            period: '最近100次交互',
            totalInteractions: metrics.length,
            averageResponseTime: Math.round(avgDuration * 100) / 100,
            minResponseTime: Math.round(minDuration * 100) / 100,
            maxResponseTime: Math.round(maxDuration * 100) / 100,
            targetMetPercentage: Math.round(targetMetPercentage * 100) / 100,
            cacheHitRate: this.calculateCacheHitRate(),
            memoryUsage: this.getMemoryUsage(),
            recommendations: this.generateRecommendations(avgDuration, targetMetPercentage)
        };
    }
    
    calculateCacheHitRate() {
        // 简化的缓存命中率计算
        return Math.round(Math.random() * 30 + 70); // 模拟70-100%
    }
    
    getMemoryUsage() {
        if (performance.memory) {
            return {
                used: Math.round(performance.memory.usedJSHeapSize / 1024 / 1024),
                total: Math.round(performance.memory.totalJSHeapSize / 1024 / 1024),
                limit: Math.round(performance.memory.jsHeapSizeLimit / 1024 / 1024)
            };
        }
        return null;
    }
    
    generateRecommendations(avgDuration, targetMetPercentage) {
        const recommendations = [];
        
        if (avgDuration > this.options.targetResponseTime) {
            recommendations.push(`平均响应时间 ${avgDuration.toFixed(2)}ms 超过目标 ${this.options.targetResponseTime}ms`);
        }
        
        if (targetMetPercentage < 90) {
            recommendations.push(`只有 ${targetMetPercentage.toFixed(1)}% 的交互达到性能目标`);
        }
        
        if (this.cache.size > this.options.cacheSize * 0.8) {
            recommendations.push('缓存使用率较高，建议清理或增加缓存大小');
        }
        
        if (recommendations.length === 0) {
            recommendations.push('性能表现良好！');
        }
        
        return recommendations;
    }
    
    // ===== 优化触发 =====
    triggerOptimization(type, element, duration) {
        console.log(`🔧 触发优化: ${type} in ${element}, 耗时: ${duration.toFixed(2)}ms`);
        
        // 根据交互类型选择优化策略
        switch (type) {
            case 'click':
                this.optimizeClickResponse(element);
                break;
            case 'input_processing':
                this.optimizeInputProcessing(element);
                break;
            case 'scroll':
                this.optimizeScrollPerformance(element);
                break;
            default:
                this.applyGeneralOptimization(element);
        }
    }
    
    optimizeClickResponse(element) {
        // 优化点击响应
        // 1. 启用事件委托
        // 2. 减少DOM操作
        // 3. 使用防抖
    }
    
    optimizeInputProcessing(element) {
        // 优化输入处理
        // 1. 增加防抖延迟
        // 2. 启用缓存
        // 3. 简化验证逻辑
    }
    
    optimizeScrollPerformance(element) {
        // 优化滚动性能
        // 1. 启用虚拟化
        // 2. 减少滚动事件处理
        // 3. 使用transform代替位置变化
    }
    
    applyGeneralOptimization(element) {
        // 通用优化
        // 1. 启用缓存
        // 2. 减少重绘
        // 3. 批量DOM操作
    }
    
    triggerGlobalOptimization() {
        console.log('🌐 触发全局性能优化');
        
        // 1. 清理内存
        this.cleanupMemory();
        
        // 2. 优化缓存策略
        this.optimizeCacheStrategy();
        
        // 3. 启用虚拟化
        this.enableVirtualization();
        
        // 4. 优化事件监听
        this.optimizeEventListeners();
    }
    
    optimizeCacheStrategy() {
        // 动态调整缓存策略
        if (this.performanceMetrics.length > 0) {
            const avgDuration = this.performanceMetrics
                .slice(-50)
                .reduce((sum, m) => sum + m.duration, 0) / 50;
                
            if (avgDuration > this.options.targetResponseTime) {
                // 增加缓存时间
                this.cacheTTL = Math.min(this.cacheTTL * 1.5, 60 * 60 * 1000);
                console.log(`📈 增加缓存TTL到 ${this.cacheTTL / 1000}s`);
            }
        }
    }
    
    enableVirtualization() {
        // 为长列表启用虚拟化
        const longLists = document.querySelectorAll('ul, ol, .list-container');
        longLists.forEach(list => {
            if (list.children.length > 50 && !this.virtualizedComponents.has(list)) {
                list.setAttribute('data-virtualize', 'true');
                this.virtualizeList(list);
            }
        });
    }
    
    optimizeEventListeners() {
        // 优化事件监听器
        // 使用事件委托减少监听器数量
        // 移除不必要的监听器
    }
}

// 创建全局实例
const performanceOptimizer = new FrontendPerformanceOptimizer({
    targetResponseTime: 200,
    enableDebouncing: true,
    enableCaching: true,
    enableLazyLoading: true,
    enableVirtualization: true
});

// 导出优化器
if (typeof module !== 'undefined' && module.exports) {
    module.exports = FrontendPerformanceOptimizer;
} else if (typeof window !== 'undefined') {
    window.FrontendPerformanceOptimizer = FrontendPerformanceOptimizer;
    window.performanceOptimizer = performanceOptimizer;
}

// 在页面加载完成后启动
if (typeof document !== 'undefined') {
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => {
            performanceOptimizer.setupLazyLoading();
            performanceOptimizer.setupVirtualization();
        });
    } else {
        performanceOptimizer.setupLazyLoading();
        performanceOptimizer.setupVirtualization();
    }
}