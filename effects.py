from orbs import LightningOrb

class Effect:
    def execute(self, user, target):
        pass
    def get_desc(self):
        return ""

class DamageAction(Effect):
    def __init__(self, amount):
        self.amount = amount
    def get_desc(self):
        return f"피해를 {self.amount} 줍니다."
    def execute(self, user, target, enemies):
        final_damage = user.calculate_damage_output(self.amount)
        target.take_damage(final_damage)

class BlockAction(Effect):
    def __init__(self, amount):
        self.amount = amount
    def get_desc(self):
        return f"방어도를 {self.amount} 얻습니다."
    def execute(self, user, target, enemies):
        final_block = user.calculate_block_output(self.amount)
        user.gain_block(final_block)

class ChannelOrbAction(Effect):
    def __init__(self, orb_type):
        self.orb_type = orb_type
        
    def get_desc(self):
        return f"{self.orb_type} 구체를 1개 영창합니다."
    
    def execute(self, user, target, enemies):
        new_orb = None
        if self.orb_type == '전기':
            new_orb = LightningOrb()

        if new_orb:
            user.orbs.append(new_orb)
            print(f" 🔮 {user.name}이(가) [{new_orb.name} 구체] 영창!")

        if len(user.orbs) > user.max_orbs:
            evoked_orb = user.orbs.pop(0)
            print(" ⚠️ 구체 슬롯 초과! 가장 앞의 구체가 밀려나며 발현됩니다.")
            # 임시로 현재 타겟을 리스트 형태로 묶어서 넘깁니다 (나중엔 모든 적 리스트를 전달)
            evoked_orb.evoke(user, enemies)
        
        print(f" ⚡ {user.name}이(가) [{self.orb_type} 구체] 영창! (현재 구체: {user.orbs})")

class EvokeOrbAction(Effect):
    def __init__(self, times=1):
        self.times = times
    def get_desc(self):
        return f"가장 앞의 구체를 {self.times}번 발현합니다."
    def execute(self, user, target, enemies, vfx_callback=None):
        if user.orbs:
            orb = user.orbs.pop(0)
            for i in range(self.times):
                print(f" 💥 가장 앞의 [{orb} 구체] 발현!")
                orb.evoke(user, enemies, vfx_callback = vfx_callback)
            print(f"현재 남은 구체 : {user.orbs}")
            
        else:
            print(" 텅 빈 구체 슬롯! 발현할 구체가 없습니다.")