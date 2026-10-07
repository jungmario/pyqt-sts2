class Entity:
    def __init__(self, name, max_hp):
        self.name = name
        self.max_hp = max_hp
        self.hp = max_hp
        self.block = 0

        self.strength = 0
        self.dexterity = 0

        self.weak = 0
        self.vulnerable = 0
        self.frail = 0
        self.weak_rate = 0.75
        self.vulnerable_rate = 1.25
        self.frail_rate = 0.75

    def calculate_damage_output(self, amount):
        damage = self.strength + amount
        return damage if not self.weak else self.weak_rate * damage

    def calculate_block_output(self, amount):
        block = self.dexterity + amount
        return block if not self.frail else self.frail_rate * block

    def gain_block(self, amount):
        self.block += amount
        print(f" {self.name}이(가) {self.block}의 방어를 얻음 (현재 방어도: {self.block})")

    def take_damage(self, amount):
        amount = amount if not self.vulnerable else self.vulnerable_rate * amount

        if self.block >= amount:
            self.block -= amount
            print(f" 🛡️ {self.name}의 방어도가 피해를 모두 흡수! (남은 방어도: {self.block})")
        else:
            actual_damage = amount - self.block
            self.block = 0
            self.hp -= actual_damage
            print(f" 🩸 {self.name}이(가) {actual_damage}의 피해를 입음! (남은 체력: {self.hp}/{self.max_hp})")


class Player(Entity):
    def __init__(self, name, max_hp, max_mana):
        super().__init__(name, max_hp)
        self.max_mana = max_mana
        self.mana = max_mana
        self.orbs = []

class Enemy(Entity):
    def __init__(self, name, max_hp):
        super().__init__(name, max_hp)