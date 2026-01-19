# Flappy Bird with Procedural Content Generation

### Implementation Status

## COMPLETED:
- ✅ Core game mechanics
- ✅ Grafical mode
- ✅ Three AI bot strategies
  - **Aggressive Bot**: A* pathfinding with risk-taking
  - **Reactive Bot**: Balanced survival vs. progress
  - **Coin Collector Bot**: Prioritizes coin collection
- ✅ First approach to procedural level generation using MAP-Elites

## REMAINING:
- [ ] Improve and expand level generator
- [ ] Implement additional generation methods (including search-based approaches)
- [ ] Collect detailed metrics and statistical analysis
- [ ] Compare level generation methods
- [ ] Save interesting levels


### Current PCG: MAP-Elites

**Level Genome (11 parameters):**
- Pipe parameters (4): spacing, gap_size, max_height_change, gap_variance
- Item spawn rates (3): coin, powerup, debuff
- Item placement (4): coin_offset_min/max, item_spacing, gold_probability

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