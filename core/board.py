from typing import List, Optional, Tuple

class UnionFind:
    """并查集实现"""
    def __init__(self, n):
        self.parent = list(range(n))
        self.rank = [0] * n
    
    def find(self, x):
        """查找x的根节点"""
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])
        return self.parent[x]
    
    def union(self, x, y):
        """合并x和y所在的集合"""
        root_x = self.find(x)
        root_y = self.find(y)
        if root_x == root_y:
            return
        if self.rank[root_x] < self.rank[root_y]:
            self.parent[root_x] = root_y
        else:
            self.parent[root_y] = root_x
            if self.rank[root_x] == self.rank[root_y]:
                self.rank[root_x] += 1
    
    def connected(self, x, y):
        """判断x和y是否连通"""
        return self.find(x) == self.find(y)

class Board:
    def __init__(self, size: int = 11):
        """初始化棋盘
        Args:
            size: 棋盘大小，默认11x11
        """
        self.size = size
        self.board = [['.' for _ in range(size)] for _ in range(size)]
        # 为红蓝双方分别创建棋子矩阵
        self.red_stones = [[False for _ in range(size)] for _ in range(size)]
        self.blue_stones = [[False for _ in range(size)] for _ in range(size)]
        # 为每个颜色维护一个并查集
        self.uf_b = UnionFind(size * size + 2)  # 蓝方(B)的并查集
        self.uf_r = UnionFind(size * size + 2)  # 红方(R)的并查集
        self.virtual1 = size * size      # 虚拟节点1（用于连接边界）
        self.virtual2 = size * size + 1  # 虚拟节点2（用于连接边界）
        self.available = [(r, c) for r in range(size) for c in range(size)]

    def place_stone(self, row: int, col: int, color: str) -> bool:
        """在指定位置落子
        Args:
            row: 行坐标
            col: 列坐标
            color: 棋子颜色 ('B' 或 'R')
        Returns:
            bool: 落子是否成功
        """
        if not self.is_valid_move(row, col):
            return False
            
        self.board[row][col] = color
        # 更新红蓝棋子矩阵
        if color == 'R':
            self.red_stones[row][col] = True
        else:
            self.blue_stones[row][col] = True
            
        self.available.remove((row, col))
        
        # 选择对应颜色的并查集
        uf = self.uf_b if color == 'B' else self.uf_r
        cur_id = self._node_id(row, col)
        
        # 连接虚拟节点
        if color == 'B':
            if col == 0:
                uf.union(cur_id, self.virtual1)
            if col == self.size - 1:
                uf.union(cur_id, self.virtual2)
        else:
            if row == 0:
                uf.union(cur_id, self.virtual1)
            if row == self.size - 1:
                uf.union(cur_id, self.virtual2)
        
        # 检查周围节点
        directions = [(-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0)]
        for dx, dy in directions:
            nr, nc = row + dx, col + dy
            if 0 <= nr < self.size and 0 <= nc < self.size and self.board[nr][nc] == color:
                uf.union(cur_id, self._node_id(nr, nc))
        
        return True

    def is_valid_move(self, row: int, col: int) -> bool:
        """检查移动是否合法
        Args:
            row: 行坐标
            col: 列坐标
        Returns:
            bool: 是否合法
        """
        return (0 <= row < self.size and 
                0 <= col < self.size and 
                self.board[row][col] == '.' and 
                (row, col) in self.available)

    def get_board_state(self) -> List[List[str]]:
        """获取当前棋盘状态
        Returns:
            List[List[str]]: 棋盘状态的深拷贝
        """
        return [row[:] for row in self.board]

    def check_winner(self) -> Optional[str]:
        """检查是否有获胜方
        Returns:
            Optional[str]: 获胜方颜色，无获胜方时返回 None
        """
        if self.uf_b.connected(self.virtual1, self.virtual2):
            return 'B'
        if self.uf_r.connected(self.virtual1, self.virtual2):
            return 'R'
        return None

    def _node_id(self, row: int, col: int) -> int:
        """将二维坐标转换为一维节点编号"""
        return row * self.size + col 