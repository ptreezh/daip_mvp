# Knowledge 命令使用说明

## 默认行为

### 同步操作
```bash
daip-cli knowledge auto
```
当运行此命令时，如果没有指定查询参数，将自动执行知识库同步操作。

### 搜索操作
```bash
daip-cli knowledge auto "搜索查询"
```
当运行此命令时，如果指定了查询参数，将自动执行搜索操作。

## 传统子命令

### 同步
```bash
daip-cli knowledge sync
```

### 状态
```bash
daip-cli knowledge status
```

### 搜索
```bash
daip-cli knowledge search "搜索查询"
```

## 说明

由于 Typer 框架的限制，我们无法直接实现 `/knowledge` (无参数) 和 `/knowledge <query>` (有参数) 的形式，而不影响子命令访问。因此，我们提供了一个 `auto` 子命令来实现所需的默认行为，同时保留了所有传统子命令的功能。