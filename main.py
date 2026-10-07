from cards import create_strike, create_defend, create_zap, create_dualcast
from battle import BattleManager
from entities import Player, Enemy

def main():
    # 1. 덱 구성
    my_deck = []
    for _ in range(4): my_deck.append(create_strike())
    for _ in range(4): my_deck.append(create_defend())
    my_deck.append(create_zap())
    my_deck.append(create_dualcast())

    # 2. 엔티티 생성
    defect = Player("디펙트", max_hp=75, max_mana=3)
    jaw_worm = Enemy("턱벌레", max_hp=40)

    # 3. 전투 매니저 생성 및 전투 루프 시작!
    battle = BattleManager(my_deck)
    battle.start_combat(defect, jaw_worm)

if __name__ == "__main__":
    main()