def player_link(player):
    return f"[{player['name']}](tg://user?id={player['id']})"

def get_rank_emoji(index):
    ranks = ["🥇", "🥈", "🥉"]
    return ranks[index % len(ranks)]

def format_alive_list(players_alive):
    lines = []
    for i, p in enumerate(players_alive):
        lines.append(f"{get_rank_emoji(i)} {player_link(p)}: 🙋‍♂️ زنده")
    return "\n".join(lines)

def format_dead_list(players_dead):
    lines = []
    for i, p in enumerate(players_dead):
        role = p.get('role', '❓')
        result = p.get('result', 'باخت')
        lines.append(f"{get_rank_emoji(i)} {p['name']}: 💀 مرده - {role} {result}")
    return "\n".join(lines)

def format_players_status(players_alive, players_dead):
    total = len(players_alive) + len(players_dead)
    alive_count = len(players_alive)
    text = f"بازیکنان زنده: {alive_count} / {total}\n\n"
    text += format_alive_list(players_alive)
    if players_dead:
        text += "\n\nبازیکنان مرده:\n"
        text += format_dead_list(players_dead)
    return text
