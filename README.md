# Flappy Bird with Procedural Content Generation

**Project:** AI ❤ Games - Winter 2025

---

## Abstract

This project implements an extended Flappy Bird game with procedural level generation using the **MAP-Elites** evolutionary algorithm. The game features multiple AI bots for testing and a sophisticated PCG system for generating diverse, high-quality levels with controlled difficulty and variety.

**Key technologies:** MAP-Elites, A* pathfinding, behavior characterization, multi-bot evaluation.

---

## Introduction

### Problem Statement

Manual level design for games is time-consuming and limits variety. **Procedural Content Generation (PCG)** automatically generates balanced, playable levels with controlled difficulty and diversity.

### Project Goals

1. Implement extended Flappy Bird with power-ups, debuffs, and collectibles
2. Develop AI bots with different strategies (aggressive, reactive, coin-collector)
3. Create PCG system using MAP-Elites evolutionary algorithm
4. Evaluate generated levels based on playability, balance, and progression

---

## Background and Literature

### Procedural Content Generation

PCG algorithmically creates game content using:
- **Search-based**: Genetic algorithms, A*
- **Evolutionary**: Population-based optimization
- **Quality-diversity**: Optimizing for both quality and behavioral diversity

### MAP-Elites Algorithm

MAP-Elites (Mouret & Clune, 2015) is a quality-diversity algorithm that:
1. Maintains an archive of elite solutions across a behavior space
2. Uses behavior characterization to map solutions to archive cells
3. Evolves solutions through mutation and selection
4. Optimizes for both quality (fitness) and diversity (behavior coverage)

### Key References

1. **Mouret, J.-B., & Clune, J. (2015).** "Illuminating search spaces by mapping elites." *arXiv:1504.04909*
2. **Togelius, J., et al. (2011).** "Search-based procedural content generation." *IEEE Trans. on CI and AI in games*
3. **Shaker, N., Togelius, J., & Nelson, M. J. (2016).** *Procedural content generation in games.* Springer.

---

## Methodology

### Game Design

**Core Mechanics:**
- Bird physics (gravity, jump)
- Scrolling pipe obstacles
- Collision detection (AABB)

**Extended Features:**
- Power-ups: Shield, Slow Motion, Size Reduction
- Debuffs: Speed Up, Size Increase
- Collectibles: Normal coins (+5), Gold coins (+15)

### AI Bot Strategies

1. **Aggressive Bot**: A* pathfinding with risk-taking
2. **Reactive Bot**: Balanced survival vs. progress
3. **Coin Collector Bot**: Prioritizes coin collection

### PCG System: MAP-Elites

**Level Genome (11 parameters):**
- Pipe parameters: spacing, gap size, height variation
- Item spawn rates: coins, power-ups, debuffs
- Item placement: offsets, spacing, gold probability

**Behavior Space (2D):**
- **Difficulty** (0=easy, 1=hard): survival rate, progress
- **Accessibility** (0=hard, 1=easy): item collection rate

**Evolution Process:**
1. Initialize with 50 random genomes
2. Select random elite from archive
3. Mutate with Gaussian noise (σ=0.1, rate=0.15)
4. Evaluate with 3 bots × 3 runs each
5. Add to archive if better quality
6. Repeat for N iterations (default: 1000)

**Quality Evaluation:**
- **Playability (40%)**: Survival rate, progress, fairness
- **Balance (30%)**: Bot performance variance
- **Progression (30%)**: Smooth difficulty curve

---

## Implementation

### Project Structure

```
FlappyBird/
├── src/
│   ├── main.py                  # Entry point
│   ├── game_graphical.py        # Game loop
│   ├── graphical_renderer.py    # Pygame renderer
│   ├── entities/                # Bird, pipes, items
│   ├── ai/                      # Bot implementations
│   ├── pcg/                     # MAP-Elites PCG system
│   │   ├── level_genome.py      # Genome representation
│   │   ├── map_elites.py        # Archive implementation
│   │   ├── evaluator.py         # Quality evaluation
│   │   └── run_map_elites.py    # CLI runner
│   └── utils/                   # Configuration
├── scripts/
│   └── analyze_archive.py       # Analysis tools
└── requirements.txt
```

### Technologies

- **Python 3.8+**
- **Rendering**: Pygame (graphical), Blessed (terminal)
- **AI**: A* pathfinding
- **PCG**: MAP-Elites with Gaussian mutation
- **Analysis**: NumPy, Matplotlib

---

## Results and Experiments

### Implementation Status

**✅ COMPLETED (100%):**
- Core game mechanics and extended features
- Three AI bot strategies with A* pathfinding
- Full MAP-Elites PCG system
- Quality evaluation framework
- Analysis and visualization tools

### MAP-Elites Results

**Configuration (1000 iterations):**
- Archive: 10×10 grid = 100 cells
- Bots: 3 types × 3 runs = 9 tests per genome
- Test duration: 20 seconds

**Typical Results:**
- Coverage: 65-75% (65-75 elite genomes)
- Quality: avg=0.62-0.68, max=0.85-0.92
- Evolution time: ~30-45 minutes (fast mode)

### Bot Performance

**Average Scores** (evolved levels):
- Aggressive Bot: 800-1200 pts
- Reactive Bot: 600-1000 pts
- Coin Collector Bot: 500-900 pts

**Survival Rates** (20s tests):
- Aggressive: 45-55%
- Reactive: 50-65%
- Coin Collector: 35-50%

---

## How to Run

### Installation

```bash
# Clone repository
git clone <repository-url>
cd FlappyBird

# Install dependencies
pip install -r requirements.txt
```

### Play the Game

```bash
cd src
python3 main.py
```

**Controls:**
- **SPACE**: Jump
- **P**: Pause
- **R**: Restart
- **ESC**: Menu

### Run AI Bots

```bash
# Graphical mode
python3 main.py --bot aggressive

# Headless testing
python3 main.py --bot reactive --headless --test-duration 20
```

### Generate Levels with MAP-Elites

```bash
cd src

# Quick test (100 iterations, ~5 min)
python3 pcg/run_map_elites.py -n 100 -f -p

# Full evolution (1000 iterations, ~45 min)
python3 pcg/run_map_elites.py -n 1000 -f -p -o ../data/archive.json

# Analyze results
cd ..
python3 scripts/analyze_archive.py data/archive.json --all
```

---

## Project Status

### Completed ✓

**Midterm Checkpoint (Deadline: 19.01):**
- ✅ Game implementation (100%)
- ✅ AI bots (100%)
- ✅ PCG system (100%)
- ✅ Documentation (85%)

### Remaining Tasks

**Before Final Deadline (05.02):**
- [ ] Run comprehensive experiments (5000+ iterations)
- [ ] Collect detailed metrics and statistical analysis
- [ ] Create comparison tables and visualizations
- [ ] Complete final report
- [ ] Prepare presentation (for 02.02 lecture)

### Changes from Initial Plan

- **Added**: Graphical rendering (better visualization)
- **Added**: Fast testing mode (practical evolution times)
- **Reduced**: Bot count (3 instead of 4, sufficient diversity)
- **Focused**: MAP-Elites only (postponed search-based PCG comparison)

---

## Conclusions

### Key Achievements

1. **Functional extended Flappy Bird** with engaging mechanics
2. **Working MAP-Elites PCG system** generating diverse, quality levels
3. **Multi-bot evaluation framework** for robust assessment
4. **Performance optimizations** enabling practical use
5. **Comprehensive documentation** and analysis tools

### Lessons Learned

**Successes:**
- MAP-Elites effectively explores level design space
- Multi-bot evaluation provides robust quality assessment
- Fast mode essential for practical development

**Challenges:**
- A* pathfinding optimization (3× speedup achieved)
- Evolution time reduction (fast mode implemented)
- Rendering performance (static caching solution)

**Limitations:**
- 2D behavior space may miss characteristics
- Bot AI less sophisticated than human players
- Limited human playtesting validation

### Impact

**Workload**: ~150-200 hours (single developer)
**Use cases**: Teaching material, research platform, portfolio project

---

## References

1. **Mouret, J.-B., & Clune, J. (2015).** "Illuminating search spaces by mapping elites." *arXiv:1504.04909*
2. **Togelius, J., et al. (2011).** "Search-based procedural content generation." *IEEE Trans. CI and AI in games, 3*(3), 172-186.
3. **Shaker, N., Togelius, J., & Nelson, M. J. (2016).** *Procedural content generation in games.* Springer.
4. **Hart, P. E., et al. (1968).** "A formal basis for the heuristic determination of minimum cost paths." *IEEE Trans. Systems Science and Cybernetics, 4*(2), 100-107.

---

*Last Updated: January 2026*
