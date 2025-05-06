import tkinter as tk
from tkinter import messagebox
import random
import pickle
import os

ACTIONS = ['attack', 'heal'] 

class Beast:
    def __init__(self, name, health=100, attack=20, defense=5):
        self.name = name
        self.max_health = health
        self.health = health
        self.attack = attack
        self.defense = defense

    def is_alive(self):
        return self.health > 0

    def deal_damage(self):
        return random.randint(self.attack - 2, self.attack + 2)

    def take_damage(self, damage):
        reduced = max(damage - self.defense, 0)
        self.health = max(0, self.health - reduced)
        return reduced

    def heal(self):
        heal_amt = int(self.max_health * 0.2)
        self.health = min(self.max_health, self.health + heal_amt)
        return heal_amt

    def reset(self):
        self.health = self.max_health

class QLearningAgent:
    def __init__(self):
        self.q_table = {}
        self.alpha = 0.1
        self.gamma = 0.9
        self.epsilon = 0.0

    def get_state_key(self, agent_hp, enemy_hp):
        return (round(agent_hp, -1), round(enemy_hp, -1))

    def best_action(self, state):
        q_vals = [self.q_table.get((state, a), 0.0) for a in ACTIONS]
        max_q = max(q_vals)
        return ACTIONS[q_vals.index(max_q)]

def load_trained_agent(path='battlebeast_q_agent.pkl'):
    if os.path.exists(path):
        with open(path, "rb") as f:
            agent = pickle.load(f)
            agent.epsilon = 0.0  # no exploration
            return agent
    else:
        messagebox.showerror("Error", "Trained AI not found. Train first using CLI version.")
        exit()

class BattleGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("BattleBeast AI")
        self.player = Beast("You")
        self.ai = Beast("AI")
        self.agent = load_trained_agent()

        self.log_text = tk.Text(root, height=10, width=50, state=tk.DISABLED)
        self.log_text.pack(pady=5)

        self.status = tk.Label(root, text="", font=('Helvetica', 12))
        self.status.pack()

        self.hp_labels = tk.Label(root, text="", font=("Helvetica", 14))
        self.hp_labels.pack(pady=5)

        self.attack_button = tk.Button(root, text="Attack", command=self.player_attack)
        self.heal_button = tk.Button(root, text="Heal", command=self.player_heal)
        self.attack_button.pack(side=tk.LEFT, padx=20, pady=10)
        self.heal_button.pack(side=tk.RIGHT, padx=20)

        self.update_ui()

    def log(self, message):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.config(state=tk.DISABLED)
        self.log_text.yview(tk.END)

    def update_ui(self):
        self.hp_labels.config(text=f"Your HP: {self.player.health} | AI HP: {self.ai.health}")
        if not self.player.is_alive():
            self.status.config(text="You lost! 😢")
            self.attack_button.config(state=tk.DISABLED)
            self.heal_button.config(state=tk.DISABLED)
        elif not self.ai.is_alive():
            self.status.config(text="You won! 🏆")
            self.attack_button.config(state=tk.DISABLED)
            self.heal_button.config(state=tk.DISABLED)

    def player_attack(self):
        dmg = self.player.deal_damage()
        self.ai.take_damage(dmg)
        self.log(f"You attacked for {dmg} damage.")
        self.check_end()
        if self.ai.is_alive():
            self.root.after(1000, self.ai_turn)

    def player_heal(self):
        healed = self.player.heal()
        self.log(f"You healed for {healed} HP.")
        self.check_end()
        if self.ai.is_alive():
            self.root.after(1000, self.ai_turn)

    def ai_turn(self):
        state = self.agent.get_state_key(self.ai.health, self.player.health)
        action = self.agent.best_action(state)
        if action == 'attack':
            dmg = self.ai.deal_damage()
            self.player.take_damage(dmg)
            self.log(f"AI attacked for {dmg} damage.")
        elif action == 'heal':
            healed = self.ai.heal()
            self.log(f"AI healed for {healed} HP.")
        self.check_end()

    def check_end(self):
        self.update_ui()

def main():
    root = tk.Tk()
    app = BattleGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
