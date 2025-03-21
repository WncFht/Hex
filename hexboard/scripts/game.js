// game.js
class HexGame {
    constructor(board) {
        this.board = board;
        this.currentPlayer = 'R'; // 红方先手
        this.moveHistory = [];
        this.gameOver = false;
        this.winner = null;
        this.firstMove = null;
        this.canSwapNow = false;
    }

    makeMove(row, col) {
        if (this.gameOver) return false;

        if (this.board.placeStone(row, col, this.currentPlayer)) {
            const moveStr = this.formatMove(row, col);
            this.moveHistory.push({ row, col, color: this.currentPlayer, moveStr });

            // 记录第一步，用于交换规则
            if (this.moveHistory.length === 1) {
                this.firstMove = { row, col };
                this.canSwapNow = true;
            } else {
                this.canSwapNow = false;
            }

            // 切换玩家
            this.currentPlayer = this.currentPlayer === 'R' ? 'B' : 'R';

            return true;
        }

        return false;
    }

    swap() {
        if (!this.canSwapNow || this.moveHistory.length !== 1) return false;

        // 交换第一步的颜色并放到对称位置
        const { row, col } = this.firstMove;
        this.board.board[row][col] = null;

        // 计算对称位置
        const newRow = col;
        const newCol = row;

        // 放置交换后的棋子
        this.board.placeStone(newRow, newCol, 'B');

        // 更新历史记录
        this.moveHistory = [{ row: newRow, col: newCol, color: 'B', moveStr: this.formatMove(newRow, newCol) }];

        // 设置当前玩家为红方
        this.currentPlayer = 'R';
        this.canSwapNow = false;

        // 重绘棋盘
        this.board.init();

        return true;
    }

    undo() {
        if (this.moveHistory.length === 0) return false;

        const lastMove = this.moveHistory.pop();
        this.board.board[lastMove.row][lastMove.col] = null;
        this.currentPlayer = lastMove.color;
        this.gameOver = false;
        this.winner = null;

        // 处理交换规则状态
        if (this.moveHistory.length === 1) {
            this.canSwapNow = true;
        }

        // 重绘棋盘
        this.board.init();

        return true;
    }

    // 更新游戏状态（由外部API设置胜负）
    setGameResult(isGameOver, winner) {
        if (isGameOver && winner) {
            this.gameOver = true;
            this.winner = winner;
        }
    }

    formatMove(row, col) {
        return `${String.fromCharCode(97 + col)}${row + 1}`;
    }

    parseMove(moveStr) {
        if (moveStr.length < 2) return null;
        const col = moveStr.charCodeAt(0) - 97;
        const row = parseInt(moveStr.slice(1)) - 1;
        return { row, col };
    }

    getGameState() {
        return {
            board: this.board.board,
            currentPlayer: this.currentPlayer,
            moveHistory: this.moveHistory,
            gameOver: this.gameOver,
            winner: this.winner,
            canSwap: this.canSwapNow
        };
    }

    loadGameState(state) {
        this.board.board = state.board;
        this.currentPlayer = state.currentPlayer;
        this.moveHistory = state.moveHistory;
        this.gameOver = state.gameOver;
        this.winner = state.winner;
        this.canSwapNow = state.canSwap;

        // 重绘棋盘
        this.board.init();
    }

    resetGame() {
        this.board.board = Array(this.board.size).fill().map(() => Array(this.board.size).fill(null));
        this.currentPlayer = 'R';
        this.moveHistory = [];
        this.gameOver = false;
        this.winner = null;
        this.firstMove = null;
        this.canSwapNow = false;

        // 重绘棋盘
        this.board.init();
    }
}