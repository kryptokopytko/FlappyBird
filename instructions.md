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

# Quick test
python3 pcg/run_map_elites.py -n 100 -f -p

# Full evolution
python3 pcg/run_map_elites.py -n 1000 -f -p -o ../data/archive.json

# Analyze results
cd ..
python3 scripts/analyze_archive.py data/archive.json --all
```
