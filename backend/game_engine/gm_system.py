import re
from .dice import roll_d20

class GMSystem:
    def __init__(self, characters):
        self.characters = characters
        self.state = {
            "chapter": 1,
            "node": "1_start",
            "flags": {},
            "combat_active": False,
            "combat_engine": None,
            "logs": [],
            "narrative_history": []
        }
        self.keyword_map = {
            "angreifen": "attack", "schlagen": "attack", "attackieren": "attack",
            "zaubern": "spell", "magie": "spell",
            "gehen": "move", "laufen": "move", "rennen": "move",
            "untersuchen": "examine", "öffnen": "interact", "drücken": "interact",
            "nehmen": "take", "lesen": "examine",
            "sagen": "talk", "fragen": "talk", "reden": "talk",
            "verteidigen": "defend",
            "benutzen": "use_item", "trank": "use_item",
            "warten": "wait",
            "hilfe": "help", "hinweis": "help",
            "fliehen": "flee", "flucht": "flee"
        }

    def get_current_node_key(self):
        return self.state["node"]

    def evaluate_input(self, text):
        text_lower = text.lower().strip()
        intent = None
        target = None
        for keyword, detected_intent in self.keyword_map.items():
            if keyword in text_lower:
                intent = detected_intent
                break
        nouns = re.findall(r'\b(goblin|ork|schatten|spinnenkrabbe|skelett|troll|finnian|elara|tür|schatz|wald|brücke|wasserfall|mine|bibliothek|rätsel|mond)\b', text_lower)
        if nouns:
            target = nouns[0]
        if not intent:
            intent = "creative"
        return {"intent": intent, "target": target, "original": text}

    def _match_transition(self, user_text, transitions):
        if not transitions:
            return None
        user_lower = user_text.lower().strip()
        for pattern, target_node in transitions.items():
            if pattern.lower() in user_lower:
                return target_node
        words = user_lower.split()
        for pattern, target_node in transitions.items():
            for w in words:
                if len(w) > 2 and w in pattern.lower():
                    return target_node
        return None

    def process_action(self, character, action_text):
        parsed = self.evaluate_input(action_text)
        from .adventure_data import ADVENTURE_NODES
        node_key = self.get_current_node_key()
        node_data = ADVENTURE_NODES.get(node_key)

        if self.state["combat_active"]:
            if parsed["intent"] in ("attack", "spell", "defend", "use_item", "wait", "flee"):
                result = self._handle_combat(character, parsed)
            else:
                result = {"narrative": "Du bist im Kampf! Greife an oder verteidige dich.", "audio_text": "Im Kampf!"}
            state = self.get_state()
            result.update(self._state_to_response(state))
            return result

        node_data = ADVENTURE_NODES.get(node_key)
        if not node_data:
            return self._fallback_response()

        if node_data.get("type") == "combat" and node_data.get("enemies"):
            self._start_combat(character, node_data["enemies"])
            result = self._node_response(node_data)
            state = self.get_state()
            result.update(self._state_to_response(state))
            return result

        transitions = node_data.get("transitions", {})
        matched = self._match_transition(action_text, transitions)
        if matched:
            self.state["node"] = matched
            self.state["logs"].append(f"{character.name}: {action_text} -> {matched}")
            new_key = self.get_current_node_key()
            new_node = ADVENTURE_NODES.get(new_key)
            if new_node:
                if new_node.get("type") == "combat" and new_node.get("enemies"):
                    self._start_combat(character, new_node["enemies"])
                result = self._node_response(new_node)
                state = self.get_state()
                result.update(self._state_to_response(state))
                return result

        result = self._node_response(node_data)
        state = self.get_state()
        result.update(self._state_to_response(state))
        return result

    def _node_response(self, node_data):
        return {
            "narrative": node_data.get("narrative", ""),
            "audio_text": node_data.get("audio_text", node_data.get("narrative", "")),
            "options": node_data.get("options", []),
            "puzzle": node_data.get("puzzle"),
            "puzzle_active": bool(node_data.get("puzzle")),
            "loot": node_data.get("loot", []),
        }

    def _state_to_response(self, state):
        node_data = state.get("node_data") or {}
        return {
            "scene": node_data.get("scene", ""),
            "combat_active": state.get("combat_active", False),
            "combat_state": state.get("combat_state"),
            "adventure_complete": node_data.get("adventure_complete", False),
            "combat_start": node_data.get("type") == "combat",
        }

    def _fallback_response(self):
        return {
            "narrative": "Du stehst an einem unbekannten Ort.",
            "audio_text": "Du stehst an einem unbekannten Ort.",
            "options": ["Zurück", "Weiter"],
            "puzzle_active": False,
            "loot": []
        }

    def _handle_combat(self, character, parsed):
        engine = self.state.get("combat_engine")
        if not engine:
            return {"narrative": "Kein aktiver Kampf.", "audio_text": "Kein aktiver Kampf."}

        alive_enemies = [c for c in engine.combatants if not c.is_player and c.is_alive]
        player_char = next((c for c in engine.combatants if c.is_player and c.name == character.name), None)
        player_alive = player_char and player_char.is_alive

        if not alive_enemies:
            return self._end_combat({"narrative": "Alle Gegner besiegt!", "audio_text": "Sieg!"})

        if not player_alive:
            return {"narrative": f"{character.name} ist kampfunfähig!", "audio_text": "Ohnmächtig!", "combat_over": True}

        if parsed["intent"] in ("attack", "spell"):
            target = None
            if parsed["target"]:
                target = next((c for c in alive_enemies if parsed["target"] in c.name.lower()), None)
            if not target:
                target = alive_enemies[0]
            result = engine.player_attack(character.name, target.name)
            if "error" in result:
                return {"narrative": result["error"], "audio_text": result["error"]}
            enemy_result = engine.enemy_turn()
            d = {
                "narrative": result["message"],
                "audio_text": result["message"],
                "roll": result["roll"],
                "success": result["hit"],
                "combat_result": result
            }
            alive_enemies = [c for c in engine.combatants if not c.is_player and c.is_alive]
            if not alive_enemies:
                return self._end_combat(d)
            engine.next_turn()
            d["your_turn"] = True
            return d

        elif parsed["intent"] == "defend":
            if player_char:
                player_char.ac += 2
            engine.enemy_turn()
            d = {"narrative": f"{character.name} geht in Verteidigung. RK +2.", "audio_text": "In Verteidigung."}
            alive_enemies = [c for c in engine.combatants if not c.is_player and c.is_alive]
            if not alive_enemies:
                return self._end_combat(d)
            engine.next_turn()
            return d

        elif parsed["intent"] == "wait":
            engine.enemy_turn()
            d = {"narrative": f"{character.name} wartet.", "audio_text": "Warten."}
            alive_enemies = [c for c in engine.combatants if not c.is_player and c.is_alive]
            if not alive_enemies:
                return self._end_combat(d)
            engine.next_turn()
            return d

        elif parsed["intent"] == "flee":
            roll = roll_d20()
            if roll > 12:
                self.state["combat_active"] = False
                return {"narrative": "Flucht erfolgreich!", "audio_text": "Ihr flieht.", "fled": True}
            return {"narrative": "Flucht fehlgeschlagen!", "audio_text": "Der Weg ist versperrt!"}

        return {"narrative": f"{character.name} tut nichts.", "audio_text": "Nichts."}

    def _end_combat(self, partial=None):
        self.state["combat_active"] = False
        engine = self.state.get("combat_engine")
        base = {"narrative": "Kampf beendet!", "audio_text": "Kampf beendet!", "combat_over": True}
        if partial:
            base.update(partial)
        if engine:
            node_key = self.get_current_node_key()
            from .adventure_data import ADVENTURE_NODES
            node_data = ADVENTURE_NODES.get(node_key)
            if node_data and node_data.get("next_on_success"):
                self.state["node"] = node_data["next_on_success"]
        self.state["combat_engine"] = None
        return base

    def _start_combat(self, character, enemies_data):
        from .combat import Combatant, CombatEngine
        player_damage_dice = {"krieger": "1d10", "schurke": "1d8", "magier": "1d6", "kleriker": "1d6"}
        damage_dice = player_damage_dice.get(getattr(character, 'char_class', ''), "1d8")
        player = Combatant(
            character.name, is_player=True,
            hp=character.hp_current, hp_max=character.hp_max,
            ac=character.ac, attack_bonus=character.attack_bonus,
            damage_dice=damage_dice, damage_bonus=character.damage_bonus,
            initiative_bonus=character.initiative_bonus
        )
        from .bestiary import get_monster, scale_monster
        enemies = []
        for ed in enemies_data:
            template = get_monster(ed["id"])
            if template:
                scaled = scale_monster(template, character.level)
                for _ in range(ed.get("count", 1)):
                    name = f"{template['name']} {len(enemies)+1}" if ed.get("count", 1) > 1 else template["name"]
                    e = Combatant(name, is_player=False,
                        hp=scaled["hp"], ac=scaled["ac"],
                        attack_bonus=scaled["attack_bonus"],
                        damage_dice=scaled["damage_dice"],
                        damage_bonus=scaled["damage_bonus"],
                        damage_type=scaled["damage_type"],
                        xp_reward=scaled["xp_reward"],
                        special_abilities=scaled["special_abilities"],
                        weaknesses=scaled["weaknesses"],
                        resistances=scaled["resistances"])
                    enemies.append(e)
        engine = CombatEngine([player], enemies)
        engine.start_combat()
        self.state["combat_active"] = True
        self.state["combat_engine"] = engine

    def get_state(self):
        from .adventure_data import ADVENTURE_NODES
        node_data = ADVENTURE_NODES.get(self.state["node"])
        return {
            "node": self.state["node"],
            "node_data": node_data,
            "combat_active": self.state["combat_active"],
            "combat_state": self.state["combat_engine"].get_state() if self.state["combat_engine"] else None,
            "flags": self.state["flags"],
            "log": self.state["logs"][-10:]
        }
