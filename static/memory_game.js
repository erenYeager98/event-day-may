document.addEventListener('DOMContentLoaded', () => {
    const pads = document.querySelectorAll('.pad');
    const messageEl = document.getElementById('message');
    const flagRewardEl = document.getElementById('flag-reward');
    const gameBoardEl = document.getElementById('game-board');

    // --- Difficulty Tweaks ---
    // Longer sequences
    const levels = {
        easy: 4,
        medium: 8,
        hard: 14 // Original was 3, 5, 7
    };
    
    // Faster speeds (in milliseconds)
    const speeds = {
        easy: {
            flashDelay: 400,  // How long the pad stays lit
            nextPadDelay: 150, // Pause between pads
            nextRoundDelay: 1000 // Pause before player's turn
        },
        medium: {
            flashDelay: 300,
            nextPadDelay: 100,
            nextRoundDelay: 800
        },
        hard: {
            flashDelay: 200,
            nextPadDelay: 75,
            nextRoundDelay: 600
        }
    };
    // -------------------------
    
    let currentLevel = 'easy';
    let sequence = [];
    let playerSequence = [];
    let gameActive = false;

    /**
     * Generates a new random sequence based on the current level's length.
     */
    function generateSequence() {
        sequence = [];
        const levelLength = levels[currentLevel];
        for (let i = 0; i < levelLength; i++) {
            sequence.push(Math.floor(Math.random() * 4) + 1);
        }
    }

    /**
     * Lights up a specific pad for a dynamic duration.
     * @param {number} padId - The ID of the pad to light (1-4).
     */
    function lightUpPad(padId) {
        const pad = document.querySelector(`.pad[data-id="${padId}"]`);
        const { flashDelay } = speeds[currentLevel]; // Get dynamic speed
        
        pad.classList.add('active');
        setTimeout(() => {
            pad.classList.remove('active');
        }, flashDelay);
    }

    /**
     * Plays the generated sequence for the player, using dynamic speeds.
     */
    async function playSequence() {
        gameActive = false;
        messageEl.textContent = `Level: ${currentLevel}. Watch...`;
        
        const { nextPadDelay, flashDelay, nextRoundDelay } = speeds[currentLevel];

        // Wait a moment before starting
        await new Promise(res => setTimeout(res, nextRoundDelay));

        for (const padId of sequence) {
            // Wait for the pause *between* pads
            await new Promise(res => setTimeout(res, nextPadDelay));
            lightUpPad(padId);
            // Wait for the pad to finish flashing before starting the next pause
            await new Promise(res => setTimeout(res, flashDelay));
        }

        // Wait a final moment before player's turn
        await new Promise(res => setTimeout(res, 300)); 
        messageEl.textContent = "Your turn...";
        gameActive = true;
        playerSequence = [];
    }

    /**
     * Handles the player clicking on a pad.
     * @param {Event} e - The click event.
     */
    function handlePadClick(e) {
        if (!gameActive) return;

        const clickedPadId = parseInt(e.target.dataset.id);
        lightUpPad(clickedPadId); // Light up player's click
        playerSequence.push(clickedPadId);

        // Check if the click was correct
        const currentIndex = playerSequence.length - 1;
        if (playerSequence[currentIndex] !== sequence[currentIndex]) {
            // Wrong!
            messageEl.textContent = "Wrong! Restarting level...";
            gameActive = false;
            setTimeout(startGame, 2000); // Restart this level
            return;
        }

        // Check if player has finished the sequence
        if (playerSequence.length === sequence.length) {
            gameActive = false;
            setTimeout(handleLevelWin, 500); // Move to next level
        }
    }

    /**
     * Handles the logic for winning a level and progressing.
     */
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

    /**
     * Resets sequences and starts the game for the current level.
     */
    function startGame() {
        generateSequence();
        playSequence();
    }

    // Attach click listeners to all pads
    pads.forEach(pad => pad.addEventListener('click', handlePadClick));

    // Start the first game on page load
    startGame();
});