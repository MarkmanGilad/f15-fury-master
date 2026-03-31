# Update Log

## Session – March 31, 2026

### 1. Extract Constants to `constant.py`

Created `thegame/constant.py` and moved **all magic numbers and hardcoded constants** out of the source files into a single, flat module. Added `from constant import *` in every file that needs them.

**New file:** `thegame/constant.py` (~130 constants)

| Section | Key Constants |
|---------|--------------|
| Screen | `SCREEN_WIDTH`, `SCREEN_HEIGHT`, `FPS` |
| Colors | `COLOR_BLACK`, `COLOR_WHITE`, `COLOR_YELLOW`, `COLOR_RED`, `CRYSTAL_COLOR`, `MOON_COLOR`, `BACKGROUND_COLOR`, `OPENSCREEN_BACKGROUND_COLOR`, `ENDGAME_BACKGROUND_COLOR`, `BLUE`, `LIGHTGRAY` |
| Airplane | `AIRPLANE_START_X/Y`, `AIRPLANE_RESET_Y`, `AIRPLANE_IMAGE_SIZE`, `AIRPLANE_SPEED`, `AIRPLANE_COOLDOWN_THRESHOLD`, `AIRPLANE_MAX_RIGHT`, `AIRPLANE_MAX_CRYSTALS`, `CRYSTAL_RADIUS`, `BULLET_OFFSET_X/Y`, `CRYSTAL_DX_RANGE`, `CRYSTAL_DY_RANGE` |
| Building | `BUILDING_WIDTH`, `BUILDING_SCREEN_HEIGHT`, `BUILDING_SPEED`, `BUILDING_START_X`, `BUILDING_KILL_X`, `BUILDING_HEIGHT_MIN/MAX/STEP`, `BUILDING_GAP_OFFSET` |
| Bullet | `BULLET_IMAGE_SIZE`, `BULLET_SPEED`, `BULLET_KILL_X` |
| Enemy | `ENEMY_IMAGE_SIZE`, `ENEMY_START_X`, `ENEMY_VERTICAL_SPEED`, `ENEMY_VERTICAL_RANGE`, `ENEMY_KILL_X`, `ENEMY_X_OFFSET` |
| Fuel | `FUEL_IMAGE_SIZE`, `FUEL_Y_MIN`, `FUEL_START_X`, `FUEL_X_OFFSET_MIN/MAX`, `FUEL_SPEED_INCREMENT`, `FUEL_KILL_X`, `FUEL_INITIAL_COUNT`, `FUEL_ROTATION_SPEED/MAX`, `FUEL_PICKUP_BONUS` |
| DQN | `DQN_INPUT_SIZE`, `DQN_LAYER1/2/3`, `DQN_OUTPUT_SIZE`, `GAMMA` |
| AI Agent | `EPSILON_START`, `EPSILON_FINAL`, `EPSILON_DECAY`, `SOFT_UPDATE_TAU`, `ACTIONS` |
| Rewards | `DIE_REWARD`, `HOLE_REWARD`, `DISTANCE_REWARD`, `ENEMY_REWARD`, `PICKUP_REWARD`, `SHOOT_REWARD`, `SURVIVAL_REWARD`, `THROUGH_HOLE_REWARD`, `HOLE_CENTER_TOLERANCE`, `EDGE_TOO_CLOSE_PENALTY` |
| Environment | `INITIAL_FUEL_PERCENTAGE`, `INITIAL_FUEL_DROP`, `INITIAL_ENEMY_CHANCE`, `INITIAL_SPEED`, `NUM_STARS`, `MOON_RADIUS/Y`, `MOON_X_OFFSET`, `COLLISION_IMAGE_SIZE`, `OUT_OF_GAS_IMAGE_SIZE`, `SPEED_INCREMENT`, `PLAYER_SPEED_INCREMENT`, `STAR_SPEED`, `MOON_SPEED`, `EDGE_DISTANCE_THRESHOLD`, `FONT_SIZE`, `TIMER_TICKS`, `SCORE_INTERVAL`, `ENV_DEFAULT_DELAY` |
| Endgame | `ENDGAME_FONT_SIZE`, `ENDGAME_STATS_FONT_SIZE`, `ENDGAME_BUTTON_FONT_SIZE`, `ENDGAME_BUTTON_WIDTH/HEIGHT/SPACING`, `SHADOW_OFFSET`, `ENDGAME_VOLUME` |
| Openscreen | `OPENSCREEN_MUSIC_VOLUME`, `NUM_ASTEROIDS`, `AIRPLANE_VERTICAL_SPEED`, `AIRPLANE_UPPER_BOUND`, `AIRPLANE_LOWER_OFFSET` |
| Training | `BATCH_SIZE`, `LEARNING_RATE`, `TRAINING_EPOCHS`, `TARGET_UPDATE_FREQ`, `MIN_BUFFER_SIZE`, `TRAINING_FPS`, `SAVE_FREQUENCY`, `SCHEDULER_MILESTONES`, `SCHEDULER_GAMMA` |
| Replay Buffer | `REPLAY_BUFFER_CAPACITY` |

**Files updated (14):**

| File | Changes |
|------|---------|
| `airplane.py` | Removed local `WIDTH`, `HEIGHT`; replaced `(0,0,0)`, sizes, speed, cooldown threshold, crystal limits, color tuples |
| `buildings.py` | Removed local `WIDTH`, `HEIGHT`; replaced speed, height range, positions |
| `bullet.py` | Removed local `WIDTH`, `HEIGHT`; replaced image size, speed, kill boundary |
| `DQN.py` | Removed `input_size`, `layer1–3`, `output_size`, `gamma`; replaced with `DQN_*` and `GAMMA` |
| `Ai_Agent.py` | Removed `epsilon_start/final`, `epsiln_decay`; replaced with `EPSILON_*`, `ACTIONS`, `SOFT_UPDATE_TAU` |
| `Environment.py` | Removed `WIDTH`, `HEIGHT`, `FPS`, all reward constants; replaced ~30 magic numbers |
| `enemy.py` | Removed local `WIDTH`, `HEIGHT`; replaced image size, positions, speeds, ranges |
| `fuel.py` | Removed local `WIDTH`, `HEIGHT`; replaced image size, positions, speeds, rotation |
| `Graphic.py` | Removed `BLUE`, `LIGHTGRAY`, `WIDTH`, `HEIGHT`, `FPS`; replaced sizes, colors, tick rate |
| `openscreen.py` | Removed `WIDTH`, `HEIGHT`, `FPS`; replaced screen size, colors, star count, volumes, button sizes |
| `endgame.py` | Added import; replaced screen size, colors, font sizes, button sizes, volumes |
| `Game.py` | Added import; replaced FPS tick |
| `train.py` | Added import; replaced batch size, learning rate, epochs, scheduler, save frequency, buffer threshold, tick rate |
| `replaybuffer.py` | Removed `capacity`; replaced with `REPLAY_BUFFER_CAPACITY` |

---

### 2. Create `Train.md` – Training Documentation

Created `Train.md` at the project root documenting the full training pipeline:

- **State space** – 13-dimensional normalized tensor (player position, fuel, cooldown, buildings, fuel items, enemy flag)
- **Action space** – 6 discrete actions (no-op, up, down, right, left, shoot)
- **Reward structure** – terminal rewards, directional distance shaping, edge penalty, event bonuses, unused/reserved rewards
- **Training loop** – DDQN with replay buffer, epsilon-greedy exploration, hard target updates
- **Hyperparameters** – learning rate, batch size, buffer capacity, scheduler milestones, etc.
- **DQN architecture** – 4-layer MLP (13 → 64 → 128 → 64 → 6)
- **Game dynamics** – progressive difficulty (speed increases, enemy spawn rate, fuel drain)

---

### 3. Fix State Tensor Bugs in `Environment.py`

Found and fixed **3 bugs** in `Tensor_env()`, `move()`, and `building_reward()`:

| # | Severity | Bug | Fix |
|---|----------|-----|-----|
| 1 | **CRITICAL** | `self.player.x` / `self.player.y` are never updated after `__init__` — state[0] and state[1] were frozen constants; the agent was blind to its own position | Changed to `self.player.rect.centerx` / `self.player.rect.centery` |
| 2 | Medium | Building order from `list(self.buildingsG)` depends on `pygame.sprite.Group` iteration order, which is not API-guaranteed | Replaced with `sorted(self.buildingsG, key=lambda b: b.rect.top, reverse=True)` in all 3 methods |
| 3 | Low | Fuel loop had no bounds guard — could overwrite `env_state[12]` (enemy flag) or crash if >2 fuels existed | Added `if i >= 2: break` cap |
| 4 | Low | Comments labelled bottom building as "upper" and vice versa | Fixed comments |

---

### 4. Fix Cooldown Reset & Edge Penalty Consistency

| # | Bug | Fix |
|---|-----|-----|
| 1 | `Airplane.cooldown` (class variable) not reset between episodes — `state[3]` carried over from previous death | Added `Airplane.cooldown = 0` in `Environment.reset()` after creating new Airplane |
| 2 | Edge penalty used `self.player.rect.x` (left edge of sprite) while state reports `rect.centerx` — ~75px mismatch | Changed to `self.player.rect.centerx` for consistency |

---

### 5. Fix Reward Logic Bugs

| # | Severity | Bug | Fix |
|---|----------|-----|-----|
| 1 | **CRITICAL** | Edge penalty was inverted — `EDGE_TOO_CLOSE_PENALTY = -0.5` meant `self.reward -= (-0.25)` **rewarded** staying near the edge | Changed constant to `+0.5`, flipped sign on the moving-right branch to `self.reward -= EDGE_TOO_CLOSE_PENALTY` |
| 2 | Medium | `Building.speed == 6` float equality almost never triggers — enemy chance reduction was dead code | Changed to range check `Building.speed >= 6 and Building.speed < 6 + SPEED_INCREMENT` |
| 3 | Low | On death, `self.reward` stayed `0.0` (early return skipped assignment) — wandb logged wrong reward for death episodes | Added `self.reward = DIE_REWARD` before the early return |

### 6. Building Reward & Positive Alignment Reward

| # | Change | Detail |
|---|--------|--------|
| 1 | Removed dead `building_reward()` method | Its logic (hole-center distance) was already handled inline by the directional reward in `move()`, so the standalone method was redundant dead code — deleted it |
| 2 | Added positive reward for alignment | When `|delta| ≤ HOLE_CENTER_TOLERANCE` and action is NOT vertical (1/2), the agent now receives a positive reward for staying centered on the hole |

### 7. Reward Audit — Fix Per-Step Alignment Magnitude

**Hole calculation verified correct** — bottom building `rect.top`, top building `rect.bottom`, average gives true hole center. Gap is always `BUILDING_GAP_OFFSET (200px)`.

| # | Severity | Bug | Fix |
|---|----------|-----|-----|
| 1 | **CRITICAL** | Alignment reward used `+HOLE_REWARD (0.9)` per step — over ~380 steps per building pair this accumulates to ~180+, completely drowning out `DIE_REWARD (−1.0)`. Causes Q-value explosion and agent ignoring death | Changed alignment reward from `HOLE_REWARD (0.9)` to `SURVIVAL_REWARD (0.01)` — proportional to death penalty over an episode |

### 8. DDQN Training Loop Fixes

| # | Severity | File | Bug | Fix |
|---|----------|------|-----|-----|
| 1 | **CRITICAL** | `DQN.py` | `__call__` overrides `nn.Module.__call__` — bypasses all PyTorch module infrastructure (hooks, train/eval mode, gradient profiling). Works by accident only because no dropout/batchnorm/GPU is used | Removed the `__call__` method — `nn.Module.__call__` already delegates to `forward()` |
| 2 | **HIGH** | `train.py` | wandb logged `env.reward` (last step's reward, always `DIE_REWARD = −1.0` on death) instead of cumulative episode reward — training progress was invisible in dashboards | Added `total_reward` accumulator, reset each episode, logged to wandb and console |
| 3 | **MEDIUM** | `train.py` | Target net update used `env.is_end_of_game()` which re-runs collision detection — could detect new collisions after `move()` physics, causing off-timing updates | Changed to use the existing `done` flag from `move()` |
| 4 | **LOW** | `train.py` | `optim.zero_grad()` called after `optim.step()` — functionally correct but non-standard PyTorch pattern | Reordered to standard `zero_grad() → backward() → step()` |

### 9. wandb Logging Improvements

| # | Change | Detail |
|---|--------|--------|
| 1 | Average loss per episode | Added `total_loss` and `loss_count` accumulators. Each training step adds `loss.item()`. At episode end, `avg_loss = total_loss / loss_count` is logged to wandb, then both reset |
| 2 | `wandb.init` config | Now logs all key hyperparameters: LR, batch size, gamma, epsilon (start/final/decay), target update freq, buffer capacity/min size, scheduler milestones/gamma, input/output size, and `str(player.DQN)` (full network architecture) |

### 10. Epsilon Print & Score Rewards

| # | Change | File | Detail |
|---|--------|------|--------|
| 1 | Epsilon in console output | `train.py` | Added current epsilon value to the per-episode print line |
| 2 | Per-step survival reward | `Environment.py` | Added `+SURVIVAL_REWARD (+0.01)` every step the agent is alive — shifts baseline positive to counterbalance death penalty |
| 3 | Through-hole reward | `Environment.py` | Added `+THROUGH_HOLE_REWARD (+0.5)` when both buildings scroll off screen — directly rewards the core objective of passing through gaps |

### 11. Score Logging & Reward Corrections

| # | Change | File | Detail |
|---|--------|------|--------|
| 1 | Score counters for logging | `Environment.py` | Added `holes_passed`, `enemies_killed`, `fuels_collected` counters — reset each episode, incremented in `move()`, purely for progress tracking |
| 2 | Score logged to console + wandb | `train.py` | Console prints `holes: X kills: X fuel: X` per episode; wandb logs all three as metrics |
| 3 | Edge penalty only on move-right | `Environment.py` | Previously all actions in the right 34% of the screen got −0.25 penalty — was the main cause of always-negative rewards. Now only action 3 (move right) is penalized (−0.5) |
| 4 | Removed double SURVIVAL_REWARD | `Environment.py` | When aligned, agent got `SURVIVAL_REWARD` from per-step line AND from alignment branch (double-counting). Removed the alignment branch duplicate |

### 12. Target Net Update Frequency

| # | Change | File | Detail |
|---|--------|------|--------|
| 1 | `TARGET_UPDATE_FREQ` 4 → 20 | `constant.py` | With C=4 the target net absorbed degraded policy weights too quickly, causing a smooth co-drift where both networks decline together (loss stays stable ~0.02 but Q-values drift downward). C=20 keeps the target anchored to a good policy for longer, giving the policy net time to recover from brief performance drops |
