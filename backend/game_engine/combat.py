from .dice import roll_d20, roll_dice

class Combatant:
    def __init__(self, name, is_player=False, **stats):
        self.name = name
        self.is_player = is_player
        self.hp = stats.get("hp", 30)
        self.hp_max = stats.get("hp_max", stats.get("hp", 30))
        self.ac = stats.get("ac", 12)
        self.attack_bonus = stats.get("attack_bonus", 3)
        self.damage_dice = stats.get("damage_dice", "1d6")
        self.damage_bonus = stats.get("damage_bonus", 0)
        self.damage_type = stats.get("damage_type", "physical")
        self.initiative_bonus = stats.get("initiative_bonus", 0)
        self.initiative = 0
        self.threat = 0
        self.is_alive = True
        self.conditions = []
        self.special_abilities = stats.get("special_abilities", "")
        self.weaknesses = stats.get("weaknesses", "")
        self.resistances = stats.get("resistances", "")
        self.xp_reward = stats.get("xp_reward", 0)

    def roll_initiative(self):
        self.initiative = roll_d20() + self.initiative_bonus
        return self.initiative

    def take_damage(self, amount, dmg_type="physical"):
        if self.resistances:
            for res in self.resistances.split(","):
                res = res.strip().lower()
                if dmg_type in res or "physisch" in res:
                    if "-50%" in res or "-33%" in res:
                        amount = int(amount * 0.67)
                    elif "-25%" in res:
                        amount = int(amount * 0.75)
        if self.weaknesses:
            for weak in self.weaknesses.split(","):
                weak = weak.strip().lower()
                if dmg_type in weak or "+100%" in weak and dmg_type in weak:
                    amount *= 2
                elif "+50%" in weak and dmg_type in weak:
                    amount = int(amount * 1.5)
                elif "+25%" in weak and dmg_type in weak:
                    amount = int(amount * 1.25)
        self.hp = max(0, self.hp - amount)
        if self.hp <= 0:
            self.is_alive = False
        return amount

    def attack(self, target):
        roll = roll_d20()
        if roll == 1:
            return {"hit": False, "critical": False, "roll": 1, "total": 1, "damage": 0, "message": "Kritischer Fehlschlag!"}
        total = roll + self.attack_bonus
        is_critical = roll == 20
        if total >= target.ac or is_critical:
            dmg_total, dmg_rolls = roll_dice(self.damage_dice)
            if is_critical:
                dmg_total, _ = roll_dice(f"2{self.damage_dice[1:]}")
            dmg_total += self.damage_bonus
            actual_damage = target.take_damage(dmg_total, self.damage_type)
            hit_type = "kritisch" if is_critical else "normal"
            return {
                "hit": True,
                "critical": is_critical,
                "roll": roll,
                "total": total,
                "damage": actual_damage,
                "dmg_rolls": dmg_rolls,
                "hit_type": hit_type,
                "target": target.name,
                "message": f"{hit_type.upper()}! {actual_damage} Schaden an {target.name}"
            }
        return {
            "hit": False,
            "critical": False,
            "roll": roll,
            "total": total,
            "damage": 0,
            "message": f"Verfehlt! {total} vs RK {target.ac}"
        }

    def to_dict(self):
        return {
            "name": self.name,
            "is_player": self.is_player,
            "hp": self.hp,
            "hp_max": self.hp_max,
            "ac": self.ac,
            "initiative": self.initiative,
            "is_alive": self.is_alive,
            "conditions": self.conditions,
            "threat": self.threat
        }

class CombatEngine:
    def __init__(self, players, enemies):
        self.combatants = players + enemies
        self.round = 1
        self.turn_index = 0
        self.is_active = False
        self.log = []

    def start_combat(self):
        for c in self.combatants:
            c.roll_initiative()
        self.combatants.sort(key=lambda c: c.initiative, reverse=True)
        self.is_active = True
        self.turn_index = 0
        self.log.append("Kampf beginnt!")
        order = " -> ".join([f"{c.name} (INI:{c.initiative})" for c in self.combatants])
        self.log.append(f"Initiative: {order}")

    def current_turn(self):
        if not self.combatants:
            return None
        return self.combatants[self.turn_index] if self.turn_index < len(self.combatants) else None

    def next_turn(self):
        self.turn_index += 1
        alive = [c for c in self.combatants if c.is_alive]
        if not alive:
            self.is_active = False
            return None
        if self.turn_index >= len(self.combatants):
            self.turn_index = 0
            self.round += 1
            self.log.append(f"--- Runde {self.round} ---")
        current = self.current_turn()
        while current and not current.is_alive:
            self.turn_index += 1
            if self.turn_index >= len(self.combatants):
                self.turn_index = 0
                self.round += 1
                self.log.append(f"--- Runde {self.round} ---")
            current = self.current_turn()
        return current

    def player_attack(self, player_name, target_name):
        player = next((c for c in self.combatants if c.is_player and c.name == player_name and c.is_alive), None)
        target = next((c for c in self.combatants if not c.is_player and c.name.lower() == target_name.lower() and c.is_alive), None)
        if not player:
            return {"error": f"{player_name} kann nicht angreifen"}
        if not target:
            return {"error": f"{target_name} nicht gefunden oder bereits besiegt"}
        result = player.attack(target)
        player.threat += result["damage"]
        self.log.append(f"{player.name} greift {target.name} an: {result['message']}")
        if not target.is_alive:
            self.log.append(f"{target.name} wurde besiegt!")
        return result

    def enemy_turn(self):
        current = self.current_turn()
        if not current or current.is_player or not current.is_alive:
            return None
        valid_targets = [c for c in self.combatants if c.is_player and c.is_alive]
        if not valid_targets:
            return None
        valid_targets.sort(key=lambda c: c.threat, reverse=True)
        target = valid_targets[0]
        result = current.attack(target)
        self.log.append(f"{current.name} greift {target.name} an: {result['message']}")
        if not target.is_alive:
            self.log.append(f"{target.name} wurde besiegt!")
        return result

    def get_state(self):
        return {
            "round": self.round,
            "turn_index": self.turn_index,
            "is_active": self.is_active,
            "combatants": [c.to_dict() for c in self.combatants if c.is_alive],
            "all_combatants": [c.to_dict() for c in self.combatants],
            "current_turn": self.current_turn().name if self.current_turn() else None,
            "log": self.log[-20:]
        }
