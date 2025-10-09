# PhotosynthesisAI
An AI to play the board game Photosynthesis.

## Quickstart guide

Go to `src/psai/control/training_configs/default.json` and edit the training parameters.

Each round refers to a number of training timesteps run against fixed opponents. In the first round, the opponents are random agents that uniformly select from available actions. After that the agent is frozen at the end of a round and distributed to the other seats.

Then, run the training with:

```
brew install pipx
pipx ensurepath
pipx install poetry
cd PhotosynthesisAI
poetry run python src/psai/learn.train.py
```

This saves simple training logs in `logs/`. You can save detailed state logs with the `log_records()` method of the environment.

After running training, go to `notebooks/analysis.ipynb`. This automatically accesses the most recent logs subfolder and plots the reward curves. This also calls the visualiser to plot an animation of a game (currently this requires manually logging records with `log_records()`).