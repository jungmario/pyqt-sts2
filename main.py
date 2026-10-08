import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QLabel, QProgressBar, QPushButton, QFrame, QDialog, QListWidget, QWidget, QHBoxLayout
from PyQt5 import uic
from PyQt5.QtGui import QPixmap 
from PyQt5.QtCore import Qt, QTimer, QRect

# 우리가 만든 엔진 클래스들 불러오기
from entities import Defect, FuzzyWurmCrawler, Nibbit
from battle import BattleManager
from cards import create_strike, create_defend, create_zap, create_dualcast

class CardListDialog(QDialog):
    def __init__(self, title, cards, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.resize(400, 500)
        # 💡 창 크기 고정 (예: 가로 1280, 세로 720) - 원하시는 해상도로 숫자를 바꿔주세요!
        self.setFixedSize(1280, 720)
        
        layout = QVBoxLayout(self)
        
        # 타이틀 라벨
        lbl_title = QLabel(f"<b>{title} (총 {len(cards)}장)</b>")
        lbl_title.setStyleSheet("font-size: 15px; color: #ecf0f1; margin-bottom: 5px;")
        layout.addWidget(lbl_title)
        
        # 카드 목록 리스트 위젯 (다크 테마)
        list_widget = QListWidget()
        list_widget.setStyleSheet("""
            QListWidget {
                background-color: #2c3e50;
                color: white;
                border-radius: 8px;
                padding: 5px;
                font-size: 13px;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #34495e;
            }
            QListWidget::item:hover {
                background-color: #34495e;
            }
        """)
        
        if not cards:
            list_widget.addItem("카드가 없습니다.")
        else:
            for card in cards:
                desc = card.get_description().replace('\n', ' ') if hasattr(card, 'get_description') else card.description
                item_text = f"【 {card.name} 】 (코스트: {card.cost})\n{desc}"
                list_widget.addItem(item_text)
                
        layout.addWidget(list_widget)
        
        # 확인 버튼
        btn_close = QPushButton("확인")
        btn_close.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                font-weight: bold;
                padding: 8px;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        btn_close.clicked.connect(self.accept)
        layout.addWidget(btn_close)


class ClickableEnemyWidget(QFrame):
    def __init__(self, enemy_index, click_callback, parent=None):
        super().__init__(parent)
        self.enemy_index = enemy_index
        self.click_callback = click_callback
        self.setCursor(Qt.PointingHandCursor)
        
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

        if hasattr(self, 'layout_orbs') and self.layout_orbs.parentWidget():
            self.layout_orbs.parentWidget().setMinimumHeight(200)
        
        self.battle = battle_manager
        self.selected_card_index = None
        
        # 이미지 로딩 (기존 코드 완벽 보존)
        img_path = os.path.join(os.path.dirname(__file__), "images", "defect.png") 
        pixmap = QPixmap(img_path)
        scaled_pixmap = pixmap.scaled(200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.lbl_player.setPixmap(scaled_pixmap)
        
        # 버튼 시그널 연결 (람다 대신 실제 팝업 함수로 교체)
        self.btn_end_turn.clicked.connect(self.on_end_turn_clicked)
        self.btn_draw_pile.clicked.connect(self.show_draw_pile_popup)
        self.btn_discard_pile.clicked.connect(self.show_discard_pile_popup)

        # 전투 시작
        self.battle.start_combat(Defect())
        # (main.py의 __init__ 함수 안, self.update_ui() 호출하기 전 쯤에 추가)
        
        # 💡 경로 슬래시(\)를 CSS가 인식할 수 있게 (/)로 변환
        base_dir = os.path.dirname(__file__).replace("\\", "/")
        
        # 메인 윈도우에 고유 이름을 지정해서 배경이 다른 버튼으로 번지지 않게 방지!
        self.setObjectName("GameMainWindow") 
        self.setStyleSheet(f"""
            #GameMainWindow {{
                border-image: url('{base_dir}/images/background.png');
            }}
        """)
        
        # 1. 턴 종료 버튼 (크기 키우고 글자 얹기)
        if hasattr(self, 'btn_end_turn'):
            self.btn_end_turn.setText("End Turn") # 💡 버튼 위에 들어갈 글자 세팅!
            self.btn_end_turn.setFixedSize(130, 60) # 💡 넉넉한 사이즈로 키우기 (가로, 세로)
            self.btn_end_turn.setStyleSheet(f"""
                QPushButton {{
                    border-image: url('{base_dir}/images/end_turn.png');
                    color: white;             /* 글자를 하얀색으로 */
                    font-weight: bold;        /* 굵게 */
                    font-size: 15px;          /* 글자 크기 */
                }}
                QPushButton:hover {{
                    color: #f1c40f;           /* 마우스 올리면 글자가 노란색으로 빛남 */
                }}
            """)
            
        # 2. 뽑을 카드(Draw Pile) 덱 버튼
        if hasattr(self, 'btn_draw_pile'):
            self.btn_draw_pile.setText("")
            self.btn_draw_pile.setFixedSize(80, 80) # 💡 크기 큼직하게 키우기
            self.btn_draw_pile.setStyleSheet(f"""
                QPushButton {{
                    border-image: url('{base_dir}/images/draw_pile.png');
                    background-color: transparent;
                }}
            """)
            
        # 3. 버린 카드(Discard Pile) 무덤 버튼
        if hasattr(self, 'btn_discard_pile'):
            self.btn_discard_pile.setText("")
            self.btn_discard_pile.setFixedSize(80, 80) # 💡 크기 큼직하게 키우기
            self.btn_discard_pile.setStyleSheet(f"""
                QPushButton {{
                    border-image: url('{base_dir}/images/discard_pile.png');
                    background-color: transparent;
                }}
            """)

        # 첫 화면 그리기
        self.update_ui()

    def show_lightning_strike(self, target_index):
        """4프레임 번개 스프라이트 애니메이션 재생 및 타격 효과"""
        # 타겟 인덱스가 유효한지 확인
        if target_index >= self.layout_enemies.count(): 
            return

        # 1. 타겟 적의 위젯 가져오기 및 번개를 띄울 임시 라벨 생성
        target_widget = self.layout_enemies.itemAt(target_index).widget()
        lbl_lightning = QLabel(self)
        
        # 2. 4단계 번개 스프라이트 시트 이미지 로드
        base_dir = os.path.dirname(__file__).replace("\\", "/")
        sprite_sheet = QPixmap(f"{base_dir}/images/lightning_orb_particle.png") # 💡 저장하신 파일명과 똑같은지 확인하세요!
        
        # 💡 이펙트 크기를 여기서 마음대로 조절하세요! (원하는 숫자로 자유롭게 변경)
        effect_width = 150
        effect_height = 300

        # 3. 이미지 가로로 4등분 자르기 및 크기 조절
        frame_width = sprite_sheet.width() // 4
        frame_height = sprite_sheet.height()
        
        frames = []
        for i in range(4):
            rect = QRect(i * frame_width, 0, frame_width, frame_height)
            # 💡 잘라낸 원본을 내가 설정한 크기(effect_width, effect_height)로 확대/축소합니다.
            # (비율 무시하고 꽉 채우려면 Qt.IgnoreAspectRatio 를 사용하면 크기 통제가 가장 쉽습니다)
            frame = sprite_sheet.copy(rect).scaled(effect_width, effect_height, Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
            frames.append(frame)

        # 액자(QLabel) 크기를 설정한 크기와 딱 맞춥니다.
        lbl_lightning.setFixedSize(effect_width, effect_height) 
        lbl_lightning.setPixmap(frames[0]) 

        # 4. 라벨을 적 정중앙 머리 위로 이동
        target_pos = target_widget.mapTo(self, target_widget.rect().topLeft())
        
        # 💡 [핵심] 자동 정중앙 계산: 적의 가로 폭과 이펙트의 가로 폭(effect_width)을 비교해서 정중앙을 맞춥니다.
        offset_x = (target_widget.width() - effect_width) // 2
        
        # y좌표도 이펙트 높이(effect_height)만큼 끌어올려서 적 머리에 닿게 합니다.
        # (숫자 50을 키우면 더 아래로 파고들고, 줄이면 허공으로 올라갑니다)
        offset_y = -effect_height + 50 
        
        lbl_lightning.move(target_pos.x() + offset_x, target_pos.y() + offset_y)
        lbl_lightning.show()

        # 5. 적 상자가 노랗게 번쩍이는 타격 효과 씌우기
        original_style = target_widget.styleSheet()
        target_widget.setStyleSheet(original_style + """
            background-color: rgba(241, 196, 15, 0.4);
            border: 3px solid #f1c40f;
        """)

        # 6. 애니메이션 재생 로직 (타이머)
        lbl_lightning.current_frame = 0
        lbl_lightning.anim_timer = QTimer(self)

        def animate_frame():
            # 4프레임이 다 돌기 전이면 다음 프레임 띄우기
            if lbl_lightning.current_frame < 4:
                lbl_lightning.setPixmap(frames[lbl_lightning.current_frame])
                lbl_lightning.current_frame += 1
            # 애니메이션이 다 끝났다면 정리하기
            else:
                lbl_lightning.anim_timer.stop()
                lbl_lightning.deleteLater() # 번개 이미지 삭제
                target_widget.setStyleSheet(original_style) # 노란 상자 복구
                
                # ⚡ [핵심] 번개가 다 치고 사라진 직후에 화면(체력바)을 갱신합니다!
                self.update_ui() 

        # 0.05초(50ms)마다 프레임을 교체하도록 타이머 시작
        lbl_lightning.anim_timer.timeout.connect(animate_frame)
        lbl_lightning.anim_timer.start(30)

    def show_draw_pile_popup(self):
        # 엔진의 뽑을 카드 더미 변수명 확인 (보통 draw_pile 또는 draw_deck)
        cards = getattr(self.battle, 'draw_pile', [])
        dialog = CardListDialog("뽑을 카드 더미 (Draw Pile)", cards, self)
        dialog.exec_()

    def show_discard_pile_popup(self):
        # 엔진의 버린 카드 더미 변수명 확인
        cards = getattr(self.battle, 'discard_pile', [])
        dialog = CardListDialog("버린 카드 더미 (Discard Pile)", cards, self)
        dialog.exec_()
        
    def on_card_clicked(self, card_idx):
        card = self.battle.hand[card_idx]
        
        # 마나 부족 체크
        if self.battle.player.mana < card.cost:
            print(" ⚠️ 마나토큰이 부족합니다!")
            return

        if not card.requires_target:
            # 타겟 불필요 (수비, 파지직 등) -> 즉시 발동
            print(f">> [{card.name}] 즉시 발동!")
            self.selected_card_index = None
            self.battle.process_play_card(card_idx, target_index=0, vfx_callback = self.show_lightning_strike)
            self.update_ui()
        else:
            # 타겟 필요 (타격 등) -> 적 선택 대기
            self.selected_card_index = card_idx
        
        # UI 상태창에 안내 문구 띄우기
        print(f">> [{card.name}] 선택됨. 공격할 적을 클릭하세요!")
        
    def on_enemy_clicked(self, enemy_idx):
        # 1. 카드가 먼저 선택되어 있는지 확인
        if self.selected_card_index is not None:
            card_idx = self.selected_card_index
            self.selected_card_index = None # 타겟팅 상태 초기화
            
            print(f">> {enemy_idx}번 적에게 카드 사용 시도!")
            
            # 2. 💡 엔진에 선택한 카드 인덱스와 '클릭한 적의 번호(enemy_idx)'를 전달!
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
        p = self.battle.player
        # 💡 플레이어 상태 라벨 텍스트 싹 지우기 (추후 상태이상 아이콘이 들어갈 자리)
        if hasattr(self, 'lbl_player_status'):
            self.lbl_player_status.setText("") # 텍스트를 완전히 비워버립니다!
            
            # 나중에 아이콘들이 들어갈 수 있도록 공간(높이)만 살짝 확보해 둡니다.
            self.lbl_player_status.setMinimumHeight(40) 
            self.lbl_player_status.setStyleSheet("background-color: transparent;")
        # 💡 [신규] 디펙트 에너지(마나) 이미지 및 숫자 동적 렌더링
        if hasattr(self, 'lbl_energy'):
            base_dir = os.path.dirname(__file__).replace("\\", "/")
            
            self.lbl_energy.setText(f"{p.mana}/{p.max_mana}")
            self.lbl_energy.setAlignment(Qt.AlignCenter) # 글자를 정중앙으로
            self.lbl_energy.setFixedSize(80, 80)
            
            # 에너지 이미지 적용 및 폰트 세팅 (숫자가 잘 보이게 큼직하고 굵게)
            self.lbl_energy.setStyleSheet(f"""
                QLabel {{
                    image: url('{base_dir}/images/energy.png');
                    color: white;
                    font-size: 18px; 
                    font-weight: bold;
                }}
            """)

        # 💡 디펙트 진영 전체를 아래로 내리기 (gui.ui의 verticalLayout 활용)
        if hasattr(self, 'verticalLayout'):
            self.verticalLayout.setContentsMargins(120, 230, 0, 0) # 위쪽 여백 150px

        # 1. 디펙트 이름 스타일링 (금색 포인트 + 다크 박스)
        if hasattr(self, 'lbl_player_name'):
            self.lbl_player_name.setText('디펙트')
            self.lbl_player_name.setStyleSheet("""
                color: #f1c40f; 
                font-size: 14px; /* 글자 크기 축소 */
                font-weight: bold; 
                background-color: transparent; /* 💡 배경을 완전 투명하게! */
                /* border 나 padding 같은 투박한 요소 제거 */
            """)
        
        # 1. 체력바(QProgressBar) 설정
        if hasattr(self, 'bar_player_hp'):
            self.bar_player_hp.setMaximum(p.max_hp)
            self.bar_player_hp.setValue(p.hp)
            
            # '현재체력 / 최대체력' 숫자로 표시
            self.bar_player_hp.setFormat("%v / %m")
            
            # 💡 방어도가 있으면 바 색상을 하늘색(#3498db), 없으면 빨간색(#e74c3c)으로 변경!
            chunk_color = "#3498db" if p.block > 0 else "#e74c3c"
            
            self.bar_player_hp.setStyleSheet(f"""
                QProgressBar {{
                    background-color: #2c3e50;
                    border: 2px solid #34495e;
                    border-radius: 6px;
                    text-align: center;
                    color: #ffffff; /* 글자는 어떤 바 색상이든 잘 보이게 항상 흰색으로 고정 */
                    font-weight: bold;
                    font-size: 13px;
                    height: 22px;
                }}
                QProgressBar::chunk {{
                    background-color: {chunk_color}; /* 방어도 유무에 따라 바 색상 동적 변경 */
                    border-radius: 4px;
                }}
            """)

        # 2. 방패 아이콘 및 방어도 숫자 표시 (lbl_player_block)
        if hasattr(self, 'lbl_player_block'):
            if p.block > 0:
                self.lbl_player_block.setText(f"🛡️ {p.block}")
                self.lbl_player_block.setStyleSheet("""
                    color: #3498db; 
                    font-weight: bold; 
                    font-size: 14px; 
                    margin-left: 5px;
                """)
                self.lbl_player_block.show()
            else:
                self.lbl_player_block.setText("") 
                self.lbl_player_block.hide()

        # 4. 구체 슬롯 동적 렌더링 (PNG 이미지 적용 + 오른쪽부터 채우기 고증)
        if hasattr(self, 'layout_orbs') and self.layout_orbs is not None:
            self.clear_layout(self.layout_orbs)
            
            max_slots = getattr(p, 'max_slots', getattr(p, 'max_orbs', 3))
            active_orbs = getattr(p, 'orbs', [])
            empty_count = max_slots - len(active_orbs)
            
            for i in range(max_slots):
                lbl_orb = QLabel()
                lbl_orb.setAlignment(Qt.AlignCenter)
                lbl_orb.setFixedSize(48, 48)
                
                img_filename = ""
                if i < empty_count:
                    # 🕳️ 빈 슬롯 이미지 파일명 (images/ 폴더 내 파일명 확인)
                    img_filename = "orb_empty.png"
                else:
                    # ⚡ 활성화된 구체 종류별 이미지 파일명 매핑
                    orb_idx = i - empty_count
                    orb = active_orbs[orb_idx]
                    
                    if "전기" in orb.name or "Lightning" in str(type(orb)):
                        img_filename = "orb_lightning.png"
                    elif "냉기" in orb.name or "Frost" in str(type(orb)):
                        img_filename = "orb_frost.png"
                    elif "어둠" in orb.name or "Dark" in str(type(orb)):
                        img_filename = "orb_dark.png"
                    else:
                        img_filename = "orb_plasma.png"
                
                # 이미지 경로 로드 및 렌더링
                img_path = os.path.join(os.path.dirname(__file__), "images", img_filename)
                if os.path.exists(img_path):
                    pixmap = QPixmap(img_path)
                    scaled_pixmap = pixmap.scaled(44, 44, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    lbl_orb.setPixmap(scaled_pixmap)
                else:
                    # 이미지가 없을 경우 대체 텍스트
                    lbl_orb.setText("·" if i < empty_count else "⚡")
                    lbl_orb.setStyleSheet("color: white; font-weight: bold; background-color: #2c3e50; border-radius: 22px;")
                
                self.layout_orbs.addWidget(lbl_orb)

        # 5. 손패 동적 렌더링
        self.clear_layout(self.layout_cards)
        for i, card in enumerate(self.battle.hand):
            btn_card = QPushButton(f"{card.name}\n({card.cost}코스트)\n{card.get_description}")
            btn_card.setFixedSize(110, 150)
            btn_card.setStyleSheet("""
                QPushButton {
                    background-color: #34495e;
                    color: white;
                    border: 2px solid #2c3e50;
                    border-radius: 10px;
                    font-size: 11px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #4e6d8c;
                    border: 2px solid #f1c40f;
                }
            """)
            btn_card.clicked.connect(lambda checked, idx=i: self.on_card_clicked(idx))
            self.layout_cards.addWidget(btn_card)

        # 6. 적 진영 동적 렌더링 (이미지 타겟팅 & 의도 아이콘화)
        self.clear_layout(self.layout_enemies)
        self.layout_enemies.setSpacing(10)
        self.layout_enemies.setAlignment(Qt.AlignCenter)
        # 💡 [핵심] 적 몬스터 전체를 위쪽에서 150px 만큼 아래로 밀어냅니다!
        # 순서: (왼쪽, 위, 오른쪽, 아래) 여백
        self.layout_enemies.setContentsMargins(200, 200, 0, 0)
        
        import re # 텍스트에서 데미지 숫자를 추출하기 위해 사용
        
        for i, enemy in enumerate(self.battle.enemies):
            # 💡 [변경 1] 전체 프레임(ClickableEnemyWidget)을 일반 QFrame으로 변경! (전체 박스 클릭/빛남 방지)
            frame_enemy = QFrame() 
            frame_enemy.setFixedWidth(230) 
            # 💡 [변경] 적 프레임 배경과 테두리를 완전 투명하게 만들어서 배경 이미지와 어우러지게 함!
            frame_enemy.setStyleSheet("""
                QFrame {
                    background-color: transparent; 
                    border: none;
                    color: white;
                    padding: 8px;
                }
            """)
            
            vbox = QVBoxLayout(frame_enemy)
            vbox.setAlignment(Qt.AlignCenter)
            
            # 2. 의도(Intent) 아이콘화 처리 (복합 의도 동시 표시 지원)
            raw_intent = getattr(enemy, 'intent_msg', '대기중')
            
            # 아이콘을 모아둘 빈 리스트 생성
            intent_icons = []
            
            # 💡 [1] 공격 검사
            if "공격" in raw_intent or "피해" in raw_intent:
                nums = re.findall(r'\d+', raw_intent)
                # 숫자가 여러 개(예: 공격 7, 방어 5)일 수 있으므로 보통 맨 앞 숫자를 데미지로 간주합니다.
                dmg = nums[0] if nums else "?"
                intent_icons.append(f"⚔️ {dmg}")
                
            # 💡 [2] 방어 검사 (elif가 아닌 if를 사용해 공격과 함께 추가될 수 있게 함!)
            if "방어" in raw_intent:
                intent_icons.append("🛡️")
                
            # 💡 [3] 힘/강화 검사
            if "힘" in raw_intent or "강화" in raw_intent:
                intent_icons.append("⬆️")
                
            # 💡 [4] 취약/약화 등 디버프 공격 시
            if "약화" in raw_intent or "취약" in raw_intent or "디버프" in raw_intent:
                intent_icons.append("⬇️")
                
            # 걸러진 아이콘이 하나도 없다면 대기 아이콘(💤), 있다면 띄어쓰기로 예쁘게 이어붙임
            if not intent_icons:
                display_intent = "💤"
            else:
                display_intent = " ".join(intent_icons) # 예: "⚔️ 7 🛡️"
                
            lbl_intent = QLabel(display_intent)
            lbl_intent.setStyleSheet("color: #e74c3c; font-weight: bold; font-size: 18px;")
            lbl_intent.setAlignment(Qt.AlignCenter)
            
            # 💡 [변경 3] 적 이미지를 QPushButton으로 만들어서 이미지에만 호버/클릭 효과 부여!
            btn_enemy_img = QPushButton()
            btn_enemy_img.setFixedSize(180, 180)
            btn_enemy_img.setCursor(Qt.PointingHandCursor) # 마우스 올리면 손가락 모양으로 변경
            
            img_filename = self.get_enemy_image_filename(enemy.name)
            enemy_img_path = os.path.join(os.path.dirname(__file__), "images", img_filename)
            img_url = enemy_img_path.replace("\\", "/") # CSS 적용을 위한 슬래시 변환
            
            if os.path.exists(enemy_img_path):
                btn_enemy_img.setStyleSheet(f"""
                    QPushButton {{
                        image: url('{img_url}');
                        background-color: transparent;
                        border: 2px solid transparent;
                        border-radius: 10px;
                    }}
                    QPushButton:hover {{
                        border: 2px solid #f1c40f; /* 마우스를 올리면 이미지만 노랗게 빛남! */
                        background-color: rgba(241, 196, 15, 0.1);
                    }}
                """)
            else:
                btn_enemy_img.setText("(이미지 없음)")
                btn_enemy_img.setStyleSheet("QPushButton:hover { border: 2px solid #f1c40f; }")
            
            # 이미지 클릭 시 타겟팅되도록 시그널 연결
            btn_enemy_img.clicked.connect(lambda checked, idx=i: self.on_enemy_clicked(idx))
            
            # 적 이름
            lbl_name = QLabel(enemy.name)
            lbl_name.setStyleSheet("font-weight: bold; font-size: 13px; color: #ecf0f1;")
            lbl_name.setAlignment(Qt.AlignCenter)
            
            # 체력바 & 방패 컨테이너 (이전 코드 동일)
            widget_hp_block = QWidget()
            layout_hp_block = QHBoxLayout(widget_hp_block)
            layout_hp_block.setContentsMargins(0, 0, 0, 0)
            layout_hp_block.setSpacing(5) 
            layout_hp_block.setAlignment(Qt.AlignCenter) 
            
            lbl_enemy_block = QLabel()
            lbl_enemy_block.setFixedWidth(55) 
            lbl_enemy_block.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            
            if enemy.block > 0:
                lbl_enemy_block.setText(f"🛡️ {enemy.block}")
                lbl_enemy_block.setStyleSheet("color: #3498db; font-weight: bold; font-size: 13px;")
            else:
                lbl_enemy_block.setText("") 
            
            bar_hp = QProgressBar()
            bar_hp.setMaximum(enemy.max_hp)
            bar_hp.setValue(enemy.hp)
            bar_hp.setFormat("%v / %m")
            bar_hp.setFixedWidth(130) 
            
            enemy_chunk_color = "#3498db" if enemy.block > 0 else "#e74c3c"
            bar_hp.setStyleSheet(f"""
                QProgressBar {{
                    background-color: #7f8c8d;
                    border-radius: 4px;
                    text-align: center;
                    color: #ffffff;
                    font-size: 11px;
                    font-weight: bold;
                    height: 18px;
                }}
                QProgressBar::chunk {{
                    background-color: {enemy_chunk_color};
                    border-radius: 4px;
                }}
            """)
            
            layout_hp_block.addWidget(lbl_enemy_block)
            layout_hp_block.addWidget(bar_hp)
            
            # 레이아웃에 조립
            vbox.addWidget(lbl_intent)
            vbox.addWidget(btn_enemy_img) # QLabel 대신 생성한 QPushButton 삽입
            vbox.addWidget(lbl_name)
            vbox.addWidget(widget_hp_block)
            
            self.layout_enemies.addWidget(frame_enemy)
    # --------------------------------------------------------
    # [이벤트 핸들러] 턴 종료 버튼 클릭 시
    # --------------------------------------------------------
    def on_end_turn_clicked(self):
        print(">> 턴 종료 버튼 클릭됨!")
        # 1. 플레이어에게 전기 구체가 있는지 확인 (애니메이션 대기 여부 판단)
        has_lightning = False
        if hasattr(self.battle.player, 'orbs'):
            for orb in self.battle.player.orbs:
                orb_name = getattr(orb, 'name', orb.__class__.__name__)
                if "전기" in orb_name or "Lightning" in orb_name:
                    has_lightning = True
                    break
                    
        # 2. battle.py의 로직을 실행하면서, 번개 이펙트 함수(리모컨)를 넘겨줍니다!
        self.battle.process_end_turn(vfx_callback=self.show_lightning_strike)

        # 3. 전기 구체가 없다면 애니메이션이 돌지 않으므로 여기서 즉시 화면 갱신
        if not has_lightning:
            self.update_ui()

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