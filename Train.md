# Training Documentation

## Overview

This project trains a **Double DQN (DDQN)** agent to fly a spaceship through gaps between buildings, avoid enemies, collect fuel, and survive as long as possible.

---

## State Space

The environment is represented as a **13-dimensional float tensor**, normalized to the `[0, 1]` range.

| Index | Feature | Normalization |
|-------|---------|---------------|
| 0 | Player center X position | `rect.centerx / SCREEN_WIDTH` |
| 1 | Player center Y position | `rect.centery / SCREEN_HEIGHT` |
| 2 | Fuel percentage | `/ 100` |
| 3 | Can shoot (cooldown ready) | `1.0` if `cooldown > 70`, else `0.0` |
| 4 | Building 1 (bottom) X | `/ SCREEN_WIDTH` |
| 5 | Building 1 (bottom) top edge | `/ SCREEN_HEIGHT` |
| 6 | Building 2 (top) X | `/ SCREEN_WIDTH` |
| 7 | Building 2 (top) bottom edge | `/ SCREEN_HEIGHT` |
| 8 | Fuel item 1 X | `/ SCREEN_WIDTH` |
| 9 | Fuel item 1 Y | `/ SCREEN_HEIGHT` |
| 10 | Fuel item 2 X | `/ SCREEN_WIDTH` |
| 11 | Fuel item 2 Y | `/ SCREEN_HEIGHT` |
| 12 | Enemy incoming flag | `1.0` if enemy will spawn with next building pair, else `0.0` |

> Produced by `Environment.Tensor_env()`.

---

## Action Space

The agent chooses from **6 discrete actions** each step:

| Action | Meaning | Effect |
|--------|---------|--------|
| 0 | No-op | Do nothing |
| 1 | Move Up | `centery -= speed` (if `top > 0`) |
| 2 | Move Down | `centery += speed` (if `bottom < SCREEN_HEIGHT`) |
| 3 | Move Right | `centerx += speed` (if `right < AIRPLANE_MAX_RIGHT`) |
| 4 | Move Left | `centerx -= speed` (if `left > 0`) |
| 5 | Shoot | Fire bullet (if cooldown > `AIRPLANE_COOLDOWN_THRESHOLD`) |

> Action selection uses **epsilon-greedy** exploration during training. Epsilon decays linearly from `EPSILON_START` (1.0) to `EPSILON_FINAL` (0.01) over the first `EPSILON_DECAY` (100) episodes.

---

## Reward Structure

Rewards are computed in `Environment.move()` every step. Multiple reward components can stack in a single step.

### Terminal Reward

| Condition | Reward | Notes |
|-----------|--------|-------|
| Collision with building or enemy | `DIE_REWARD` (−1.0) | Episode ends (`done = True`) |
| Out of fuel (0%) | `DIE_REWARD` (−1.0) | Episode ends (`done = True`) |

### Directional Distance Reward

The agent is rewarded/penalized based on whether its action **moves it toward the center of the hole** between buildings:

```
delta = hole_center_y − player_center_y
```

| Situation | Action | Reward |
|-----------|--------|--------|
| Aligned (`|delta| ≤ 10px`) | Up (1) or Down (2) | `−DISTANCE_REWARD` (−0.3) — don't move away |
| Aligned (`|delta| ≤ 10px`) | Other (0, 3, 4, 5) | No shaping reward (survival reward already applied) |
| Hole below (`delta > 10`) | Down (2) | `+DISTANCE_REWARD` (+0.3) — moving toward hole |
| Hole below (`delta > 10`) | Up (1) | `−DISTANCE_REWARD` (−0.3) — moving away |
| Hole below (`delta > 10`) | Other | `−DISTANCE_REWARD / 2` (−0.15) |
| Hole above (`delta < −10`) | Up (1) | `+DISTANCE_REWARD` (+0.3) — moving toward hole |
| Hole above (`delta < −10`) | Down (2) | `−DISTANCE_REWARD` (−0.3) — moving away |
| Hole above (`delta < −10`) | Other | `−DISTANCE_REWARD / 2` (−0.15) |

### Edge Penalty

Discourages the player from drifting too far right (within 500px of the right edge):

| Action | Reward |
|--------|--------|
| Move Right (3) | `−EDGE_TOO_CLOSE_PENALTY` (−0.5) |
| Any other | No penalty |

### Event-Based Rewards

| Event | Reward | Notes |
|-------|--------|-------|
| Staying alive (per step) | `+SURVIVAL_REWARD` (+0.01) | Unconditional per-step bonus |
| Pass through hole | `+THROUGH_HOLE_REWARD` (+0.5) | When both buildings scroll off screen |
| Kill enemy (bullet hits) | `+ENEMY_REWARD` (+0.1) | |
| Collect fuel pickup | `+PICKUP_REWARD` (+0.1) | Fuel +2% |
| Shoot | `+SHOOT_REWARD` (−0.02) | Penalty to discourage spam |

### Defined but Unused

| Constant | Value | Notes |
|----------|-------|-------|
| `HOLE_REWARD` | +0.9 | Originally used in removed `building_reward()` method |

---

## Training Loop

```
for each step:
    1. Get state          → Tensor_env()
    2. Select action      → epsilon-greedy via DQN
    3. Execute action     → Environment.move(action) → (reward, done)
    4. Accumulate reward   → total_reward += reward
    5. Get next state     → Tensor_env()
    6. Store transition   → ReplayBuffer.push(s, a, r, s', done)
    7. If buffer ≥ 2000:
        a. Sample batch of 50
        b. Compute Q(s, a) from policy net
        c. Compute a' = argmax_a Q_policy(s', a)         ← DDQN
        d. Compute Q_target(s', a') from target net
        e. Loss = MSE( Q(s,a),  r + γ·Q_target(s',a')·(1−done) )
        f. Accumulate loss  → total_loss += loss.item()
        g. zero_grad() → Backprop → Adam step → scheduler step
    8. If done and epoch % C == 0:
        → Hard-copy policy net weights to target net
    9. If done:
        → Log total_reward, avg_loss, time, steps to wandb
        → Reset total_reward, total_loss, loss_count = 0
```

### Hyperparameters

| Parameter | Value |
|-----------|-------|
| Discount factor (γ) | 0.99 |
| Learning rate | 0.0001 |
| Batch size | 50 |
| Replay buffer capacity | 100,000 |
| Min buffer before training | 2,000 |
| Target net update frequency | Every 20 episodes |
| Target net update method | Hard copy |
| Epsilon schedule | Linear: 1.0 → 0.01 over 100 episodes |
| LR scheduler | MultiStepLR at [5M, 10M, 15M] steps, γ=0.5 |
| Training FPS | 300 |
| Checkpoint save frequency | Every 1,000 episodes |

### wandb Logging

**Per-episode metrics** logged via `wanrun.log()`:

| Metric | Description |
|--------|-------------|
| `time` | In-game time survived |
| `reward` | Cumulative episode reward (`total_reward`) |
| `step_to_end` | Steps in the episode |
| `avg_loss` | Mean MSE loss over training steps in the episode |
| `holes_passed` | Number of building pairs passed |
| `enemies_killed` | Number of enemies killed |
| `fuels_collected` | Number of fuel pickups collected |
| `score` | In-game score (`Environment.score`) |

**Run config** logged at `wandb.init()`: learning rate, batch size, gamma, epsilon (start/final/decay), target update freq, buffer capacity, min buffer size, scheduler milestones/gamma, DQN input/output size, and full network architecture string.

### DQN Architecture

```
Input (13) → Linear(64) → LeakyReLU
          → Linear(128) → LeakyReLU
          → Linear(64)  → LeakyReLU
          → Linear(6)   → Q-values
```

---

## Game Dynamics (affecting training)

- **Building speed** increases by `+0.005` every step — the game gets progressively harder.
- **Player speed** increases by `+0.6` when building speed crosses an even number — controls become more sensitive.
- **Enemy spawn rate** increases when building speed reaches 6 (enemy chance decreases).
- **Fuel drains** at a fixed rate (1% every 30 render ticks). Collecting fuel restores +2%.
- **Buildings** spawn in pairs (top + bottom) creating a gap the agent must fly through.
- **Enemies** appear after every N-th building pair, oscillating vertically ±25px.
