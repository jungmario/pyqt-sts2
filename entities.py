from orbs import LightningOrb

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

    def start_of_combat(self):
        self.block = 0
        self.mana = self.max_mana

    def start_of_turn(self):
        self.block = 0
        self.mana = self.max_mana

# Player를 상속받는 디펙트 전용 클래스
class Defect(Player):
    def __init__(self, name="디펙트", max_hp=75, max_mana=3):
        # 부모(Player)의 초기화 메서드 호출
        super().__init__(name, max_hp, max_mana)
        
        # 디펙트만의 고유 특성(매니퓰레이터) 장착
        self.orbs = []
        self.max_orbs = 3
        self.focus = 0

    def start_of_combat(self):
        super().start_of_combat()
        self.orbs = []
        self.orbs.append(LightningOrb())
        print(f" 🔮 [균열된 코어] {self.name}이(가) 전투 시작과 함께 ['전기'] 구체를 영창합니다!")

    def start_of_turn(self):
        super().start_of_turn()
        print(self.orbs)

class Enemy(Entity):
    def __init__(self, name, max_hp):
        super().__init__(name, max_hp)
        self.intent_msg = ""
        self.intent_damage = 0
        self.intent_type = ""
        self.strength = 0  # 💡 힘(Strength) 스탯 추가!
        self.turn_count = 0 

    def roll_intent(self):
        pass

    def execute_intent(self, player):
        pass


class FuzzyWurmCrawler(Enemy):
    def __init__(self, name="Fuzzy Wurm Crawler", max_hp=56):
        super().__init__(name, max_hp)

    def roll_intent(self):
        self.turn_count += 1
        
        if self.turn_count == 1:
            self.intent_type = "공격"
            # 💡 수동으로 더하지 않고, 부모(Entity)의 데미지 계산기를 사용합니다!
            self.intent_damage = self.calculate_damage_output(4) 
            self.intent_msg = f"🧪 Acid Goop ({self.intent_damage} 피해)"
        else:
            cycle = (self.turn_count - 2) % 3
            if cycle == 0:
                self.intent_type = "버프"
                self.intent_damage = 0
                self.intent_msg = "💨 Inhale (힘 7 획득)"
            else:
                self.intent_type = "공격"
                self.intent_damage = self.calculate_damage_output(4)
                self.intent_msg = f"🧪 Acid Goop ({self.intent_damage} 피해)"

    def execute_intent(self, player):
        self.block = 0
        print(f"[{self.name}]의 행동: {self.intent_msg}")
        
        if self.intent_type == "공격":
            # 이미 roll_intent에서 힘이 계산된 intent_damage를 그대로 전달합니다.
            player.take_damage(self.intent_damage)
        elif self.intent_type == "버프":
            # 부모(Entity)에 이미 있는 self.strength를 바로 올려줍니다.
            self.strength += 7
            print(f" 💪 {self.name}이(가) 힘을 7 얻었습니다! (현재 힘: {self.strength})")


class Nibbit(Enemy):
    def __init__(self, name="Nibbit", max_hp=46, start_step=0):
        super().__init__(name, max_hp)
        self.start_step = start_step

    def roll_intent(self):
        self.turn_count += 1
        cycle = (self.turn_count - 1 + self.start_step) % 3
        
        if cycle == 0:
            self.intent_type = "공격"
            # 기본 데미지 12에 부모 클래스의 계산기 적용
            self.intent_damage = self.calculate_damage_output(12)
            self.intent_msg = f"🐏 Butt ({self.intent_damage} 피해)"
        elif cycle == 1:
            self.intent_type = "공방"
            self.intent_damage = self.calculate_damage_output(6)
            self.intent_msg = f"🔪 Slice ({self.intent_damage} 피해, 5 방어도)"
        elif cycle == 2:
            self.intent_type = "버프"
            self.intent_damage = 0
            self.intent_msg = "🐍 Hiss (힘 2 획득)"

    def execute_intent(self, player):
        self.block = 0
        print(f"[{self.name}]의 행동: {self.intent_msg}")
        
        if self.intent_type == "공격":
            player.take_damage(self.intent_damage)
        elif self.intent_type == "공방":
            player.take_damage(self.intent_damage)
            # 방어도 획득도 부모의 gain_block 메서드가 있다면 그걸 써도 좋습니다!
            self.block += 5
            print(f" 🛡️ {self.name}이(가) 방어도 5를 획득했습니다!")
        elif self.intent_type == "버프":
            self.strength += 2
            print(f" 💪 {self.name}이(가) 힘을 2 얻었습니다! (현재 힘: {self.strength})")