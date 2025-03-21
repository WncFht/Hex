from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
import os
import logging
import traceback
from datetime import datetime
from core.game import Game
from core.utils import move_to_coord, coord_to_move, get_symmetric_move
from core.board import Board

# 创建logs目录（如果不存在）
os.makedirs('logs', exist_ok=True)

app = Flask(__name__, static_folder='hexboard', static_url_path='')
CORS(app)  # 允许跨域请求

# 配置日志
logging.basicConfig(
    filename=f'logs/app_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log',
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

# 创建游戏实例
game = Game()

@app.route('/')
def index():
    """提供前端页面"""
    logging.info("请求首页")
    return app.send_static_file('index.html')

@app.route('/api/init', methods=['POST'])
def init_game():
    """初始化游戏"""
    try:
        data = request.json
        is_first = data.get('first', True)
        difficulty = data.get('difficulty', 'medium')
        
        logging.info(f"初始化游戏 - 玩家选择先手: {is_first}, 难度: {difficulty}")
        
        # 重置游戏
        global game
        game = Game()
        
        # 设置AI难度
        game.set_difficulty(difficulty)
        
        if is_first:
            # 如果前端选择先手，则后端为后手
            game.my_color = 'B'  # AI使用蓝色
            logging.info("玩家选择先手，AI使用蓝色")
            return jsonify({
                'success': True,
                'current_player': game.current_color
            })
        else:
            # 前端选择后手，AI先手
            game.my_color = 'R'  # AI使用红色
            logging.info("玩家选择后手，AI使用红色并先行")
            move = game.handle_first_move()
            
            if not move:
                logging.error("AI首步落子失败")
                return jsonify({'error': 'AI failed to make the first move'}), 500
                
            logging.info(f"AI首步: {move}")
            return jsonify({
                'success': True,
                'move': move,
                'current_player': game.current_color
            })
    except Exception as e:
        error_msg = f"初始化游戏失败: {str(e)}\n{traceback.format_exc()}"
        logging.error(error_msg)
        return jsonify({'error': error_msg}), 500

@app.route('/api/move', methods=['POST'])
def make_move():
    """接收前端的移动并响应"""
    try:
        data = request.json
        move_str = data.get('move')
        difficulty = data.get('difficulty', 'medium')
        
        if not move_str:
            return jsonify({'error': 'No move provided'}), 400
        
        logging.info(f"收到玩家移动请求: {move_str}, 难度: {difficulty}")
        
        # 更新AI难度
        game.set_difficulty(difficulty)
        
        # 解析前端移动
        move = game._parse_move(move_str)
        if not move:
            logging.error(f"无效的移动格式: {move_str}")
            return jsonify({'error': 'Invalid move format'}), 400
        
        # 执行移动
        success = game.make_move(move)
        if not success:
            logging.error(f"无效移动: {move_str} -> ({move[0]},{move[1]})")
            return jsonify({'error': 'Invalid move'}), 400
        
        # 检查游戏是否结束
        winner = game.get_winner()
        if winner:
            logging.info(f"游戏结束，获胜者: {winner}")
            return jsonify({
                'success': True,
                'current_player': game.current_color,
                'game_over': True,
                'winner': winner
            })
        
        # 获取AI的响应
        logging.info("请求AI响应...")
        ai_move = game.get_ai_move()
        
        if ai_move:
            logging.info(f"AI响应: {ai_move}")
            # 检查游戏是否结束
            winner = game.get_winner()
            if winner:
                logging.info(f"AI移动后游戏结束，获胜者: {winner}")
                
            response = {
                'success': True,
                'move': ai_move,
                'current_player': game.current_color,
                'game_over': winner is not None,
                'winner': winner
            }
            logging.info(f"返回响应: {response}")
            return jsonify(response)
        else:
            logging.info("AI未生成响应，可能是游戏已结束")
            return jsonify({
                'success': True,
                'current_player': game.current_color,
                'game_over': False
            })
    except Exception as e:
        error_msg = f"处理移动失败: {str(e)}\n{traceback.format_exc()}"
        logging.error(error_msg)
        return jsonify({'error': error_msg}), 500

@app.route('/api/ai_move', methods=['GET'])
def get_ai_move():
    """获取AI的下一步移动"""
    try:
        difficulty = request.args.get('difficulty', 'medium')
        logging.info(f"直接请求AI移动，难度: {difficulty}")
        
        # 更新AI难度
        game.set_difficulty(difficulty)
        
        ai_move = game.get_ai_move()
        
        if not ai_move:
            logging.error("AI未能生成移动")
            return jsonify({'error': 'AI failed to generate a move'}), 500
        
        # 检查游戏是否结束
        winner = game.get_winner()
        if winner:
            logging.info(f"AI移动后游戏结束，获胜者: {winner}")
            
        response = {
            'move': ai_move,
            'current_player': game.current_color,
            'game_over': winner is not None,
            'winner': winner
        }
        logging.info(f"返回AI移动: {response}")
        return jsonify(response)
    except Exception as e:
        error_msg = f"获取AI移动失败: {str(e)}\n{traceback.format_exc()}"
        logging.error(error_msg)
        return jsonify({'error': error_msg}), 500

@app.route('/api/swap', methods=['POST'])
def swap():
    """处理交换规则"""
    try:
        logging.info("收到交换规则请求")
        data = request.json or {}
        difficulty = data.get('difficulty', 'medium')
        
        logging.info(f"交换规则请求，难度: {difficulty}")
        game.set_difficulty(difficulty)
        
        # 确保只有在第一步后才能交换
        if len(game.move_history) != 1:
            logging.error(f"交换规则只能在第一步后使用! 当前历史: {len(game.move_history)}")
            return jsonify({'error': 'Swap is only allowed after the first move'}), 400
        
        # 处理交换
        success = game.handle_swap()
        if not success:
            logging.error("应用交换规则失败")
            return jsonify({'error': 'Failed to apply swap rule'}), 400
        
        # 交换后由AI下一步棋
        logging.info("交换后请求AI移动...")
        ai_move = game.get_ai_move()
        
        # 对称位置的格式化
        first_move = game.move_history[0][0]  # 获取坐标元组
        symmetric_move = game._format_move(first_move[0], first_move[1])
        
        response = {
            'success': True,
            'symmetric_move': symmetric_move,
            'move': ai_move,
            'current_player': game.current_color
        }
        
        logging.info(f"交换规则应用成功，返回: {response}")
        return jsonify(response)
    except Exception as e:
        error_msg = f"处理交换规则失败: {str(e)}\n{traceback.format_exc()}"
        logging.error(error_msg)
        return jsonify({'error': error_msg}), 500

@app.route('/api/board', methods=['GET'])
def get_board_state():
    """获取当前棋盘状态"""
    try:
        logging.info("请求棋盘状态")
        
        # 构建棋盘状态
        board_state = {
            'size': game.board.size,
            'red_stones': [],
            'blue_stones': [],
            'current_player': game.current_color,
            'moves_history': [],
            'game_over': game.is_game_over(),
            'winner': game.get_winner()
        }
        
        # 添加棋子信息
        for r in range(game.board.size):
            for c in range(game.board.size):
                if game.board.red_stones[r][c]:
                    board_state['red_stones'].append((r, c))
                elif game.board.blue_stones[r][c]:
                    board_state['blue_stones'].append((r, c))
        
        # 添加移动历史
        for move, color in game.move_history:
            move_str = game._format_move(move[0], move[1])
            board_state['moves_history'].append({
                'move': move_str,
                'color': color
            })
        
        logging.info(f"返回棋盘状态，红子:{len(board_state['red_stones'])}个，蓝子:{len(board_state['blue_stones'])}个")
        return jsonify(board_state)
    except Exception as e:
        error_msg = f"获取棋盘状态失败: {str(e)}\n{traceback.format_exc()}"
        logging.error(error_msg)
        return jsonify({'error': error_msg}), 500

if __name__ == '__main__':
    try:
        logging.info("启动Flask应用，端口:5000")
        app.run(debug=True, port=5000)
    except Exception as e:
        logging.error(f"应用启动失败: {str(e)}\n{traceback.format_exc()}")
        sys.exit(1) 