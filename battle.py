import random

class BattleManager:
    def __init__(self, master_deck):
        self.draw_pile = master_deck[:] 
        self.hand = []
        self.discard_pile = []
        random.shuffle(self.draw_pile)

    def draw_card(self, amount):
        print(f"\n--- 🃏 카드 {amount}장 뽑기 시도 ---")
        for _ in range(amount):
            if len(self.draw_pile) == 0:
                if len(self.discard_pile) == 0:
                    print("뽑을 카드와 버린 카드 더미가 모두 비어있습니다!")
                    break
                print("!! 뽑을 카드 더미가 비어 버린 카드 더미를 섞습니다 !!")
                self.draw_pile = self.discard_pile[:]
                self.discard_pile.clear()
                random.shuffle(self.draw_pile)
            drawn_card = self.draw_pile.pop()
            self.hand.append(drawn_card)
            print(f"[{drawn_card.name}]을(를) 뽑았습니다.")

    def play_card(self, hand_index, player, enemy):

        if hand_index < 0 or hand_index >= len(self.hand):
            print('잘못된 카드 번호입니다.')
            return

        card = self.hand[hand_index]

        if player.mana < card.cost :
            print(f'마나가 부족합니다! (필요: {card.cost}, 현재: {player.mana})')
            return

        played_card = self.hand.pop(hand_index)
        player.mana -= played_card.cost
        played_card.play(player, enemy)
        self.discard_pile.append(played_card)

    def discard_hand(self):
        print("\n--- 턴 종료: 손패를 모두 버립니다 ---")
        for card in self.hand:
            self.discard_pile.append(card)
        self.hand.clear()
        print(f"현재 무덤에 있는 카드 수: {len(self.discard_pile)}장")

    def print_status(self):
        print(f"\n[상태] 뽑을 카드: {len(self.draw_pile)}장 | 손패: {len(self.hand)}장 | 무덤: {len(self.discard_pile)}장")
        if self.hand:
            print("현재 손패: " + ", ".join([card.name for card in self.hand]))


    def start_combat(self, player, enemy):
        print(f"\n⚔️ 전투 시작! {player.name} VS {enemy.name} ⚔️")
        turn_count = 1

        while player.hp > 0 and enemy.hp > 0:
            print(f"\n========== [ {turn_count} 턴 시작 ] ==========")
            
            # 1. 턴 시작 셋업
            player.mana = player.max_mana
            self.draw_card(5)

            # 2. 플레이어 턴 루프 (카드를 내거나 턴을 종료할 때까지 반복)
            while True:
                # 현재 상태 출력
                print(f"\n[나] HP: {player.hp}/{player.max_hp} | 방어도: {player.block} | 마나: {player.mana}/{player.max_mana} | 구체: {player.orbs}")
                print(f"[적] {enemy.name} HP: {enemy.hp}/{enemy.max_hp} | 방어도: {enemy.block}")
                
                print("\n[현재 손패]")
                for i, card in enumerate(self.hand):
                    # 효과 설명을 한 줄로 합쳐서 보여줍니다.
                    desc = card.get_description().replace('\n', ' / ')
                    print(f"  {i} : {card.name} (코스트: {card.cost}) - {desc}")
                print("  e : 턴 종료")

                # 사용자 입력 받기
                choice = input("\n사용할 카드 번호를 입력하세요 (턴 종료는 e): ")

                if choice.lower() == 'e':
                    break

                try:
                    idx = int(choice)
                    self.play_card(idx, player, enemy)
                except ValueError:
                    print("잘못된 입력입니다. 숫자나 'e'를 입력하세요.")
                except IndexError:
                    print("없는 카드 번호입니다.")
                
                # 카드를 쓴 직후 적이 죽었는지 확인
                if enemy.hp <= 0:
                    break

            # 3. 전투 종료 판정 (플레이어 승리)
            if enemy.hp <= 0:
                print(f"\n🎉 {enemy.name} 처치 성공! 전투에서 승리했습니다!")
                break

            # 4. 플레이어 턴 종료 처리
            self.discard_hand()
            player.block = 0 # 턴 종료 시 방어도는 0으로 초기화 (바리케이드 등 예외가 없다면)

            # 5. 적의 턴 (아직 패턴이 없으므로 단순 고정 공격)
            print(f"\n--- 👿 {enemy.name}의 턴 ---")
            enemy_damage = 8 
            print(f"{enemy.name}이(가) {enemy_damage}의 피해를 가합니다!")
            player.calculate_damage_output(enemy_damage) # 적도 공격 계산기를 거침 (임시로 플레이어의 방어도 연산으로 바로 전달)
            
            # 적의 데미지 처리를 위해 take_damage 직접 호출
            player.take_damage(enemy_damage) 
            enemy.block = 0 # 적 턴 종료 시 적의 방어도 초기화

            # 6. 전투 종료 판정 (플레이어 패배)
            if player.hp <= 0:
                print(f"\n💀 {player.name} 사망... 게임 오버!")
                break
                
            turn_count += 1

