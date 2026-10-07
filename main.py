import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QLabel, QProgressBar, QPushButton, QFrame
from PyQt5 import uic
from PyQt5.QtGui import QPixmap 
from PyQt5.QtCore import Qt, QTimer

# 우리가 만든 엔진 클래스들 불러오기
from entities import Defect, FuzzyWurmCrawler, Nibbit
from battle import BattleManager
from cards import create_strike, create_defend, create_zap, create_dualcast

class ClickableEnemyWidget(QFrame):
    def __init__(self, enemy_index, click_callback, parent=None):
        super().__init__(parent)
        self.enemy_index = enemy_index
        self.click_callback = click_callback
        self.setCursor(Qt.PointingHandCursor) # 마우스 올리면 손가락 모양으로 변경
        
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.click_callback(self.enemy_index)
        super().mousePressEvent(event)
        
class GameWindow(QMainWindow):
    def __init__(self, battle_manager):
        super().__init__()
        
        # 💡 gui.ui 로드 
        ui_path = os.path.join(os.path.dirname(__file__), "gui.ui")
        uic.loadUi(ui_path, self)
        
        self.battle = battle_manager
        
        self.selected_card_index = None
        
        #이미지
        img_path = os.path.join(os.path.dirname(__file__), "images", "defect.png") 
        pixmap = QPixmap(img_path)
        scaled_pixmap = pixmap.scaled(200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.lbl_player.setPixmap(scaled_pixmap)
        
        
        # 버튼 시그널 연결
        self.btn_end_turn.clicked.connect(self.on_end_turn_clicked)
        self.btn_draw_pile.clicked.connect(lambda: print("🃏 뽑을 카드 확인 클릭!"))
        self.btn_discard_pile.clicked.connect(lambda: print("🗑️ 버린 카드 확인 클릭!"))

        # 전투 시작
        self.battle.start_combat(Defect())
        
        # 첫 화면 그리기
        self.update_ui()
        
    def on_card_clicked(self, card_idx):
        card = self.battle.hand[card_idx]
        
        # 마나 부족 체크는 엔진(process_play_card)에 맡기거나 여기서 미리 확인
        if self.battle.player.mana < card.cost:
            print(" ⚠️ 마나가 부족합니다!")
            return

        # 💡 카드를 누르면 즉시 발동하는 게 아니라, '타겟을 골라주세요' 상태로 진입합니다.
        self.selected_card_index = card_idx
        
        # 하단 상태창이나 플레이어 상태 라벨에 안내 문구 띄우기
        self.lbl_player_status.setText(f"🎯 [{card.name}] 타겟을 선택하세요! (공격할 적 클릭)")
        print(f">> [{card.name}] 선택됨. 공격할 적을 클릭하세요!")
        
    def on_enemy_clicked(self, enemy_idx):
        # 1. 카드를 먼저 골랐는지 확인
        if self.selected_card_index is not None:
            card_idx = self.selected_card_index
            self.selected_card_index = None # 타겟팅 상태 초기화
            
            # 2. 엔진에 선택한 카드와 적 번호(target_index) 전달하여 카드 사용!
            self.battle.process_play_card(card_idx, target_index=enemy_idx)
            
            # 3. 화면 갱신
            self.update_ui()
        else:
            print(" ⚠️ 먼저 손패에서 카드를 선택해주세요!")
        
    def get_enemy_image_filename(self, enemy_name):
        # 적 이름에 따라 보여줄 이미지 파일명 매핑
        if "Nibbit" in enemy_name:
            return "Nibbit.png"      # nibbit 이미지 파일명
        elif "Fuzzy Wurm" in enemy_name:
            return "Fuzzy_Wurm_Crawler.png"  # fuzzy_wurm 이미지 파일명
        return "Inklet.png"         # 예외 처리용 기본 이미지

    # --------------------------------------------------------
    # [핵심] 화면 갱신 함수 (턴 시작/카드 사용 시 매번 호출됨)
    # --------------------------------------------------------
    def update_ui(self):
        # 1. 내 캐릭터(디펙트) 상태 업데이트
        p = self.battle.player
        self.bar_player_hp.setMaximum(p.max_hp)
        self.bar_player_hp.setValue(p.hp)
        self.lbl_player_status.setText(f"마나: {p.mana}/{p.max_mana} | 방어: {p.block}")
        self.lbl_player_name.setText(p.name)
        
        # 1-2. 구체 슬롯 동적 렌더링 (색상 분기 수정)
        if hasattr(self, 'layout_orbs') and self.layout_orbs is not None:
            self.clear_layout(self.layout_orbs)
            p = self.battle.player
            if hasattr(p, 'orbs') and p.orbs:
                for orb in p.orbs:
                    # 구체 이름에 따른 이모지와 슬더스풍 배경색 매핑
                    if "전기" in orb.name or "Lightning" in str(type(orb)):
                        text = "⚡"
                        bg_color = "#f1c40f"  # ⚡ 번개색 (노란색/금색)
                    elif "냉기" in orb.name or "Frost" in str(type(orb)):
                        text = "❄️"
                        bg_color = "#3498db"  # ❄️ 얼음색 (파란색)
                    elif "어둠" in orb.name or "Dark" in str(type(orb)):
                        text = "🔮"
                        bg_color = "#8e44ad"  # 🔮 어둠색 (보라색)
                    else:
                        text = "🔥"
                        bg_color = "#e84393"  # 플라즈마색 (핑크색)
                    
                    lbl_orb = QLabel(text)
                    lbl_orb.setAlignment(Qt.AlignCenter)
                    lbl_orb.setFixedSize(50, 50)
                    # 둥근 동그라미 모양 + 가독성을 위한 글자 색상(흰색)
                    lbl_orb.setStyleSheet(f"""
                        background-color: {bg_color};
                        color: white;
                        border-radius: 25px; 
                        font-weight: bold;
                        font-size: 10px;
                    """)
                    self.layout_orbs.addWidget(lbl_orb)

        # 2. 적 진영 동적 렌더링 (클릭 가능한 프레임 패널 생성)
        self.clear_layout(self.layout_enemies)
        for i, enemy in enumerate(self.battle.enemies):
            # 💡 QPushButton 대신 QFrame 기반의 클릭 가능한 위젯 사용
            frame_enemy = ClickableEnemyWidget(i, self.on_enemy_clicked)
            frame_enemy.setFixedWidth(200)
            
            # 슬더스풍 다크 테마 디자인 + 마우스 올릴 때(hover) 노란 테두리 효과
            frame_enemy.setStyleSheet("""
                QFrame {
                    background-color: #2c3e50;
                    border: 2px solid #34495e;
                    border-radius: 12px;
                    color: white;
                    padding: 8px;
                }
                QFrame:hover {
                    border: 2px solid #f1c40f; /* 마우스 올리면 노란색으로 조준 표시! */
                    background-color: #34495e;
                }
            """)
            
            # 프레임 내부에 들어갈 세로 레이아웃
            vbox = QVBoxLayout(frame_enemy)
            
            lbl_intent = QLabel(f"의도: {enemy.intent_msg}" if hasattr(enemy, 'intent_msg') else "의도: 대기중")
            lbl_intent.setStyleSheet("color: #e74c3c; font-weight: bold; font-size: 12px;")
            lbl_intent.setAlignment(Qt.AlignCenter)
            
            # 🖼️ 적 이미지 라벨 (이제 잘 나옵니다!)
            lbl_enemy_img = QLabel()
            img_filename = self.get_enemy_image_filename(enemy.name)
            enemy_img_path = os.path.join(os.path.dirname(__file__), "images", img_filename)
            
            if os.path.exists(enemy_img_path):
                enemy_pixmap = QPixmap(enemy_img_path)
                scaled_enemy_pixmap = enemy_pixmap.scaled(110, 110, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                lbl_enemy_img.setPixmap(scaled_enemy_pixmap)
                lbl_enemy_img.setAlignment(Qt.AlignCenter)
            else:
                lbl_enemy_img.setText("(이미지 없음)")
                lbl_enemy_img.setAlignment(Qt.AlignCenter)
            
            lbl_name = QLabel(f"{enemy.name}\n방어: {enemy.block}")
            lbl_name.setStyleSheet("font-weight: bold; font-size: 13px; color: #ecf0f1;")
            lbl_name.setAlignment(Qt.AlignCenter)
            
            # 💚 체력바 (이제 다시 나타납니다!)
            bar_hp = QProgressBar()
            bar_hp.setMaximum(enemy.max_hp)
            bar_hp.setValue(enemy.hp)
            bar_hp.setStyleSheet("""
                QProgressBar {
                    background-color: #7f8c8d;
                    border-radius: 4px;
                    text-align: center;
                    color: white;
                    font-size: 10px;
                    height: 14px;
                }
                QProgressBar::chunk {
                    background-color: #2ecc71;
                    border-radius: 4px;
                }
            """)
            
            vbox.addWidget(lbl_intent)
            vbox.addWidget(lbl_enemy_img)
            vbox.addWidget(lbl_name)
            vbox.addWidget(bar_hp)
            
            self.layout_enemies.addWidget(frame_enemy)

        # 3. 손패(카드) 동적 렌더링 (기존 카드 지우고 새로 그리기)
        self.clear_layout(self.layout_cards)
        for i, card in enumerate(self.battle.hand):
            # 카드 버튼 텍스트 구성
            desc = card.get_description().replace('\n', ' ')
            btn_text = f"【 {card.name} 】\n코스트: {card.cost}\n\n{desc}"
            
            btn_card = QPushButton(btn_text)
            btn_card.setMinimumSize(120, 160) # 카드 모양으로 길쭉하게
            
            # 💡 카드를 클릭하면 on_card_clicked 함수 실행 (i번째 카드라는 정보 전달)
            btn_card.clicked.connect(lambda checked, idx=i: self.on_card_clicked(idx))
            
            self.layout_cards.addWidget(btn_card)

    # --------------------------------------------------------
    # [이벤트 핸들러] 카드 클릭 시
    # --------------------------------------------------------
    def on_card_clicked(self, card_idx):
        print(f">> {card_idx}번 카드 클릭됨!")
        # 일단은 무조건 맨 앞의 적(0번)을 타겟으로 잡도록 하드코딩
        # (타겟팅 시스템은 다음 단계에서 구현)
        self.battle.process_play_card(card_idx, target_index=0)
        self.update_ui() # 카드 썼으니 화면 갱신!

    # --------------------------------------------------------
    # [이벤트 핸들러] 턴 종료 버튼 클릭 시
    # --------------------------------------------------------
    def on_end_turn_clicked(self):
        print(">> 턴 종료 버튼 클릭됨!")
        self.battle.process_end_turn()
        self.update_ui() # 적이 때렸으니 화면 갱신!

    # --------------------------------------------------------
    # [유틸리티] 레이아웃 안의 위젯들을 깨끗하게 비우는 함수
    # --------------------------------------------------------
    def clear_layout(self, layout):
        if layout is not None:
            while layout.count():
                child = layout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()
                elif child.layout():
                    self.clear_layout(child.layout())
                    
    def play_lightning_effect(self, target_index):
        """특정 적에게 번개가 칠 때 시각적 효과를 주는 함수"""
        if target_index >= len(self.layout_enemies.children()):
            return
            
        # 해당 적의 레이아웃(vbox)을 가져옴
        enemy_item = self.layout_enemies.itemAt(target_index)
        if enemy_item and enemy_item.layout():
            vbox = enemy_item.layout()
            
            # 1. 번개 타격 순간 배경을 노란색으로 확 번쩍이게 변경 (QSS 적용)
            for i in range(vbox.count()):
                widget = vbox.itemAt(i).widget()
                if isinstance(widget, QLabel):
                    widget.setStyleSheet("background-color: yellow; color: black;")
            
            # 2. 0.2초(200밀리초) 뒤에 원래 색상으로 되돌리기
            QTimer.singleShot(200, lambda: self.update_ui())

# main() 함수는 이전과 동일
def main():
    # --- 1. 엔진 셋업 ---
    my_deck = []
    for _ in range(4): my_deck.append(create_strike())
    for _ in range(4): my_deck.append(create_defend())
    my_deck.append(create_zap())
    my_deck.append(create_dualcast())

    front_nibbit = Nibbit("Nibbit(앞)", max_hp=44, start_step=1) 
    back_nibbit = Nibbit("Nibbit(뒤)", max_hp=46, start_step=2)
    crawler = FuzzyWurmCrawler("Fuzzy Wurm", max_hp=56)
    enemies = [front_nibbit, back_nibbit, crawler] 

    battle = BattleManager(my_deck, enemies)

    # --- 2. GUI 실행 ---
    app = QApplication(sys.argv)
    window = GameWindow(battle)
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()