import random
import re

DICE_PATTERN = re.compile(r"(\d*)d(\d+)(?:\s*\+\s*(\d+))?", re.IGNORECASE)

def roll_dice(dice_str):
    match = DICE_PATTERN.match(dice_str.strip())
    if not match:
        return 0, 0
    count = int(match.group(1)) if match.group(1) else 1
    sides = int(match.group(2))
    bonus = int(match.group(3)) if match.group(3) else 0
    rolls = [random.randint(1, sides) for _ in range(count)]
    total = sum(rolls) + bonus
    return total, rolls

def roll_d20():
    return random.randint(1, 20)

def roll_d(sides):
    return random.randint(1, sides)

def roll_with_advantage():
    r1, r2 = roll_d20(), roll_d20()
    return max(r1, r2), (r1, r2, "advantage")

def roll_with_disadvantage():
    r1, r2 = roll_d20(), roll_d20()
    return min(r1, r2), (r1, r2, "disadvantage")

def damage_dice_to_range(dice_str):
    match = DICE_PATTERN.match(dice_str.strip())
    if not match:
        return (0, 0)
    count = int(match.group(1)) if match.group(1) else 1
    sides = int(match.group(2))
    bonus = int(match.group(3)) if match.group(3) else 0
    return (count * 1 + bonus, count * sides + bonus)
