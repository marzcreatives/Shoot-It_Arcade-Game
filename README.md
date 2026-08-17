# Shoot-It_Arcade-Game

![Shoot-It Arcade Game Preview](https://user-images.githubusercontent.com/116493523/226599856-9fb603b2-f09a-4490-a51b-45f96a226a69.png)

A classic arcade-style shooting game built with **Python** and **Pygame**.

Shoot moving targets, rack up points, and challenge yourself across three different game modes. All game assets are included in the repository, including custom balloons, cups, ducks, sound effects, and menu screens.

## Getting Started

### Prerequisites

- Python 3.10+
- Pygame
### Installation

Clone the repository:

```bash
git clone https://github.com/marzcreatives/Shoot-It_Arcade-Game.git
cd Shoot-It_Arcade-Game
```

Install dependencies:

```bash
pip install pygame
```

### Run the Game

From the project root directory:

```bash
python main.py
```

On some systems you may need:

```bash
python3 main.py
```

### Project Structure

```text
Shoot-It_Arcade-Game/
├── main.py
├── high_scores.txt
├── assets/
│ ├── bgs/
│ ├── banners/
│ ├── font/
│ ├── guns/
│ ├── menus/
│ ├── sounds/
│ └── targets/
```

> The game loads assets using relative paths, so ensure you run `main.py` from the root directory.

---

## Game Modes

### 🎯 Freeplay

Clear all targets as quickly as possible. Your score is based on the time taken to complete all levels.

[Watch Freeplay Gameplay](https://github.com/marzcreatives/Shoot-It_Arcade-Game/assets/116493523/bcd6f36c-f450-4be2-9486-ff505e98ae71)

### 🔫 Accuracy

You have a limited number of pellets. Make every shot count and achieve the highest score possible before running out of ammo.

[Watch Accuracy Mode](https://user-images.githubusercontent.com/116493523/226651242-cc73da70-2b93-4c02-a73c-de85c70043fe.mov)

### ⏱️ Countdown

Race against the clock and score as many points as possible before time runs out.

[Watch Countdown Mode](https://user-images.githubusercontent.com/116493523/226652574-ff0fdf77-7bfc-4703-b2aa-333154aa03d5.mov)

---

Good luck, and happy shooting! 🎮
