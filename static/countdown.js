document.addEventListener("DOMContentLoaded", function () {
    const timerElement = document.getElementById("timer");
    const pointsElement = document.getElementById("points");
    let seconds = 5;
    let points = 0;

    function updateTimer() {
        timerElement.textContent = seconds;
        seconds--;

        if (seconds < 0) {
            clearInterval(interval);
            timerElement.textContent = "Time's up!";
        }
    }

    function updatePoints() {
        pointsElement.textContent = points;
    }

    updateTimer(); // Update immediately
    updatePoints(); // Update points counter immediately

    const interval = setInterval(updateTimer, 1000); // Update every second


    const terminateButton = document.getElementById("terminate-button");

    terminateButton.addEventListener("click", () => {
        window.location.href = "/";
    });

    const paperButton = document.querySelector(".paper-button");
    paperButton.addEventListener("click", () =>{
        clearInterval(interval);
        timerElement.textContent = "You picked Paper!";
        // points++;
        // updatePoints();
    });

    const scissorsButton = document.querySelector(".scissors-button");
    scissorsButton.addEventListener("click", () => {
        clearInterval(interval);
        timerElement.textContent = "You picked Scissors!";
    });

    const rockButton = document.querySelector(".rock-button");
    rockButton.addEventListener("click", () => {
        clearInterval(interval);
        timerElement.textContent = "You picked Rock!";
    });

    // document.querySelector('rock-button').addEventListener('click', function() {
    //     socket.emit('player_move', { move: 'rock' });
    //     timerElement.textContent = "You picked rock";
    // });
    
    // document.querySelector('paper-button').addEventListener('click', function() {
    //     socket.emit('player_move', { move: 'paper' });
    //     timerElement.textContent = "You picked paper";
    // });
    
    // document.querySelector('scissors-button').addEventListener('click', function() {
    //     socket.emit('player_move', { move: 'scissors' });
    //     timerElement.textContent = "You picked scissors";
    // }); 

    // socket.on('opponent_move', function(data) {
    //     timerElement.textContent = "Opponent picked " + data.move;
    // });
    
    

    const restartButton = document.getElementById("restart-button");
    restartButton.addEventListener("click", () => {
        window.location.href = "/ready";
        points = 0;
        updatePoints();
    });

});
