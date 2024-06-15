from errors import GameError
import random


class Game:
    def __init__(self, user_limit):
        self.user_limit = user_limit
        self.players = []
        self.turn_player_id = 0
        self.game_live = False

    def start(self, players_sockets):
        # Initialize game
        if len(players_sockets) < 2:
            raise GameError("Game must have at least 2 players")
        if len(players_sockets) > self.user_limit:
            raise GameError(f"Game can have at most {self.user_limit} players")

        self.players = [{
            "id": index,
            "socket": player,
            "score": 0,
            "board": [i for i in range(1, 9)],
            "last_roll": None,
            "name": "Player 1",
        } for index, player in enumerate(players_sockets)]
        self.turn_player_id = random.randint(0, len(self.players) - 1)
        self.game_live = True

    def get_players_ids(self):
        return [player["id"] for player in self.players]

    def get_player_id(self, socket):
        for player in self.players:
            if player["socket"] == socket:
                return player["id"]
        return None

    def get_current_player(self):
        return self.get_player(self.turn_player_id)

    def remove_player(self, player_socket):
        player = self.get_player_by_socket(player_socket)
        if player is None:
            raise GameError("Player not found")
        self.players.remove(player)

    def end(self):
        # check who won

        self.game_live = False

    def terminate(self):
        players = self.players
        self.game_live = False
        self.players = []
        return players

    def __one_dice_roll(self, list):
        for item in [7, 8, 9]:
            if item in list:
                return False
        return True

    def roll_dice(self):
        player = self.get_current_player()
        if player is None:
            raise GameError("No current player found")
        if player["last_roll"] is not None:
            raise GameError("You must make a move first")
        if self.__one_dice_roll(player["board"]):
            print("Rolling 6 sided dice")
            roll = random.randint(1, 6)
        else:
            roll = random.randint(1, 12)
        player["last_roll"] = roll
        return roll

    def make_move(self, move):
        player = self.get_current_player()
        if player is None:
            raise GameError("No current player found")
        if player["last_roll"] is None:
            raise GameError("You must roll the dice first")
        if player["last_roll"] != sum(move):
            raise GameError("Sum of the move is not equal to your last roll")
        if len(move) > 2:
            raise GameError("You can close max two numbers at a time")
        if len(move) == 2:
            if move[0] == move[1]:
                raise GameError("You can't close the same number twice")
        for number in move:
            if number not in player["board"]:
                raise GameError(f"Number {number} was already used")
        for number in move:
            player["board"].remove(number)
        player["last_roll"] = None
        if len(player["board"]) == 0:
            return True
        return False

    def check_if_move_possible(self, roll):
        player = self.get_current_player()
        if roll in player["board"]:
            return True

        # check if the sum of the numbers in the move is equal to the last roll
        seen = set()
        for num in player["board"]:
            if roll - num in seen:
                return True
            seen.add(num)
        return False

    def get_score(self):
        return {player["id"]: player["score"] for player in self.players}

    def next_player_turn(self):
        player = self.get_current_player()

        turn_temp = (self.turn_player_id + 1) % len(self.players)
        for i in range(len(self.players)):
            if self.get_player(turn_temp)["score"] >= 45:
                turn_temp = (turn_temp + 1) % len(self.players)
            else:
                break
            #TODO: end condition

        self.turn_player_id = turn_temp

        player["score"] += sum(player["board"])
        player["board"] = [i for i in range(1, 9)]
        if player["score"] >= 45:
            return True
        return False

    def check_win_condition(self):
        player = self.get_current_player()
        return len(player["board"]) == 0

    def get_player(self, player_id):
        for player in self.players:
            if player['id'] == player_id:
                return player
        return None

    def get_player_count(self):
        return len(self.players)

    def get_player_by_socket(self, player_socket):
        for player in self.players:
            if player['socket'] == player_socket:
                return player
        return None
