// board.js
class HexBoard {
    constructor(canvas, size = 11) {
        this.canvas = canvas;
        this.ctx = canvas.getContext('2d');
        this.size = size;
        this.hexSize = 30; // 增大六边形大小
        this.board = Array(size).fill().map(() => Array(size).fill(null));
        this.redColor = '#FF5252';
        this.blueColor = '#4285F4';

        this.offsetX = 100;
        this.offsetY = 50;
        this.initialWidth = 0;
        this.initialHeight = 0;

        // 棋盘样式参数
        this.gridLineWidth = 1.0;
        this.gridLineColor = 'rgba(0, 0, 0, 0.08)';
        this.backgroundColor = '#f5f7fa';
        this.coordinateColor = 'rgba(0, 0, 0, 0.4)';
        this.showCoordinates = false; // 默认不显示坐标
        this.highlightLastMove = true;
        this.lastMove = null;

        // 增强视觉效果的参数
        this.useGradient = true;
        this.useShadow = true;
        this.hexPadding = 0.92; // 增大六边形填充比例
        this.redGradient = ['#FF5252', '#FF1744'];
        this.blueGradient = ['#4285F4', '#0D47A1'];
        this.highlightColor = '#FFD700';
        this.highlightGlow = 8;

        this.init();
    }

    init() {
        // 保存初始画布尺寸
        if (this.initialWidth === 0) {
            this.initialWidth = this.canvas.width;
            this.initialHeight = this.canvas.height;
        }

        this.clear();
        this.adjustDimensions();
        this.drawBoard();
    }

    clear() {
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
    }

    // 根据棋盘大小自动调整尺寸
    adjustDimensions() {
        // 计算可用空间
        const availableWidth = this.canvas.width * 0.95;  // 留出5%边距
        const availableHeight = this.canvas.height * 0.95; // 留出5%边距

        // 计算棋盘网格需要的总宽度和高度
        const gridWidth = (this.size + 0.5) * 1.5; // 水平方向需要的单位数
        const gridHeight = this.size * Math.sqrt(3); // 垂直方向需要的单位数

        // 计算每个单位的大小
        const unitWidth = availableWidth / gridWidth;
        const unitHeight = availableHeight / gridHeight;

        // 选择较小的值作为六边形大小，确保棋盘完全适应画布
        this.hexSize = Math.min(unitWidth, unitHeight / Math.sqrt(3));

        // 设置一个最小和最大限制，防止太小或太大
        this.hexSize = Math.max(22, Math.min(this.hexSize, 45)); // 增大六边形尺寸范围

        // 计算偏移量使棋盘居中
        const boardWidth = this.hexSize * 1.5 * this.size;
        const boardHeight = this.hexSize * Math.sqrt(3) * this.size;

        this.offsetX = (this.canvas.width - boardWidth) / 2 + this.hexSize;
        this.offsetY = this.hexSize;
    }

    drawBoard() {
        // 绘制背景
        this.drawBackground();

        // 绘制棋盘边界
        this.ctx.fillStyle = this.redColor;
        this.drawBoardEdges('red');

        this.ctx.fillStyle = this.blueColor;
        this.drawBoardEdges('blue');

        // 绘制六边形格子
        for (let r = 0; r < this.size; r++) {
            for (let c = 0; c < this.size; c++) {
                this.drawHex(r, c);
                if (this.showCoordinates) {
                    this.drawCoordinate(r, c);
                }
            }
        }
    }

    drawBackground() {
        // 创建背景渐变
        const gradient = this.ctx.createLinearGradient(0, 0, this.canvas.width, this.canvas.height);
        gradient.addColorStop(0, '#f5f7fa');
        gradient.addColorStop(1, '#eef2f7');

        this.ctx.fillStyle = gradient;
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);

        // 添加微妙的网格图案
        this.ctx.strokeStyle = 'rgba(0, 0, 0, 0.03)';
        this.ctx.lineWidth = 0.5;

        const gridSize = 20;
        for (let x = 0; x < this.canvas.width; x += gridSize) {
            this.ctx.beginPath();
            this.ctx.moveTo(x, 0);
            this.ctx.lineTo(x, this.canvas.height);
            this.ctx.stroke();
        }

        for (let y = 0; y < this.canvas.height; y += gridSize) {
            this.ctx.beginPath();
            this.ctx.moveTo(0, y);
            this.ctx.lineTo(this.canvas.width, y);
            this.ctx.stroke();
        }
    }

    drawBoardEdges(color) {
        // 绘制棋盘边框
        const edgeSize = this.hexSize * 0.6;

        if (color === 'red') {
            // 绘制红色的上下边界
            for (let c = 0; c < this.size; c++) {
                const topHex = this.getHexCenter(0, c);
                const bottomHex = this.getHexCenter(this.size - 1, c);

                // 上边界 - 渐变圆形
                // const topGradient = this.ctx.createRadialGradient(
                //     topHex.x, topHex.y - this.hexSize - 10, 0,
                //     topHex.x, topHex.y - this.hexSize - 10, edgeSize
                // );
                // topGradient.addColorStop(0, this.redGradient[0]);
                // topGradient.addColorStop(1, this.redGradient[1]);

                this.ctx.beginPath();
                this.ctx.arc(topHex.x, topHex.y - this.hexSize - 10, edgeSize, 0, Math.PI * 2);
                // this.ctx.fillStyle = topGradient;
                // this.ctx.fillStyle = this.redColor;
                this.ctx.shadowColor = 'rgba(255, 0, 0, 0.3)';
                this.ctx.shadowBlur = 5;
                this.ctx.fill();
                this.ctx.shadowBlur = 0;

                // // 下边界 - 渐变圆形
                // const bottomGradient = this.ctx.createRadialGradient(
                //     bottomHex.x, bottomHex.y + this.hexSize + 10, 0,
                //     bottomHex.x, bottomHex.y + this.hexSize + 10, edgeSize
                // );
                // bottomGradient.addColorStop(0, this.redGradient[0]);
                // bottomGradient.addColorStop(1, this.redGradient[1]);

                this.ctx.beginPath();
                this.ctx.arc(bottomHex.x, bottomHex.y + this.hexSize + 10, edgeSize, 0, Math.PI * 2);
                // this.ctx.fillStyle = bottomGradient;
                // this.ctx.fillStyle = this.redColor;
                this.ctx.shadowColor = 'rgba(255, 0, 0, 0.3)';
                this.ctx.shadowBlur = 5;
                this.ctx.fill();
                this.ctx.shadowBlur = 0;
            }
        } else {
            // 绘制蓝色的左右边界
            for (let r = 0; r < this.size; r++) {
                const leftHex = this.getHexCenter(r, 0);
                const rightHex = this.getHexCenter(r, this.size - 1);

                // 左边界 - 渐变圆形
                // const leftGradient = this.ctx.createRadialGradient(
                //     leftHex.x - this.hexSize - 10, leftHex.y, 0,
                //     leftHex.x - this.hexSize - 10, leftHex.y, edgeSize
                // );
                // leftGradient.addColorStop(0, this.blueGradient[0]);
                // leftGradient.addColorStop(1, this.blueGradient[1]);

                this.ctx.beginPath();
                this.ctx.arc(leftHex.x - this.hexSize - 10, leftHex.y, edgeSize, 0, Math.PI * 2);
                // this.ctx.fillStyle = leftGradient;
                // this.ctx.fillStyle = this.blueColor;
                this.ctx.shadowColor = 'rgba(0, 0, 255, 0.3)';
                this.ctx.shadowBlur = 5;
                this.ctx.fill();
                this.ctx.shadowBlur = 0;

                // 右边界 - 渐变圆形
                // const rightGradient = this.ctx.createRadialGradient(
                //     rightHex.x + this.hexSize + 10, rightHex.y, 0,
                //     rightHex.x + this.hexSize + 10, rightHex.y, edgeSize
                // );
                // rightGradient.addColorStop(0, this.blueGradient[0]);
                // rightGradient.addColorStop(1, this.blueGradient[1]);

                this.ctx.beginPath();
                this.ctx.arc(rightHex.x + this.hexSize + 10, rightHex.y, edgeSize, 0, Math.PI * 2);
                // this.ctx.fillStyle = rightGradient;
                // this.ctx.fillStyle = this.blueColor;
                this.ctx.shadowColor = 'rgba(0, 0, 255, 0.3)';
                this.ctx.shadowBlur = 5;
                this.ctx.fill();
                this.ctx.shadowBlur = 0;
            }
        }
    }

    drawHex(row, col) {
        const { x, y } = this.getHexCenter(row, col);
        const color = this.board[row][col];
        const isLastMove = this.lastMove && this.lastMove.row === row && this.lastMove.col === col;
        const padding = this.hexSize * this.hexPadding;

        // 使用带有内部填充的六边形路径
        const drawHexPath = (size) => {
            this.ctx.beginPath();
            for (let i = 0; i < 6; i++) {
                const angle = (i * 60) * Math.PI / 180;
                const xPos = x + size * Math.cos(angle);
                const yPos = y + size * Math.sin(angle);

                if (i === 0) {
                    this.ctx.moveTo(xPos, yPos);
                } else {
                    this.ctx.lineTo(xPos, yPos);
                }
            }
            this.ctx.closePath();
        };

        // 绘制六边形外框
        drawHexPath(this.hexSize);

        // 根据是否是最后一步决定边框样式
        if (isLastMove && this.highlightLastMove) {
            // 高亮最后一步 - 改进的高亮效果
            this.ctx.save();

            // 先绘制外层发光效果
            this.ctx.shadowColor = this.highlightColor;
            this.ctx.shadowBlur = this.highlightGlow;
            this.ctx.strokeStyle = this.highlightColor;
            this.ctx.lineWidth = 2.0;
            this.ctx.stroke();

            // 移除阴影以绘制内部
            this.ctx.shadowBlur = 0;
            this.ctx.restore();
        } else {
            // 普通六边形边框
            this.ctx.strokeStyle = this.gridLineColor;
            this.ctx.lineWidth = this.gridLineWidth;
            this.ctx.stroke();
        }

        // 填充颜色
        drawHexPath(padding); // 使用较小的六边形作为填充区域

        if (color) {
            // 如果有棋子，使用渐变填充
            if (this.useGradient) {
                // 创建径向渐变
                const gradient = this.ctx.createRadialGradient(
                    x - padding * 0.2, y - padding * 0.2, 0,
                    x, y, padding
                );

                if (color === 'R') {
                    gradient.addColorStop(0, this.redGradient[0]);
                    gradient.addColorStop(1, this.redGradient[1]);
                } else {
                    gradient.addColorStop(0, this.blueGradient[0]);
                    gradient.addColorStop(1, this.blueGradient[1]);
                }

                this.ctx.fillStyle = gradient;
            } else {
                this.ctx.fillStyle = color === 'R' ? this.redColor : this.blueColor;
            }

            // 添加阴影效果
            if (this.useShadow) {
                this.ctx.shadowColor = 'rgba(0, 0, 0, 0.2)';
                this.ctx.shadowBlur = 4;
                this.ctx.shadowOffsetX = 1;
                this.ctx.shadowOffsetY = 1;
            }

            this.ctx.fill();

            // 重置阴影
            this.ctx.shadowColor = 'transparent';
            this.ctx.shadowBlur = 0;
            this.ctx.shadowOffsetX = 0;
            this.ctx.shadowOffsetY = 0;

            // 添加高光效果
            this.ctx.save();
            drawHexPath(padding * 0.65);

            // 设置白色半透明高光
            this.ctx.fillStyle = 'rgba(255, 255, 255, 0.15)';
            this.ctx.fill();
            this.ctx.restore();

        } else {
            // 如果无棋子，使用几乎透明的淡色填充
            this.ctx.fillStyle = 'rgba(255, 255, 255, 0.5)';
            this.ctx.fill();
        }
    }

    drawCoordinate(row, col) {
        const { x, y } = this.getHexCenter(row, col);
        const coordStr = `${String.fromCharCode(97 + col)}${row + 1}`;

        this.ctx.fillStyle = this.coordinateColor;
        this.ctx.font = `${Math.max(9, this.hexSize / 3.5)}px Arial`;
        this.ctx.textAlign = 'center';
        this.ctx.textBaseline = 'middle';
        this.ctx.fillText(coordStr, x, y);
    }

    getHexCenter(row, col) {
        // 计算六边形中心点坐标
        const x = this.offsetX + this.hexSize * 1.5 * col;
        const y = this.offsetY + this.hexSize * Math.sqrt(3) * (row + col / 2);
        return { x, y };
    }

    getHexFromPoint(x, y) {
        // 从点击坐标计算六边形格子位置
        // 反向计算，找到最接近点击位置的六边形中心
        let closestDist = Infinity;
        let closestHex = null;

        for (let r = 0; r < this.size; r++) {
            for (let c = 0; c < this.size; c++) {
                const center = this.getHexCenter(r, c);
                const distance = Math.sqrt(Math.pow(center.x - x, 2) + Math.pow(center.y - y, 2));

                // 如果找到更近的六边形
                if (distance < closestDist) {
                    closestDist = distance;
                    closestHex = { row: r, col: c };
                }
            }
        }

        // 使用动态阈值，根据hexSize计算合理的点击范围
        const clickThreshold = this.hexSize * 1.5; // 点击范围为六边形大小的1.5倍
        if (closestDist <= clickThreshold) {
            return closestHex;
        }

        return null;
    }

    placeStone(row, col, color) {
        if (row >= 0 && row < this.size && col >= 0 && col < this.size && !this.board[row][col]) {
            this.board[row][col] = color;
            // 记录最后一步
            this.lastMove = { row, col };
            this.drawHex(row, col);
            return true;
        }
        return false;
    }

    updateColors(redColor, blueColor) {
        this.redColor = redColor;
        this.blueColor = blueColor;

        // 更新渐变颜色
        this.redGradient = [redColor, this.shadeColor(redColor, -20)];
        this.blueGradient = [blueColor, this.shadeColor(blueColor, -20)];

        this.init();
    }

    // 辅助函数：颜色深浅调整
    shadeColor(color, percent) {
        let R = parseInt(color.substring(1, 3), 16);
        let G = parseInt(color.substring(3, 5), 16);
        let B = parseInt(color.substring(5, 7), 16);

        R = parseInt(R * (100 + percent) / 100);
        G = parseInt(G * (100 + percent) / 100);
        B = parseInt(B * (100 + percent) / 100);

        R = (R < 255) ? R : 255;
        G = (G < 255) ? G : 255;
        B = (B < 255) ? B : 255;

        R = Math.max(0, Math.min(255, R)).toString(16).padStart(2, '0');
        G = Math.max(0, Math.min(255, G)).toString(16).padStart(2, '0');
        B = Math.max(0, Math.min(255, B)).toString(16).padStart(2, '0');

        return `#${R}${G}${B}`;
    }

    resize(newSize) {
        this.size = newSize;
        this.board = Array(newSize).fill().map(() => Array(newSize).fill(null));
        this.lastMove = null;
        this.init();
    }
}