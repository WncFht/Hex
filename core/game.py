import sys
import logging
import time
import os
import random
from typing import Tuple, Optional
from datetime import datetime

from .board import Board
from ai.mcts import MCTS

# 创建logs目录（如果不存在）
os.makedirs('logs', exist_ok=True)

# 配置日志
logging.basicConfig(
    filename=f'logs/game_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    encoding='utf-8'  # 明确指定UTF-8编码
)

# 添加一个控制台处理器，让日志同时输出到控制台
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler.setFormatter(console_formatter)
logging.getLogger().addHandler(console_handler)

    
class Game:
    def __init__(self, board_size: int = 11):
        """初始化游戏
        Args:
            board_size: 棋盘大小
        """
        self.board = Board(board_size)
        self.mcts = None
        self.my_color = None
        self.current_color = 'R'  # 红方先手
        self.move_history = []
        self.start_time = time.time()
        self.difficulty = 'medium'  # 默认中等难度
        self.search_times = {
            'easy': 2.0,    # 简单难度搜索2秒
            'medium': 5.0,  # 中等难度搜索5秒
            'hard': 10.0    # 困难难度搜索10秒
        }
        logging.info("Game initialized with board size %d", board_size)
        self._log_board_state()

    def set_difficulty(self, difficulty: str):
        """设置AI难度
        Args:
            difficulty: 难度级别 ('easy', 'medium', 'hard')
        """
        if difficulty in self.search_times:
            old_difficulty = self.difficulty
            self.difficulty = difficulty
            logging.info(f"AI难度从 {old_difficulty} 更改为 {difficulty}")
        else:
            logging.warning(f"无效的难度设置: {difficulty}，使用默认难度: {self.difficulty}")

    def handle_first_move(self) -> str:
        """处理先手情况
        Returns:
            str: 第一步的移动
        """
        # 中心位置
        center = self.board.size // 2
        
        # 在中心位置放置棋子
        success = self.make_move((center, center))
        first_move = self._format_move(center, center)
        
        if not success:
            # 尝试其他位置
            logging.info("中心位置不可用，尝试其他位置")
            for r in range(center-1, center+2):
                for c in range(center-1, center+2):
                    if r < 0 or r >= self.board.size or c < 0 or c >= self.board.size:
                        continue
                    if (r, c) in self.board.available:
                        success = self.make_move((r, c))
                        if success:
                            first_move = self._format_move(r, c)
                            logging.info(f"使用备选位置: ({r}, {c})")
                            break
                if success:
                    break
                    
            if not success:
                # 如果附近位置都不可用，选择任意可用位置
                logging.info("所有临近位置不可用，选择任意可用位置")
                if self.board.available:
                    r, c = self.board.available[0]
                    success = self.make_move((r, c))
                    if success:
                        first_move = self._format_move(r, c)
                        logging.info(f"使用随机位置: ({r}, {c})")
        
        self.my_color = 'R'
        logging.info(f"AI作为先手，移动到 {first_move}")
        self._log_board_state()
        return first_move

    def handle_opponent_first_move(self, move_str: str) -> str:
        """处理对手先手情况
        Args:
            move_str: 对手的移动
        Returns:
            str: 我方的响应（change 或 移动坐标）
        """
        move = self._parse_move(move_str)
        self.make_move(move)
        
        # 判断是否交换
        if 3 <= move[0] <= 7 and 3 <= move[1] <= 7:
            self.my_color = 'R'
            logging.info("Choosing to swap")
            return "change"
        else:
            sym_move = self._get_symmetric_move(move_str)
            move = self._parse_move(sym_move)
            self.make_move(move)
            self.my_color = 'B'
            logging.info("Not swapping, moved to %s", sym_move)
            return sym_move

    def make_move(self, move: Tuple[int, int]) -> bool:
        """执行一步移动
        Args:
            move: (row, col) 坐标
        Returns:
            bool: 移动是否成功
        """
        success = self.board.place_stone(move[0], move[1], self.current_color)
        if success:
            self.move_history.append((move, self.current_color))
            old_color = self.current_color
            self.current_color = 'B' if self.current_color == 'R' else 'R'
            self._log_move(move, old_color)
            self._log_performance()
            
            # 移动后检查是否有赢家
            winner = self.get_winner()
            if winner:
                logging.info(f"移动后检测到赢家: {winner}")
        else:
            logging.warning(f"移动失败! 位置: ({move[0]},{move[1]}), 颜色: {self.current_color}")
            
        return success

    def handle_swap(self):
        """处理交换规则"""
        if len(self.move_history) != 1:
            logging.error(f"交换规则只能在第一步后使用! 当前历史: {len(self.move_history)}")
            return False
            
        # 获取第一步移动
        first_move, first_color = self.move_history[0]
        logging.info(f"应用交换规则，第一步: ({first_move[0]},{first_move[1]}), 颜色: {first_color}")
        
        # 重置棋盘
        self.board = Board(self.board.size)
        
        # 计算对称位置
        new_row, new_col = first_move[1], first_move[0]
        
        # 在对称位置放置棋子
        success = self.board.place_stone(new_row, new_col, 'B')
        if not success:
            logging.error(f"交换规则应用失败! 目标位置: ({new_row},{new_col})")
            return False
        
        # 更新游戏状态
        self.move_history = [((new_row, new_col), 'B')]
        self.current_color = 'R'  # 轮到红方
        
        # 如果AI原来是红方，现在变为蓝方
        old_color = self.my_color
        if self.my_color == 'R':
            self.my_color = 'B'
        else:
            self.my_color = 'R'
            
        logging.info(f"交换规则应用成功 - 对称位置: ({new_row},{new_col}), AI颜色从 {old_color} 变为 {self.my_color}")
        self._log_board_state()
        
        # 重置MCTS
        self.mcts = None
        
        return True

    def get_ai_move(self) -> Optional[str]:
        """获取 AI 的下一步移动
        Returns:
            str: 移动坐标
        """
        logging.info(f"请求AI移动 - 当前玩家:{self.current_color}, AI颜色:{self.my_color or '未设置'}, 难度:{self.difficulty}")
        
        # 检查是否已经结束
        winner = self.get_winner()
        if winner:
            logging.info(f"游戏已结束，获胜者: {winner}")
            return None
            
        # 检查是否有可用移动
        if not self.board.available:
            logging.info("没有可用的移动位置")
            return None
        
        # 如果不是AI的回合
        if self.my_color and self.current_color != self.my_color:
            logging.warning(f"不是AI的回合! 当前回合: {self.current_color}, AI: {self.my_color}")
            return None
            
        if not self.mcts:
            # 确保my_color已设置，如果未设置，默认为当前颜色
            if self.my_color is None:
                self.my_color = self.current_color
                logging.info(f"未设置AI颜色，默认设为当前颜色: {self.current_color}")
                
            logging.info(f"创建新的MCTS实例 - 当前颜色:{self.current_color}, AI颜色:{self.my_color}")
            self.mcts = MCTS(self.board, self.current_color, self.my_color)
        else:
            # 更新MCTS的状态
            logging.info(f"更新MCTS实例 - 当前颜色:{self.current_color}")
            self.mcts.hex = self.board
            self.mcts.color = self.current_color
        
        # 根据难度获取搜索时间
        time_limit = self.search_times.get(self.difficulty, 5.0)
        logging.info(f"开始MCTS搜索...难度: {self.difficulty}, 搜索时间: {time_limit}秒")
        
        # 执行搜索
        start_time = time.time()
        move, ratio, count, time_spent = self.mcts.search(time_limit=time_limit)
        
        if move:
            move_str = self._format_move(move[0], move[1])
            logging.info(f"AI选择移动: {move_str} ({move[0]},{move[1]}), 胜率: {ratio:.3f}, 模拟次数: {count}")
            
            # 检查移动是否有效
            if move not in self.board.available:
                logging.error(f"AI尝试无效移动! 位置: {move}")
                available_moves = list(self.board.available)
                if available_moves:
                    move = random.choice(available_moves)
                    move_str = self._format_move(move[0], move[1])
                    logging.info(f"回退到随机移动: {move_str}")
                else:
                    logging.error("没有可用的移动位置!")
                    return None
            
            # 执行移动
            success = self.make_move(move)
            if success:
                logging.info(f"AI成功移动到: {move_str}")
                self._log_board_state()
                return move_str
            else:
                logging.error(f"AI移动失败: {move_str}")
                return None
        else:
            logging.error("AI无法生成有效移动!")
            return None

    def is_game_over(self) -> bool:
        """检查游戏是否结束"""
        winner = self.board.check_winner()
        if winner:
            logging.info(f"游戏结束，获胜者: {winner}")
        return winner is not None

    def get_winner(self) -> Optional[str]:
        """获取获胜方"""
        return self.board.check_winner()

    def _parse_move(self, move_str: str) -> Optional[Tuple[int, int]]:
        """解析移动坐标
        Args:
            move_str: 坐标字符串 (如 'a1')
        Returns:
            Tuple[int, int]: (row, col) 坐标
        """
        try:
            if len(move_str) < 2:
                logging.error(f"无效的移动格式! 输入: {move_str}")
                return None
            col = ord(move_str[0].lower()) - ord('a')
            row = int(move_str[1:]) - 1
            
            # 检查坐标有效性
            if row < 0 or row >= self.board.size or col < 0 or col >= self.board.size:
                logging.error(f"坐标超出范围! 解析结果: ({row},{col}), 输入: {move_str}")
                return None
                
            return (row, col)
        except Exception as e:
            logging.error(f"解析移动坐标失败! 输入: {move_str}, 错误: {str(e)}")
            return None

    def _format_move(self, row: int, col: int) -> str:
        """格式化移动坐标
        Args:
            row: 行坐标
            col: 列坐标
        Returns:
            str: 格式化的坐标字符串
        """
        return f"{chr(ord('a') + col)}{row + 1}"

    def _get_symmetric_move(self, move_str: str) -> Optional[str]:
        """获取对称位置
        Args:
            move_str: 原始坐标
        Returns:
            str: 对称坐标
        """
        move = self._parse_move(move_str)
        if move:
            new_row, new_col = move[1], move[0]
            return self._format_move(new_row, new_col)
        return None

    def _log_move(self, move: Tuple[int, int], color: str):
        """记录移动日志"""
        move_str = self._format_move(move[0], move[1])
        logging.info(
            "Move: %s, Color: %s, Position: (%d, %d)", 
            move_str,
            color, 
            move[0], 
            move[1]
        )

    def _log_performance(self):
        """记录性能统计"""
        elapsed = time.time() - self.start_time
        moves = len(self.move_history)
        avg_time = elapsed / moves if moves > 0 else 0
        logging.info(
            "Performance - Total time: %.2fs, Moves: %d, Avg time per move: %.2fs",
            elapsed, moves, avg_time
        )

    def _log_board_state(self):
        """记录当前棋盘状态"""
        board_str = "\n"
        row_header = "   "
        for c in range(self.board.size):
            row_header += f"{chr(ord('a') + c)} "
        board_str += row_header + "\n"
        
        for r in range(self.board.size):
            row = f"{r+1:2d} "
            # 添加正确的空格缩进
            if r > 0:
                row = " " * (r) + row 
            
            for c in range(self.board.size):
                pos = (r, c)
                if self.board.red_stones[r][c]:
                    row += "R "
                elif self.board.blue_stones[r][c]:
                    row += "B "
                else:
                    row += ". "
            board_str += row + "\n"
        
        logging.info(f"当前棋盘状态:\n{board_str}")

def main():
    """主游戏循环"""
    game = Game()
    
    # 读取第一行输入
    first_input = input().strip()
    
    if first_input == "first":
        # 作为先手
        print(game.handle_first_move())
        sys.stdout.flush()
    else:
        # 作为后手
        response = game.handle_opponent_first_move(first_input)
        print(response)
        sys.stdout.flush()
    
    # 主游戏循环
    while True:
        cmd = input().strip()
        
        if cmd == "finish":
            break
            
        if cmd == "change":
            game.handle_swap()
        else:
            move = game._parse_move(cmd)
            if move:
                game.make_move(move)
                
                # 获取 AI 的响应
                ai_move = game.get_ai_move()
                if ai_move:
                    print(ai_move)
                    sys.stdout.flush()

if __name__ == "__main__":
    main() 