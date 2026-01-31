GAME_CONFIG = {
    "screen": {
        "width": 80,
        "height": 24,
        "fps": 60,
    },
    "bird": {
        "gravity": 1,
        "jump_force": -22,
        "terminal_velocity": 40.0,
        "start_y": 12,
        "start_x": 15,
    },
    "level": {
        "scroll_speed": 30.0,
        "pipe_spacing": 45,
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
        "num_iterations": 2000,
        "initial_samples": 150,
        "mutation_rate": 0.25,
        "mutation_sigma": 0.15,
        "archive_dims": (8, 8),
    },
    "evaluation": {
        "num_runs_per_bot": 2,
        "test_duration": 30,
        "bots": ["aggressive", "reactive", "coin_collector"],
    },
    "quality": {
        "playability_weight": 0.5,
        "balance_weight": 0.25,
        "progression_weight": 0.25,
        "target_survival_rate": 0.6,
        "control_threshold": 0.7,
    },
    "genome_bounds": {
        "pipe_spacing": (35, 52),
        "gap_size": (7.5, 10.5),
        "max_height_change": (4, 10),
        "gap_center_variance": (2, 8),
        "coin_spawn_rate": (0.15, 0.85),
        "powerup_spawn_rate": (0.0, 0.5),
        "debuff_spawn_rate": (0.0, 0.3),
        "coin_offset_min": (3, 12),
        "coin_offset_max": (12, 28),
        "item_spacing": (2, 10),
        "gold_coin_probability": (0.05, 0.35),
    },
}
