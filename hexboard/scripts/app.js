// app.js
const { createApp } = Vue;

createApp({
    data() {
        return {
            hexBoard: null,
            game: null,
            api: null,
            boardSize: 11,
            currentPlayer: 'R',
            gameStatus: '',
            moveHistory: [],
            canUndo: false,
            canSwap: false,
            gameMode: 'human',
            aiLevel: 'medium',
            redColor: '#FF5252',
            blueColor: '#4285F4',
            isAIThinking: false
        };
    },
    mounted() {
        const canvas = document.getElementById('hexBoard');
        this.hexBoard = new HexBoard(canvas, this.boardSize);
        this.game = new HexGame(this.hexBoard);
        this.api = new HexAPI();

        window.addEventListener('resize', this.resizeCanvas);
        this.resizeCanvas();
    },
    methods: {
        resizeCanvas() {
            const canvas = document.getElementById('hexBoard');
            const container = canvas.parentElement;
            canvas.width = container.clientWidth;
            canvas.height = container.clientWidth * 0.75;
            this.hexBoard.init();
        },

        async newGame() {
            // 重置本地游戏状态
            this.game.resetGame();

            if (this.gameMode === 'ai') {
                // 在人机对弈模式下，初始化后端游戏
                this.isAIThinking = true;
                const response = await this.api.initGame(true, this.aiLevel); // 玩家先手，传递难度
                this.isAIThinking = false;

                if (response && response.success) {
                    // 显示AI的第一步
                    if (response.move) {
                        const moveCoord = this.game.parseMove(response.move);
                        if (moveCoord) {
                            this.game.makeMove(moveCoord.row, moveCoord.col);
                        }
                    }
                }
            }

            this.updateGameState();
        },

        async handleBoardClick(event) {
            if (this.isAIThinking || this.game.gameOver) return;

            const rect = event.target.getBoundingClientRect();
            const x = event.clientX - rect.left;
            const y = event.clientY - rect.top;

            // 将鼠标坐标转换为相对于画布的坐标（考虑缩放）
            const scaledX = x * (this.hexBoard.canvas.width / rect.width);
            const scaledY = y * (this.hexBoard.canvas.height / rect.height);

            const hexCoord = this.hexBoard.getHexFromPoint(scaledX, scaledY);
            if (!hexCoord) return;

            const { row, col } = hexCoord;
            const moveStr = this.game.formatMove(row, col);

            // 人人对弈模式下直接处理本地逻辑
            if (this.gameMode === 'human') {
                if (this.game.makeMove(row, col)) {
                    this.updateGameState();

                    // 对于人人对弈，需要模拟判断胜负（可选），这里假设没有胜负逻辑
                }
                return;
            }

            // 人机对弈模式
            // 首先在本地执行落子
            if (this.game.makeMove(row, col)) {
                this.updateGameState();

                if (!this.game.gameOver) {
                    this.isAIThinking = true;

                    try {
                        // 发送玩家的移动到后端，传递难度
                        const response = await this.api.makeMove(moveStr, this.aiLevel);

                        if (response && response.success) {
                            // 如果后端返回了AI的移动
                            if (response.move) {
                                const aiMoveCoord = this.game.parseMove(response.move);
                                if (aiMoveCoord) {
                                    this.game.makeMove(aiMoveCoord.row, aiMoveCoord.col);
                                }
                            }

                            // 使用后端的胜负判断结果
                            if (response.game_over) {
                                this.game.setGameResult(true, response.winner);
                            }

                            this.updateGameState();
                        }
                    } catch (error) {
                        console.error('Error communicating with backend:', error);
                    } finally {
                        this.isAIThinking = false;
                    }
                }
            }
        },

        updateGameState() {
            const state = this.game.getGameState();
            this.currentPlayer = state.currentPlayer;
            this.moveHistory = state.moveHistory.map(m => m.moveStr);
            this.canUndo = this.moveHistory.length > 0 && this.gameMode !== 'ai';
            this.canSwap = state.canSwap && (this.gameMode === 'human' || this.currentPlayer === 'B');

            if (state.gameOver) {
                this.gameStatus = state.winner === 'R' ? '红方获胜！' : '蓝方获胜！';
            } else {
                this.gameStatus = '';
            }
        },

        undo() {
            // 人机对弈模式下禁用悔棋
            if (this.gameMode === 'ai') return false;

            if (this.game.undo()) {
                this.updateGameState();
            }
        },

        async swap() {
            if (!this.game.canSwapNow || this.game.moveHistory.length !== 1) return false;

            if (this.gameMode === 'human') {
                // 人人对弈模式下，直接在前端执行交换
                if (this.game.swap()) {
                    this.updateGameState();
                }
            } else {
                // 人机对弈模式下，通过API执行交换
                this.isAIThinking = true;

                try {
                    const response = await this.api.swap(this.aiLevel);

                    if (response && response.success) {
                        // 重置本地游戏状态
                        this.game.resetGame();

                        // 应用对称移动
                        if (response.symmetric_move) {
                            const moveCoord = this.game.parseMove(response.symmetric_move);
                            if (moveCoord) {
                                this.game.makeMove(moveCoord.row, moveCoord.col);
                            }
                        }

                        // 应用AI移动
                        if (response.move) {
                            const aiMoveCoord = this.game.parseMove(response.move);
                            if (aiMoveCoord) {
                                this.game.makeMove(aiMoveCoord.row, aiMoveCoord.col);
                            }
                        }

                        this.updateGameState();
                    }
                } catch (error) {
                    console.error('Error swapping:', error);
                } finally {
                    this.isAIThinking = false;
                }
            }
        },

        goToMove(index) {
            // 实现回到历史特定步骤的功能
            // 代码实现略
        },

        changeBoardSize() {
            this.hexBoard.resize(Number(this.boardSize));
            this.game = new HexGame(this.hexBoard);
            this.updateGameState();
        },

        updateBoardColors() {
            this.hexBoard.updateColors(this.redColor, this.blueColor);
        },

        saveGame() {
            const gameState = this.game.getGameState();
            const blob = new Blob([JSON.stringify(gameState)], { type: 'application/json' });
            const url = URL.createObjectURL(blob);

            const a = document.createElement('a');
            a.href = url;
            a.download = `hex_game_${new Date().toISOString().slice(0, 10)}.json`;
            a.click();

            URL.revokeObjectURL(url);
        },

        loadGame(event) {
            const file = event.target.files[0];
            if (!file) return;

            const reader = new FileReader();
            reader.onload = (e) => {
                try {
                    const gameState = JSON.parse(e.target.result);
                    this.game.loadGameState(gameState);
                    this.updateGameState();
                } catch (error) {
                    console.error('Error loading game:', error);
                    alert('无法读取棋谱文件');
                }
            };
            reader.readAsText(file);
        }
    }
}).mount('#app');