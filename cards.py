from effects import DamageAction, BlockAction, ChannelOrbAction, EvokeOrbAction

class Card:
    def __init__(self, name, card_type, cost, effects = None, requires_target = True):
        self.name = name
        self.type = card_type
        self.cost = cost
        self.effects = effects
        self.requires_target = requires_target

    def get_description(self):
        desc_list = [effect.get_desc() for effect in self.effects]
        return "\n".join(desc_list)

    def play(self, user, target, enemies):
        print(f"\n▶ [{self.name}] 사용! (코스트: {self.cost})")
        for effect in self.effects:
            effect.execute(user, target, enemies)

def create_strike():
    return Card("타격", "ATTACK", 1, effects=[DamageAction(6)], requires_target=True)

def create_defend():
    return Card("수비", "SKILL", 1, effects=[BlockAction(5)], requires_target=False)

def create_zap():
    return Card("파지직", "SKILL", 1, effects=[ChannelOrbAction("전기")], requires_target=False)

def create_dualcast():
    return Card("이중시전", "SKILL", 1, effects=[EvokeOrbAction(2)], requires_target=False)