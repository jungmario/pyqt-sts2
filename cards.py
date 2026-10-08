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

    def play(self, user, target, enemies, vfx_callback = None):
        print(f"\n▶ [{self.name}] 사용! (코스트: {self.cost})")
        for effect in self.effects:
            # 💡 effect가 '구체 발현(EvokeOrbAction)' 효과일 때만 콜백을 넘겨줍니다!
            if effect.__class__.__name__ == "EvokeOrbAction":
                effect.execute(user, target, enemies, vfx_callback=vfx_callback)
            else:
                # 일반 공격/수비 카드 등은 기존대로 실행 (에러 방지)
                effect.execute(user, target, enemies)

def create_strike():
    return Card("타격", "ATTACK", 1, effects=[DamageAction(6)], requires_target=True)

def create_defend():
    return Card("수비", "SKILL", 1, effects=[BlockAction(5)], requires_target=False)

def create_zap():
    return Card("파지직", "SKILL", 1, effects=[ChannelOrbAction("전기")], requires_target=False)

def create_dualcast():
    return Card("이중시전", "SKILL", 1, effects=[EvokeOrbAction(2)], requires_target=False)