// 为模块页面添加动画初始化脚本
document.addEventListener('DOMContentLoaded', function() {
    // 导入动画控制脚本
    const script = document.createElement('script');
    script.src = 'module-animations.js';
    script.onload = function() {
        if (typeof initAllAnimations === 'function') {
            initAllAnimations();
        }
    };
    document.head.appendChild(script);
});