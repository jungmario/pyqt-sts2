import random

class BattleManager:
    def __init__(self, master_deck, enemies):
        self.draw_pile = master_deck[:] 
        self.hand = []
        self.discard_pile = []
        self.enemies = enemies
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

    def play_card(self, hand_index, player, target_index = 0):

        if hand_index < 0 or hand_index >= len(self.hand):
            print('잘못된 카드 번호입니다.')
            return

        card = self.hand[hand_index]

        if player.mana < card.cost :
            print(f'마나가 부족합니다! (필요: {card.cost}, 현재: {player.mana})')
            return

        played_card = self.hand.pop(hand_index)
        player.mana -= played_card.cost

        selected_target = self.enemies[target_index]
        played_card.play(player, selected_target, self.enemies)
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


    # BattleManager 클래스 내부
    def start_combat(self, player, enemies):
        enemy_names = ", ".join([e.name for e in enemies])
        print(f"\n⚔️ 전투 시작! {player.name} VS {enemy_names} ⚔️")
        turn_count = 1

        player.start_of_combat()

        while player.hp > 0 and enemies:
            print(f"\n========== [ {turn_count} 턴 시작 ] ==========")
            
            player.start_of_turn()
            self.draw_card(5)

            # 💡 [핵심 1] 매 턴이 시작될 때, 살아있는 적들이 이번 턴에 할 행동을 미리 결정합니다.
            for e in enemies:
                e.roll_intent()

            while True:
                print(f"\n[나] HP: {player.hp}/{player.max_hp} | 방어도: {player.block} | 마나: {player.mana}/{player.max_mana} | 구체: {player.orbs}")
                
                # 💡 [핵심 2] 상태창에 적들의 '의도(intent_msg)'를 함께 출력합니다.
                for i, e in enumerate(enemies):
                    print(f"[{i}번 적] {e.name} HP: {e.hp}/{e.max_hp} | 방어도: {e.block} | 의도: {e.intent_msg}")
                
                print("\n[현재 손패]")
                for i, card in enumerate(self.hand):
                    desc = card.get_description().replace('\n', ' / ')
                    print(f"  {i} : {card.name} (코스트: {card.cost}) - {desc}")
                print("  e : 턴 종료")

                choice = input("\n사용할 카드 번호와 대상 번호를 띄어쓰기로 입력하세요 (예: 0 1, 턴 종료는 e): ")

                if choice.lower() == 'e':
                    break

                try:
                    inputs = choice.split()
                    card_idx = int(inputs[0])
                    
                    # 타겟 미지정 시 살아있는 첫 번째 적 자동 조준
                    if len(inputs) > 1:
                        target_idx = int(inputs[1])
                    else:
                        alive_indices = [idx for idx, e in enumerate(enemies) if e.hp > 0]
                        target_idx = alive_indices[0] if alive_indices else 0
                    
                    if target_idx >= len(enemies):
                        print(" ⚠️ 잘못된 대상 번호입니다.")
                        continue
                        
                    self.play_card(card_idx, player, target_idx)
                except ValueError:
                    print("잘못된 입력입니다. '0 1' 형식의 숫자나 'e'를 입력하세요.")
                except IndexError:
                    print("없는 카드 번호이거나 잘못된 대상 번호입니다.")
                
                # 카드 사용 후 시체 청소
                enemies[:] = [e for e in enemies if e.hp > 0]
                if not enemies: 
                    break

            if not enemies:
                print(f"\n🎉 모든 적 처치 성공! 전투에서 승리했습니다!")
                break

            self.discard_hand()

            # 구체 지속 효과 발동
            if hasattr(player, 'orbs') and player.orbs:
                print("\n[ 턴 종료: 구체 지속 효과 발동 ]")
                for orb in player.orbs:
                    orb.passive(player, enemies) 
            
            # 구체 발동 후 시체 청소
            enemies[:] = [e for e in enemies if e.hp > 0]
            if not enemies:
                print(f"\n🎉 모든 적 처치 성공! 전투에서 승리했습니다!")
                break

            # 💡 [핵심 3] 적들의 턴에 미리 결정해둔 행동(execute_intent)을 실행합니다.
            print("\n--- 👿 적들의 턴 ---")
            for e in enemies:
                e.execute_intent(player)
                if player.hp <= 0:
                    break

            if player.hp <= 0:
                print(f"\n💀 {player.name} 사망... 게임 오버!")
                break
                
            turn_count += 1