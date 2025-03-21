// api.js
class HexAPI {
    constructor(baseUrl = '') {
        this.baseUrl = baseUrl || 'http://localhost:5000';
    }

    async initGame(isFirstPlayer, difficulty = 'medium') {
        try {
            const response = await fetch(`${this.baseUrl}/api/init`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    first: isFirstPlayer,
                    difficulty: difficulty
                })
            });
            const data = await response.json();
            return data;
        } catch (error) {
            console.error('Error initializing game:', error);
            return null;
        }
    }

    async makeMove(moveStr, difficulty = 'medium') {
        try {
            const response = await fetch(`${this.baseUrl}/api/move`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    move: moveStr,
                    difficulty: difficulty
                })
            });
            const data = await response.json();
            return data;
        } catch (error) {
            console.error('Error making move:', error);
            return null;
        }
    }

    async getAIMove(difficulty = 'medium') {
        try {
            const response = await fetch(`${this.baseUrl}/api/ai_move?difficulty=${difficulty}`);
            const data = await response.json();
            return data;
        } catch (error) {
            console.error('Error getting AI move:', error);
            return null;
        }
    }

    async swap(difficulty = 'medium') {
        try {
            const response = await fetch(`${this.baseUrl}/api/swap`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ difficulty: difficulty })
            });
            const data = await response.json();
            return data;
        } catch (error) {
            console.error('Error swapping:', error);
            return null;
        }
    }
}