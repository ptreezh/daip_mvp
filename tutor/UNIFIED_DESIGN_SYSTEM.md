# 🎨 统一设计系统 (Unified Design System)

## 📋 概述

本文档定义了整个网站的统一设计系统，确保所有页面在视觉风格、交互体验和组件使用上保持一致性，提升用户体验和品牌识别度。

## 🎯 设计原则

### 1. 一致性原则
- 所有页面使用统一的颜色、字体、间距系统
- 组件样式和行为保持一致
- 导航结构和交互模式统一

### 2. 可用性原则
- 界面清晰易懂
- 操作反馈及时明确
- 无障碍访问支持

### 3. 美观性原则
- 现代化视觉设计
- 合理的视觉层次
- 适度的动效增强体验

### 4. 响应式原则
- 适配各种设备屏幕
- 触控友好的交互设计
- 性能优化的加载体验

## 🎨 视觉设计规范

### 1. 颜色系统

#### 主要色彩
```css
:root {
  /* 主色调 - 科技蓝紫渐变 */
  --primary-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  --secondary-gradient: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  --accent-gradient: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
  
  /* 语义化颜色 */
  --primary: #667eea;
  --primary-dark: #5a67d8;
  --primary-light: #93c5fd;
  --secondary: #764ba2;
  --secondary-dark: #6b46c1;
  --accent: #4facfe;
  --success: #10b981;
  --success-dark: #059669;
  --warning: #f59e0b;
  --warning-dark: #d97706;
  --error: #ef4444;
  --error-dark: #dc2626;
  --info: #3b82f6;
  
  /* 中性色系 */
  --gray-50: #f9fafb;
  --gray-100: #f3f4f6;
  --gray-200: #e5e7eb;
  --gray-300: #d1d5db;
  --gray-400: #9ca3af;
  --gray-500: #6b7280;
  --gray-600: #4b5563;
  --gray-700: #374151;
  --gray-800: #1f2937;
  --gray-900: #111827;
  
  /* 背景色 */
  --bg-primary: #ffffff;
  --bg-secondary: #f9fafb;
  --bg-tertiary: #f3f4f6;
  --bg-dark: #1f2937;
  --bg-gradient: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
  
  /* 文字颜色 */
  --text-primary: #111827;
  --text-secondary: #4b5563;
  --text-tertiary: #6b7280;
  --text-muted: #9ca3af;
  --text-inverse: #ffffff;
  
  /* 边框颜色 */
  --border-primary: #e5e7eb;
  --border-secondary: #d1d5db;
  --border-tertiary: #cbd5e1;
  --border-accent: var(--primary);
}
```

#### 颜色使用指南
```markdown
## 颜色应用场景

### 主要操作颜色
- **Primary (#667eea)**: 主要按钮、重要链接、激活状态
- **Secondary (#764ba2)**: 次要按钮、辅助操作
- **Accent (#4facfe)**: 强调元素、高亮信息

### 状态反馈颜色
- **Success (#10b981)**: 成功状态、正确答案、完成操作
- **Warning (#f59e0b)**: 警告信息、需要注意的事项
- **Error (#ef4444)**: 错误状态、失败操作、危险操作
- **Info (#3b82f6)**: 信息提示、帮助说明

### 背景和文字
- **Bg-primary (#ffffff)**: 主要背景色
- **Bg-secondary (#f9fafb)**: 次要背景色、卡片背景
- **Text-primary (#111827)**: 主要文字颜色
- **Text-secondary (#4b5563)**: 次要文字、说明文字
```

### 2. 字体系统

#### 字体家族
```css
:root {
  /* 主字体 */
  --font-sans: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  --font-serif: Georgia, 'Times New Roman', Times, serif;
  --font-mono: 'Fira Code', 'JetBrains Mono', 'Monaco', 'Consolas', monospace;
  
  /* 字重 */
  --font-thin: 100;
  --font-extralight: 200;
  --font-light: 300;
  --font-normal: 400;
  --font-medium: 500;
  --font-semibold: 600;
  --font-bold: 700;
  --font-extrabold: 800;
  --font-black: 900;
  
  /* 字号 */
  --text-xs: 0.75rem;     /* 12px */
  --text-sm: 0.875rem;     /* 14px */
  --text-base: 1rem;       /* 16px */
  --text-lg: 1.125rem;     /* 18px */
  --text-xl: 1.25rem;      /* 20px */
  --text-2xl: 1.5rem;      /* 24px */
  --text-3xl: 1.875rem;    /* 30px */
  --text-4xl: 2.25rem;     /* 36px */
  --text-5xl: 3rem;        /* 48px */
  --text-6xl: 3.75rem;     /* 60px */
  
  /* 行高 */
  --leading-none: 1;
  --leading-tight: 1.25;
  --leading-snug: 1.375;
  --leading-normal: 1.5;
  --leading-relaxed: 1.625;
  --leading-loose: 2;
}
```

#### 字体使用规范
```markdown
## 字体层级规范

### 标题层级
- **H1**: 3rem (48px), bold, primary color
- **H2**: 2.25rem (36px), semibold, primary color
- **H3**: 1.875rem (30px), semibold, primary color
- **H4**: 1.5rem (24px), semibold, secondary color
- **H5**: 1.25rem (20px), medium, secondary color
- **H6**: 1.125rem (18px), medium, tertiary color

### 正文层级
- **正文大**: 1.125rem (18px), regular, primary text
- **正文**: 1rem (16px), regular, primary text
- **正文小**: 0.875rem (14px), regular, secondary text
- **辅助文字**: 0.75rem (12px), regular, tertiary text

### 特殊用途
- **代码**: 0.875rem (14px), mono font, inline code bg
- **引用**: 1rem (16px), italic, muted text
- **链接**: 1rem (16px), primary color, underline on hover
```

### 3. 间距系统

```css
:root {
  /* 间距单位 */
  --space-px: 1px;
  --space-0: 0;
  --space-0-5: 0.125rem;   /* 2px */
  --space-1: 0.25rem;      /* 4px */
  --space-1-5: 0.375rem;   /* 6px */
  --space-2: 0.5rem;       /* 8px */
  --space-2-5: 0.625rem;   /* 10px */
  --space-3: 0.75rem;      /* 12px */
  --space-3-5: 0.875rem;   /* 14px */
  --space-4: 1rem;         /* 16px */
  --space-5: 1.25rem;      /* 20px */
  --space-6: 1.5rem;       /* 24px */
  --space-7: 1.75rem;      /* 28px */
  --space-8: 2rem;         /* 32px */
  --space-9: 2.25rem;      /* 36px */
  --space-10: 2.5rem;      /* 40px */
  --space-12: 3rem;        /* 48px */
  --space-16: 4rem;        /* 64px */
  --space-20: 5rem;        /* 80px */
  --space-24: 6rem;        /* 96px */
  --space-32: 8rem;        /* 128px */
  --space-40: 10rem;       /* 160px */
  --space-48: 12rem;       /* 192px */
  --space-56: 14rem;       /* 224px */
  --space-64: 16rem;       /* 256px */
}
```

### 4. 圆角系统

```css
:root {
  --radius-xs: 0.125rem;   /* 2px */
  --radius-sm: 0.25rem;    /* 4px */
  --radius: 0.375rem;      /* 6px */
  --radius-md: 0.5rem;     /* 8px */
  --radius-lg: 0.75rem;    /* 12px */
  --radius-xl: 1rem;       /* 16px */
  --radius-2xl: 1.5rem;    /* 24px */
  --radius-3xl: 2rem;      /* 32px */
  --radius-full: 9999px;
}
```

### 5. 阴影系统

```css
:root {
  --shadow-xs: 0 1px 2px 0 rgb(0 0 0 / 0.05);
  --shadow-sm: 0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1);
  --shadow: 0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1);
  --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
  --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1);
  --shadow-xl: 0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1);
  --shadow-2xl: 0 25px 50px -12px rgb(0 0 0 / 0.25);
  --shadow-inner: inset 0 2px 4px 0 rgb(0 0 0 / 0.06);
}
```

## 🧩 组件库规范

### 1. 按钮组件

#### 基础样式
```css
/* 基础按钮样式 */
.unified-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-2);
  padding: var(--space-3) var(--space-6);
  border-radius: var(--radius-lg);
  font-size: var(--text-base);
  font-weight: var(--font-semibold);
  text-decoration: none;
  transition: all 0.2s ease;
  border: none;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  white-space: nowrap;
  min-height: 40px;
}

/* 按钮变体 */
.unified-btn-primary {
  background: var(--primary-gradient);
  color: var(--text-inverse);
  box-shadow: var(--shadow);
}

.unified-btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-lg);
}

.unified-btn-primary:active {
  transform: translateY(0);
  box-shadow: var(--shadow);
}

.unified-btn-secondary {
  background: var(--bg-primary);
  color: var(--text-primary);
  border: 1px solid var(--border-secondary);
  box-shadow: var(--shadow-xs);
}

.unified-btn-secondary:hover {
  background: var(--gray-50);
  border-color: var(--primary);
  transform: translateY(-1px);
  box-shadow: var(--shadow-sm);
}

.unified-btn-outline {
  background: transparent;
  color: var(--primary);
  border: 1px solid var(--primary);
}

.unified-btn-outline:hover {
  background: var(--primary);
  color: var(--text-inverse);
}

.unified-btn-success {
  background: var(--success-gradient);
  color: var(--text-inverse);
}

.unified-btn-warning {
  background: var(--warning-gradient);
  color: var(--text-inverse);
}

.unified-btn-error {
  background: var(--error-gradient);
  color: var(--text-inverse);
}

/* 按钮尺寸 */
.unified-btn-sm {
  padding: var(--space-2) var(--space-4);
  font-size: var(--text-sm);
  min-height: 32px;
}

.unified-btn-lg {
  padding: var(--space-4) var(--space-8);
  font-size: var(--text-lg);
  min-height: 48px;
}

/* 按钮状态 */
.unified-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none !important;
  box-shadow: none !important;
}

.unified-btn-loading {
  position: relative;
  pointer-events: none;
}

.unified-btn-loading::after {
  content: '';
  width: 16px;
  height: 16px;
  border: 2px solid transparent;
  border-top-color: currentColor;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}
```

#### 使用示例
```html
<!-- 主要按钮 -->
<button class="unified-btn unified-btn-primary">
  <i class="fas fa-download"></i>
  下载资料
</button>

<!-- 次要按钮 -->
<button class="unified-btn unified-btn-secondary">
  取消
</button>

<!-- 成功按钮 -->
<button class="unified-btn unified-btn-success">
  提交
</button>

<!-- 小尺寸按钮 -->
<button class="unified-btn unified-btn-primary unified-btn-sm">
  小按钮
</button>

<!-- 大尺寸按钮 -->
<button class="unified-btn unified-btn-primary unified-btn-lg">
  大按钮
</button>

<!-- 禁用状态 -->
<button class="unified-btn unified-btn-primary" disabled>
  禁用按钮
</button>
```

### 2. 卡片组件

#### 基础样式
```css
/* 基础卡片样式 */
.unified-card {
  background: var(--bg-primary);
  border: 1px solid var(--border-primary);
  border-radius: var(--radius-xl);
  padding: var(--space-8);
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
  box-shadow: var(--shadow-xs);
}

.unified-card:hover {
  border-color: var(--primary-light);
  box-shadow: var(--shadow-xl);
  transform: translateY(-4px);
}

/* 卡片头部 */
.unified-card-header {
  display: flex;
  align-items: center;
  gap: var(--space-4);
  margin-bottom: var(--space-6);
}

.unified-card-icon {
  width: 3rem;
  height: 3rem;
  background: var(--primary-gradient);
  border-radius: var(--radius-lg);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 1.25rem;
  font-weight: var(--font-bold);
  flex-shrink: 0;
}

.unified-card-title {
  font-size: var(--text-2xl);
  font-weight: var(--font-bold);
  color: var(--text-primary);
  line-height: var(--leading-tight);
  margin: 0;
}

.unified-card-description {
  color: var(--text-secondary);
  margin-bottom: var(--space-6);
  line-height: var(--leading-relaxed);
}

.unified-card-content {
  margin-bottom: var(--space-6);
}

.unified-card-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-4);
  margin-top: var(--space-6);
  padding-top: var(--space-6);
  border-top: 1px solid var(--border-primary);
}

/* 卡片变体 */
.unified-card-primary {
  border-top: 4px solid var(--primary);
}

.unified-card-success {
  border-top: 4px solid var(--success);
}

.unified-card-warning {
  border-top: 4px solid var(--warning);
}

.unified-card-error {
  border-top: 4px solid var(--error);
}
```

#### 使用示例
```html
<!-- 基础卡片 -->
<div class="unified-card">
  <div class="unified-card-header">
    <div class="unified-card-icon">
      <i class="fas fa-rocket"></i>
    </div>
    <h3 class="unified-card-title">快速开始</h3>
  </div>
  <p class="unified-card-description">
    通过简单的几步快速上手我们的平台
  </p>
  <div class="unified-card-content">
    <ul>
      <li>注册账户</li>
      <li>创建第一个项目</li>
      <li>邀请团队成员</li>
    </ul>
  </div>
  <div class="unified-card-footer">
    <button class="unified-btn unified-btn-primary">
      立即开始
    </button>
  </div>
</div>
```

### 3. 导航组件

#### 顶部导航
```css
/* 统一导航栏 */
.unified-navbar {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-bottom: 1px solid var(--border-primary);
  position: sticky;
  top: 0;
  z-index: 50;
  transition: all 0.3s ease;
}

.unified-navbar.scrolled {
  background: rgba(255, 255, 255, 0.98);
  box-shadow: var(--shadow-sm);
}

.navbar-container {
  display: flex;
  align-items: center;
  justify-content: space-between;
  max-width: 1280px;
  height: 4rem;
  margin: 0 auto;
  padding: 0 var(--space-6);
}

.navbar-brand {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  font-size: var(--text-xl);
  font-weight: var(--font-bold);
  color: var(--primary);
  text-decoration: none;
  background: var(--primary-gradient);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.navbar-logo {
  width: 2rem;
  height: 2rem;
}

.navbar-nav {
  display: flex;
  align-items: center;
  gap: var(--space-1);
  list-style: none;
}

.nav-link {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-2) var(--space-4);
  border-radius: var(--radius-full);
  color: var(--text-secondary);
  text-decoration: none;
  font-weight: var(--font-medium);
  transition: all 0.2s ease;
  white-space: nowrap;
}

.nav-link:hover,
.nav-link.active {
  color: var(--primary);
  background-color: var(--gray-100);
}

.navbar-actions {
  display: flex;
  align-items: center;
  gap: var(--space-3);
}

/* 移动端汉堡菜单 */
.navbar-toggle {
  display: none;
  flex-direction: column;
  justify-content: space-around;
  width: 2rem;
  height: 2rem;
  background: transparent;
  border: none;
  cursor: pointer;
  padding: 0;
}

.navbar-toggle span {
  width: 100%;
  height: 2px;
  background: var(--text-primary);
  border-radius: var(--radius);
  transition: all 0.3s ease;
}

@media (max-width: 768px) {
  .navbar-toggle {
    display: flex;
  }
  
  .navbar-nav {
    position: fixed;
    top: 4rem;
    left: 0;
    right: 0;
    background: var(--bg-primary);
    flex-direction: column;
    align-items: stretch;
    padding: var(--space-4);
    border-bottom: 1px solid var(--border-primary);
    transform: translateY(-100%);
    opacity: 0;
    visibility: hidden;
    transition: all 0.3s ease;
  }
  
  .navbar-nav.active {
    transform: translateY(0);
    opacity: 1;
    visibility: visible;
  }
  
  .nav-link {
    padding: var(--space-3) var(--space-4);
    justify-content: center;
  }
}
```

#### 使用示例
```html
<!-- 顶部导航栏 -->
<nav class="unified-navbar" id="navbar">
  <div class="navbar-container">
    <a href="index.html" class="navbar-brand">
      <span class="navbar-logo">🤖</span>
      <span>0代码AI规范化编程</span>
    </a>
    
    <button class="navbar-toggle" id="navbarToggle">
      <span></span>
      <span></span>
      <span></span>
    </button>
    
    <ul class="navbar-nav" id="navbarNav">
      <li><a href="index.html" class="nav-link active">首页</a></li>
      <li><a href="#learning" class="nav-link">学习</a></li>
      <li><a href="#modules" class="nav-link">模块</a></li>
      <li><a href="#projects" class="nav-link">项目</a></li>
      <li><a href="#resources" class="nav-link">资源</a></li>
    </ul>
    
    <div class="navbar-actions">
      <a href="#start-learning" class="unified-btn unified-btn-primary">
        开始学习
      </a>
    </div>
  </div>
</nav>
```

### 4. 标签组件

#### 基础样式
```css
/* 统一标签组件 */
.unified-tag {
  display: inline-flex;
  align-items: center;
  gap: var(--space-1);
  padding: var(--space-1) var(--space-3);
  border-radius: var(--radius-full);
  font-size: 0.875rem;
  font-weight: var(--font-medium);
  background: var(--primary-gradient);
  color: var(--text-inverse);
  border: none;
  cursor: default;
  white-space: nowrap;
  transition: all 0.2s ease;
}

.unified-tag:hover {
  transform: translateY(-1px);
  box-shadow: var(--shadow-sm);
}

/* 标签变体 */
.unified-tag-outline {
  background: transparent;
  color: var(--primary);
  border: 1px solid var(--primary);
}

.unified-tag-outline:hover {
  background: var(--primary);
  color: var(--text-inverse);
}

.unified-tag-success {
  background: var(--success-gradient);
}

.unified-tag-warning {
  background: var(--warning-gradient);
}

.unified-tag-error {
  background: var(--error-gradient);
}

.unified-tag-secondary {
  background: var(--secondary-gradient);
}

/* 标签尺寸 */
.unified-tag-sm {
  padding: var(--space-0-5) var(--space-2);
  font-size: 0.75rem;
}

.unified-tag-lg {
  padding: var(--space-2) var(--space-4);
  font-size: 1rem;
}
```

#### 使用示例
```html
<!-- 基础标签 -->
<span class="unified-tag">
  <i class="fas fa-star"></i>
  热门
</span>

<!-- 轮廓标签 -->
<span class="unified-tag unified-tag-outline">
  新功能
</span>

<!-- 成功标签 -->
<span class="unified-tag unified-tag-success">
  已完成
</span>

<!-- 警告标签 -->
<span class="unified-tag unified-tag-warning">
  进行中
</span>
```

## 📱 响应式设计规范

### 1. 断点系统

```css
/* 响应式断点 */
:root {
  --breakpoint-sm: 640px;
  --breakpoint-md: 768px;
  --breakpoint-lg: 1024px;
  --breakpoint-xl: 1280px;
  --breakpoint-2xl: 1536px;
}

/* 容器系统 */
.container {
  width: 100%;
  margin-left: auto;
  margin-right: auto;
  padding-left: var(--space-4);
  padding-right: var(--space-4);
}

@media (min-width: 640px) {
  .container {
    max-width: 640px;
    padding-left: var(--space-6);
    padding-right: var(--space-6);
  }
}

@media (min-width: 768px) {
  .container {
    max-width: 768px;
  }
}

@media (min-width: 1024px) {
  .container {
    max-width: 1024px;
    padding-left: var(--space-8);
    padding-right: var(--space-8);
  }
}

@media (min-width: 1280px) {
  .container {
    max-width: 1280px;
  }
}

@media (min-width: 1536px) {
  .container {
    max-width: 1536px;
  }
}
```

### 2. 网格系统

```css
/* 响应式网格 */
.grid {
  display: grid;
  gap: var(--space-6);
}

.grid-cols-1 {
  grid-template-columns: 1fr;
}

.grid-cols-2 {
  grid-template-columns: repeat(2, 1fr);
}

.grid-cols-3 {
  grid-template-columns: repeat(3, 1fr);
}

.grid-cols-4 {
  grid-template-columns: repeat(4, 1fr);
}

@media (min-width: 640px) {
  .sm\:grid-cols-2 {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (min-width: 768px) {
  .md\:grid-cols-2 {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .md\:grid-cols-3 {
    grid-template-columns: repeat(3, 1fr);
  }
  
  .md\:grid-cols-4 {
    grid-template-columns: repeat(4, 1fr);
  }
}

@media (min-width: 1024px) {
  .lg\:grid-cols-2 {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .lg\:grid-cols-3 {
    grid-template-columns: repeat(3, 1fr);
  }
  
  .lg\:grid-cols-4 {
    grid-template-columns: repeat(4, 1fr);
  }
}
```

### 3. 移动端优化

```css
/* 移动端友好设计 */
@media (max-width: 768px) {
  /* 调整间距 */
  :root {
    --space-8: 1.5rem;
    --space-6: 1rem;
    --space-4: 0.75rem;
  }
  
  /* 简化卡片 */
  .unified-card {
    padding: var(--space-6);
  }
  
  /* 调整字体 */
  .unified-card-title {
    font-size: var(--text-xl);
  }
  
  /* 简化导航 */
  .navbar-container {
    padding: 0 var(--space-4);
  }
  
  /* 响应式表格 */
  .responsive-table {
    overflow-x: auto;
  }
  
  .responsive-table table {
    min-width: 600px;
  }
}
```

## 🎯 学习认知设计原则

### 1. 渐进式信息披露

```css
/* 可展开内容组件 */
.expandable-content {
  border: 1px solid var(--border-primary);
  border-radius: var(--radius-lg);
  overflow: hidden;
  margin-bottom: var(--space-6);
}

.expandable-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--space-4) var(--space-6);
  background: var(--bg-secondary);
  cursor: pointer;
  transition: background 0.2s ease;
}

.expandable-header:hover {
  background: var(--gray-100);
}

.expandable-title {
  font-weight: var(--font-semibold);
  color: var(--text-primary);
  margin: 0;
}

.expandable-icon {
  transition: transform 0.3s ease;
}

.expandable-icon.rotated {
  transform: rotate(180deg);
}

.expandable-body {
  padding: 0 var(--space-6);
  max-height: 0;
  overflow: hidden;
  transition: max-height 0.3s ease, padding 0.3s ease;
}

.expandable-body.expanded {
  padding: var(--space-6);
  max-height: 1000px;
}
```

### 2. 视觉层次设计

```css
/* 视觉层次系统 */
.visual-hierarchy-level-1 {
  font-size: var(--text-4xl);
  font-weight: var(--font-bold);
  color: var(--primary);
  margin-bottom: var(--space-4);
}

.visual-hierarchy-level-2 {
  font-size: var(--text-2xl);
  font-weight: var(--font-semibold);
  color: var(--secondary);
  margin-bottom: var(--space-4);
}

.visual-hierarchy-level-3 {
  font-size: var(--text-xl);
  font-weight: var(--font-medium);
  color: var(--text-primary);
  margin-bottom: var(--space-3);
}

.visual-hierarchy-level-4 {
  font-size: var(--text-lg);
  font-weight: var(--font-normal);
  color: var(--text-secondary);
  margin-bottom: var(--space-2);
}
```

### 3. 认知负荷管理

```css
/* 信息分组 */
.info-group {
  background: var(--bg-secondary);
  border-radius: var(--radius-lg);
  padding: var(--space-6);
  margin-bottom: var(--space-6);
}

.info-group-title {
  font-size: var(--text-lg);
  font-weight: var(--font-semibold);
  color: var(--primary);
  margin-bottom: var(--space-4);
  padding-bottom: var(--space-3);
  border-bottom: 1px solid var(--border-primary);
}

/* 进度指示器 */
.progress-container {
  margin: var(--space-6) 0;
}

.progress-bar {
  height: 8px;
  background: var(--gray-200);
  border-radius: var(--radius-full);
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: var(--primary-gradient);
  border-radius: var(--radius-full);
  transition: width 0.3s ease;
}

.progress-text {
  display: flex;
  justify-content: space-between;
  margin-top: var(--space-2);
  font-size: var(--text-sm);
  color: var(--text-secondary);
}
```

## 🔧 实施指南

### 1. 页面结构模板

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>页面标题 - 0代码AI规范化编程实践教学</title>
  <meta name="description" content="页面描述">
  
  <!-- 统一样式表 -->
  <link rel="stylesheet" href="assets/css/unified-styles.css">
  
  <!-- 字体和图标 -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
</head>
<body>
  <!-- 加载动画 -->
  <div id="page-loader" class="page-loader">
    <div class="loader-content">
      <div class="loader-spinner"></div>
      <div class="loader-text">加载中...</div>
    </div>
  </div>
  
  <!-- 滚动指示器 -->
  <div class="scroll-progress">
    <div class="scroll-progress-bar"></div>
  </div>
  
  <!-- 统一导航栏 -->
  <nav class="unified-navbar" id="navbar">
    <div class="navbar-container">
      <a href="index.html" class="navbar-brand">
        <span class="navbar-logo">🤖</span>
        <span>0代码AI规范化编程</span>
      </a>
      
      <button class="navbar-toggle" id="navbarToggle">
        <span></span>
        <span></span>
        <span></span>
      </button>
      
      <ul class="navbar-nav" id="navbarNav">
        <li><a href="index.html" class="nav-link">首页</a></li>
        <li><a href="#learning" class="nav-link">学习</a></li>
        <li><a href="#modules" class="nav-link">模块</a></li>
        <li><a href="#projects" class="nav-link">项目</a></li>
        <li><a href="#resources" class="nav-link">资源</a></li>
      </ul>
      
      <div class="navbar-actions">
        <a href="#start-learning" class="unified-btn unified-btn-primary">
          开始学习
        </a>
      </div>
    </div>
  </nav>
  
  <!-- 主要内容 -->
  <main class="main-container">
    <!-- 页面特定内容 -->
    <section class="hero-section">
      <div class="container">
        <div class="hero-content">
          <h1 class="hero-title">页面主标题</h1>
          <p class="hero-description">页面描述内容</p>
        </div>
      </div>
    </section>
    
    <section class="content-section">
      <div class="container">
        <!-- 内容区域 -->
      </div>
    </section>
  </main>
  
  <!-- 统一页脚 -->
  <footer class="unified-footer">
    <div class="container">
      <div class="footer-content">
        <div class="footer-info">
          <div class="footer-logo">
            <span class="navbar-logo">🤖</span>
            <span>0代码AI规范化编程</span>
          </div>
          <p class="footer-description">
            通过AI驱动的学习平台，帮助开发者掌握规范化编程技能
          </p>
        </div>
        
        <div class="footer-links">
          <div class="footer-column">
            <h4>学习资源</h4>
            <ul>
              <li><a href="#">文档中心</a></li>
              <li><a href="#">视频教程</a></li>
              <li><a href="#">实战项目</a></li>
            </ul>
          </div>
          
          <div class="footer-column">
            <h4>支持服务</h4>
            <ul>
              <li><a href="#">帮助中心</a></li>
              <li><a href="#">技术支持</a></li>
              <li><a href="#">联系我们</a></li>
            </ul>
          </div>
        </div>
      </div>
      
      <div class="footer-bottom">
        <p>&copy; 2025 0代码AI规范化编程. 保留所有权利.</p>
      </div>
    </div>
  </footer>
  
  <!-- 统一JavaScript -->
  <script src="assets/js/unified-scripts.js"></script>
</body>
</html>
```

### 2. 组件使用检查清单

```markdown
## 组件使用检查清单

### 颜色使用
- [ ] 是否使用了设计系统定义的颜色变量？
- [ ] 是否遵循了颜色语义化使用原则？
- [ ] 是否考虑了暗色模式兼容性？

### 字体排版
- [ ] 是否使用了设计系统的字体层级？
- [ ] 标题和正文的视觉层次是否清晰？
- [ ] 行高和字间距是否合适？

### 组件一致性
- [ ] 按钮样式是否统一？
- [ ] 卡片设计是否一致？
- [ ] 导航结构是否统一？

### 响应式适配
- [ ] 是否在各断点下显示正常？
- [ ] 移动端交互是否友好？
- [ ] 触控目标大小是否合适？

### 可访问性
- [ ] 是否提供了足够的颜色对比度？
- [ ] 是否支持键盘导航？
- [ ] 是否添加了适当的ARIA标签？
```

## 📊 质量保证

### 1. 设计系统审计

```javascript
// 设计系统合规性检查工具
class DesignSystemAuditor {
  constructor() {
    this.rules = [
      {
        name: '颜色使用检查',
        selector: '[class*="color-"], [style*="color:"], [style*="background:"]',
        check: this.checkColorUsage
      },
      {
        name: '字体层级检查',
        selector: 'h1, h2, h3, h4, h5, h6, p, span',
        check: this.checkTypographyHierarchy
      },
      {
        name: '组件一致性检查',
        selector: '.unified-btn, .unified-card, .unified-tag',
        check: this.checkComponentConsistency
      }
    ];
  }
  
  auditPage(pageContent) {
    const results = [];
    
    this.rules.forEach(rule => {
      const elements = this.querySelectorAll(rule.selector, pageContent);
      const ruleResults = rule.check(elements);
      
      results.push({
        rule: rule.name,
        passed: ruleResults.passed,
        issues: ruleResults.issues
      });
    });
    
    return {
      overall: results.every(r => r.passed),
      details: results
    };
  }
  
  checkColorUsage(elements) {
    const issues = [];
    const allowedColors = [
      '--primary', '--secondary', '--success', '--warning', '--error',
      '--text-primary', '--text-secondary', '--text-tertiary'
    ];
    
    elements.forEach(element => {
      const style = window.getComputedStyle(element);
      const color = style.color;
      const bgColor = style.backgroundColor;
      
      // 检查是否使用了CSS变量
      if (!color.includes('var(') && color !== 'rgba(0, 0, 0, 0)') {
        issues.push({
          element: element.tagName,
          property: 'color',
          value: color,
          message: '建议使用CSS变量定义的颜色'
        });
      }
    });
    
    return {
      passed: issues.length === 0,
      issues
    };
  }
}
```

### 2. 持续集成检查

```yaml
# .github/workflows/design-system-audit.yml
name: Design System Audit

on:
  pull_request:
    branches: [ main, develop ]
    paths:
      - '**/*.html'
      - '**/*.css'
      - '**/*.js'

jobs:
  design-audit:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Setup Node.js
      uses: actions/setup-node@v2
      with:
        node-version: '16'
        
    - name: Install dependencies
      run: npm install
      
    - name: Run design system audit
      run: |
        npm run audit:design-system
        
    - name: Check for violations
      run: |
        VIOLATIONS=$(node scripts/check-design-violations.js)
        if [ "$VIOLATIONS" -gt "0" ]; then
          echo "发现 $VIOLATIONS 个设计系统违规"
          exit 1
        fi
        
    - name: Generate audit report
      run: |
        node scripts/generate-design-audit-report.js > design-audit-report.md
        
    - name: Upload audit report
      uses: actions/upload-artifact@v2
      with:
        name: design-audit-report
        path: design-audit-report.md
```

## 🚀 实施路线图

### 阶段一: 基础组件统一 (1周)
- [ ] 统一按钮样式
- [ ] 统一卡片设计
- [ ] 统一导航栏
- [ ] 统一标签组件

### 阶段二: 视觉风格统一 (2周)
- [ ] 统一颜色系统应用
- [ ] 统一字体排版
- [ ] 统一间距系统
- [ ] 统一阴影和圆角

### 阶段三: 响应式优化 (1周)
- [ ] 移动端适配优化
- [ ] 触控交互优化
- [ ] 加载性能优化
- [ ] 可访问性增强

### 阶段四: 质量保证 (1周)
- [ ] 设计系统审计工具
- [ ] 自动化检查集成
- [ ] 团队培训和文档
- [ ] 持续改进机制

---
*本文档将持续更新，以反映最新的统一设计系统实践经验和最佳做法。*