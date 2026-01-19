# Flappy Bird with Procedural Level Generation

## Abstract

The aim of the project is to create a **Flappy Bird–style game** extended with additional gameplay mechanics.  
Players will navigate through pipe obstacles while collecting **power-ups** (size reduction, shield, slowdown), facing **debuffs** (speed-up, size increase), and gathering **coins** to increase their score.  

The project will also involve the creation of **AI-controlled bots** using pathfinding and heuristic decision-making (e.g. A*), each with a distinct play style.  

The main focus of the study is to explore and **compare different level generation methods**, including **evolutionary algorithms** and **search-based procedural generation**, evaluating them in terms of difficulty, balance, and gameplay experience.

## Background

Although games like Flappy Bird are based on simple mechanics, difficulty largely depends on level design and player decision-making, making manual creation of balanced levels time-consuming and often repetitive

**Procedural Content Generation (PCG)** allows automatic creation of levels with controlled difficulty and variety.  
Adding AI-controlled bots makes it possible to test levels under different strategies and evaluate their balance in a more systematic way.

## Project goal

The goal of the project is to build an extended Flappy Bird–style game and analyze different approaches to level design and gameplay strategies.

The main objectives are:
- implement power-ups, debuffs, and coin-based scoring,
- implement AI bots with different behaviors (e.g. cautious, coin-focused, random),
- generate levels using evolutionary and search-based methods,
- compare levels using player and bot performance.

## Methodology

The project combines game development, AI implementation, and level generation experiments.

- Core gameplay is based on flying through obstacles while collecting items.
- AI bots use pathfinding (e.g. **A\*** ) and heuristic rules:
  - **cautious bot** – prioritizes survival and avoids risky paths,
  - **collector bot** – prioritizes coins over safety,
  - **random bot** – makes non-deterministic decisions.
- Procedural levels are generated using search-based or optimization techniques.
- Levels are evaluated based on playability, difficulty, and bot performance.
