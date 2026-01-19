"""Game configuration settings."""

GAME_CONFIG = {
    "screen": {"width": 80, "height": 24, "fps": 60},  # 2x faster (was 30)
    "bird": {
        "gravity": 1,  # Slower gravity for longer jump duration
        "jump_force": -22,  # Jump lifts bird 1/3 height over ~1 second
        "terminal_velocity": 40.0,  # Moderate max speed
        "start_y": 12,
        "start_x": 15,
    },
    "level": {
        "scroll_speed": 30.0,  # 2x faster (was 12.0)
        "pipe_spacing": 45,  # More space for height transitions
        "gap_size": 8,
        "difficulty": "medium",
    },
    "items": {
        "coin_spawn_rate": 0.3,
        "powerup_spawn_rate": 0.1,
        "debuff_spawn_rate": 0.05,
    },
}

PCG_CONFIG = {
    "map_elites": {
        "num_iterations": 1000,  # Total evolutionary iterations
        "initial_samples": 50,    # Initial random population size
        "mutation_rate": 0.15,    # Probability of mutating each gene
        "mutation_sigma": 0.1,    # Gaussian noise std dev (% of param range)
        "archive_dims": (10, 10), # Behavior space dimensions (difficulty × accessibility)
    },
    "evaluation": {
        "num_runs_per_bot": 3,    # Test runs per bot per level (reduced from 5 for speed)
        "test_duration": 20,       # Seconds per test run (reduced from 30 for speed)
        "bots": ['aggressive', 'reactive', 'coin_collector'],
    },
    "quality": {
        "playability_weight": 0.4,    # Weight for playability score
        "balance_weight": 0.3,         # Weight for bot balance score
        "progression_weight": 0.3,     # Weight for progression smoothness
        "target_survival_rate": 0.5,   # Ideal survival rate (50%)
        "control_threshold": 0.7,      # Minimum control score to accept level
    },
    "genome_bounds": {
        # (min, max) for each parameter
        "pipe_spacing": (35, 50),
        "gap_size": (6, 12),
        "max_height_change": (3, 10),
        "gap_center_variance": (2, 8),
        "coin_spawn_rate": (0.0, 0.6),
        "powerup_spawn_rate": (0.0, 0.3),
        "debuff_spawn_rate": (0.0, 0.2),
        "coin_offset_min": (4, 15),
        "coin_offset_max": (10, 25),
        "item_spacing": (3, 8),
        "gold_coin_probability": (0.05, 0.3),
    },
}
