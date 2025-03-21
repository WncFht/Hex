import random
import time
import math
import copy
import logging
import sys
from typing import Tuple, List, Optional

# 为MCTS类设置日志编码
if not logging.getLogger().handlers:
    logging.basicConfig(encoding='utf-8')  # 确保日志使用UTF-8编码

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
        self.untried_actions = list(self.hex.available)
        
        # 如果棋盘中间位置可用，则增加权重
        center = self.hex.size // 2
        center_region = [(r, c) for r in range(center-1, center+2) for c in range(center-1, center+2)]
        
        self.prioritized_actions = []
        # 优先选择靠近中心的位置
        for action in self.untried_actions:
            if action in center_region:
                self.prioritized_actions.append(action)
        
        if parent is None:  # 根节点记录详细日志
            logging.info(f"MCTS初始化 - 当前颜色:{color}, AI颜色:{ai_color}, 可用动作数量:{len(self.untried_actions)}")
    
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
        if node.hex.check_winner() is not None:
            if self.parent is None:  # 只在根节点记录
                logging.info(f"选择阶段 - 到达终止节点，赢家: {node.hex.check_winner()}")
            return node, False
        
        # 存在未尝试的动作
        if node.untried_actions:
            if self.parent is None:  # 只在根节点记录
                logging.info(f"选择阶段 - 节点有未尝试动作，数量: {len(node.untried_actions)}")
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
            
        if self.parent is None:  # 只在根节点记录
            row, col = best_child.action
            logging.info(f"选择阶段 - 选择最佳子节点，动作:({row},{col})，UCT分数:{best_score:.4f}")
            
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
        row, col = action
        self.hex.place_stone(row, col, self.color)
        
        # 创建子节点
        child = MCTS(copy.deepcopy(self.hex), next_color, self.ai_color, self, action)
        self.children[action] = child
        
        if action in self.untried_actions:
            self.untried_actions.remove(action)
        
        if self.parent is None:  # 只在根节点记录
            logging.info(f"扩展阶段 - 在位置({row},{col})扩展新节点，当前颜色:{self.color}，下一颜色:{next_color}")
            
        return child
    
    def simulate(self):
        """
        模拟游戏直到终局
        Returns:
            float: 模拟结果的奖励值
        """
        state = copy.deepcopy(self.hex)
        cur_color = self.color
        moves_count = 0
        
        while state.check_winner() is None:
            actions = list(state.available)
            if not actions:
                break
                
            # 使用启发式选择：优先选择靠近中心的位置
            center = state.size // 2
            center_region = [(r, c) for r in range(center-1, center+2) for c in range(center-1, center+2)]
            
            prioritized_actions = [action for action in actions if action in center_region]
            
            if prioritized_actions and random.random() < 0.5:  # 50%的概率选择中心区域
                action = random.choice(prioritized_actions)
            else:
                action = random.choice(actions)
                
            state.place_stone(action[0], action[1], cur_color)
            cur_color = 'B' if cur_color == 'R' else 'R'
            moves_count += 1
        
        # 从AI视角计算奖励
        winner = state.check_winner()
        reward = 0.0
        
        if winner == self.ai_color:
            reward = 1.0  # AI获胜
        elif winner is not None:
            reward = -1.0  # AI失败
        
        if self.parent is None and random.random() < 0.05:  # 根节点，并且有5%概率记录详细模拟结果
            logging.info(f"模拟阶段 - 进行了{moves_count}步模拟，结果: {winner or '平局'}，奖励值:{reward}")
            
        return reward
    
    def backpropagate(self, reward):
        """
        反向传播更新节点统计信息
        Args:
            reward: 模拟获得的奖励
        """
        node = self
        while node:
            old_n = node.N
            old_q = node.Q
            node.N += 1
            node.Q += reward
            
            if node.parent is None:  # 只在根节点记录，每100次更新记录一次
                if node.N % 100 == 0:
                    logging.info(f"反向传播 - 根节点更新: N:{old_n}->{node.N}, Q:{old_q:.2f}->{node.Q:.2f}, 平均值:{node.Q/node.N:.4f}")
            
            node = node.parent

    def search(self, time_limit=5.0):
        """
        执行MCTS搜索，找到最佳动作
        Args:
            time_limit: 搜索时间限制（秒）
        Returns:
            Tuple: (最佳动作, 胜率, 模拟次数, 搜索时间)
        """
        start_time = time.time()
        simulation_count = 0
        
        logging.info(f"开始MCTS搜索 - 时间限制:{time_limit}秒")
        
        # 如果是首步，优先选择中心位置
        if len(self.untried_actions) == self.hex.size * self.hex.size:
            center = self.hex.size // 2
            center_move = (center, center)
            if center_move in self.untried_actions:
                logging.info(f"首步直接选择中心位置 ({center}, {center})")
                return center_move, 1.0, 1, 0.0
                
        # 为加快计算，首先限制在时间允许的情况下扩展主要的动作
        expand_limit = min(20, len(self.untried_actions))  # 最多扩展20个动作
        
        # 优先扩展靠近中心的位置
        if self.prioritized_actions:
            for action in self.prioritized_actions[:min(5, len(self.prioritized_actions))]:
                if time.time() - start_time >= time_limit:
                    break
                node = self.expand(action)
                reward = node.simulate()
                node.backpropagate(reward)
                simulation_count += 1
        
        while time.time() - start_time < time_limit:
            node, need_expand = self.select()
            
            if need_expand and node.untried_actions:
                if node.prioritized_actions:
                    action = random.choice(node.prioritized_actions)
                    node.prioritized_actions.remove(action)
                else:
                    action = random.choice(node.untried_actions)
                node = node.expand(action)
            
            reward = node.simulate()
            node.backpropagate(reward)
            simulation_count += 1
            
            # 每500次模拟记录一次进度
            if simulation_count % 500 == 0:
                elapsed = time.time() - start_time
                logging.info(f"搜索进度 - 已完成{simulation_count}次模拟，用时:{elapsed:.2f}秒，平均:{simulation_count/elapsed:.1f}次/秒")
        
        # 选择胜率最高的动作
        best_ratio = float('-inf')
        best_action = None
        
        # 记录所有动作的统计信息
        action_stats = []
        
        for action, child in self.children.items():
            if child.N > 0:
                win_ratio = child.Q / child.N
                action_stats.append((action, win_ratio, child.N))
                if win_ratio > best_ratio:
                    best_ratio = win_ratio
                    best_action = action
        
        search_time = time.time() - start_time
        
        # 如果没有找到最佳动作（可能是时间太短），则从未尝试的动作中随机选择一个
        if best_action is None and self.untried_actions:
            # 优先选择中心区域
            center = self.hex.size // 2
            center_moves = [(r, c) for r, c in self.untried_actions 
                            if abs(r - center) <= 2 and abs(c - center) <= 2]
            
            if center_moves:
                best_action = random.choice(center_moves)
            else:
                best_action = random.choice(self.untried_actions)
            best_ratio = 0.5  # 随机估计
            
            logging.info(f"未能找到最佳动作，随机选择: {best_action}")
        
        # 记录前5个最佳动作
        action_stats.sort(key=lambda x: x[1], reverse=True)
        top_moves = action_stats[:min(5, len(action_stats))]
        
        log_msg = f"MCTS搜索完成 - 用时:{search_time:.2f}秒，模拟次数:{simulation_count}\n"
        log_msg += f"前{len(top_moves)}个最佳动作:\n"
        
        for i, (action, ratio, visits) in enumerate(top_moves):
            row, col = action
            log_msg += f"  {i+1}. 位置:({row},{col}) - 胜率:{ratio:.4f}, 访问次数:{visits}\n"
        
        if best_action:
            row, col = best_action
            log_msg += f"选择最佳动作:({row},{col})，胜率:{best_ratio:.4f}"
        else:
            log_msg += "未找到有效动作"
            
        logging.info(log_msg)
        
        return best_action, best_ratio, simulation_count, search_time