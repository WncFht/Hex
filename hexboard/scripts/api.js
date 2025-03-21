// api.js
class HexAPI {
    constructor(baseUrl = '') {
        this.baseUrl = baseUrl || 'http://localhost:5000';
    }

    async initGame(isFirstPlayer) {
        try {
            const response = await fetch(`${this.baseUrl}/api/init`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ first: isFirstPlayer })
            });
            const data = await response.json();
            return data;
        } catch (error) {
            console.error('Error initializing game:', error);
            return null;
        }
    }

    async makeMove(moveStr) {
        try {
            const response = await fetch(`${this.baseUrl}/api/move`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ move: moveStr })
            });
            const data = await response.json();
            return data;
        } catch (error) {
            console.error('Error making move:', error);
            return null;
        }
    }

    async getAIMove() {
        try {
            const response = await fetch(`${this.baseUrl}/api/ai_move`);
            const data = await response.json();
            return data;
        } catch (error) {
            console.error('Error getting AI move:', error);
            return null;
        }
    }

    async swap() {
        try {
            const response = await fetch(`${this.baseUrl}/api/swap`, {
                method: 'POST'
            });
            const data = await response.json();
            return data;
        } catch (error) {
            console.error('Error swapping:', error);
            return null;
        }
    }
}