// board.js
class HexBoard {
    constructor(canvas, size = 11) {
        this.canvas = canvas;
        this.ctx = canvas.getContext('2d');
        this.size = size;
        this.hexSize = 20; // 六边形边长
        this.board = Array(size).fill().map(() => Array(size).fill(null));
        this.redColor = '#FF5252';
        this.blueColor = '#4285F4';

        this.offsetX = 100;
        this.offsetY = 50;
        this.initialWidth = 0;
        this.initialHeight = 0;

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
        const availableWidth = this.canvas.width * 0.9;  // 留出10%边距
        const availableHeight = this.canvas.height * 0.9; // 留出10%边距

        // 计算棋盘网格需要的总宽度和高度
        const gridWidth = (this.size + 0.5) * 1.5; // 水平方向需要的单位数
        const gridHeight = this.size * Math.sqrt(3); // 垂直方向需要的单位数

        // 计算每个单位的大小
        const unitWidth = availableWidth / gridWidth;
        const unitHeight = availableHeight / gridHeight;

        // 选择较小的值作为六边形大小，确保棋盘完全适应画布
        this.hexSize = Math.min(unitWidth, unitHeight / Math.sqrt(3));

        // 设置一个最小和最大限制，防止太小或太大
        this.hexSize = Math.max(12, Math.min(this.hexSize, 35));

        // 计算偏移量使棋盘居中
        const boardWidth = this.hexSize * 1.5 * this.size;
        const boardHeight = this.hexSize * Math.sqrt(3) * this.size;

        this.offsetX = (this.canvas.width - boardWidth) / 2 + this.hexSize;
        this.offsetY = (this.canvas.height - boardHeight) / 2 + this.hexSize;
    }

    drawBoard() {
        // 绘制棋盘边界
        this.ctx.fillStyle = this.redColor;
        this.drawBoardEdges('red');

        this.ctx.fillStyle = this.blueColor;
        this.drawBoardEdges('blue');

        // 绘制六边形格子
        for (let r = 0; r < this.size; r++) {
            for (let c = 0; c < this.size; c++) {
                this.drawHex(r, c);
                this.drawCoordinate(r, c);
            }
        }
    }

    drawBoardEdges(color) {
        // 绘制棋盘边框
        if (color === 'red') {
            // 绘制红色的上下边界
            for (let c = 0; c < this.size; c++) {
                const topHex = this.getHexCenter(0, c);
                const bottomHex = this.getHexCenter(this.size - 1, c);

                this.ctx.fillStyle = this.redColor;
                this.ctx.fillRect(topHex.x - 10, topHex.y - 40, 20, 10);
                this.ctx.fillRect(bottomHex.x - 10, bottomHex.y + 30, 20, 10);
            }
        } else {
            // 绘制蓝色的左右边界
            for (let r = 0; r < this.size; r++) {
                const leftHex = this.getHexCenter(r, 0);
                const rightHex = this.getHexCenter(r, this.size - 1);

                this.ctx.fillStyle = this.blueColor;
                this.ctx.fillRect(leftHex.x - 40, leftHex.y - 10, 10, 20);
                this.ctx.fillRect(rightHex.x + 30, rightHex.y - 10, 10, 20);
            }
        }
    }

    drawHex(row, col) {
        const { x, y } = this.getHexCenter(row, col);
        const color = this.board[row][col];

        this.ctx.beginPath();
        for (let i = 0; i < 6; i++) {
            const angle = (i * 60) * Math.PI / 180;
            const xPos = x + this.hexSize * Math.cos(angle);
            const yPos = y + this.hexSize * Math.sin(angle);

            if (i === 0) {
                this.ctx.moveTo(xPos, yPos);
            } else {
                this.ctx.lineTo(xPos, yPos);
            }
        }
        this.ctx.closePath();

        // 填充颜色
        if (color) {
            this.ctx.fillStyle = color === 'R' ? this.redColor : this.blueColor;
            this.ctx.fill();
        } else {
            this.ctx.fillStyle = '#FFFFFF';
            this.ctx.fill();
        }

        this.ctx.strokeStyle = '#000000';
        this.ctx.stroke();
    }

    drawCoordinate(row, col) {
        const { x, y } = this.getHexCenter(row, col);
        const coordStr = `${String.fromCharCode(97 + col)}${row + 1}`;

        this.ctx.fillStyle = '#000000';
        this.ctx.font = `${Math.max(10, this.hexSize / 2)}px Arial`;
        this.ctx.textAlign = 'center';
        this.ctx.fillText(coordStr, x, y + 3);
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
        if (row >= 0 && row < this.size && col >= 0 && col < this.size) {
            this.board[row][col] = color;
            this.drawHex(row, col);
            return true;
        }
        return false;
    }

    updateColors(redColor, blueColor) {
        this.redColor = redColor;
        this.blueColor = blueColor;
        this.init();
    }

    resize(newSize) {
        this.size = newSize;
        this.board = Array(newSize).fill().map(() => Array(newSize).fill(null));
        this.init();
    }
}