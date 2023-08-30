var socket = io.connect('http://localhost:5000');

let waitingTime = 0;
let waitingInterval;


document.getElementById('readyButton').addEventListener('click', function() {
    socket.emit('player_ready', { player_id: 'user_id' });  // Replace 'your_player_id' with actual player ID
});

socket.on('start_game', function() {
    // Start your game logic here
});


document.getElementById('readyButton').addEventListener('click', function() {
    // Emit player_ready event to the server
    socket.emit('player_ready');

    // Start a local timer
    waitingInterval = setInterval(function() {
        waitingTime++;
        document.getElementById('waitingTimeDisplay').innerText = `Waiting for ${waitingTime} seconds`;
    }, 1000);
});

// Listen for start_game event from the server
socket.on('start_game', function() {
    clearInterval(waitingInterval);  // Stop the waiting timer
    // You can now transition to the game or do whatever you need to start the game
});


// Join a room
socket.emit('join_room', {room: 'room1'});

// Send player move to the server
socket.emit('player_move', {move: 'rock', room: 'room1'});

// Listen for game result
socket.on('game_result', function(data) {
    alert(data['winner']);
});
