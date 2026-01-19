"""Color definitions for ASCII art."""

COLORS = {
    'bird': '\033[93m',        # Yellow
    'pipe': '\033[92m',        # Green
    'coin': '\033[93m',        # Gold
    'powerup': '\033[96m',     # Cyan
    'debuff': '\033[91m',      # Red
    'background': '\033[94m',  # Blue
    'shield': '\033[95m',      # Magenta
    'ui': '\033[97m',          # White
    'reset': '\033[0m'
}

def colorize(text, color_name):
    """Wrap text with color codes."""
    return f"{COLORS.get(color_name, '')}{text}{COLORS['reset']}"
