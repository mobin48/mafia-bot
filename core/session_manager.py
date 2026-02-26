from sessions.game_session import GameSession

class SessionManager:
    def __init__(self):
        self.sessions = {}

    def get_session(self, chat_id):
        if chat_id not in self.sessions:
            self.sessions[chat_id] = GameSession(chat_id)
        return self.sessions[chat_id]

    def remove_session(self, chat_id):
        if chat_id in self.sessions:
            del self.sessions[chat_id]
