# Hex 游戏 AI 实现

这是一个基于 Monte Carlo Tree Search (MCTS) 算法的 Hex 游戏 AI 实现，包含了完整的游戏逻辑和 Web 界面。

## 项目结构

```
.
├── MCTS.py         # MCTS 算法和 Hex 游戏核心逻辑实现
├── game.py         # 与裁判程序的交互接口
├── index.html      # Web 界面的 HTML 文件
├── script.js       # Web 界面的交互逻辑
└── style.css       # Web 界面的样式文件
```

## 功能特性

- 完整的 Hex 游戏规则实现
- 基于 MCTS 的 AI 对手
- 支持先手让子规则
- 支持交换规则
- 使用并查集（Union-Find）数据结构进行胜负判定
- 交互式 Web 界面
- 支持人机对战和人人对战模式

## 环境要求

- Python 3.6+
- 现代浏览器（支持 HTML5）

## 依赖模块

Python 标准库：
- time
- random
- math
- copy
- sys

## 运行方式

### AI 对战模式

```bash
python game.py
```

### Web 界面

直接在浏览器中打开 `index.html` 文件即可开始游戏。

## 技术实现

### AI 实现 (MCTS.py)

- 使用 Monte Carlo Tree Search 算法
- 实现了以下核心类：
  - `UnionFind`：用于高效判定胜负
  - `Hex`：游戏核心逻辑
  - `MCTS`：AI 决策算法

### 游戏接口 (game.py)

- 实现了与裁判程序的标准交互接口
- 支持先手让子和交换规则
- 包含移动格式转换功能

### Web 界面

- 响应式设计
- 支持人机和人人对战模式切换
- 实时显示当前玩家
- 棋盘重置功能

## 注意事项

1. AI 思考时间默认限制为 9.99 秒
2. 首次落子位置固定为 b4（优化策略）
3. Web 界面需要在支持 HTML5 的现代浏览器中运行

## 开发计划

- [ ] 优化 MCTS 算法性能
- [ ] 添加难度级别选择
- [ ] 优化 Web 界面用户体验
- [ ] 添加游戏记录和回放功能

## 许可证

MIT License 