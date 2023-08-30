document.addEventListener("DOMContentLoaded", function() {
    var readyButton = document.getElementById("ready-button");
    const readyTimerElement = document.getElementById("ready-timer");
    let clicked = false;
    var timerInterval;
    let totalSeconds = 0;
    
    let readyStatus = false;


    readyButton.addEventListener("click", function() {
        // Start the timer when the ready button is clicked
        if (!timerInterval && clicked == false) {
            console.log("readyStatus",readyStatus);
            if (readyStatus == false){
                readyStatus = true;
            }
            else{
                socket.on('start_game', function() {
                    window.location.href = '/ready';
                });
            }
            socket.emit('player_ready');
            clicked = true;
            timerInterval = setInterval(function() {
                totalSeconds++;
                var minutes = Math.floor(totalSeconds / 60);
                var seconds = totalSeconds - (minutes * 60);
                readyTimerElement.textContent = minutes + ":" + (seconds < 10 ? "0" : "") + seconds;
            }, 1000);
        }
    });
    
    // When the server says to start the game
    socket.on('start_game', function() {
        window.location.href = '/ready';
    });
    

});