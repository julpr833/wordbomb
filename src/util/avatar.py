def get_avatar(username: str) -> str:
    return f"https://api.dicebear.com/9.x/pixel-art/svg?seed={username}"