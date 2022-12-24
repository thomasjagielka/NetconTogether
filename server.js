const SocketServer = require('ws').Server;
const express = require('express');

const app = express();
const port = process.env.PORT || 80;

// Web server.
app.use(express.static("public", {
    // maxAge: '5000' // Milliseconds per file.
}))

const server = app.listen(port, function () {
    console.log(`127.0.0.1:${port}: Server started!`)
})

// Websocket.
const wss = new SocketServer({ server });

wss.broadcast = function broadcast(msg) {
    wss.clients.forEach(function each(client) {
        client.send(msg);
     });
 };

wss.on('connection', (ws, req) => {
    console.log(`${req.socket.remoteAddress}:${req.socket.remotePort}: Connected.`);

    ws.on('message', message => {
        if (message)
            wss.broadcast(message, ()=>{});
        // console.log(`${req.socket.remoteAddress}:${req.socket.remotePort}: ${message}`);
    });
});