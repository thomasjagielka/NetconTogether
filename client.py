import asyncio
import time
import json
import pymem
import requests
import struct
import websockets

class Offsets:
    pass

class Position:
    def __init__(self, x = 0, y = 0, z = 0):
        self.x = x
        self.y = y
        self.z = z
    #     self.to_list = self.to_list()

    # def to_list(self):
    #     return [self.x, self.y, self.z]

    def tuple_to_position(tuple):
        if len(tuple) == 2:
            return Position(tuple[0], tuple[1])
        if len(tuple) == 3:
            return Position(tuple[0], tuple[1], tuple[2])

class Client:
    def __init__(self, pm):
        self.pm = pm
        self.address = pymem.process.module_from_name(pm.process_handle, "client.dll").lpBaseOfDll
        self.game_rules = self.pm.read_int(self.address + Offsets.dwGameRulesProxy)

    def get_local_player(self):
        return self.pm.read_int(self.address + Offsets.dwLocalPlayer)

    def is_freeze_period(self):
        return self.pm.read_bool(self.game_rules + Offsets.m_bFreezePeriod)

class Engine:
    def __init__(self, pm):
        self.pm = pm
        self.address = pymem.process.module_from_name(pm.process_handle, "engine.dll").lpBaseOfDll

    def get_local_view_angles(self):
        client_state = self.pm.read_uint(self.address + Offsets.dwClientState)
        return Position.tuple_to_position(struct.unpack("f"*2, self.pm.read_bytes(client_state + Offsets.dwClientState_ViewAngles, 2*4)))

class Player:
    not_dormant_time = None
    elapsed_time_diff_since_not_dormant = None
    is_dormant = None
    health = None
    team_num = None
    last_place_name = None
    money = None
    position = None
    view_angles = None

    def __init__(self, pm, address, index = None):
        self.pm = pm
        self.address = address
        self.index = index

    def __lt__(self, other):
        return int(self.not_dormant_time) < int(other.not_dormant_time)

    def get_dormant(self):
        self.is_dormant = self.pm.read_bool(self.address + Offsets.m_bDormant)
        return self.is_dormant

    def get_health(self):
        self.health = self.pm.read_int(self.address + Offsets.m_iHealth)
        return self.health

    def get_team_num(self):
        self.team_num = self.pm.read_int(self.address + Offsets.m_iTeamNum)
        return self.team_num

    def get_last_place_name(self):
        self.last_place_name = self.pm.read_string(self.address + Offsets.m_szLastPlaceName)
        return self.last_place_name

    def get_money(self):
        self.money = self.pm.read_int(self.address + 0x117B8)
        return self.money

    def get_elapsed_time_diff_since_not_dormant(self):
        self.elapsed_time_diff_since_not_dormant = int(time.time() - self.not_dormant_time)
        return self.elapsed_time_diff_since_not_dormant if self.elapsed_time_diff_since_not_dormant > 0 else None

    def get_position(self):
        self.position = Position.tuple_to_position(struct.unpack("f"*3, self.pm.read_bytes(self.address + Offsets.m_vecOrigin, 3*4)))
        return self.position

    def get_view_angles(self):
        self.view_angles = Position.tuple_to_position(struct.unpack("f"*2, self.pm.read_bytes(self.address + Offsets.m_angEyeAnglesX, 2*4)))
        return self.view_angles

def fetch_offsets():
    hazedumper = requests.get("https://raw.githubusercontent.com/frk1/hazedumper/master/csgo.min.json").json()
    # hazedumper = json.load(open("csgo.json"))
    [setattr(Offsets, k, v) for k, v in hazedumper["signatures"].items()]
    [setattr(Offsets, k, v) for k, v in hazedumper["netvars"].items()]

def get_players(pm, client):
    player_list = pm.read_bytes(client + Offsets.dwEntityList, 1024)
    players = []

    # Adresses in entity list are 0x10 apart, so step by 16 (0x10).
    for i in range(0, len(player_list), 16):
        player_address = int.from_bytes(player_list[i:i+4], byteorder="little")
        players.append(Player(pm, player_address, int(i / 16)))

    return players


async def main(uri):
    async with websockets.connect(uri) as websocket:
        print(f"{uri}: Connected.")

        fetch_offsets()
        pm = pymem.Pymem("csgo.exe")
        client = Client(pm)
        engine = Engine(pm)
        # engine = Engine(pm)

        player_buffer = []

        while True:
            local_player = Player(pm, client.get_local_player())

            for player in get_players(pm, client.address):
                if not player.address:
                    for buffored_player in player_buffer:
                        if player.index == buffored_player.index:
                            player_buffer.remove(buffored_player)

                    continue

                # if player.address == local_player.address:
                #     continue

                if client.is_freeze_period():
                    for buffored_player in player_buffer:
                        if player.address == buffored_player.address:
                            player_buffer.remove(buffored_player)

                    continue
                            
                if player.get_dormant():
                    continue

                # player_team_num = player.get_team_num() 
                # if player_team_num == local_player.get_team_num() or player_team_num == 0:
                #     continue

                if player.get_health() <= 0:
                    for buffored_player in player_buffer:
                        if player.address == buffored_player.address:
                            player_buffer.remove(buffored_player)

                    continue

                player.not_dormant_time = time.time()

                found_player = False
                for i in range(0, len(player_buffer)):
                    if player.address == player_buffer[i].address:
                        player_buffer[i] = player
                        found_player = True
                
                # Needed for web radar.
                player.get_team_num()
                player.get_position()
                
                # Local player view angles are inaccurate with m_angEyeAngles method.
                if player.address == local_player.address:
                    player.view_angles = engine.get_local_view_angles()
                else:
                    player.get_view_angles()

                if not found_player:
                    player_buffer.append(player)

            # Prepare data for websocket.
            player_info = []
            if player_buffer:
                for player in player_buffer:
                    player_dict = player.__dict__.copy()

                    player.get_elapsed_time_diff_since_not_dormant()

                    # Get rid of unneeded data to save bandwidth.
                    del player_dict["pm"]
                    del player_dict["address"]
                    del player_dict["index"]
                    del player_dict["not_dormant_time"]

                    player_info.append(json.dumps(player_dict, skipkeys=True, default=lambda o: o.__dict__))


            await websocket.send(json.dumps(player_info))
            await websocket.recv()
            await asyncio.sleep(0.02)

if __name__ == '__main__':
    asyncio.run(main("ws://localhost:80"))