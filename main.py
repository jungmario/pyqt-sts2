from entities import Defect, FuzzyWurmCrawler, Nibbit
from battle import BattleManager
from cards import create_strike, create_defend, create_zap, create_dualcast

def main():
    # 1. 덱 구성
    my_deck = []
    for _ in range(4): my_deck.append(create_strike())
    for _ in range(4): my_deck.append(create_defend())
    my_deck.append(create_zap())
    my_deck.append(create_dualcast())

    # 2. 플레이어 생성
    defect = Defect()
    
    # 3. 💡 도감 설정대로 몬스터 소환 및 리스트 묶기
    front_nibbit = Nibbit("Nibbit(앞)", max_hp=44, start_step=1) 
    back_nibbit = Nibbit("Nibbit(뒤)", max_hp=46, start_step=2)
    crawler = FuzzyWurmCrawler("Fuzzy Wurm", max_hp=56)
    
    enemies = [front_nibbit, back_nibbit, crawler] 

    # 4. 전투 시작
    battle = BattleManager(my_deck, enemies)
    battle.start_combat(defect, enemies)

if __name__ == "__main__":
    main()