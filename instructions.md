# FlappyBird with MAP-Elites PCG

Flappy Bird clone with AI bots and procedural content generation using MAP-Elites algorithm.

## Features

- **Playable Game**: Classic Flappy Bird gameplay with ASCII rendering
- **AI Bots**: 3 different bot strategies (Aggressive, Reactive, A* pathfinding)
- **PCG with MAP-Elites**: Procedurally generate diverse, concrete levels
- **Concrete Levels**: Levels are stored as specific pipe/item positions (900 units, ~30s)
- **Victory Screen**: Complete levels to see victory celebration!
- **Quality Metrics**: Playability, balance, progression analysis

---

## Installation

```bash
# Clone repository
git clone <repository-url>
cd FlappyBird

# Install dependencies
pip install -r requirements.txt
```

---

## How to Play

### Play Manually

```bash
cd src
python3 main.py
```

**Controls:**
- **SPACE**: Jump
- **P**: Pause
- **R**: Restart
- **ESC**: Return to menu

---

## AI Bots

Three bot strategies are available:

### 1. Aggressive Bot
- Simple reactive behavior
- Jumps when near pipes
- Fast decision making

### 2. Reactive Bot
- Analyzes pipe gaps
- Medium difficulty
- No prediction

### 3. Coin Collector Bot (A*)
- Uses A* pathfinding
- Plans trajectory ahead
- Best performance
- Collects coins optimally

### Run Bots

```bash
cd src

# Graphical mode
python3 main.py --bot aggressive
python3 main.py --bot reactive
python3 main.py --bot coin_collector

# Headless testing
python3 main.py --bot coin_collector --headless --test-duration 30
```

---

## Procedural Content Generation (MAP-Elites)

### Generate Levels

```bash
# Quick test (100 iterations, ~30 seconds)
python3 src/pcg/run_map_elites.py --iterations 100

# Standard run (1000 iterations, ~5 minutes)
python3 src/pcg/run_map_elites.py --iterations 1000 --plot

# Full evolution (5000 iterations, ~25 minutes)
python3 src/pcg/run_map_elites.py --iterations 5000 --plot
```

**Output:**
- Archive: `data/map_elites_archive.json`
- Top levels: `data/pcg_levels/level_top1_q*.json`
- Console: Coverage, quality range, top 5 levels

### Concrete Level Format

Levels are now stored as **concrete sequences** (not procedural parameters):

```json
{
  "quality": 0.784,
  "cell": [5, 4],
  "genome": {
    "length": 900.0,
    "pipes": [
      {"x": 45.2, "gap_center": 12.5, "gap_size": 7.8},
      {"x": 87.3, "gap_center": 15.2, "gap_size": 8.1},
      ...
    ],
    "items": [
      {"x": 52.0, "y": 10.0, "type": "coin", "is_gold": false},
      ...
    ]
  }
}
```

**Advantages:**
- ✅ **100% deterministic** - same level every time
- ✅ **Reproducible tests** - reliable bot benchmarks
- ✅ **Archivable** - save and replay best levels
- ✅ **30 seconds long** - ~900 units, 20-30 pipes

---

## Test Specific Levels

```bash
# Play best level with coin collector bot
./play_level.py data/pcg_levels/level_top1_q0.827.json

# Try different bots
./play_level.py data/pcg_levels/level_top1_q0.827.json --bot aggressive
./play_level.py data/pcg_levels/level_top1_q0.827.json --bot reactive

# Headless testing
./play_level.py data/pcg_levels/level_top1_q0.827.json --headless

# Show top 3 levels visually
./show_top_levels.py
```

---

## MAP-Elites Configuration

Edit `src/utils/config.py` to adjust PCG parameters:

```python
PCG_CONFIG = {
    "map_elites": {
        "num_iterations": 500,      # Evolution iterations
        "initial_samples": 100,     # Random starting levels
        "mutation_rate": 0.25,      # Probability of mutation
        "mutation_sigma": 0.15,     # Mutation magnitude
        "archive_dims": (8, 8),     # 2D grid size
    },
    "evaluation": {
        "num_runs_per_bot": 2,      # Runs per bot per level
        "test_duration": 30,         # Seconds per test
        "bots": ["aggressive", "reactive", "coin_collector"],
    },
    "genome_bounds": {
        "pipe_spacing": (28, 48),   # Distance between pipes
        "gap_size": (6, 11),         # Gap size (screen height = 24)
        "coin_spawn_rate": (0.15, 0.85),
        ...
    }
}
```

---

## Level Quality Metrics

Quality is computed from:

1. **Playability** (40%):
   - Survival rate (~50% target)
   - Average distance traveled
   - No instant deaths

2. **Balance** (30%):
   - Different bots perform similarly
   - Low coefficient of variation

3. **Progression** (30%):
   - Smooth difficulty curve
   - Score increases with distance

**Quality scores:**
- `0.8+` - Excellent level
- `0.6-0.8` - Good level
- `0.4-0.6` - Average level
- `<0.4` - Poor level

---

## Victory Screen

When a bot completes the entire 900-unit level:
- **Green overlay** with "VICTORY!" message
- Final statistics displayed
- Press ENTER to continue

---

## Project Structure

```
FlappyBird/
├── src/
│   ├── main.py                    # Entry point
│   ├── game_graphical.py          # Game loop
│   ├── entities/                  # Game entities (bird, pipe, coin)
│   ├── ai/                        # Bot implementations
│   │   ├── aggressive_bot.py
│   │   ├── reactive_bot.py
│   │   └── astar_bot.py           # A* pathfinding bot
│   ├── pcg/                       # Procedural content generation
│   │   ├── map_elites.py          # MAP-Elites algorithm
│   │   ├── level_genome.py        # Concrete level representation
│   │   ├── concrete_level.py      # Level data structures
│   │   ├── evaluator.py           # Quality metrics
│   │   └── level_tester.py        # Bot testing
│   └── utils/
│       └── config.py              # Configuration
├── data/
│   ├── map_elites_archive.json    # Evolution archive
│   └── pcg_levels/                # Generated levels
└── OCENA_CONCRETE_LEVELS.md       # Detailed analysis
```

---

## Testing & Analysis

### Run Complete MAP-Elites Test

Test the entire MAP-Elites system with analysis:

```bash
# Run MAP-Elites with 1000 iterations
python3 src/pcg/run_map_elites.py --iterations 1000 --plot

# Analyze generated levels
python3 analyze_new_levels.py

# Test bots on best levels
python3 test_best_concrete_level.py
```

### Test Individual Levels

```bash
# Test specific level with all bots
python3 test_concrete_levels.py data/pcg_levels/level_top1_q*.json

# Play level visually
python3 play_level.py data/pcg_levels/level_top1_q*.json

# Show top 3 levels
python3 show_top_levels.py
```

### View Analysis Results

After running MAP-Elites, check:
- **Archive heatmap**: `data/map_elites_archive_heatmap.png`
- **Full analysis**: `ANALIZA_MAP_ELITES.md`
- **Coverage statistics**: Console output from run_map_elites.py
- **Top levels**: `data/pcg_levels/level_top*.json`

### Performance Metrics

Current system performance (as of 2026-01-31):
- **Coverage**: 90.6% (58/64 cells filled)
- **Max quality**: 0.755
- **Speed**: 3.6 iterations/second (ultra-fast mode)
- **1000 iterations**: ~4.6 minutes

---

## Troubleshooting

**Bot dies immediately:**
- Levels may be too difficult (tight gaps)
- Try coin_collector bot (best performance with A* pathfinding)
- Increase `gap_size` bounds in config

**MAP-Elites too slow:**
- Reduce `--iterations` (default uses ultra-fast mode)
- Use `--quiet` flag to reduce output
- Reduce `test_duration` in config.py

**No levels generated:**
- Check `data/pcg_levels/` directory exists
- Run from correct directory (`/home/kasia/FlappyBird`)

---

## Performance

Current benchmarks (as of 2026-01-31):
- **Speed**: 3.6 iterations/second (ultra-fast mode, always enabled)
- **MAP-Elites (1000 iter)**: ~4.6 minutes
- **Coverage**: 90.6% (58/64 cells)
- **Quality range**: 0.305 - 0.755
- **Max quality achieved**: 0.755

---

## Credits

- PCG System: MAP-Elites algorithm by Jean-Baptiste Mouret & Jeff Clune
- A* Pathfinding: Based on classic A* algorithm
- Implementation: Built with Python + Pygame
- Date: 2026-01-29
