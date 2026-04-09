# State & Reward Logic — F15 Fury

## State Representation (`Tensor_env`)

The environment exposes a **13-element normalized float tensor** to the DQN agent:

| Index | Feature | Normalization |
|-------|---------|---------------|
| 0 | Player center X | `/ SCREEN_WIDTH` |
| 1 | Player center Y | `/ SCREEN_HEIGHT` |
| 2 | Fuel percentage | `/ 100` |
| 3 | Can shoot (cooldown > threshold) | `0` or `1` |
| 4 | Bottom building X | `/ SCREEN_WIDTH` |
| 5 | Bottom building top edge (hole bottom) | `/ SCREEN_HEIGHT` |
| 6 | Top building X | `/ SCREEN_WIDTH` |
| 7 | Top building bottom edge (hole top) | `/ SCREEN_HEIGHT` |
| 8 | Fuel item 1 X | `/ SCREEN_WIDTH` |
| 9 | Fuel item 1 Y | `/ SCREEN_HEIGHT` |
| 10 | Fuel item 2 X | `/ SCREEN_WIDTH` |
| 11 | Fuel item 2 Y | `/ SCREEN_HEIGHT` |
| 12 | Next building pair spawns enemy | `0` or `1` |

All values are in the `[0, 1]` range. Fuel slots default to `0` when fewer than 2 fuel items exist.

---

## Action Space

| Action | Meaning |
|--------|---------|
| 0 | No-op (stay) |
| 1 | Move up |
| 2 | Move down |
| 3 | Move right |
| 4 | Move left |
| 5 | Shoot |

---

## Reward Logic (`Environment.move`)

Rewards are computed **per step** inside `move(action)`. The hole center is calculated as the midpoint between the bottom building top edge and the top building bottom edge.

### Terminal (episode ends)

| Event | Reward | Constant |
|-------|--------|----------|
| Collision with building/enemy **or** fuel reaches 0% | **−1.0** | `DIE_REWARD` |

### Per-Step Shaping

| Event | Reward | Constant |
|-------|--------|----------|
| Survival (every step) | **+0.01** | `SURVIVAL_REWARD` |
| Pass through a hole (all buildings cleared) | **+0.5** | `THROUGH_HOLE_REWARD` |
| Kill an enemy (bullet hits) | **+0.1** | `ENEMY_REWARD` |
| Pick up fuel item | **+0.1** | `PICKUP_REWARD` |
| Shoot (action 5) | **−0.02** | `SHOOT_REWARD` |

### Directional Distance Shaping (relative to hole center)

The agent is rewarded/penalized based on whether its movement direction aligns with moving toward the hole center:

| Condition | Action Taken | Reward |
|-----------|-------------|--------|
| Within ±10 px of hole center | Up (1) or Down (2) | **−0.3** (unnecessary movement) |
| Hole is **below** player (δ > 10) | Down (2) — correct | **+0.3** |
| Hole is **below** player (δ > 10) | Up (1) — wrong | **−0.3** |
| Hole is **below** player (δ > 10) | Other | **−0.15** |
| Hole is **above** player (δ < −10) | Up (1) — correct | **+0.3** |
| Hole is **above** player (δ < −10) | Down (2) — wrong | **−0.3** |
| Hole is **above** player (δ < −10) | Other | **−0.15** |

### Edge Penalty

| Condition | Reward | Constant |
|-----------|--------|----------|
| Player X within 500 px of right screen edge **and** action is Move Right (3) | **−0.5** | `EDGE_TOO_CLOSE_PENALTY` |

---

## DQN Loss

Standard DQN temporal-difference target with `γ = 0.99`:

$$Q_{\text{target}} = r + \gamma \cdot Q_{\hat{\theta}}(s', \arg\max_{a'} Q) \cdot (1 - \text{done})$$

Loss: **MSE** between predicted Q-values and targets.

Target network is updated via **soft update** with `τ = 0.001`.
