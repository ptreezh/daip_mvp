/**
 * 统一设计系统 JavaScript 支持
 * 基于 UNIFIED_DESIGN_SYSTEM.md 规范
 */

// DOM 加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
  // 初始化导航栏
  initNavbar();
  
  // 初始化滚动效果
  initScrollEffects();
  
  // 初始化可展开内容
  initExpandableContent();
  
  // 初始化代码块复制功能
  initCodeCopy();
  
  // 初始化页面加载动画
  initPageLoader();
});

// 导航栏初始化
function initNavbar() {
  const navbar = document.querySelector('.unified-navbar');
  const navbarToggle = document.getElementById('navbarToggle');
  const navbarNav = document.getElementById('navbarNav');
  
  // 滚动效果
  window.addEventListener('scroll', function() {
    if (window.scrollY > 50) {
      navbar.classList.add('scrolled');
    } else {
      navbar.classList.remove('scrolled');
    }
  });
  
  // 移动端菜单切换
  if (navbarToggle && navbarNav) {
    navbarToggle.addEventListener('click', function() {
      navbarToggle.classList.toggle('active');
      navbarNav.classList.toggle('active');
    });
    
    // 点击导航链接后关闭移动端菜单
    const navLinks = navbarNav.querySelectorAll('.nav-link');
    navLinks.forEach(link => {
      link.addEventListener('click', function() {
        navbarToggle.classList.remove('active');
        navbarNav.classList.remove('active');
      });
    });
  }
}

// 滚动效果初始化
function initScrollEffects() {
  // 滚动进度条
  const scrollProgressBar = document.querySelector('.scroll-progress-bar');
  
  if (scrollProgressBar) {
    window.addEventListener('scroll', function() {
      const scrollTop = window.scrollY;
      const docHeight = document.body.scrollHeight - window.innerHeight;
      const scrollPercent = (scrollTop / docHeight) * 100;
      
      scrollProgressBar.style.width = scrollPercent + '%';
    });
  }
  
  // 滚动动画
  initScrollAnimations();
}

// 滚动动画
function initScrollAnimations() {
  const observerOptions = {
    root: null,
    rootMargin: '0px',
    threshold: 0.1
  };
  
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('animate-in');
      }
    });
  }, observerOptions);
  
  // 观察所有需要动画的元素
  const animateElements = document.querySelectorAll('.unified-card, .unified-btn, .hero-section');
  animateElements.forEach(el => observer.observe(el));
}

// 可展开内容初始化
function initExpandableContent() {
  const expandables = document.querySelectorAll('.expandable-header');
  
  expandables.forEach(header => {
    header.addEventListener('click', function() {
      const body = this.nextElementSibling;
      const icon = this.querySelector('.expandable-icon');
      
      body.classList.toggle('expanded');
      icon.classList.toggle('rotated');
    });
  });
}

// 代码块复制功能
function initCodeCopy() {
  const copyButtons = document.querySelectorAll('.code-copy-btn');
  
  copyButtons.forEach(button => {
    button.addEventListener('click', function() {
      const codeBlock = this.closest('.code-container').querySelector('code');
      const text = codeBlock.textContent;
      
      navigator.clipboard.writeText(text).then(() => {
        // 显示成功提示
        const originalText = this.innerHTML;
        this.innerHTML = '<i class="fas fa-check"></i> 已复制';
        
        setTimeout(() => {
          this.innerHTML = originalText;
        }, 2000);
      }).catch(err => {
        console.error('复制失败:', err);
      });
    });
  });
}

// 页面加载动画
function initPageLoader() {
  const loader = document.getElementById('page-loader');
  
  if (loader) {
    // 页面加载完成后隐藏加载动画
    window.addEventListener('load', function() {
      loader.style.opacity = '0';
      setTimeout(() => {
        loader.style.display = 'none';
      }, 300);
    });
  }
}

// 工具函数：平滑滚动到指定元素
function smoothScrollTo(target) {
  const element = typeof target === 'string' ? document.querySelector(target) : target;
  
  if (element) {
    element.scrollIntoView({
      behavior: 'smooth',
      block: 'start'
    });
  }
}

// 工具函数：显示通知
function showToast(message, type = 'info') {
  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;
  toast.textContent = message;
  
  // 添加样式
  toast.style.position = 'fixed';
  toast.style.bottom = '20px';
  toast.style.right = '20px';
  toast.style.padding = '12px 20px';
  toast.style.borderRadius = '8px';
  toast.style.color = 'white';
  toast.style.zIndex = '10000';
  toast.style.boxShadow = '0 4px 12px rgba(0,0,0,0.15)';
  toast.style.transform = 'translateY(100px)';
  toast.style.transition = 'transform 0.3s ease';
  
  // 设置背景色
  switch(type) {
    case 'success':
      toast.style.background = 'linear-gradient(135deg, #10b981 0%, #059669 100%)';
      break;
    case 'error':
      toast.style.background = 'linear-gradient(135deg, #ef4444 0%, #dc2626 100%)';
      break;
    case 'warning':
      toast.style.background = 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)';
      break;
    default:
      toast.style.background = 'linear-gradient(135deg, #3b82f6 0%, #2563eb 100%)';
  }
  
  document.body.appendChild(toast);
  
  // 动画显示
  setTimeout(() => {
    toast.style.transform = 'translateY(0)';
  }, 100);
  
  // 3秒后自动消失
  setTimeout(() => {
    toast.style.transform = 'translateY(100px)';
    setTimeout(() => {
      document.body.removeChild(toast);
    }, 300);
  }, 3000);
}

// 工具函数：表单验证
function validateForm(form) {
  const inputs = form.querySelectorAll('input, textarea, select');
  let isValid = true;
  
  inputs.forEach(input => {
    // 移除之前的错误状态
    input.classList.remove('invalid');
    
    // 检查必填字段
    if (input.hasAttribute('required') && !input.value.trim()) {
      input.classList.add('invalid');
      isValid = false;
      
      // 显示错误提示
      const errorElement = document.createElement('div');
      errorElement.className = 'form-error';
      errorElement.textContent = '此字段为必填项';
      errorElement.style.color = '#ef4444';
      errorElement.style.fontSize = '0.875rem';
      errorElement.style.marginTop = '0.25rem';
      
      // 插入错误提示
      if (!input.parentNode.querySelector('.form-error')) {
        input.parentNode.appendChild(errorElement);
      }
    }
  });
  
  return isValid;
}

// 导出公共函数
window.smoothScrollTo = smoothScrollTo;
window.showToast = showToast;
window.validateForm = validateForm;