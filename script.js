class HexGame {
    constructor(size = 11) {
        this.size = size;
        this.board = Array(size).fill().map(() => Array(size).fill(null));//初始化棋盘状态
        this.currentPlayer = "red";
        this.gameOver = false;
        this.firstMoveDone = false; // 标记第一步是否已经完成
        this.createBoard();
        this.setupEventListeners();
        this.updatePlayerTurn();
        this.mode = 'pvp';//bonus2.4接入智能模型：默认模式是玩家对玩家
    }


    createBoard() {
        const boardElement = document.getElementById("hex-board");
        boardElement.innerHTML = ''; // 清空棋盘
    
        const letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ';
    
        for (let i = 0; i < this.size + 2; i++) { 
            const row = document.createElement('div');
            row.className = 'hex-row';
            row.style.display = 'flex'; 
    
                if(i===0){
                row.style.marginLeft = `${(i) * 20 + 40}px`;}
                else if(i === this.size + 1){
                    row.style.marginLeft = `${(i-2) * 20 + 45}px`;
                }else {
                row.style.marginLeft = `${(i - 1) * 20 + 40}px`;
            }
    
            for (let j = 0; j < this.size + 2; j++) { 
                const cell = document.createElement("div");
    
                 //创建棋盘格子以及数字、字母标签
                if (i === 0 && j !== 0 && j !== this.size + 1) {
                    cell.className = 'label-cell';
                    cell.textContent = letters[j - 1];
                } else if (i === this.size + 1 && j !== 0 && j !== this.size + 1) {
                    cell.className = 'label-cell';
                    cell.textContent = letters[j - 1];
                } else if (j === 0 && i !== 0 && i !== this.size + 1) {
                    cell.className = 'label-cell';
                    cell.textContent = i;
                } else if (j === this.size + 1 && i !== 0 && i !== this.size + 1) {
                    cell.className = 'label-cell';
                    cell.textContent = i;
                } else if (i !== 0 && i !== this.size + 1 && j !== 0 && j !== this.size + 1) {
                    cell.className = 'hex-cell';
                    cell.dataset.row = i - 1;
                    cell.dataset.col = j - 1;
                } else {
                    cell.style.width = '40px';
                    cell.style.height = '46px';
                }
                // 统一样式
                cell.style.textAlign = 'center';
                cell.style.lineHeight = '46px';
    
                row.appendChild(cell);
            }
    
            boardElement.appendChild(row);
        }
    }
    

    setupEventListeners() {
        const board = document.getElementById('hex-board');//监听棋盘是否被点击
        board.addEventListener('click', (e) => {
            const cell = e.target.closest('.hex-cell');
            if (!cell || this.gameOver) return;

            const row = parseInt(cell.dataset.row);
            const col = parseInt(cell.dataset.col);

            if (this.isValidMove(row, col)) {//检查是否能落子
                this.makeMove(row, col);
                if (!this.firstMoveDone) {
                    this.firstMoveDone = true;
                    this.handleFirstMoveSwap(row, col);  // 提示用户进行交换
                    this.firstMoveDone = False;
                }
            }
        });

        document.getElementById('reset-button').addEventListener('click', () => {
            this.resetGame();
        });//监听reset-botton是否被点击

        document.getElementById('mode-select').addEventListener('change', (e) => {
            this.mode = e.target.value;
            this.resetGame();
        });//监听是否切换模式；若切换模式，重新开始游戏
    }

    isValidMove(row, col) {
        return row >= 0 && row < this.size && 
               col >= 0 && col < this.size && 
               this.board[row][col] === null;
    }

    makeMove(row, col) {
        this.board[row][col] = this.currentPlayer;//更新棋盘状态
        const cell = document.querySelector(`[data-row="${row}"][data-col="${col}"]`);//选中对应位置的cell
        cell.classList.add(this.currentPlayer);//给该格子添加颜色

        if (this.checkWin(row, col)) {
            this.gameOver = true;
            alert(`${this.currentPlayer === 'red' ? 'Red' : 'Blue'}获胜！`);
            return;
        }

        this.currentPlayer = this.currentPlayer === 'red' ? 'blue' : 'red';//改变执方
        this.updatePlayerTurn();
    }

    handleFirstMoveSwap(row, col) {
            const swap = confirm('是否要交换棋子？');
            if (swap) {
                    this.board[row][col] = null;  // 移除原棋子
                    const cell = document.querySelector(`[data-row="${row}"][data-col="${col}"]`);//选中对应位置的cell
                    cell.classList.remove(this.currentPlayer === 'red' ? 'blue' : 'red');//给该格子添加颜色
                    const targetRow = this.size - 1 - row;
                    const targetCol = this.size - 1 - col;
                    
                    // 将当前棋子移到对角线对称的位置
                    const targetCell = document.querySelector(`[data-row="${targetRow}"][data-col="${targetCol}"]`);
                    targetCell.classList.add(this.currentPlayer);
            
                    // 更新棋盘
                    this.board[targetRow][targetCol] = this.currentPlayer;
            
                    // 允许对方进行落子
                    this.currentPlayer = this.currentPlayer === 'red' ? 'blue' : 'red';
                    this.updatePlayerTurn();
            }
    }



    checkWin(row, col) {
        // 当前玩家
        const player = this.currentPlayer;
    
        // 用于记录已访问的格子
        const visited = Array(this.size).fill().map(() => Array(this.size).fill(false));
    
        // 深度优先搜索（DFS）函数
        const dfs = (r, c) => {
            if (r < 0 || r >= this.size || c < 0 || c >= this.size || visited[r][c] || this.board[r][c] !== player) {
                return false;
            }
    
            visited[r][c] = true;
    
            // 判断是否已达到胜利条件
            if (player === 'red' && r === this.size - 1) {
                return true; // 红方从顶部到底部
            }
            if (player === 'blue' && c === this.size - 1) {
                return true; // 蓝方从左到右
            }
    
            // 四个方向：上、下、左、右
            const directions = [[-1, 0], [1, 0], [0, -1], [0, 1]];
    
            for (const [dx, dy] of directions) {
                const newRow = r + dx;
                const newCol = c + dy;
                if (dfs(newRow, newCol)) {
                    return true;
                }
            }
    
            return false;
        };
    
        // 根据当前玩家选择起始点
        if (player === 'red') {
            // 红方从顶部任意一列开始
            for (let i = 0; i < this.size; i++) {
                if (this.board[0][i] === 'red' && !visited[0][i] && dfs(0, i)) {
                    return true;
                }
            }
        } else if (player === 'blue') {
            // 蓝方从左侧任意一行开始
            for (let i = 0; i < this.size; i++) {
                if (this.board[i][0] === 'blue' && !visited[i][0] && dfs(i, 0)) {
                    return true;
                }
            }
        }
    
        return false;
    }
    
    
    


    updatePlayerTurn() {
        const playerElement = document.getElementById('current-player');
        playerElement.textContent = this.currentPlayer === 'red' ? 'Red' : 'Blue';
        playerElement.style.color = this.currentPlayer;
    }

    resetGame() {
        this.board = Array(this.size).fill().map(() => Array(this.size).fill(null));
        this.currentPlayer = 'red';
        this.gameOver = false;
        this.firstMoveDone = false;  // 重置第一步状态
        this.createBoard();
        this.updatePlayerTurn();
    }
}

const game = new HexGame(); 