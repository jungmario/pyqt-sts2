import random

class BattleManager:
    def __init__(self, master_deck, enemies):
        self.draw_pile = master_deck[:] 
        self.hand = []
        self.discard_pile = []
        self.enemies = enemies
        self.player = None           # GUI 셋업을 위해 추가
        self.turn_count = 1          # GUI 셋업을 위해 추가
        self.is_game_over = False    # GUI 셋업을 위해 추가
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

    # --------------------------------------------------------
    # [이벤트 1] 전투 초기화 (창 띄울 때 1번 실행)
    # --------------------------------------------------------
    def start_combat(self, player):
        self.player = player
        self.turn_count = 1
        self.is_game_over = False
        
        enemy_names = ", ".join([e.name for e in self.enemies])
        print(f"\n⚔️ 전투 시작! {self.player.name} VS {enemy_names} ⚔️")
        
        self.player.start_of_combat()
        
        # 셋업 후 첫 턴 바로 시작
        self.start_player_turn()

    # --------------------------------------------------------
    # [이벤트 2] 내 턴 시작 (매 턴 자동으로 호출)
    # --------------------------------------------------------
    def start_player_turn(self):
        if self.is_game_over: return

        print(f"\n========== [ {self.turn_count} 턴 시작 ] ==========")
        self.player.start_of_turn()
        self.draw_card(5)

        for e in self.enemies:
            if e.hp > 0:
                e.roll_intent()

        self.print_status()
        print(" ⏳ (엔진 대기 중... UI 창에서 카드나 턴 종료 버튼 클릭을 기다립니다)")

    # --------------------------------------------------------
    # [이벤트 3] 카드 사용 (UI의 카드 버튼 클릭 시 실행)
    # 기존 play_card 메서드가 이렇게 변경되었습니다!
    # --------------------------------------------------------
    def process_play_card(self, hand_index, target_index, vfx_callback = None):
        if self.is_game_over: return

        if hand_index < 0 or hand_index >= len(self.hand):
            print('잘못된 카드 번호입니다.')
            return

        if target_index >= len(self.enemies) or self.enemies[target_index].hp <= 0:
            print('잘못되었거나 이미 죽은 대상입니다.')
            return

        card = self.hand[hand_index]

        if self.player.mana < card.cost :
            print(f'마나가 부족합니다! (필요: {card.cost}, 현재: {self.player.mana})')
            return

        played_card = self.hand.pop(hand_index)
        self.player.mana -= played_card.cost

        selected_target = self.enemies[target_index]
        # self.player를 사용하도록 변경
        played_card.play(self.player, selected_target, self.enemies, vfx_callback = vfx_callback) 
        self.discard_pile.append(played_card)

        # 💡 시체 청소 및 승리 판정
        self.check_dead_enemies_and_win()

    # --------------------------------------------------------
    # [이벤트 4] 턴 종료 (UI의 턴 종료 버튼 클릭 시 실행)
    # --------------------------------------------------------
    def process_end_turn(self, vfx_callback = None):
        if self.is_game_over: return

        self.discard_hand()

        # 1. 구체 발동
        if hasattr(self.player, 'orbs') and self.player.orbs:
            print("\n[ 턴 종료: 구체 지속 효과 발동 ]")
            for orb in self.player.orbs:
                orb.passive(self.player, self.enemies, vfx_callback) 

        if self.check_dead_enemies_and_win(): return

        # 2. 적 턴 실행
        print("\n--- 👿 적들의 턴 ---")
        for e in self.enemies:
            if e.hp > 0:
                e.execute_intent(self.player)
            if self.player.hp <= 0:
                break

        # 3. 패배 판정
        if self.player.hp <= 0:
            print(f"\n💀 {self.player.name} 사망... 게임 오버!")
            self.is_game_over = True
            return

        # 4. 다음 턴으로
        self.turn_count += 1
        self.start_player_turn()

    # --------------------------------------------------------
    # 유틸리티 메서드들
    # --------------------------------------------------------
    def check_dead_enemies_and_win(self):
        self.enemies[:] = [e for e in self.enemies if e.hp > 0]
        if not self.enemies:
            print(f"\n🎉 모든 적 처치 성공! 전투에서 승리했습니다!")
            self.is_game_over = True
            return True
        return False

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