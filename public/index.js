class Position {
    constructor(x = 0, y = 0, z = 0) {
        this.x = x;
        this.y = y;
        this.z = z;
    }
}

function setRendererPosition(context, position) {
    context.width = position.x;
    context.height = position.y;
}

function draw(renderer, ctx, overviewPos, miragePos, MIRAGE_SCALE, playerData) {
    if (renderer.getContext) {
        playerData = JSON.parse(playerData)

        if (!playerData)
            return

        // Clear frame for redrawing.
        ctx.clearRect(0, 0, renderer.width, renderer.height);

        for (let player of playerData) {
            player = JSON.parse(player);
            let playerPosition = new Position(player["position"]["x"], player["position"]["y"]);
            // Scale player position to renderer size.
            playerPosition = new Position(
                (playerPosition.x - miragePos.x) / MIRAGE_SCALE * (overviewPos.x / 1024), 
                Math.abs(playerPosition.y - miragePos.y) / MIRAGE_SCALE * (overviewPos.y / 1024));

            // Aim angle visualization.
            // TODO: Cleanup.

            const radius = MIRAGE_SCALE * (overviewPos.x / 1024) * 3;

            ctx.beginPath();
            ctx.fillStyle = "rgba(255, 255, 255, 0.25)";

            var PI = Math.PI;
            var cx = playerPosition.x;
            var cy = playerPosition.y;
            var radius2 = 0;
            var triLength1 = radius * 2.5;
            var triLength2 = radius * 3.4;
            var rAngle =- player["view_angles"]["y"] * Math.PI / 180;

            var x0 = cx + radius2 * Math.cos(rAngle);
            var y0 = cy + radius2 * Math.sin(rAngle);
            var tricx = cx + (radius2 + triLength1) * Math.cos(rAngle);
            var tricy = cy + (radius2 + triLength1) * Math.sin(rAngle);
            var x1 = tricx+triLength2 * Math.cos(rAngle-PI/2);
            var y1 = tricy+triLength2 * Math.sin(rAngle-PI/2);
            var x2 = tricx+triLength2 * Math.cos(rAngle+PI/2);
            var y2 = tricy+triLength2 * Math.sin(rAngle+PI/2);

            ctx.moveTo(x0,y0);
            ctx.lineTo(x1,y1);
            ctx.lineTo(x2,y2);
            ctx.closePath();
            // ctx.stroke();
            ctx.fill();
    
            if (player["team_num"] == 2)
                ctx.fillStyle = "rgb(255, 128, 0)";
            else
                ctx.fillStyle = "rgb(8, 128, 255)";

            let strokeStyle;
            if (player["elapsed_time_diff_since_not_dormant"]) {
                strokeStyle = `rgba(150, 150, 150`;
            } else {
                strokeStyle = `rgba(0, 255, 0`;
            }

            const endAngle = 1.5 * Math.PI + (2 * Math.PI * (player["health"])) / 100;

            ctx.lineWidth = 5;

            // Health bar - foreground bar.
            ctx.beginPath();
            ctx.strokeStyle = `${strokeStyle})`;
            ctx.arc(playerPosition.x, playerPosition.y, radius, 1.5 * Math.PI, endAngle);
            ctx.stroke();

            // Health bar - background bar.
            ctx.beginPath();
            ctx.strokeStyle = `${strokeStyle}, 0.25)`;
            ctx.arc(playerPosition.x, playerPosition.y, radius, 1.5 * Math.PI, endAngle, true);
            ctx.stroke();

            // Inner circle.
            ctx.beginPath();
            ctx.arc(playerPosition.x, playerPosition.y, radius / 1.2, 0, 2 * Math.PI);
            ctx.fill();

            // // Rotated rectangle
            // ctx.translate(playerPosition.x, playerPosition.y);
            // ctx.rotate(-(player["view_angles"]["y"] * Math.PI / 180));
            // ctx.fillStyle = "red";
            // ctx.fillRect(15, -10, 80, 20);

            // Reset transformation matrix to the identity matrix
            // ctx.resetTransform()
        }
    }
} 

function main() {
    const overview = document.getElementById("overview");
    const overviewPos = new Position(overview.width, overview.height);

    const renderer = document.getElementById("renderer");
    setRendererPosition(renderer, overviewPos);
    const ctx = renderer.getContext('2d');
    
    const miragePos = new Position(-3230, 1713);
    const MIRAGE_SCALE = 5;
    
    const socket = new WebSocket(`ws://${location.host}`);
    
    socket.addEventListener('message', function (event) {
        reader = new FileReader();
        reader.onload = () =>
            draw(renderer, ctx, overviewPos, miragePos, MIRAGE_SCALE, reader.result);
        reader.readAsText(event.data);
    });
}

main();