from states.game_state import GameState

class GameSession:
    def __init__(self, chat_id):
        self.chat_id = chat_id
        self.players = {}
        self.state = GameState.WAITING
        self.roles_assigned = False

    def add_player(self, user_id, username):
        if self.state != GameState.WAITING:
            return False
        
        if user_id not in self.players:
            self.players[user_id] = {
                "username": username,
                "role": None,
                "alive": True
            }
            return True
        return False

    def start_game(self):
        if len(self.players) < 4:
            return False
        
        self.state = GameState.STARTING
        return True

    def set_state(self, new_state):
        self.state = new_state
