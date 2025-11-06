document.addEventListener('DOMContentLoaded', () => {
    const pads = document.querySelectorAll('.pad');
    const messageEl = document.getElementById('message');
    const flagRewardEl = document.getElementById('flag-reward');
    const gameBoardEl = document.getElementById('game-board');

    const levels = {
        easy: 3,
        medium: 5,
        hard: 7
    };
    
    let currentLevel = 'easy';
    let sequence = [];
    let playerSequence = [];
    let gameActive = false;
    const flashDelay = 400; // ms to show a pad lit up
    const nextRoundDelay = 1000; // ms after sequence before player can go

    function generateSequence() {
        sequence = [];
        const levelLength = levels[currentLevel];
        for (let i = 0; i < levelLength; i++) {
            sequence.push(Math.floor(Math.random() * 4) + 1);
        }
    }

    function lightUpPad(padId) {
        const pad = document.querySelector(`.pad[data-id="${padId}"]`);
        pad.classList.add('active');
        setTimeout(() => {
            pad.classList.remove('active');
        }, flashDelay);
    }

    async function playSequence() {
        gameActive = false;
        messageEl.textContent = `Level: ${currentLevel}. Watch...`;
        
        // Wait a moment before starting
        await new Promise(res => setTimeout(res, nextRoundDelay));

        for (const padId of sequence) {
            await new Promise(res => setTimeout(res, flashDelay + 100));
            lightUpPad(padId);
        }

        await new Promise(res => setTimeout(res, flashDelay));
        messageEl.textContent = "Your turn...";
        gameActive = true;
        playerSequence = [];
    }

    function handlePadClick(e) {
        if (!gameActive) return;

        const clickedPadId = parseInt(e.target.dataset.id);
        lightUpPad(clickedPadId);
        playerSequence.push(clickedPadId);

        // Check if the click was correct
        const currentIndex = playerSequence.length - 1;
        if (playerSequence[currentIndex] !== sequence[currentIndex]) {
            // Wrong!
            messageEl.textContent = "Wrong! Restarting level...";
            gameActive = false;
            setTimeout(startGame, 2000);
            return;
        }

        // Check if player has finished the sequence
        if (playerSequence.length === sequence.length) {
            gameActive = false;
            setTimeout(handleLevelWin, 500);
        }
    }

    function handleLevelWin() {
        if (currentLevel === 'easy') {
            currentLevel = 'medium';
            messageEl.textContent = "Correct! Moving to Medium.";
            setTimeout(startGame, 2000);
        } else if (currentLevel === 'medium') {
            currentLevel = 'hard';
            messageEl.textContent = "Great! Moving to Hard.";
            setTimeout(startGame, 2000);
        } else if (currentLevel === 'hard') {
            // Won the final level
            messageEl.textContent = "You win!";
            gameBoardEl.classList.add('hidden');
            flagRewardEl.classList.remove('hidden');
        }
    }

    function startGame() {
        generateSequence();
        playSequence();
    }

    pads.forEach(pad => pad.addEventListener('click', handlePadClick));

    // Start the first game
    startGame();
});