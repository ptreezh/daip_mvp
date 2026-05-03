// 动画控制脚本 - 为index.html提供完整的动画效果支持
// 包括页面加载、滚动、交互和代码块动画

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
                expandBtn.className = 'code-expand-btn';
                expandBtn.innerHTML = '🔍 展开';
                expandBtn.style.position = 'absolute';
                expandBtn.style.bottom = '8px';
                expandBtn.style.right = '60px';
                expandBtn.style.background = 'var(--primary)';
                expandBtn.style.color = 'white';
                expandBtn.style.border = 'none';
                expandBtn.style.padding = '4px 8px';
                expandBtn.style.borderRadius = '4px';
                expandBtn.style.cursor = 'pointer';
                expandBtn.style.fontSize = '0.75rem';
                expandBtn.style.transition = 'var(--transition-colors)';
                
                expandBtn.addEventListener('mouseenter', () => {
                    expandBtn.style.background = 'var(--primary-dark)';
                    expandBtn.style.transform = 'translateY(-1px)';
                });
                
                expandBtn.addEventListener('mouseleave', () => {
                    expandBtn.style.background = 'var(--primary)';
                    expandBtn.style.transform = 'translateY(0)';
                });
                
                let isExpanded = false;
                expandBtn.addEventListener('click', () => {
                    isExpanded = !isExpanded;
                    if (isExpanded) {
                        content.classList.add('expanded');
                        expandBtn.innerHTML = '📦 收起';
                    } else {
                        content.classList.remove('expanded');
                        expandBtn.innerHTML = '🔍 展开';
                    }
                });
                
                container.style.position = 'relative';
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

// 鼠标跟随效果
function initMouseFollowEffect() {
    let mouseX = 0, mouseY = 0;
    let cursorX = 0, cursorY = 0;
    
    // 创建自定义光标
    const cursor = document.createElement('div');
    cursor.className = 'custom-cursor';
    cursor.style.cssText = `
        position: fixed;
        width: 20px;
        height: 20px;
        background: var(--primary);
        border-radius: 50%;
        pointer-events: none;
        z-index: 9999;
        mix-blend-mode: difference;
        transition: all 0.1s ease;
        opacity: 0;
    `;
    document.body.appendChild(cursor);
    
    // 监听鼠标移动
    document.addEventListener('mousemove', (e) => {
        mouseX = e.clientX;
        mouseY = e.clientY;
        cursor.style.opacity = '1';
    });
    
    document.addEventListener('mouseleave', () => {
        cursor.style.opacity = '0';
    });
    
    // 动画循环
    function animate() {
        cursorX += (mouseX - cursorX) * 0.1;
        cursorY += (mouseY - cursorY) * 0.1;
        
        cursor.style.left = cursorX - 10 + 'px';
        cursor.style.top = cursorY - 10 + 'px';
        
        requestAnimationFrame(animate);
    }
    animate();
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
        
        // 可选：启用鼠标跟随效果（需要用户同意）
        // initMouseFollowEffect();
    }, 100);
}

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