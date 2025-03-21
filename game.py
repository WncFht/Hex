from MCTS import Hex, MCTS
import sys

# 格式转换
def parse_move(move_str):
    try:
        if len(move_str) < 2:
            return None
        col = ord(move_str[0].lower()) - ord('a')
        row = int(move_str[1:]) - 1
        return (row, col)
    except:
        return None

# 格式转换
def format_move(row, col):
    return f"{chr(ord('a') + col)}{row + 1}"

# 获取对称位置
def get_symmetric_move(move_str):
    move = parse_move(move_str)
    if move:
        # 交换行列位置
        new_row, new_col = move[1], move[0]
        return format_move(new_row, new_col)
    return None

def main():
    board_size = 11
    game = Hex(board_size)
    mcts = None
    
    # 读取第一行输入
    first_input = input().strip()
    
    if first_input == "first":
        # 作为先手，固定在b4位置落子
        first_move = "b4"
        print(first_move)
        sys.stdout.flush()
        
        move = parse_move(first_move)
        game.play(move, 'R')  # 先手为红色
        my_color = 'R'
    else:
        # 作为后手，考虑是否交换
        opponent_move = first_input
        move = parse_move(opponent_move)
        game.play(move, 'R')  # 先手为红色
        
        # 如果对手下在好位置
        if 3 <= move[0] <= 7 and 3 <= move[1] <= 7:
            print("change")
            sys.stdout.flush()
            my_color = 'R'
        else:
            # 不交换
            sym_move = get_symmetric_move(opponent_move)
            print(sym_move)
            sys.stdout.flush()
            move = parse_move(sym_move)
            game.play(move, 'B')
            my_color = 'B'
    
    # 主游戏循环
    while True:
        # 读取输入
        cmd = input().strip()
        
        # 检查是否游戏结束
        if cmd == "finish":
            break
            
        # 处理对手的移动
        if cmd == "change":
            # 对手选择交换，更新颜色
            my_color = 'B' if my_color == 'R' else 'R'
        else:
            # 对手落子
            move = parse_move(cmd)
            opponent_color = 'B' if my_color == 'R' else 'R'
            game.play(move, opponent_color)
        
        # 计算下一步移动
        if not mcts:
            mcts = MCTS(game, my_color, my_color)
        
        move, ratio, _, _ = mcts.search(time_limit=9.99)  # 限制思考时间
        
        # 输出移动
        if move:
            move_str = format_move(move[0], move[1])
            print(move_str)
            sys.stdout.flush()
            
            # 更新游戏状态
            game.play(move, my_color)
            
            # 更新MCTS树
            for child in mcts.children.values():
                if child.action == move:
                    mcts = child
                    break
            else:
                mcts = None

if __name__ == "__main__":
    main()