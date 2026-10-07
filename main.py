import copy

# 1. 효과(Action) 블록의 청사진
class Effect:
    def execute(self, user, target):
        pass
    def get_desc(self):
        return ""

# 2. 디펙트에게 필요한 4가지 개별 효과 블록
class DamageAction(Effect):
    def __init__(self, amount):
        self.amount = amount
        
    def get_desc(self):
        return f"피해를 {self.amount} 줍니다."

class BlockAction(Effect):
    def __init__(self, amount):
        self.amount = amount
        
    def get_desc(self):
        return f"방어도를 {self.amount} 얻습니다."

class ChannelOrbAction(Effect):
    def __init__(self, orb_type):
        self.orb_type = orb_type # "전기", "냉기" 등
        
    def get_desc(self):
        return f"{self.orb_type} 구체를 1개 영창합니다."

class EvokeOrbAction(Effect):
    def __init__(self, times=1):
        self.times = times
        
    def get_desc(self):
        return f"가장 앞의 구체를 {self.times}번 발현합니다."

# 3. 레고 판(Card) 정의
class Card:
    def __init__(self, name, card_type, cost, effects):
        self.name = name
        self.type = card_type
        self.cost = cost
        self.effects = effects

    def get_description(self):
        desc_list = [effect.get_desc() for effect in self.effects]
        return "\n".join(desc_list)

# 4. 카드 공장 (인스턴스를 각각 독립적으로 찍어내기 위함)
# 슬더스에서는 전투 중 개별 카드의 코스트나 데미지가 바뀔 수 있으므로 
# 같은 카드라도 참조를 공유하지 않고 메모리에 각각 독립적으로 생성해야 합니다.
def create_strike():
    return Card("타격", "ATTACK", 1, effects=[DamageAction(6)])

def create_defend():
    return Card("수비", "SKILL", 1, effects=[BlockAction(5)])

def create_zap():
    return Card("파지직", "SKILL", 1, effects=[ChannelOrbAction("전기")])

def create_dualcast():
    return Card("이중시전", "SKILL", 1, effects=[EvokeOrbAction(2)])

# 5. 디펙트 시작 덱 조립 (타격 4장, 수비 4장, 파지직 1장, 이중시전 1장)
my_deck = []
for _ in range(4): my_deck.append(create_strike())
for _ in range(4): my_deck.append(create_defend())
my_deck.append(create_zap())
my_deck.append(create_dualcast())

# 6. 결과 확인 (디버깅)
print("--- 디펙트 시작 덱 (총 10장) ---\n")
for i, card in enumerate(my_deck, 1):
    print(f"{i}. [{card.name}] (비용: {card.cost})")
    print(f"   효과: {card.get_description()}")
    print("-" * 30)