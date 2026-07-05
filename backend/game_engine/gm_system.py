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

    def _get_character_from_text(self, text):
        text_lower = text.lower()
        best = None
        for c in self.characters:
            if c.name.lower() in text_lower:
                best = c
                break
        return best

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
            result["current_character"] = character.name
            return result

        node_data = ADVENTURE_NODES.get(node_key)
        if not node_data:
            return self._fallback_response()

        if node_data.get("type") == "combat" and node_data.get("enemies"):
            self._start_combat(node_data["enemies"])
            result = self._node_response(node_data)
            state = self.get_state()
            result.update(self._state_to_response(state))
            result["current_character"] = character.name
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
                    self._start_combat(new_node["enemies"])
                result = self._node_response(new_node)
                state = self.get_state()
                result.update(self._state_to_response(state))
                result["current_character"] = character.name
                return result

        result = self._node_response(node_data)
        state = self.get_state()
        result.update(self._state_to_response(state))
        result["current_character"] = character.name
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

        result = None
        if parsed["intent"] in ("attack", "spell"):
            target = None
            if parsed["target"]:
                target = next((c for c in alive_enemies if parsed["target"] in c.name.lower()), None)
            if not target:
                target = alive_enemies[0]
            result = engine.player_attack(character.name, target.name)
            if "error" in result:
                return {"narrative": result["error"], "audio_text": result["error"]}
            result = {
                "narrative": result["message"],
                "audio_text": result["message"],
                "roll": result["roll"],
                "success": result["hit"],
                "combat_result": result
            }

        elif parsed["intent"] == "defend":
            if player_char:
                player_char.ac += 2
            result = {"narrative": f"{character.name} geht in Verteidigung. RK +2.", "audio_text": "In Verteidigung."}

        elif parsed["intent"] == "wait":
            result = {"narrative": f"{character.name} wartet.", "audio_text": "Warten."}

        elif parsed["intent"] == "flee":
            roll = roll_d20()
            if roll > 12:
                self.state["combat_active"] = False
                return {"narrative": "Flucht erfolgreich!", "audio_text": "Ihr flieht.", "fled": True}
            return {"narrative": "Flucht fehlgeschlagen!", "audio_text": "Der Weg ist versperrt!"}
        else:
            result = {"narrative": f"{character.name} tut nichts.", "audio_text": "Nichts."}

        remaining_players = [c for c in engine.combatants if c.is_player and c.is_alive]
        if remaining_players and all(not c.is_player or not c.is_alive for c in engine.combatants):
            pass

        engine.enemy_turn()
        alive_enemies = [c for c in engine.combatants if not c.is_player and c.is_alive]
        if not alive_enemies:
            return self._end_combat(result)
        engine.next_turn()
        result["your_turn"] = True
        result["current_character"] = character.name
        return result

    def _end_combat(self, partial=None):
        self.state["combat_active"] = False
        engine = self.state.get("combat_engine")
        base = {"narrative": "Kampf beendet!", "audio_text": "Kampf beendet!", "combat_over": True}
        if partial:
            base.update(partial)
        if engine:
            for pc in engine.combatants:
                if pc.is_player:
                    char_model = next((c for c in self.characters if c.name == pc.name), None)
                    if char_model:
                        char_model.hp_current = pc.hp
            node_key = self.get_current_node_key()
            from .adventure_data import ADVENTURE_NODES
            node_data = ADVENTURE_NODES.get(node_key)
            if node_data and node_data.get("next_on_success"):
                self.state["node"] = node_data["next_on_success"]
        self.state["combat_engine"] = None
        return base

    def _start_combat(self, enemies_data):
        from .combat import Combatant, CombatEngine
        player_damage_dice = {"krieger": "1d10", "schurke": "1d8", "magier": "1d6", "kleriker": "1d6"}
        players = []
        for char_model in self.characters:
            dd = player_damage_dice.get(getattr(char_model, 'char_class', ''), "1d8")
            p = Combatant(
                char_model.name, is_player=True,
                hp=char_model.hp_current, hp_max=char_model.hp_max,
                ac=char_model.ac, attack_bonus=char_model.attack_bonus,
                damage_dice=dd, damage_bonus=char_model.damage_bonus,
                initiative_bonus=char_model.initiative_bonus
            )
            p.threat = 0
            players.append(p)
        from .bestiary import get_monster, scale_monster
        avg_level = max(c.level for c in self.characters) if self.characters else 1
        enemies = []
        for ed in enemies_data:
            template = get_monster(ed["id"])
            if template:
                scaled = scale_monster(template, avg_level)
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
        engine = CombatEngine(players, enemies)
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
