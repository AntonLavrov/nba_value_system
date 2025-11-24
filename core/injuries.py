PLAYER_IMPACT = {
    "star": (-6, -5),
    "starter": (-3, -2),
    "role": (-1.5, -0.5)
}


def get_player_impact(role):
    """Возвращает средний импакт по роли"""
    if role not in PLAYER_IMPACT:
        return 0

    low, high = PLAYER_IMPACT[role]
    return (low + high) / 2
