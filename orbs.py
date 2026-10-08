import random

class LightningOrb:
    def __init__(self):
        self.name = "전기"

    # 리스트 안에서 출력될 때 보여줄 모습을 정의하는 파이썬 특수 메서드
    def __repr__(self):
        return f"'{self.name}'"

    def passive(self, user, enemies, vfx_callback=None):
        # 지속 효과(턴 종료 시): 무작위 적에게 3 + 밀집 데미지
        if not enemies: return
        target = random.choice(enemies) # 적 리스트 중 1명 무작위 선택
        damage = 3 + user.focus
        
        print(f" ⚡ [전기 구체 지속효과] {target.name}에게 {damage}의 피해!")
        target.take_damage(damage)

        if vfx_callback:
            vfx_callback(enemies.index(target))

    def evoke(self, user, enemies, vfx_callback=None):
        # 발현 효과: 무작위 적에게 8 + 밀집 데미지
        if not enemies: return
        target = random.choice(enemies)
        damage = 8 + user.focus
        
        print(f" 💥 [전기 구체 발현] {target.name}에게 {damage}의 폭발 피해!")
        target.take_damage(damage)

        if vfx_callback:
            vfx_callback(enemies.index(target))