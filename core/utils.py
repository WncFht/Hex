from typing import Tuple, Optional

def coord_to_move(row: int, col: int) -> str:
    """将坐标转换为移动字符串
    Args:
        row: 行坐标
        col: 列坐标
    Returns:
        str: 移动字符串 (如 'a1')
    """
    return f"{chr(ord('a') + col)}{row + 1}"

def move_to_coord(move_str: str) -> Optional[Tuple[int, int]]:
    """将移动字符串转换为坐标
    Args:
        move_str: 移动字符串 (如 'a1')
    Returns:
        Optional[Tuple[int, int]]: (row, col) 坐标，无效输入返回 None
    """
    try:
        if len(move_str) < 2:
            return None
        col = ord(move_str[0].lower()) - ord('a')
        row = int(move_str[1:]) - 1
        return (row, col)
    except:
        return None

def get_symmetric_move(move_str: str) -> Optional[str]:
    """获取对称位置
    Args:
        move_str: 原始坐标
    Returns:
        Optional[str]: 对称坐标，无效输入返回 None
    """
    coords = move_to_coord(move_str)
    if coords:
        row, col = coords
        return coord_to_move(col, row)
    return None 