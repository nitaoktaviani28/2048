import random
import numpy as np
from collections import deque
import tensorflow as tf
from board import Board2048, Direction
from game import Game2048
from tqdm import tqdm
from easy_logs import get_logger
import json

logger = get_logger(lvl=10)
tf.keras.utils.disable_interactive_logging()


class DQNAgent:
    def __init__(
        self,
        actions=[
            Direction.UP.value,
            Direction.DOWN.value,
            Direction.LEFT.value,
            Direction.RIGHT.value,
        ],
        memory_size=22000,
        gamma=0.95,  # discount rate
        epsilon=1.0,  # exploration rate
        epsilon_min=0.1,
        epsilon_decay=0.9997,
        learning_rate=0.001,
    ):
        self.memory = deque(maxlen=memory_size)
        self.gamma = gamma
        self.epsilon = epsilon
        self.epsilon_min = epsilon_min
        self.actions = actions
        self.epsilon_decay = epsilon_decay
        self.model = self._build_model(actions, learning_rate)
        self.target_model = self._build_model(actions, learning_rate)
        self.update_target_model()

    def _build_model(self, actions, learning_rate):
        model = tf.keras.Sequential(
            [
                tf.keras.layers.Input(shape=(4, 4, 1)),
                tf.keras.layers.Flatten(),
                tf.keras.layers.Dense(196, activation="relu"),
                tf.keras.layers.Dense(len(actions), activation=None),
            ]
        )

        model.compile(
            loss="mse",
            optimizer=tf.keras.optimizers.Adam(learning_rate=learning_rate),
        )

        return model

    def update_target_model(self):
        self.target_model.set_weights(self.model.get_weights())

    def update_memory(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))

    def do_action(self, state) -> int:
        """
        Return index of action to take
        """
        if np.random.rand() > self.epsilon:
            act_values = self.model.predict(np.expand_dims(state, axis=0))
            action_index = np.argmax(act_values[0])
        else:
            action_index = np.random.choice(len(self.actions))
        return self.actions[action_index]

    def replay(
        self,
        batch_size,
    ):
        minibatch = np.array(random.sample(self.memory, batch_size), dtype=object)
        states = np.array(minibatch[:, 0].tolist())
        actions = minibatch[:, 1].astype(int)
        rewards = minibatch[:, 2]
        next_states = np.array(minibatch[:, 3].tolist())
        dones = minibatch[:, 4]
        # convert to
        targets = self.model.predict(states)
        targets[np.arange(len(targets)), actions] = rewards + self.gamma * np.amax(
            self.target_model.predict(next_states), axis=1
        ) * (1 - dones)
        self.model.fit(
            states,
            targets,
            epochs=1,
            verbose=1,
        )
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay

    def load(self, name):
        self.model.load_weights(name)
        self.update_target_model()

    def save(self, name):
        self.target_model.save_weights(name)


if __name__ == "__main__":
    EPOCHS = 200
    UPDATE_TARGET_FREQ = 5
    BATCH_SIZE = 256
    history = {}
    board = Board2048()
    agent = DQNAgent()
    for e in range(EPOCHS):
        bar = tqdm(total=1000, desc=f"Epoch {e}", position=0)
        state = board.reset()
        frame = 0
        while not board.is_game_over:
            frame += 1
            action = agent.do_action(state)
            next_state, reward, not_done = board.move(action, tf=True)
            reward = len(board.empty_cells)
            done = not not_done
            agent.update_memory(state, action, reward, next_state, done)
            state = next_state
            bar.update(1)
            bar.set_postfix(score=reward)
            bar.set_description(
                f"Epoch {e} score: {board.score} frame: {frame} e:  {agent.epsilon:.2f}, a: {action} mem: {len(agent.memory)}"
            )
            if len(agent.memory) > BATCH_SIZE * 22 and frame % 2 == 0:
                agent.replay(BATCH_SIZE)
            if e % UPDATE_TARGET_FREQ == 0:
                agent.update_target_model()
        history[e] = board.score
        bar.close()

    with open("history.json", "w") as f:
        json.dump(history, f)

    # save model
    agent.save("model.h5")
