import copy
import math
import random
import time


class UnionFind:
    def __init__(self, n):
        """
        初始化并查集
        Args:
            n: 节点数量
        """
        self.parent = list(range(n))

    def find(self, x):
        """
        查找x的根节点，并进行路径压缩
        Args:
            x: 要查找的节点
        Returns:
            x的根节点
        """
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]  # 路径压缩
            x = self.parent[x]
        return x

    def union(self, x, y):
        """
        合并x和y所在的集合
        Args:
            x: 第一个节点
            y: 第二个节点
        """
        fx = self.find(x)
        fy = self.find(y)
        if fx != fy:
            self.parent[fx] = fy

    def connected(self, x, y):
        """
        判断x和y是否在同一个集合中
        Args:
            x: 第一个节点
            y: 第二个节点
        Returns:
            bool: 是否连通
        """
        return self.find(x) == self.find(y)


class Hex:
    def __init__(self, size=11):
        """
        初始化Hex棋盘
        Args:
            size: 棋盘大小，默认11x11
        """
        self.size = size
        self.board = [['.' for _ in range(size)] for _ in range(size)]
        # 为每个颜色维护一个并查集
        self.uf_b = UnionFind(size * size + 2)  # 蓝方(B)的并查集
        self.uf_r = UnionFind(size * size + 2)  # 红方(R)的并查集
        self.virtual1 = size * size      # 虚拟节点1（用于连接边界）
        self.virtual2 = size * size + 1  # 虚拟节点2（用于连接边界）
        self.available = [(r, c) for r in range(size) for c in range(size)]

    def node_id(self, r, c):
        """
        将二维坐标转换为一维节点编号
        """
        return r * self.size + c

    def play(self, action, color):
        """
        在指定位置落子
        Args:
            r: 行坐标
            c: 列坐标
            color: 棋子颜色 ('B' 或 'R')
        Returns:
            bool: 落子是否成功
        """
        r = action[0]
        c = action[1]
        if self.board[r][c] == '.':
            self.board[r][c] = color
            self.available.remove((r, c))
            
            # 选择对应颜色的并查集
            uf = self.uf_b if color == 'B' else self.uf_r
            cur_id = self.node_id(r, c)
            
            # 连接虚拟节点
            if color == 'B':
                if c == 0:
                    uf.union(cur_id, self.virtual1)
                if c == self.size - 1:
                    uf.union(cur_id, self.virtual2)
            else:
                if r == 0:
                    uf.union(cur_id, self.virtual1)
                if r == self.size - 1:
                    uf.union(cur_id, self.virtual2)
            
            # 检查周围节点
            directions = [(-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0)]
            for dx, dy in directions:
                nr, nc = r + dx, c + dy
                if 0 <= nr < self.size and 0 <= nc < self.size and self.board[nr][nc] == color:
                    uf.union(cur_id, self.node_id(nr, nc))
            
            return True
        return False

    def iswin(self, color):
        """
        检查指定颜色是否获胜
        Args:
            color: 棋子颜色 ('B' 或 'R')
        Returns:
            bool: 是否获胜
        """
        uf = self.uf_b if color == 'B' else self.uf_r
        return uf.connected(self.virtual1, self.virtual2)

    def isterminal(self):
        """
        检查游戏是否结束
        Returns:
            bool: 是否结束
        """
        return self.iswin('B') or self.iswin('R')

    def get_nearby_positions(self, distance=2):
        """
        获取所有已下棋子附近的可用位置
        Args:
            distance: 搜索范围
        Returns:
            list: 合法位置列表
        """
        # 检查是否是第一步
        is_first_move = all(self.board[r][c] == '.' for r in range(self.size) for c in range(self.size))
        if is_first_move:
            return [(3, 1)]  # 返回b4位置 (第4行，第2列)
            
        nearby = set()
        # 遍历棋盘找到所有已下的棋子
        for r in range(self.size):
            for c in range(self.size):
                if self.board[r][c] != '.':
                    # 检查这个棋子周围的位置
                    for dr in range(-distance, distance):
                        for dc in range(-distance, distance):
                            if max(abs(dr), abs(dc), abs(dr + dc)) <= distance:  # 确保在指定距离内！！！
                                nr, nc = r + dr, c + dc
                                if (0 <= nr < self.size and 0 <= nc < self.size and 
                                    self.board[nr][nc] == '.' and
                                    (nr, nc) in self.available):
                                    nearby.add((nr, nc))
        return list(nearby) if nearby else self.available


class MCTS:
    def __init__(self, hex, color, ai_color, parent=None, action=None):
        """
        初始化MCTS节点
        Args:
            hex: Hex棋盘状态
            color: 当前玩家颜色
            ai_color: AI的颜色
            parent: 父节点
            action: 到达该节点的动作
        """
        self.hex = copy.deepcopy(hex)  # 当前棋盘状态
        self.color = color    # 当前节点的玩家颜色
        self.ai_color = ai_color  # AI的颜色
        self.parent = parent    # 父节点
        self.action = action    # 到达该节点的动作
        self.children = {}      # 子节点字典 {动作: 子节点}
        self.N = 0  # 访问次数
        self.Q = 0  # 累计奖励
        
        # 获取当前可用的动作
        self.untried_actions = self.hex.get_nearby_positions()
    
    def select(self, c=1.5):
        """
        选择一个子节点进行扩展
        Args:
            c: UCT公式中的探索参数
        Returns:
            MCTS: 选中的节点，以及是否需要扩展新节点
        """
        node = self

        # 终止节点
        if node.hex.isterminal():
            return node, False
        
        # 存在未尝试的动作
        if node.untried_actions:
            return node, True
         
        # 选择最佳子节点
        best_score = float('-inf')
        best_child = None
        
        for action, child in node.children.items():
            if child.N == 0:
                return child, False
            
            # 计算UCT分数（从AI视角）
            exploit = child.Q / child.N
            explore = c * math.sqrt(math.log(node.N) / child.N)
            score = exploit + explore
            
            if score > best_score:
                best_score = score
                best_child = child
        
        if best_child is None:
            return node, False
            
        return best_child.select(c)
    
    def expand(self, action):
        """
        扩展当前节点
        Args:
            action: 选择的动作
        Returns:
            MCTS: 新创建的子节点
        """
        # 创建新的棋盘状态
        next_color = 'B' if self.color == 'R' else 'R'
        self.hex.play(action, self.color)
        
        # 创建子节点
        child = MCTS(copy.deepcopy(self.hex), next_color, self.ai_color, self, action)
        self.children[action] = child
        self.untried_actions.remove(action)
        
        return child
    
    def simulate(self):
        """
        模拟游戏直到终局
        Returns:
            float: 模拟结果的奖励值
        """
        state = copy.deepcopy(self.hex)
        cur_color = self.color
        
        while not state.isterminal():
            actions = state.get_nearby_positions()
            if not actions:
                break
            action = random.choice(actions)
            state.play(action, cur_color)
            cur_color = 'B' if cur_color == 'R' else 'R'
        
        # 从AI视角计算奖励
        if state.iswin(self.ai_color):
            return 1.0  # AI获胜
        elif state.iswin('B' if self.ai_color == 'R' else 'R'):
            return -1.0  # AI失败
    
    def backpropagate(self, reward):
        """
        反向传播更新节点统计信息
        Args:
            reward: 模拟获得的奖励
        """
        node = self
        while node:
            node.N += 1
            node.Q += reward
            node = node.parent

    def search(self, time_limit=5.0):
        start_time = time.time()
        simulation_count = 0
        
        while time.time() - start_time < time_limit:
            node, need_expand = self.select()
            
            if need_expand and node.untried_actions:
                action = random.choice(node.untried_actions)
                node = node.expand(action)
            
            reward = node.simulate()
            node.backpropagate(reward)
            simulation_count += 1
        
        # 选择胜率最高的动作
        best_ratio = float('-inf')
        best_action = None
        
        for action, child in self.children.items():
            if child.N > 0:
                win_ratio = child.Q / child.N
                if win_ratio > best_ratio:
                    best_ratio = win_ratio
                    best_action = action
        
        search_time = time.time() - start_time
        return best_action, best_ratio, simulation_count, search_time