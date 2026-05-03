# TDD测试驱动开发流程

## 🧪 TDD流程概述

基于测试驱动开发（TDD）原则，为网站美化项目建立完整的测试驱动开发流程，确保每个功能都经过充分测试，保证代码质量和用户体验。

## 🔄 TDD循环流程

### 红-绿-重构循环
```
1. 🔴 红色阶段 (Red Phase)
   ├── 编写测试用例
   ├── 验证测试失败
   └── 确认需求理解

2. 🟢 绿色阶段 (Green Phase)
   ├── 编写最小可行代码
   ├── 让测试通过
   └── 验证功能实现

3. 🔵 重构阶段 (Refactor Phase)
   ├── 改进代码结构
   ├── 优化性能
   └── 保持测试通过
```

## 🛠️ 测试类型体系

### 1. 单元测试 (Unit Tests)
**目标**：测试单个组件或函数的行为

#### CSS组件测试
```javascript
// test/components/card.test.js
import { render, screen } from '@testing-library/react';
import Card from '../components/Card';

describe('Card Component', () => {
  test('应该正确渲染卡片标题', () => {
    render(<Card title="测试标题" />);
    expect(screen.getByText('测试标题')).toBeInTheDocument();
  });

  test('应该正确应用主题样式', () => {
    render(<Card theme="primary" />);
    const card = screen.getByTestId('card');
    expect(card).toHaveClass('card--primary');
  });

  test('应该在悬停时应用正确的动画', () => {
    render(<Card />);
    const card = screen.getByTestId('card');
    fireEvent.mouseEnter(card);
    expect(card).toHaveClass('card--hovered');
  });
});
```

#### JavaScript功能测试
```javascript
// test/utils/navigation.test.js
import { buildNavigationTree, validateNavigationLinks } from '../utils/navigation';

describe('Navigation Utilities', () => {
  test('应该构建正确的导航树结构', () => {
    const pages = [
      { id: 'home', title: '首页', parent: null },
      { id: 'learning', title: '学习', parent: null },
      { id: 'p1', title: 'P1数据持久化', parent: 'learning' }
    ];
    
    const tree = buildNavigationTree(pages);
    expect(tree).toHaveLength(2);
    expect(tree[1].children).toHaveLength(1);
    expect(tree[1].children[0].id).toBe('p1');
  });

  test('应该检测断链', () => {
    const links = [
      { href: '/existing-page', exists: true },
      { href: '/broken-link', exists: false }
    ];
    
    const brokenLinks = validateNavigationLinks(links);
    expect(brokenLinks).toHaveLength(1);
    expect(brokenLinks[0].href).toBe('/broken-link');
  });
});
```

### 2. 集成测试 (Integration Tests)
**目标**：测试多个组件协同工作的行为

#### 页面功能测试
```javascript
// test/pages/homepage.test.js
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import HomePage from '../pages/HomePage';

describe('HomePage Integration', () => {
  test('应该正确加载所有主要组件', async () => {
    render(<HomePage />);
    
    await waitFor(() => {
      expect(screen.getByText('0代码AI规范化编程实践教学')).toBeInTheDocument();
      expect(screen.getByTestId('hero-section')).toBeInTheDocument();
      expect(screen.getByTestId('features-section')).toBeInTheDocument();
    });
  });

  test('导航链接应该正常工作', async () => {
    const user = userEvent.setup();
    render(<HomePage />);
    
    const learningLink = screen.getByText('学习');
    await user.click(learningLink);
    
    expect(window.location.pathname).toBe('/learning');
  });

  test('响应式导航应该在移动端正确工作', () => {
    // 模拟移动端视口
    Object.defineProperty(window, 'innerWidth', { writable: true, configurable: true, value: 375 });
    
    render(<HomePage />);
    
    const mobileMenuButton = screen.getByTestId('mobile-menu-button');
    expect(mobileMenuButton).toBeInTheDocument();
  });
});
```

#### 跨页面导航测试
```javascript
// test/flows/learning-path.test.js
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { createMemoryRouter, RouterProvider } from 'react-router-dom';
import App from '../App';

describe('Learning Path Flow', () => {
  test('用户应该能够完成完整的学习路径', async () => {
    const user = userEvent.setup();
    const router = createMemoryRouter([
      {
        path: '/',
        element: <App />,
        children: [
          { path: '/', element: <HomePage /> },
          { path: '/learning', element: <LearningPage /> },
          { path: '/modules/p3', element: <P3ModulePage /> }
        ]
      }
    ]);

    render(<RouterProvider router={router} />);
    
    // 从首页开始
    expect(screen.getByText('开始学习之旅')).toBeInTheDocument();
    
    // 点击开始学习
    await user.click(screen.getByText('开始学习之旅'));
    expect(screen.getByText('学习路径')).toBeInTheDocument();
    
    // 选择P3模块
    await user.click(screen.getByText('P3 模型提供商'));
    expect(screen.getByText('模型提供商模块')).toBeInTheDocument();
  });
});
```

### 3. 端到端测试 (E2E Tests)
**目标**：测试完整的用户场景

#### Cypress测试示例
```javascript
// cypress/e2e/learning-experience.cy.js
describe('完整学习体验', () => {
  it('用户应该能够从首页完成P3模块学习', () => {
    // 访问首页
    cy.visit('/');
    
    // 验证首页内容
    cy.contains('0代码AI规范化编程实践教学').should('be.visible');
    cy.get('[data-testid="hero-features"]').should('be.visible');
    
    // 进入学习路径
    cy.contains('开始学习之旅').click();
    cy.url().should('include', '/learning');
    
    // 选择学习路径
    cy.contains('基础掌握路径').click();
    cy.contains('P3 模型提供商').click();
    
    // 验证模块页面
    cy.url().should('include', '/modules/p3');
    cy.contains('模型提供商').should('be.visible');
    
    // 完成学习步骤
    cy.contains('开始学习').click();
    cy.contains('规格文档').should('be.visible');
    
    // 验证学习进度
    cy.get('[data-testid="progress-bar"]').should('be.visible');
    cy.get('[data-testid="progress-percentage"]').should('contain', '25%');
    
    // 完成模块学习
    cy.get('[data-testid="complete-module"]').click();
    cy.contains('恭喜完成P3模块学习').should('be.visible');
  });

  it('响应式设计在移动端应该正常工作', () => {
    // 模拟移动端
    cy.viewport('iphone-x');
    
    cy.visit('/');
    
    // 验证移动端导航
    cy.get('[data-testid="mobile-menu-button"]').should('be.visible');
    cy.get('[data-testid="mobile-menu-button"]').click();
    cy.get('[data-testid="mobile-menu"]').should('be.visible');
    
    // 验证移动端布局
    cy.get('[data-testid="hero-features"]').should('have.css', 'grid-template-columns', '1fr');
  });
});
```

## 🔍 质量检查工具

### 1. 代码质量检查

#### ESLint配置
```javascript
// .eslintrc.js
module.exports = {
  extends: [
    'eslint:recommended',
    '@typescript-eslint/recommended',
    'plugin:jsx-a11y/recommended'
  ],
  rules: {
    'no-unused-vars': 'error',
    'no-console': 'warn',
    'prefer-const': 'error',
    'jsx-a11y/alt-text': 'error',
    'jsx-a11y/aria-props': 'error',
    'jsx-a11y/aria-proptypes': 'error',
    'jsx-a11y/aria-unsupported-elements': 'error',
    'jsx-a11y/role-has-required-aria-props': 'error',
    'jsx-a11y/role-supports-aria-props': 'error'
  }
};
```

#### Stylelint配置
```javascript
// .stylelintrc.js
module.exports = {
  extends: ['stylelint-config-standard'],
  rules: {
    'color-hex-case': 'lower',
    'color-hex-length': 'short',
    'color-named': 'never',
    'selector-no-qualifying-type': true,
    'selector-combinator-space-after': 'always',
    'selector-attribute-quotes': 'always',
    'selector-attribute-operator-space-before': 'never',
    'selector-attribute-operator-space-after': 'never',
    'selector-attribute-brackets-space-inside': 'never',
    'declaration-block-trailing-semicolon': 'always',
    'declaration-no-important': true,
    'declaration-colon-space-before': 'never',
    'declaration-colon-space-after': 'always',
    'number-leading-zero': 'always',
    'function-url-quotes': 'always',
    'font-weight-notation': 'numeric',
    'comment-whitespace-inside': 'always',
    'rule-empty-line-before': 'always-multi-line',
    'selector-pseudo-element-colon-notation': 'double'
  }
};
```

### 2. 可访问性检查

#### Axe测试
```javascript
// test/accessibility/axe.test.js
import { render } from '@testing-library/react';
import { axe, toHaveNoViolations } from 'jest-axe';
import HomePage from '../pages/HomePage';

expect.extend(toHaveNoViolations);

describe('Accessibility Tests', () => {
  test('HomePage应该没有可访问性违规', async () => {
    const { container } = render(<HomePage />);
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });

  test('导航应该支持键盘导航', () => {
    render(<Navigation />);
    
    // 测试Tab键导航
    const firstLink = screen.getByText('首页');
    firstLink.focus();
    expect(firstLink).toHaveFocus();
    
    // 测试Enter键激活
    fireEvent.keyDown(firstLink, { key: 'Enter', code: 'Enter' });
    expect(screen.getByText('学习页面')).toBeVisible();
  });

  test('图片应该有替代文本', () => {
    render(<HomePage />);
    const images = screen.getAllByRole('img');
    images.forEach(img => {
      expect(img).toHaveAttribute('alt');
      expect(img).not.toHaveAttribute('alt', '');
    });
  });
});
```

### 3. 性能检查

#### Lighthouse CI配置
```javascript
// lighthouse.config.js
module.exports = {
  ci: {
    collect: {
      url: ['http://localhost:3000/'],
      startServerCommand: 'npm run serve',
      numberOfRuns: 3
    },
    assert: {
      assertions: {
        'categories:performance': ['error', { minScore: 0.9 }],
        'categories:accessibility': ['error', { minScore: 0.9 }],
        'categories:best-practices': ['error', { minScore: 0.9 }],
        'categories:seo': ['error', { minScore: 0.9 }],
        'first-contentful-paint': ['error', { maxNumericValue: 2000 }],
        'largest-contentful-paint': ['error', { maxNumericValue: 4000 }],
        'cumulative-layout-shift': ['error', { maxNumericValue: 0.1 }]
      }
    }
  }
};
```

#### Web Vitals测试
```javascript
// test/performance/web-vitals.test.js
import { getCLS, getFID, getFCP, getLCP, getTTFB } from 'web-vitals';

describe('Web Vitals', () => {
  test('页面应该满足Core Web Vitals标准', (done) => {
    let metrics = {};
    
    const observer = {
      observe: (entry) => {
        metrics[entry.name] = entry.value;
        if (Object.keys(metrics).length >= 5) {
          validateMetrics(metrics);
          done();
        }
      },
      disconnect: () => {}
    };
    
    // 模拟Web Vitals观察
    global.performance.getEntriesByType = () => [
      { name: 'first-contentful-paint', startTime: 1500 },
      { name: 'largest-contentful-paint', startTime: 2500 },
      { name: 'cumulative-layout-shift', value: 0.05 },
      { name: 'first-input-delay', value: 80 },
      { name: 'time-to-first-byte', startTime: 600 }
    ];
    
    // 验证指标
    function validateMetrics(metrics) {
      expect(metrics['first-contentful-paint']).toBeLessThanOrEqual(2000);
      expect(metrics['largest-contentful-paint']).toBeLessThanOrEqual(4000);
      expect(metrics['cumulative-layout-shift']).toBeLessThanOrEqual(0.1);
      expect(metrics['first-input-delay']).toBeLessThanOrEqual(100);
      expect(metrics['time-to-first-byte']).toBeLessThanOrEqual(800);
    }
  });
});
```

## 🏃‍♂️ 自动化测试脚本

### 1. 测试运行脚本
```json
// package.json
{
  "scripts": {
    "test": "jest",
    "test:watch": "jest --watch",
    "test:coverage": "jest --coverage",
    "test:e2e": "cypress run",
    "test:e2e:open": "cypress open",
    "test:lighthouse": "lhci autorun",
    "test:accessibility": "pa11y http://localhost:3000",
    "test:all": "npm run test:coverage && npm run test:e2e && npm run test:lighthouse"
  }
}
```

### 2. 持续集成配置
```yaml
# .github/workflows/test.yml
name: Test and Quality Assurance

on: [push, pull_request]

jobs:
  test:
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
    
    - name: Run linting
      run: npm run lint
    
    - name: Run unit tests
      run: npm run test:coverage
    
    - name: Run accessibility tests
      run: npm run test:accessibility
    
    - name: Build application
      run: npm run build
    
    - name: Start application
      run: npm run serve &
    
    - name: Run E2E tests
      run: npm run test:e2e
    
    - name: Run Lighthouse CI
      run: npm run test:lighthouse
    
    - name: Upload coverage reports
      uses: codecov/codecov-action@v3
```

## 📊 测试报告和监控

### 1. 测试覆盖率报告
```javascript
// jest.config.js
module.exports = {
  coverageDirectory: 'coverage',
  coverageReporters: ['text', 'lcov', 'html'],
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

### 2. 性能监控脚本
```javascript
// scripts/performance-monitor.js
const lighthouse = require('lighthouse');
const chromeLauncher = require('chrome-launcher');

async function runPerformanceAudit(url) {
  const chrome = await chromeLauncher.launch({chromeFlags: ['--headless']});
  const options = {logLevel: 'info', output: 'html', onlyCategories: ['performance'], port: chrome.port};
  const runnerResult = await lighthouse(url, options);
  const reportHtml = runnerResult.report;
  await fs.writeFile('performance-report.html', reportHtml);
  await chrome.kill();
  
  return runnerResult.lhr;
}

// 使用示例
runPerformanceAudit('http://localhost:3000').then(results => {
  console.log('Performance Score:', results.categories.performance.score);
  console.log('First Contentful Paint:', results.audits['first-contentful-paint'].numericValue);
});
```

## 🔧 测试工具配置

### 1. Jest配置
```javascript
// jest.config.js
module.exports = {
  testEnvironment: 'jsdom',
  setupFilesAfterEnv: ['<rootDir>/src/setupTests.js'],
  moduleNameMapping: {
    '\\.(css|less|scss|sass)$': 'identity-obj-proxy',
    '\\.(gif|ttf|eot|svg)$': '<rootDir>/src/__mocks__/fileMock.js'
  },
  transform: {
    '^.+\\.(js|jsx)$': 'babel-jest'
  },
  collectCoverageFrom: [
    'src/**/*.{js,jsx}',
    '!src/index.js',
    '!src/reportWebVitals.js'
  ]
};
```

### 2. Testing Library配置
```javascript
// src/setupTests.js
import '@testing-library/jest-dom';
import { TextEncoder, TextDecoder } from 'util';

// 模拟 IntersectionObserver
global.IntersectionObserver = class IntersectionObserver {
  constructor() {}
  disconnect() {}
  observe() {}
  unobserve() {}
};

// 模拟 ResizeObserver
global.ResizeObserver = class ResizeObserver {
  constructor() {}
  disconnect() {}
  observe() {}
  unobserve() {}
};
```

## 📋 测试检查清单

### 1. 功能测试
- [ ] 所有页面正确加载
- [ ] 导航链接正常工作
- [ ] 表单提交和验证
- [ ] 响应式布局适配
- [ ] 交互元素响应

### 2. 性能测试
- [ ] 页面加载时间 < 3秒
- [ ] 首屏渲染时间 < 1.5秒
- [ ] 图片和资源优化
- [ ] 缓存策略有效
- [ ] 动画流畅（60fps）

### 3. 可访问性测试
- [ ] 键盘导航支持
- [ ] 屏幕阅读器兼容
- [ ] 颜色对比度达标
- [ ] 语义化HTML标签
- [ ] ARIA标签正确使用

### 4. 兼容性测试
- [ ] 现代浏览器兼容
- [ ] 移动端浏览器兼容
- [ ] 不同屏幕尺寸适配
- [ ] 网络条件适应

## 🚀 TDD实施计划

### 阶段1: 测试框架搭建（1周）
1. 配置Jest和React Testing Library
2. 设置Cypress端到端测试
3. 配置ESLint和Stylelint
4. 建立CI/CD测试流程

### 阶段2: 基础测试编写（2周）
1. 编写组件单元测试
2. 创建页面集成测试
3. 建立可访问性测试
4. 实现性能基准测试

### 阶段3: 高级测试开发（2周）
1. 开发端到端测试用例
2. 建立视觉回归测试
3. 实现自动化质量检查
4. 创建测试报告系统

### 阶段4: 持续优化（1周）
1. 优化测试执行速度
2. 提升测试覆盖率
3. 完善测试文档
4. 培训团队TDD实践

---

*本TDD开发流程确保每个功能都经过充分测试，保证网站质量和用户体验的持续改进。*