# TDD测试驱动开发流程

## 🎯 TDD流程概述

基于测试驱动开发(TDD)原则，为网站美化项目建立完整的开发流程，确保每个功能都有对应的测试验证，最终交付高质量的教育平台。

## 🔄 TDD核心循环

### 红-绿-重构循环
```
1. 🔴 Red (编写失败的测试)
   ├── 分析需求和设计
   ├── 编写测试用例
   ├── 验证测试失败
   └── 确定实现目标

2. 🟢 Green (编写最小实现)
   ├── 编写最少代码让测试通过
   ├── 专注于功能实现
   ├── 忽略代码质量
   └── 验证测试成功

3. 🔄 Refactor (重构优化)
   ├── 重构代码结构
   ├── 优化性能和可读性
   ├── 保持测试通过
   └── 确保设计改进
```

## 📋 测试分类体系

### 1. 功能测试 (Functional Tests)
验证页面功能和交互是否符合预期

#### 导航测试
```javascript
// 测试用例: 导航链接功能
describe('Navigation Tests', () => {
  test('所有主要导航链接应该可点击', () => {
    const navLinks = document.querySelectorAll('.nav-link');
    navLinks.forEach(link => {
      expect(link).toBeInTheDocument();
      expect(link.href).toBeTruthy();
    });
  });

  test('当前页面导航链接应该有active状态', () => {
    const currentPageLink = document.querySelector('.nav-link.active');
    expect(currentPageLink).toBeTruthy();
  });
});
```

#### 内容测试
```javascript
// 测试用例: 页面内容完整性
describe('Content Tests', () => {
  test('主页面应包含所有核心元素', () => {
    expect(document.querySelector('.hero-title')).toBeTruthy();
    expect(document.querySelector('.hero-subtitle')).toBeTruthy();
    expect(document.querySelector('.hero-features')).toBeTruthy();
    expect(document.querySelector('.hero-cta')).toBeTruthy();
  });

  test('P3模块页面应包含必要的技术信息', () => {
    expect(document.querySelector('.module-title')).toContainText('模型提供商');
    expect(document.querySelector('.module-description')).toBeTruthy();
    expect(document.querySelector('.code-example')).toBeTruthy();
  });
});
```

### 2. 视觉测试 (Visual Tests)
验证页面设计和样式符合设计规范

#### 响应式测试
```javascript
// 测试用例: 响应式布局
describe('Responsive Design Tests', () => {
  test('移动端应该显示单列布局', () => {
    window.innerWidth = 640;
    window.dispatchEvent(new Event('resize'));
    
    const grid = document.querySelector('.features-grid');
    const computedStyle = window.getComputedStyle(grid);
    expect(computedStyle.gridTemplateColumns).toBe('1fr');
  });

  test('桌面端应该显示多列布局', () => {
    window.innerWidth = 1024;
    window.dispatchEvent(new Event('resize'));
    
    const grid = document.querySelector('.features-grid');
    const computedStyle = window.getComputedStyle(grid);
    expect(computedStyle.gridTemplateColumns).toContain('repeat');
  });
});
```

#### 视觉一致性测试
```javascript
// 测试用例: 设计系统一致性
describe('Design System Tests', () => {
  test('所有按钮应使用统一的主色调', () => {
    const buttons = document.querySelectorAll('.btn-primary');
    buttons.forEach(button => {
      const styles = window.getComputedStyle(button);
      expect(styles.background).toMatch(/linear-gradient.*#667eea.*#764ba2/);
    });
  });

  test('卡片阴影效果应该统一', () => {
    const cards = document.querySelectorAll('.card');
    cards.forEach(card => {
      const styles = window.getComputedStyle(card);
      expect(styles.boxShadow).toBeTruthy();
    });
  });
});
```

### 3. 性能测试 (Performance Tests)
验证页面加载和交互性能

#### 加载性能测试
```javascript
// 测试用例: 页面加载性能
describe('Performance Tests', () => {
  test('页面首屏渲染时间应小于1.5秒', async () => {
    const startTime = performance.now();
    await loadPage();
    const endTime = performance.now();
    const loadTime = endTime - startTime;
    
    expect(loadTime).toBeLessThan(1500);
  });

  test('图片应正确实现懒加载', async () => {
    const images = document.querySelectorAll('img[data-src]');
    const firstImage = images[0];
    
    // 模拟滚动到图片位置
    firstImage.scrollIntoView();
    await new Promise(resolve => setTimeout(resolve, 100));
    
    expect(firstImage.src).toBe(firstImage.dataset.src);
  });
});
```

### 4. 可访问性测试 (Accessibility Tests)
验证页面符合无障碍访问标准

#### 无障碍功能测试
```javascript
// 测试用例: 无障碍访问
describe('Accessibility Tests', () => {
  test('所有图片应有alt属性', () => {
    const images = document.querySelectorAll('img');
    images.forEach(img => {
      expect(img.alt).toBeTruthy();
      expect(img.alt.length).toBeGreaterThan(0);
    });
  });

  test('页面应该有正确的标题层级', () => {
    const headings = document.querySelectorAll('h1, h2, h3, h4, h5, h6');
    let previousLevel = 0;
    
    headings.forEach(heading => {
      const level = parseInt(heading.tagName.charAt(1));
      expect(level - previousLevel).toBeLessThanOrEqual(1);
      previousLevel = level;
    });
  });

  test('焦点应该可见', () => {
    const focusableElements = document.querySelectorAll('a, button, input, textarea');
    focusableElements.forEach(element => {
      element.focus();
      const styles = window.getComputedStyle(element, ':focus');
      expect(styles.outline).not.toBe('none');
    });
  });
});
```

## 🛠️ 测试工具和框架

### 1. 单元测试框架 - Jest
```javascript
// jest.config.js
module.exports = {
  testEnvironment: 'jsdom',
  setupFilesAfterEnv: ['<rootDir>/tests/setup.js'],
  testMatch: ['**/__tests__/**/*.test.js'],
  collectCoverageFrom: [
    'src/**/*.{js,jsx}',
    '!src/index.js',
    '!src/reportWebVitals.js'
  ],
  coverageThreshold: {
    global: {
      branches: 80,
      functions: 80,
      lines: 80,
      statements: 80
    }
  }
};
```

### 2. 端到端测试 - Cypress
```javascript
// cypress/integration/homepage.spec.js
describe('Homepage E2E Tests', () => {
  beforeEach(() => {
    cy.visit('/');
  });

  it('应该加载主页面并显示所有核心元素', () => {
    cy.get('.hero-title').should('be.visible');
    cy.get('.hero-subtitle').should('be.visible');
    cy.get('.hero-features').should('be.visible');
    cy.get('.hero-cta').should('be.visible');
  });

  it('导航链接应该正常工作', () => {
    cy.get('[data-testid="nav-learning"]').click();
    cy.url().should('include', '#learning');
    
    cy.get('[data-testid="nav-modules"]').click();
    cy.url().should('include', '#modules');
  });

  it('响应式布局在不同屏幕尺寸下应该正常', () => {
    cy.viewport('iphone-6');
    cy.get('.navbar-menu').should('not.be.visible');
    cy.get('.mobile-menu-toggle').should('be.visible');
    
    cy.viewport('macbook-15');
    cy.get('.navbar-menu').should('be.visible');
    cy.get('.mobile-menu-toggle').should('not.be.visible');
  });
});
```

### 3. 视觉回归测试 - Storybook + Chromatic
```javascript
// .storybook/main.js
module.exports = {
  stories: ['../src/**/*.stories.@(js|jsx|ts|tsx)'],
  addons: [
    '@storybook/addon-essentials',
    '@storybook/addon-a11y',
    '@storybook/addon-viewport'
  ],
  framework: {
    name: '@storybook/react-webpack5',
    options: {}
  }
};

// src/components/Button.stories.js
export default {
  title: 'Components/Button',
  component: Button,
  parameters: {
    docs: {
      description: {
        component: '统一的按钮组件，支持不同变体和尺寸'
      }
    }
  },
  argTypes: {
    variant: {
      control: { type: 'select' },
      options: ['primary', 'secondary', 'outline']
    },
    size: {
      control: { type: 'select' },
      options: ['sm', 'md', 'lg']
    }
  }
};

export const Primary = {
  args: {
    variant: 'primary',
    children: '主要按钮'
  }
};
```

## 📊 测试自动化流水线

### GitHub Actions 工作流
```yaml
# .github/workflows/test.yml
name: Test and Quality Assurance

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  unit-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
          cache: 'npm'
      
      - name: Install dependencies
        run: npm ci
      
      - name: Run unit tests
        run: npm run test -- --coverage --watchAll=false
      
      - name: Upload coverage reports
        uses: codecov/codecov-action@v3

  e2e-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
          cache: 'npm'
      
      - name: Install dependencies
        run: npm ci
      
      - name: Build application
        run: npm run build
      
      - name: Start application
        run: npm run start &
      
      - name: Run Cypress tests
        uses: cypress-io/github-action@v4
        with:
          start: npm run start
          wait-on: 'http://localhost:3000'

  visual-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
          cache: 'npm'
      
      - name: Install dependencies
        run: npm ci
      
      - name: Build Storybook
        run: npm run build-storybook
      
      - name: Publish to Chromatic
        uses: chromaui/action@v1
        with:
          projectToken: ${{ secrets.CHROMATIC_PROJECT_TOKEN }}
```

## 🔍 测试数据管理

### 测试数据工厂
```javascript
// tests/factories/pageData.js
class PageDataFactory {
  static createHomepageData() {
    return {
      title: '0代码AI规范化编程实践教学',
      subtitle: '通过多模型辩论和协同生成可信知识的平台',
      heroFeatures: [
        {
          icon: '🧠',
          title: '多模型协同',
          description: '多个AI模型协同工作，生成更准确的知识内容'
        },
        {
          icon: '⚡',
          title: '0代码体验',
          description: '无需编写代码，通过可视化界面完成复杂任务'
        },
        {
          icon: '🔍',
          title: '知识可信',
          description: '通过辩论验证，确保生成内容的准确性和可信度'
        }
      ],
      ctaButtons: [
        {
          text: '开始学习之旅',
          href: '#platform',
          variant: 'primary'
        },
        {
          text: '了解更多特性',
          href: '#features',
          variant: 'secondary'
        }
      ]
    };
  }

  static createModuleData(moduleName) {
    const moduleData = {
      'P3': {
        title: 'P3 模型提供商',
        description: 'LiteLLM集成、多模型架构、模型切换机制',
        features: [
          '支持多种AI模型提供商',
          '智能模型选择算法',
          '动态负载均衡',
          '模型性能监控'
        ],
        codeExample: `
// P3 模型提供商示例
class ModelProvider {
  constructor(config) {
    this.models = config.models;
    this.currentModel = null;
  }
  
  async generateResponse(prompt, options = {}) {
    const model = this.selectOptimalModel(prompt);
    return await model.generate(prompt, options);
  }
}
        `
      }
      // 其他模块数据...
    };
    
    return moduleData[moduleName] || {};
  }
}
```

### Mock数据管理
```javascript
// tests/mocks/apiMock.js
export const mockApiResponses = {
  getUserProgress: {
    userId: 'user123',
    completedModules: ['P1', 'P6'],
    currentModule: 'P3',
    progressPercentage: 65
  },

  getModuleList: {
    coreModules: [
      { id: 'P1', name: '数据持久化', difficulty: 'beginner', estimatedTime: '2-3周' },
      { id: 'P2', name: '知识管理', difficulty: 'intermediate', estimatedTime: '3-4周' },
      { id: 'P3', name: '模型提供商', difficulty: 'intermediate', estimatedTime: '3-4周' },
      { id: 'P5', name: '智能引擎', difficulty: 'advanced', estimatedTime: '4-5周' },
      { id: 'P6', name: '终端界面', difficulty: 'beginner', estimatedTime: '2-3周' },
      { id: 'P8', name: '辩论系统', difficulty: 'advanced', estimatedTime: '4-5周' }
    ]
  }
};

// 使用Mock
global.fetch = jest.fn(() =>
  Promise.resolve({
    json: () => Promise.resolve(mockApiResponses.getUserProgress),
    ok: true
  })
);
```

## 📈 测试覆盖率和质量指标

### 测试覆盖率目标
```javascript
// 测试覆盖率配置
const coverageConfig = {
  branches: 85,      // 分支覆盖率
  functions: 90,     // 函数覆盖率
  lines: 90,         // 行覆盖率
  statements: 90     // 语句覆盖率
};

// 关键模块覆盖率要求
const criticalModules = [
  'Navigation',
  'PageLayout',
  'ResponsiveDesign',
  'Accessibility'
];
```

### 质量门禁规则
```yaml
# quality-gates.yml
quality_gates:
  test_coverage:
    minimum: 85%
    critical_modules: 95%
  
  performance:
    first_contentful_paint: < 1.5s
    largest_contentful_paint: < 2.5s
    cumulative_layout_shift: < 0.1
  
  accessibility:
    axe_score: 95
    color_contrast_ratio: 4.5
    keyboard_navigation: 100%
  
  security:
    vulnerability_scan: pass
    dependency_audit: pass
```

## 🔧 测试环境配置

### 本地开发环境
```json
// package.json scripts
{
  "scripts": {
    "test": "jest",
    "test:watch": "jest --watch",
    "test:coverage": "jest --coverage",
    "test:e2e": "cypress run",
    "test:e2e:open": "cypress open",
    "test:visual": "npm run build-storybook && chromatic --project-token=$CHROMATIC_PROJECT_TOKEN",
    "test:all": "npm run test:coverage && npm run test:e2e && npm run test:visual"
  }
}
```

### 测试环境变量
```bash
# .env.test
NODE_ENV=test
API_BASE_URL=http://localhost:3000/api
CHROMATIC_PROJECT_TOKEN=your_chromatic_token
CYPRESS_BASE_URL=http://localhost:3000
```

## 📋 测试检查清单

### 开发前检查
- [ ] 编写单元测试用例
- [ ] 创建端到端测试场景
- [ ] 设置视觉回归测试基线
- [ ] 配置测试数据和Mock

### 开发中检查
- [ ] 运行单元测试确保通过
- [ ] 验证响应式设计在不同设备上工作
- [ ] 检查可访问性功能正常
- [ ] 测试性能和加载速度

### 部署前检查
- [ ] 所有测试用例通过
- [ ] 测试覆盖率达标
- [ ] 视觉回归测试无重大差异
- [ ] 性能指标符合要求
- [ ] 无障碍访问标准达标

---

*本TDD流程确保网站美化项目在每个开发阶段都有质量保证，最终交付高质量的教育平台。*