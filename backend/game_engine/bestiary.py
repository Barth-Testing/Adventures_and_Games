MONSTER_TEMPLATES = {
    "goblin": {
        "name": "Goblin",
        "level": 3,
        "monster_type": "humanoid",
        "rank": "normal",
        "hp": 20,
        "ac": 13,
        "attack_bonus": 4,
        "damage_dice": "1d6",
        "damage_bonus": 2,
        "damage_type": "physical_slash",
        "xp_reward": 25,
        "special_abilities": "Rudelangriff: +1 Angriff pro Goblin im Nahkampf",
        "weaknesses": "Feuerschaden +50%",
        "resistances": ""
    },
    "ork": {
        "name": "Ork-Krieger",
        "level": 5,
        "monster_type": "humanoid",
        "rank": "elite",
        "hp": 45,
        "ac": 16,
        "attack_bonus": 7,
        "damage_dice": "2d8",
        "damage_bonus": 4,
        "damage_type": "physical_slash",
        "xp_reward": 100,
        "special_abilities": "Kampfrausch: Bei <50% LP +50% Schaden, -25% RK",
        "weaknesses": "Blitzschaden +25%",
        "resistances": "Physisch -25%"
    },
    "spinnenkrabbe": {
        "name": "Spinnenkrabbe",
        "level": 3,
        "monster_type": "beast",
        "rank": "normal",
        "hp": 30,
        "ac": 14,
        "attack_bonus": 5,
        "damage_dice": "1d8",
        "damage_bonus": 2,
        "damage_type": "physical_blunt",
        "xp_reward": 40,
        "special_abilities": "Netzschuss: 1W20+5 gegen RK, bei Treffer gefesselt 1 Runde",
        "weaknesses": "Blitzschaden +50%",
        "resistances": ""
    },
    "schattenkreatur": {
        "name": "Schattenkreatur",
        "level": 5,
        "monster_type": "undead",
        "rank": "normal",
        "hp": 40,
        "ac": 15,
        "attack_bonus": 6,
        "damage_dice": "2d6",
        "damage_bonus": 3,
        "damage_type": "cold",
        "xp_reward": 65,
        "special_abilities": "Unsichtbar in Dunkelheit: +5 Ausweichen im Schatten. Stärkenraub: Senkt STR um 1W4",
        "weaknesses": "Heilig-Schaden +100%",
        "resistances": "Physisch -50%"
    },
    "grosse_schattenkreatur": {
        "name": "Große Schattenkreatur",
        "level": 7,
        "monster_type": "undead",
        "rank": "boss",
        "hp": 80,
        "ac": 17,
        "attack_bonus": 8,
        "damage_dice": "3d6",
        "damage_bonus": 5,
        "damage_type": "cold",
        "xp_reward": 200,
        "special_abilities": "Phasenverschiebung: Ignoriert 25% Schaden. Stärkenraub: Senkt STR um 1W6. Schattenexplosion: 2W8 Schaden (Radius 4m) bei Tod",
        "weaknesses": "Heilig-Schaden +100%, Lichtquellen schwächen (-50% Ausweichen)",
        "resistances": "Physisch -50%, Arkan -33%"
    },
    "trollkoenig": {
        "name": "Trollkönig",
        "level": 8,
        "monster_type": "giant",
        "rank": "boss",
        "hp": 170,
        "ac": 16,
        "attack_bonus": 9,
        "damage_dice": "3d10",
        "damage_bonus": 6,
        "damage_type": "physical_blunt",
        "xp_reward": 500,
        "special_abilities": "Regeneration: Stellt 20 LP/Runde her. Nur Feuer stoppt Regeneration 2 Runden. Wütender Schlag bei <30% LP: +100% Schaden",
        "weaknesses": "Feuerschaden +100% (stoppt Regeneration)",
        "resistances": "Physisch -33%, Kälte -50%"
    },
    "skelett": {
        "name": "Skelett",
        "level": 3,
        "monster_type": "undead",
        "rank": "normal",
        "hp": 22,
        "ac": 13,
        "attack_bonus": 4,
        "damage_dice": "1d6",
        "damage_bonus": 2,
        "damage_type": "physical_slash",
        "xp_reward": 35,
        "special_abilities": "Knochenpanzer: -5% erlittener physischer Schaden",
        "weaknesses": "Heilig-Schaden +100%, Wucht-Schaden +50%",
        "resistances": "Gift immun, Kälte -50%"
    }
}

def get_monster(monster_id):
    template = MONSTER_TEMPLATES.get(monster_id)
    if not template:
        return None
    return dict(template)

def get_monster_by_name(name):
    for mid, template in MONSTER_TEMPLATES.items():
        if template["name"].lower() == name.lower():
            return dict(template)
    return None

def scale_monster(monster, party_level):
    scaled = dict(monster)
    level_diff = party_level - scaled["level"]
    hp_scale = min(0, level_diff) * 5 if level_diff < 0 else level_diff * 10
    scaled["hp"] = max(8, scaled["hp"] + hp_scale)
    scaled["ac"] = max(8, min(20, scaled["ac"] + level_diff))
    scaled["attack_bonus"] = max(1, scaled["attack_bonus"] + level_diff)
    scaled["damage_bonus"] = max(0, scaled["damage_bonus"] + level_diff // 2)
    scaled["level"] = party_level
    return scaled
