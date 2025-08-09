import sys
import math
from PyQt6.QtWidgets import QGridLayout
from PyQt6.QtCore import Qt, QSize, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QFont, QFontDatabase, QIcon, QColor
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QScrollArea, 
                             QFrame, QSizePolicy, QMenu, QInputDialog)

class ModernCalculator(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Modern Calculator")
        self.setMinimumSize(350, 550)
        
        self.load_fonts()
        
        self.current_input = "0"
        self.stored_value = None
        self.current_operator = None
        self.calculation_history = []
        self.history_visible = False
        
        self.init_ui()
        
        self.apply_theme("dark")
        
    def load_fonts(self):
        font_id = QFontDatabase.addApplicationFont(":fonts/Montserrat-Regular.ttf")
        if font_id != -1:
            self.font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
        else:
            self.font_family = "Arial"
    
    def init_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        self.main_layout = QVBoxLayout(main_widget)
        self.main_layout.setContentsMargins(15, 15, 15, 15)
        self.main_layout.setSpacing(15)
        
        self.init_history_panel()
        
        self.init_display()
        
        self.init_buttons()
        
        self.init_menu()
    
    def init_history_panel(self):
        self.history_container = QFrame()
        self.history_container.setFrameShape(QFrame.Shape.StyledPanel)
        self.history_container.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.history_container.setFixedHeight(0)  # Start collapsed
        self.history_container.setStyleSheet("background-color: rgba(30, 30, 30, 150); border-radius: 10px;")
        
        self.history_scroll = QScrollArea()
        self.history_scroll.setWidgetResizable(True)
        self.history_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.history_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.history_scroll.setStyleSheet("border: none; background: transparent;")
        
        self.history_content = QWidget()
        self.history_layout = QVBoxLayout(self.history_content)
        self.history_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.history_layout.setContentsMargins(10, 10, 10, 10)
        self.history_layout.setSpacing(5)
        
        self.history_scroll.setWidget(self.history_content)
        
        history_container_layout = QVBoxLayout(self.history_container)
        history_container_layout.setContentsMargins(0, 0, 0, 0)
        history_container_layout.addWidget(self.history_scroll)
        
        self.main_layout.addWidget(self.history_container)
        
        self.toggle_history_btn = QPushButton("History ▼")
        self.toggle_history_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(60, 60, 60, 150);
                color: white;
                border: none;
                border-radius: 5px;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: rgba(80, 80, 80, 150);
            }
        """)
        self.toggle_history_btn.setFixedHeight(25)
        self.toggle_history_btn.clicked.connect(self.toggle_history)
        self.main_layout.addWidget(self.toggle_history_btn)
    
    def init_display(self):
        display_frame = QFrame()
        display_frame.setFrameShape(QFrame.Shape.StyledPanel)
        display_frame.setStyleSheet("""
            QFrame {
                background-color: rgba(40, 40, 40, 150);
                border-radius: 15px;
            }
        """)
        
        display_layout = QVBoxLayout(display_frame)
        display_layout.setContentsMargins(20, 15, 20, 15)
        display_layout.setSpacing(5)
        
        self.history_label = QLabel("")
        self.history_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.history_label.setStyleSheet("color: rgba(200, 200, 200, 180);")
        self.history_label.setFont(QFont(self.font_family, 12))
        display_layout.addWidget(self.history_label)
        
        self.display_label = QLabel("0")
        self.display_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.display_label.setStyleSheet("color: white;")
        self.display_label.setFont(QFont(self.font_family, 36, QFont.Weight.Bold))
        display_layout.addWidget(self.display_label)
        
        self.main_layout.addWidget(display_frame)
    
    def init_buttons(self):
        button_grid = QGridLayout()
        button_grid.setSpacing(12)
        
        buttons = [
            ('C', 0, 0), ('±', 0, 1), ('%', 0, 2), ('÷', 0, 3),
            ('7', 1, 0), ('8', 1, 1), ('9', 1, 2), ('×', 1, 3),
            ('4', 2, 0), ('5', 2, 1), ('6', 2, 2), ('-', 2, 3),
            ('1', 3, 0), ('2', 3, 1), ('3', 3, 2), ('+', 3, 3),
            ('⌫', 4, 0), ('0', 4, 1), ('.', 4, 2), ('=', 4, 3),
            ('√', 5, 0), ('x²', 5, 1), ('xⁿ', 5, 2), ('1/x', 5, 3)
        ]
        
        self.buttons = {}
        for text, row, col in buttons:
            btn = QPushButton(text)
            btn.setFixedSize(60, 60)
            btn.setFont(QFont(self.font_family, 18))
            
            if text in ['C', '±', '%', '⌫']:
                btn.setStyleSheet(self.get_button_style("function"))
            elif text in ['÷', '×', '-', '+', '=']:
                btn.setStyleSheet(self.get_button_style("operator"))
            elif text in ['√', 'x²', 'xⁿ', '1/x']:
                btn.setStyleSheet(self.get_button_style("scientific"))
            else:
                btn.setStyleSheet(self.get_button_style("number"))
            
            btn.clicked.connect(self.on_button_click)
            button_grid.addWidget(btn, row, col)
            self.buttons[text] = btn
        
        button_grid.setRowStretch(6, 1)
        
        self.main_layout.addLayout(button_grid)
    
    def get_button_style(self, button_type):
        base_style = """
            QPushButton {
                border: none;
                border-radius: 30px;
                font-weight: bold;
            }
            QPushButton:hover {
                opacity: 0.9;
            }
            QPushButton:pressed {
                opacity: 0.8;
            }
        """
        
        if button_type == "number":
            return f"""
                {base_style}
                QPushButton {{
                    background-color: #505050;
                    color: white;
                }}
                QPushButton:hover {{
                    background-color: #606060;
                }}
            """
        elif button_type == "operator":
            return f"""
                {base_style}
                QPushButton {{
                    background-color: #FF9500;
                    color: white;
                }}
                QPushButton:hover {{
                    background-color: #FFAA33;
                }}
            """
        elif button_type == "function":
            return f"""
                {base_style}
                QPushButton {{
                    background-color: #D4D4D2;
                    color: black;
                }}
                QPushButton:hover {{
                    background-color: #E4E4E2;
                }}
            """
        elif button_type == "scientific":
            return f"""
                {base_style}
                QPushButton {{
                    background-color: #3A3A3A;
                    color: white;
                }}
                QPushButton:hover {{
                    background-color: #4A4A4A;
                }}
            """
    
    def init_menu(self):
        menu_bar = self.menuBar()
        
        settings_menu = QMenu("Settings", self)
        
        theme_menu = settings_menu.addMenu("Theme")
        theme_menu.addAction("Dark", lambda: self.apply_theme("dark"))
        theme_menu.addAction("Light", lambda: self.apply_theme("light"))
        theme_menu.addAction("Blue", lambda: self.apply_theme("blue"))
        theme_menu.addAction("Custom...", self.set_custom_theme)
        
        settings_menu.addAction("Font Size...", self.set_font_size)
        
        menu_bar.addMenu(settings_menu)
    
    def apply_theme(self, theme_name):
        if theme_name == "dark":
            self.setStyleSheet("""
                QMainWindow {
                    background-color: #121212;
                }
                QLabel {
                    color: white;
                }
                QMenuBar {
                    background-color: #1E1E1E;
                    color: white;
                }
                QMenuBar::item:selected {
                    background-color: #333333;
                }
                QMenu {
                    background-color: #1E1E1E;
                    color: white;
                    border: 1px solid #333;
                }
                QMenu::item:selected {
                    background-color: #333333;
                }
            """)
        elif theme_name == "light":
            self.setStyleSheet("""
                QMainWindow {
                    background-color: #F5F5F5;
                }
                QLabel {
                    color: black;
                }
                QMenuBar {
                    background-color: #E0E0E0;
                    color: black;
                }
                QMenuBar::item:selected {
                    background-color: #CCCCCC;
                }
                QMenu {
                    background-color: #E0E0E0;
                    color: black;
                    border: 1px solid #999;
                }
                QMenu::item:selected {
                    background-color: #CCCCCC;
                }
            """)
            for text, btn in self.buttons.items():
                if text in ['C', '±', '%', '⌫']:
                    btn.setStyleSheet(self.get_button_style("function"))
                elif text in ['÷', '×', '-', '+', '=']:
                    btn.setStyleSheet(self.get_button_style("operator"))
                elif text in ['√', 'x²', 'xⁿ', '1/x']:
                    btn.setStyleSheet(self.get_button_style("scientific"))
                else:
                    btn.setStyleSheet(self.get_button_style("number"))
        elif theme_name == "blue":
            self.setStyleSheet("""
                QMainWindow {
                    background-color: #0A192F;
                }
                QLabel {
                    color: #CCD6F6;
                }
                QMenuBar {
                    background-color: #112240;
                    color: #CCD6F6;
                }
                QMenuBar::item:selected {
                    background-color: #233554;
                }
                QMenu {
                    background-color: #112240;
                    color: #CCD6F6;
                    border: 1px solid #233554;
                }
                QMenu::item:selected {
                    background-color: #233554;
                }
            """)
    
    def set_custom_theme(self):
        color = QColor.getColorDialog(QColor(18, 18, 18), self, "Select Background Color")
        if color.isValid():
            r, g, b = color.red(), color.green(), color.blue()
            self.setStyleSheet(f"""
                QMainWindow {{
                    background-color: rgb({r}, {g}, {b});
                }}
                QLabel {{
                    color: {'white' if (r + g + b) < 384 else 'black'};
                }}
                QMenuBar {{
                    background-color: rgb({r*0.8}, {g*0.8}, {b*0.8});
                    color: {'white' if (r + g + b) < 384 else 'black'};
                }}
                QMenuBar::item:selected {{
                    background-color: rgb({r*0.6}, {g*0.6}, {b*0.6});
                }}
                QMenu {{
                    background-color: rgb({r*0.8}, {g*0.8}, {b*0.8});
                    color: {'white' if (r + g + b) < 384 else 'black'};
                    border: 1px solid rgb({r*0.6}, {g*0.6}, {b*0.6});
                }}
                QMenu::item:selected {{
                    background-color: rgb({r*0.6}, {g*0.6}, {b*0.6});
                }}
            """)
    
    def set_font_size(self):
        size, ok = QInputDialog.getInt(self, "Font Size", "Enter font size (12-36):", 
                                      self.display_label.font().pointSize(), 12, 36)
        if ok:
            self.display_label.setFont(QFont(self.font_family, size, QFont.Weight.Bold))
    
    def toggle_history(self):
        self.history_visible = not self.history_visible
        
        animation = QPropertyAnimation(self.history_container, b"maximumHeight")
        animation.setDuration(300)
        animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
        
        if self.history_visible:
            self.toggle_history_btn.setText("History ▲")
            content_height = self.history_content.sizeHint().height() + 20
            max_height = min(200, content_height)  # Cap at 200px
            animation.setStartValue(0)
            animation.setEndValue(max_height)
        else:
            self.toggle_history_btn.setText("History ▼")
            animation.setStartValue(self.history_container.height())
            animation.setEndValue(0)
        
        animation.start()
    
    def add_to_history(self, expression, result):
        self.calculation_history.append((expression, result))
        
        for i in reversed(range(self.history_layout.count())): 
            self.history_layout.itemAt(i).widget().setParent(None)
        
        for expr, res in reversed(self.calculation_history[-10:]):  # Show last 10 items
            history_item = QLabel(f"{expr} = {res}")
            history_item.setStyleSheet("color: white; background: transparent;")
            history_item.setFont(QFont(self.font_family, 10))
            self.history_layout.addWidget(history_item)
    
    def on_button_click(self):
        sender = self.sender()
        button_text = sender.text()
        
        self.animate_button(sender)
        
        # Handle button press
        if button_text in '0123456789':
            self.handle_number(button_text)
        elif button_text == '.':
            self.handle_decimal()
        elif button_text in ['+', '-', '×', '÷']:
            self.handle_operator(button_text)
        elif button_text == '=':
            self.handle_equals()
        elif button_text == 'C':
            self.handle_clear()
        elif button_text == '⌫':
            self.handle_backspace()
        elif button_text == '±':
            self.handle_plus_minus()
        elif button_text == '%':
            self.handle_percent()
        elif button_text == '√':
            self.handle_square_root()
        elif button_text == 'x²':
            self.handle_power(2)
        elif button_text == 'xⁿ':
            self.handle_power(None)  
        elif button_text == '1/x':
            self.handle_reciprocal()
    
    def animate_button(self, button):
        animation = QPropertyAnimation(button, b"size")
        animation.setDuration(100)
        animation.setEasingCurve(QEasingCurve.Type.OutQuad)
        
        original_size = button.size()
        animation.setStartValue(QSize(original_size.width() - 5, original_size.height() - 5))
        animation.setEndValue(original_size)
        
        animation.start()
    
    def handle_number(self, num):
        if self.current_input == "0":
            self.current_input = num
        else:
            self.current_input += num
        
        self.update_display()
    
    def handle_decimal(self):
        if '.' not in self.current_input:
            self.current_input += '.'
            self.update_display()
    
    def handle_operator(self, op):
        if self.stored_value is None:
            self.stored_value = float(self.current_input)
        else:
            self.calculate_result()
        
        self.current_operator = op
        self.current_input = "0"
        self.history_label.setText(f"{self.stored_value} {self.current_operator}")
    
    def handle_equals(self):
        if self.stored_value is not None and self.current_operator is not None:
            expression = f"{self.stored_value} {self.current_operator} {self.current_input}"
            self.calculate_result()
            self.add_to_history(expression, self.current_input)
            self.history_label.setText("")
    
    def handle_clear(self):
        self.current_input = "0"
        self.stored_value = None
        self.current_operator = None
        self.history_label.setText("")
        self.update_display()
    
    def handle_backspace(self):
        if len(self.current_input) > 1:
            self.current_input = self.current_input[:-1]
        else:
            self.current_input = "0"
        self.update_display()
    
    def handle_plus_minus(self):
        if self.current_input != "0":
            if self.current_input[0] == '-':
                self.current_input = self.current_input[1:]
            else:
                self.current_input = '-' + self.current_input
            self.update_display()
    
    def handle_percent(self):
        value = float(self.current_input) / 100
        self.current_input = str(value)
        self.update_display()
    
    def handle_square_root(self):
        value = math.sqrt(float(self.current_input))
        self.current_input = str(value)
        self.add_to_history(f"√({self.current_input})", self.current_input)
        self.update_display()
    
    def handle_power(self, exponent):
        if exponent is None:
            exponent, ok = QInputDialog.getDouble(self, "Exponent", "Enter exponent:", 2, -100, 100, 2)
            if not ok:
                return
        
        base = float(self.current_input)
        result = math.pow(base, exponent)
        self.current_input = str(result)
        self.add_to_history(f"{base}^{exponent}", self.current_input)
        self.update_display()
    
    def handle_reciprocal(self):
        value = 1 / float(self.current_input)
        self.current_input = str(value)
        self.add_to_history(f"1/({self.current_input})", self.current_input)
        self.update_display()
    
    def calculate_result(self):
        if self.stored_value is None or self.current_operator is None:
            return
        
        a = self.stored_value
        b = float(self.current_input)
        
        if self.current_operator == '+':
            result = a + b
        elif self.current_operator == '-':
            result = a - b
        elif self.current_operator == '×':
            result = a * b
        elif self.current_operator == '÷':
            result = a / b if b != 0 else float('nan')
        
        self.current_input = str(result)
        self.stored_value = result
        self.current_operator = None
        self.update_display()
    
    def update_display(self):
        # Format the number to remove trailing .0 if it's an integer
        try:
            num = float(self.current_input)
            if num.is_integer():
                self.display_label.setText(str(int(num)))
            else:
                self.display_label.setText(self.current_input)
        except ValueError:
            self.display_label.setText(self.current_input)
    
    def keyPressEvent(self, event):
        key = event.key()
        
        key_mapping = {
            Qt.Key.Key_0: '0',
            Qt.Key.Key_1: '1',
            Qt.Key.Key_2: '2',
            Qt.Key.Key_3: '3',
            Qt.Key.Key_4: '4',
            Qt.Key.Key_5: '5',
            Qt.Key.Key_6: '6',
            Qt.Key.Key_7: '7',
            Qt.Key.Key_8: '8',
            Qt.Key.Key_9: '9',
            Qt.Key.Key_Plus: '+',
            Qt.Key.Key_Minus: '-',
            Qt.Key.Key_Asterisk: '×',
            Qt.Key.Key_Slash: '÷',
            Qt.Key.Key_Period: '.',
            Qt.Key.Key_Enter: '=',
            Qt.Key.Key_Return: '=',
            Qt.Key.Key_Backspace: '⌫',
            Qt.Key.Key_Escape: 'C',
            Qt.Key.Key_P: '%',
            Qt.Key.Key_S: '√'
        }
        
        if key in key_mapping:
            button_text = key_mapping[key]
            if button_text in self.buttons:
                self.buttons[button_text].click()
        elif key == Qt.Key.Key_H:
            self.toggle_history()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    app.setStyle("Fusion")
    
    calculator = ModernCalculator()
    calculator.show()
    
    sys.exit(app.exec())