from sqlalchemy import Column, Integer, String, Boolean, Text, ForeignKey, DateTime, Float
from sqlalchemy.orm import relationship
from .database import Base
from datetime import datetime, timezone

class Account(Base):
    __tablename__ = "accounts"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True)
    password_hash = Column(String(255))
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    last_login = Column(DateTime, nullable=True)
    legacy_glory = Column(Integer, default=0)
    characters = relationship("Character", back_populates="account")

class Character(Base):
    __tablename__ = "characters"
    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("accounts.id"))
    name = Column(String(50))
    char_class = Column(String(20))
    race = Column(String(20))
    level = Column(Integer, default=1)
    xp = Column(Integer, default=0)
    xp_to_next = Column(Integer, default=300)
    hp_current = Column(Integer, default=30)
    hp_max = Column(Integer, default=30)
    mp_current = Column(Integer, default=20)
    mp_max = Column(Integer, default=20)
    ac = Column(Integer, default=12)
    strength = Column(Integer, default=10)
    dexterity = Column(Integer, default=10)
    constitution = Column(Integer, default=10)
    intelligence = Column(Integer, default=10)
    wisdom = Column(Integer, default=10)
    charisma = Column(Integer, default=10)
    gold = Column(Integer, default=0)
    is_hardcore = Column(Boolean, default=False)
    is_dead = Column(Boolean, default=False)
    current_area = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    account = relationship("Account", back_populates="characters")

    @property
    def attack_bonus(self):
        if self.char_class == "krieger":
            return 3 + (self.strength - 10) // 2 + self.level // 4
        elif self.char_class == "schurke":
            return 3 + (self.dexterity - 10) // 2 + self.level // 4
        elif self.char_class == "magier":
            return 2 + (self.intelligence - 10) // 2 + self.level // 4
        elif self.char_class == "kleriker":
            return 2 + (self.wisdom - 10) // 2 + self.level // 4
        return 2 + self.level // 4

    @property
    def damage_bonus(self):
        if self.char_class == "krieger":
            return (self.strength - 10) // 2
        elif self.char_class == "schurke":
            return (self.dexterity - 10) // 2
        elif self.char_class == "magier":
            return (self.intelligence - 10) // 2
        elif self.char_class == "kleriker":
            return (self.wisdom - 10) // 2
        return 0

    @property
    def initiative_bonus(self):
        return (self.dexterity - 10) // 2 + self.level // 10

    @property
    def spell_save_dc(self):
        primary = max(self.intelligence, self.wisdom, self.charisma)
        return 8 + (primary - 10) // 2 + self.level // 4

    def take_damage(self, amount):
        self.hp_current = max(0, self.hp_current - amount)

    def heal(self, amount):
        self.hp_current = min(self.hp_max, self.hp_current + amount)

    def is_alive(self):
        return self.hp_current > 0

    def add_xp(self, amount):
        self.xp += amount
        while self.xp >= self.xp_to_next:
            self.xp -= self.xp_to_next
            self.level += 1
            self.xp_to_next = int(self.xp_to_next * 1.5)
            self.hp_max += 5 + (self.constitution - 10) // 2
            self.hp_current = self.hp_max
            self.mp_max += 3 + (self.intelligence - 10) // 2
            self.mp_current = self.mp_max
            self.ac += 1 if self.level % 4 == 0 else 0

class InventoryItem(Base):
    __tablename__ = "inventory"
    id = Column(Integer, primary_key=True, index=True)
    character_id = Column(Integer, ForeignKey("characters.id"))
    item_name = Column(String(100))
    item_type = Column(String(20))
    quantity = Column(Integer, default=1)
    is_equipped = Column(Boolean, default=False)
    slot = Column(String(20), nullable=True)
    rarity = Column(String(20), default="common")
    modifiers = Column(Text, nullable=True)

class MonsterTemplate(Base):
    __tablename__ = "monster_templates"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))
    level = Column(Integer)
    monster_type = Column(String(30))
    rank = Column(String(20), default="normal")
    hp_min = Column(Integer)
    hp_max = Column(Integer)
    hp = Column(Integer)
    ac = Column(Integer)
    attack_bonus = Column(Integer)
    damage_dice = Column(String(10))
    damage_bonus = Column(Integer)
    damage_type = Column(String(20), default="physical")
    xp_reward = Column(Integer)
    special_abilities = Column(Text, nullable=True)
    weaknesses = Column(Text, nullable=True)
    resistances = Column(Text, nullable=True)
