<!DOCTYPE html>
<html>
<head>
    <title>MiSTer FPGA Web UI</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.5.4/socket.io.js"></script>
    <script>
        var socket = io("http://localhost:5000");

        socket.on("status", function(data) {
            document.getElementById("status").innerText = data.running
                ? `Running: ${data.core} - ${data.game}`
                : "No game running";
        });

        async function loadConsoles() {
            let res = await fetch("/consoles");
            let consoles = await res.json();
            let select = document.getElementById("consoles");
            select.innerHTML = consoles.map(c => `<option value="${c}">${c}</option>`).join("");
            loadGames(consoles[0]);
        }

        async function loadGames(console) {
            let res = await fetch(`/games/${console}`);
            let games = await res.json();
            let gameList = document.getElementById("games");
            gameList.innerHTML = games.map(g => `<li onclick="launchGame('${console}', '${g}')">${g}</li>`).join("");
        }

        function launchGame(core, game) {
            fetch("/launch", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ core, game })
            });
        }

        function terminateGame() {
            fetch("/terminate");
        }
    </script>
</head>
<body onload="loadConsoles()">
    <h1>MiSTer FPGA Web UI</h1>
    <p id="status">No game running</p>
    <select id="consoles" onchange="loadGames(this.value)"></select>
    <ul id="games"></ul>
    <button onclick="terminateGame()">Stop Game</button>
</body>
</html>

