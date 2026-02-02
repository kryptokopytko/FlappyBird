# Flappy Bird with Procedural Content Generation
**Authors:** Katarzyna Szmagara, Kornelia Makowska

## Overview
This project implements a **Flappy Bird–style game** with additional mechanics: coins, power-ups, and debuffs.  
Levels are generated using **procedural content generation (PCG)**, including **MAP-Elites**, **Monte Carlo Tree Search (MCTS)**, and **novelty search**, allowing exploration of level diversity, difficulty, and balance.  

## AI Bots
AI-controlled bots evaluate levels with distinct play styles:

- **Aggressive Bot**: Jumps minimally, only when absolutely necessary.  
- **Reactive Bot**: Responds to current position relative to gap center.  
- **Coin Collector Bot**: Prioritizes collecting coins while maintaining safety.

## Goal
The main goal is to explore how **different level generation methods affect gameplay**, and to provide a framework for **systematic AI-based level evaluation**.

## Project Structure

```
FlappyBird/
├── src/
│   ├── main.py                    # Entry point
│   ├── entities/                  # Game entities (bird, pipe, powerups)
│   ├── core/                      # Game entities (bird, pipe, powerups)
│   ├── ai_bots/                   # Configuration and utils
│   │   ├── aggressive_bot.py
│   │   ├── reactive_bot.py
│   │   └── astar_bot.py           
│   ├── pcg/                       # Level generators
│   │   ├── map_elites/        
│   │   ├── mcts/     
│   │   ├── novelty/     
│   │   ├── evaluator.py           # Quality metrics
│   └── rendering/
│   └── tests/
├── data/                          # Generated levels and test statistics
```

## User guide

### Items in the Game

| Item Name | Type | Image |
|-----------|------|-------|
| COIN | coin | ![COIN](images/image-3.png) |
| Shield | power-up | ![POWERUP_SHIELD](images/image-4.png) |
| Slow Motion | power-up | ![POWERUP_SLOW_MOTION](images/image-6.png) |
| Small Size | power-up | ![POWERUP_SMALL](images/image-5.png) |
| Speed Up | debuff | ![DEBUFF_SPEED_UP](images/image-1.png) |
| Large Size | debuff | ![DEBUFF_LARGE](images/image-2.png) |


Points awarded for collecting coins are **non-linearly scaled** to reward collecting more coins while preventing excessive score growth.
The score is computed as:

- No coins → **0 points**
- For at least one coin, the reward grows according to a **sub-exponential power function**:
  
  \[
  \text{points} = \min\left( (1 + \frac{n}{3})^{1.5},\ 130 \right)
  \]

### Running the Game

To start the game, run:

```bash
python3 src/main.py
```

Once launched, you can select the game mode directly from the UI:
- Manual Play – control the bird using Space to flap.
- Bot Play – let an AI bot control the bird.

Levels are generated pseudorandomly based on parameters defined in GAME_CONFIG (see core/config).

For more advanced use cases (e.g. automated testing or AI evaluation), the game can also be run with additional command-line arguments:

--bot {aggressive, reactive, coin_collector}
Starts the game with a selected AI bot without using the UI.

--headless (or --no-graphics)
Runs the game without rendering graphics. Intended for automated experiments.

--test-duration <seconds>
Sets the duration of the test run in seconds
(default: 20, available only in headless mode).


## Procedural Content Generation

### Map Elites

```bash
# Generate levels
python3 src/pcg/map_elites/run_map_elites.py
```

Optional arguments (more parameters in /src/core/config):
--iterations, -n

--initial-samples, -i

--output, -o

--plot, -p
Generate and display a heatmap visualization after the run finishes.

**Output:**
- Archive: `data/map_elites_archive.json`
- Top levels: `data/pcg_levels/level_top*_q*.json`
- Console: Coverage, quality range, top 5 levels

```bash
# Test bots on best map elites levels
python3 src/tests/test_top3_levels.py
```

### MCTS

```bash
# Generate levels
python3 src/pcg/mcts/run_mcts_qd.py

# Test levels
python3 src/tests/test_mcts_levels.py
```

### Novelty

```bash
# Generate levels
python3 src/pcg/novelty/run_novelty_search.py

# Test levels
python3 src/tests/test_novelty_levels.py
```

## Level Quality Metrics

Quality is computed from:

1. **Playability** (35%):
   - Survival rate (~50% target)
   - Average distance traveled
   - No instant deaths

2. **Balance** (35%):
   - Different bots perform similarly
   - Low coefficient of variation

3. **Progression** (30%):
   - Smooth difficulty curve
   - Score increases with distance

