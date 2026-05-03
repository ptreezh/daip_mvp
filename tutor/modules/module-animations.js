// 模块页面动画控制脚本 - 为modules目录下的页面提供动画效果支持
// 复制animations.js的内容，但调整相对路径

// 页面加载动画初始化
function initPageAnimations() {
    // 为页面元素添加淡入动画
    const elements = document.querySelectorAll('.unified-card, .feature-card, .stat-card');
    elements.forEach((el, index) => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(30px)';
        el.style.transition = 'all 0.6s ease';
        
        setTimeout(() => {
            el.style.opacity = '1';
            el.style.transform = 'translateY(0)';
        }, index * 100);
    });
}

// 数字计数动画
function animateCounter(element, target, duration = 2000) {
    let current = 0;
    const increment = target / (duration / 16);
    const timer = setInterval(() => {
        current += increment;
        if (current >= target) {
            element.textContent = target.toLocaleString();
            clearInterval(timer);
        } else {
            element.textContent = Math.floor(current).toLocaleString();
        }
    }, 16);
}

// 页面滚动指示器
function initScrollIndicator() {
    const indicator = document.createElement('div');
    indicator.className = 'scroll-indicator';
    document.body.appendChild(indicator);

    window.addEventListener('scroll', () => {
        const scrollTop = window.pageYOffset;
        const docHeight = document.documentElement.scrollHeight - window.innerHeight;
        const scrollPercent = (scrollTop / docHeight) * 100;
        indicator.style.width = scrollPercent + '%';
    });
}

// 滚动动画观察器
function initScrollAnimations() {
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('in-view');
                
                // 如果是数字元素，启动计数动画
                if (entry.target.classList.contains('stat-number')) {
                    const target = parseInt(entry.target.dataset.target);
                    animateCounter(entry.target, target);
                }
            }
        });
    }, {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    });

    // 观察所有需要动画的元素
    const animatedElements = document.querySelectorAll('.animate-on-scroll, .stat-card, .feature-card');
    animatedElements.forEach(el => observer.observe(el));
}

// 代码块展开/收起动画
function initCodeBlockToggle() {
    const codeBlocks = document.querySelectorAll('.code-container');
    
    codeBlocks.forEach(container => {
        const content = container.querySelector('.code-content');
        const header = container.querySelector('.code-header');
        
        if (content && header) {
            // 检查内容是否需要展开/收起功能
            if (content.scrollHeight > content.clientHeight) {
                const expandBtn = document.createElement('button');
                expandBtn.className = 'code-toggle-btn';
                expandBtn.innerHTML = '展开';
                expandBtn.setAttribute('aria-label', '展开代码块');
                
                let isExpanded = false;
                expandBtn.addEventListener('click', () => {
                    isExpanded = !isExpanded;
                    if (isExpanded) {
                        content.classList.add('expanded');
                        expandBtn.innerHTML = '收起';
                        expandBtn.setAttribute('aria-label', '收起代码块');
                    } else {
                        content.classList.remove('expanded');
                        expandBtn.innerHTML = '展开';
                        expandBtn.setAttribute('aria-label', '展开代码块');
                    }
                });
                
                container.appendChild(expandBtn);
            }
        }
    });
}

// 按钮交互效果增强
function initButtonEffects() {
    const buttons = document.querySelectorAll('.unified-btn, .card-button');
    
    buttons.forEach(button => {
        button.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-2px)';
            this.style.boxShadow = 'var(--shadow-xl)';
        });
        
        button.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
            this.style.boxShadow = 'var(--shadow-lg)';
        });
        
        button.addEventListener('mousedown', function() {
            this.style.transform = 'translateY(0) scale(0.98)';
        });
        
        button.addEventListener('mouseup', function() {
            this.style.transform = 'translateY(-2px) scale(1)';
        });
    });
}

// 导航栏滚动效果
function initNavbarEffects() {
    const navbar = document.querySelector('.unified-navbar');
    if (!navbar) return;
    
    window.addEventListener('scroll', () => {
        if (window.scrollY > 50) {
            navbar.classList.add('navbar-scrolled');
        } else {
            navbar.classList.remove('navbar-scrolled');
        }
    });
}

// 页面骨架屏动画
function initSkeletonLoading() {
    const skeletonElements = document.querySelectorAll('.skeleton');
    skeletonElements.forEach((el, index) => {
        setTimeout(() => {
            el.classList.remove('skeleton');
            el.classList.add('fade-in');
        }, index * 200);
    });
}

// 视差滚动效果
function initParallaxScroll() {
    const parallaxElements = document.querySelectorAll('.parallax');
    
    window.addEventListener('scroll', () => {
        const scrolled = window.pageYOffset;
        
        parallaxElements.forEach(element => {
            const speed = element.dataset.speed || 0.5;
            const yPos = -(scrolled * speed);
            element.style.transform = `translateY(${yPos}px)`;
        });
    });
}

// 加载完成后的初始化
function initAllAnimations() {
    // 延迟执行，确保DOM完全加载
    setTimeout(() => {
        initPageAnimations();
        initScrollIndicator();
        initScrollAnimations();
        initCodeBlockToggle();
        initButtonEffects();
        initNavbarEffects();
        initSkeletonLoading();
        initParallaxScroll();
    }, 100);
}

// 页面加载完成后自动初始化
document.addEventListener('DOMContentLoaded', function() {
    initAllAnimations();
});

// 导出函数供外部调用
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        initAllAnimations,
        initPageAnimations,
        initScrollIndicator,
        initScrollAnimations,
        initCodeBlockToggle,
        initButtonEffects,
        initNavbarEffects,
        animateCounter
    };
}