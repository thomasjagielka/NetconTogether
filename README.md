<br><h1 align="center">NetconTogether</h1>
<p align="center">
Training software written in Python & JavaScript designed to help professional CS:GO players with their positioning and prediction skills.
</p>

<p align="center">
  <a href="https://www.python.org/"><img src="https://img.shields.io/badge/%20-Python-%233776AB?logo=python&logoColor=white" alt="Node.js"></a>
  <a href="https://www.javascript.com/"><img src="https://img.shields.io/badge/%20-JavaScript-yellow?logo=javascript&logoColor=white" alt="JavaScript"></a>
  <a href="https://expressjs.com/"><img src="https://img.shields.io/badge/%20-Express.js-gray?logo=express&logoColor=whitesmoke" alt="JavaScript"></a>
</p>

<p align="center">
  <img src="https://user-images.githubusercontent.com/54605544/208326427-3da36ff2-8e58-4a4e-9ff8-6776e93eb7a9.png" alt="Netcon Together">
</p><br><br>

## Features
* It allows you to know about the position of players without actually being aware of them, and also to know about:
* Player's team (orange circle ‐ terrorists; blue circle ‐ counter-terrorists);
* Player's viewangle (white field of view);
* Player's last known position (gray circle).
* Multiple Python clients running at the same time are supported (this allows you to extend the reach of collecting player data).

## Installation
1. Clone the repository.
 ```sh
 git clone https://github.com/tomaszjagielka/NetconTogether.git
 ```
2. Install NPM packages.
 ```sh
 npm install
 ```
3. Install Python packages.
 ```sh
 pip install -r requirements.txt
 ```
## Usage
1. Launch CS:GO.
2. Run the server using `node server.js`
3. Run the client using `py client.py`
4. Visit `localhost` or `127.0.0.1` in your web browser.
5. Additionally, if you want others to use your web radar, your IP address must be forwarded or you and others must use a LAN emulator such as [Hamachi](https://www.vpn.net/) or [ZeroTier](https://www.zerotier.com/). In this case, all they have to do is enter your IP address in their web browser.

## How it works?
1. Running the Node.js server allows it to listen for incoming messages from the Python client using WebSocket. It also hosts a website for web clients using Express.js, that allows them to view web radar.
2. Running the Python client allows it to collect player data from the game and pass it to the Node.js server. The data is then sent to the web clients.
3. The client-side JavaScript code of the web client uses the data to draw positions and other player information directly on the web page using Canvas API.
