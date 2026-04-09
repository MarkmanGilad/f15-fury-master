# Training Process Summary — F15 Fury DQN

## Network Architecture

**Model:** `DQN` — a 4-layer fully-connected network.

```
Input (13) → Linear(64) → LeakyReLU → Linear(128) → LeakyReLU → Linear(64) → LeakyReLU → Linear(6)
```

| Layer | In | Out | Activation |
|-------|----|-----|------------|
| linear1 | 13 | 64 | LeakyReLU |
| linear2 | 64 | 128 | LeakyReLU |
| linear3 | 128 | 64 | LeakyReLU |
| output | 64 | 6 | None (raw Q-values) |

Output: 6 Q-values, one per action (no-op, up, down, right, left, shoot).

---

## Algorithm: Double DQN (DDQN)

Two networks are used:

| Network | Role |
|---------|------|
| **Policy net** (`player.DQN`) | Selects actions via ε-greedy; used for gradient updates |
| **Target net** (`player_hat.DQN`) | Evaluates Q-values for the TD target; **no gradients** |

### DDQN Update Rule

1. Sample a mini-batch from the replay buffer.
2. **Policy net** selects the best next action: $a' = \arg\max_a Q_\theta(s', a)$
3. **Target net** evaluates that action: $Q_{\hat\theta}(s', a')$
4. TD target: $y = r + \gamma \cdot Q_{\hat\theta}(s', a') \cdot (1 - \text{done})$
5. Loss: $\text{MSE}(Q_\theta(s, a),\; y)$

Target net is a **hard copy** of the policy net, updated every `C = 20` episodes (at episode boundary when `epoch % C == 0`).

---

## Primary Hyperparameters

| Parameter | Value | Constant |
|-----------|-------|----------|
| Learning rate | `0.0001` | `LEARNING_RATE` |
| Batch size | `50` | `BATCH_SIZE` |
| Discount factor (γ) | `0.99` | `GAMMA` |
| Replay buffer capacity | `100,000` | `REPLAY_BUFFER_CAPACITY` |
| Min buffer before training | `2,000` | `MIN_BUFFER_SIZE` |
| Target net update freq | Every `20` episodes | `TARGET_UPDATE_FREQ` |
| Training epochs | `100,000` | `TRAINING_EPOCHS` |
| Training FPS | `300` | `TRAINING_FPS` |
| Checkpoint save freq | Every `1,000` episodes | `SAVE_FREQUENCY` |

### Epsilon-Greedy Exploration

Linear decay from start to final over a fixed number of episodes:

| Parameter | Value |
|-----------|-------|
| ε start | `1.0` |
| ε final | `0.01` |
| Decay episodes | `100` |

$$\varepsilon = \begin{cases} 1.0 - \frac{(1.0 - 0.01) \cdot \text{epoch}}{100} & \text{if epoch} < 100 \\ 0.01 & \text{otherwise} \end{cases}$$

### Learning Rate Schedule

**MultiStepLR** — halves the LR at fixed step milestones:

| Milestones (optimizer steps) | Gamma |
|------------------------------|-------|
| 5,000,000 / 10,000,000 / 15,000,000 | `0.5` |

Note: `scheduler.step()` is called every training step (not per episode), so milestones are in raw gradient steps.

---

## Replay Buffer

Simple uniform experience replay using a `deque`.

- Stores tuples: `(state, action, reward, next_state, done)`
- Sampling: uniform random, returns stacked tensors
- Capacity: 100,000 transitions

---

## Training Loop (per step)

```
1. Render environment
2. Get state tensor (13-dim)
3. Select action via ε-greedy (policy net)
4. Execute action → get reward, done, next_state
5. Push transition to replay buffer
6. If buffer < 2,000 → skip training
7. Sample mini-batch (50)
8. Compute DDQN loss & backprop
9. Step optimizer + LR scheduler
10. On episode end every 20 ep → hard-copy policy net → target net
```

---

## Logging & Checkpointing

- **W&B** logging per episode: reward, steps, avg loss, holes passed, enemies killed, fuels collected, score, time
- **Checkpoint** saved every 1,000 episodes: model weights, optimizer state, scheduler state, epoch counter
- **Buffer** also persisted alongside the checkpoint
