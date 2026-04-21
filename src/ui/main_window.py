import logging
import os
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QPushButton, QLineEdit, QTreeWidget, 
                             QTreeWidgetItem, QFrame, QProgressBar, QHeaderView, 
                             QApplication, QMessageBox)
from PyQt6.QtCore import Qt, QRect, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QPixmap, QIcon, QKeySequence, QShortcut

from src.core.threads import LoadingThread
from src.ui.card_dialog import BusinessCardDialog

logger = logging.getLogger(__name__)

class PhoneDirectoryApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.df = None
        self.is_minimized = False
        self.original_geometry = None

        self.setWindowIcon(QIcon("assets/icons/icon.ico"))
        
        screen = QApplication.primaryScreen()
        self.screen_height = screen.availableGeometry().height()
        
        self.init_splash_screen()
        self.show()
        QApplication.processEvents()
        
        self.start_loading()
    
    def init_splash_screen(self):
        self.setGeometry(0, 0, 350, int(self.screen_height))
        self.setFixedWidth(370)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setStyleSheet("background-color: #f0f0f0;")
        
        self.splash_widget = QWidget()
        self.setCentralWidget(self.splash_widget)
        
        splash_layout = QVBoxLayout(self.splash_widget)
        splash_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.splash_logo = QLabel()
        try:
            pixmap = QPixmap("assets/icons/UHBE.png")
            self.splash_logo.setPixmap(pixmap)
            self.splash_logo.setScaledContents(True)
            self.splash_logo.setFixedSize(288, 210)
        except:
            logger.error("Splash logo file 'assets/icons/UHBE.png' not found.")
            self.splash_logo.setText("Loading...")
            self.splash_logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        splash_layout.addWidget(self.splash_logo)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.progress_bar.setFixedSize(270, 4)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: none;
                background-color: #e0e0e0;
                border-radius: 2px;
            }
            QProgressBar::chunk {
                background-color: #8c321e;
                border-radius: 2px;
            }
        """)
        splash_layout.addWidget(self.progress_bar, alignment=Qt.AlignmentFlag.AlignCenter)
    
    def start_loading(self):
        self.loading_thread = LoadingThread()
        self.loading_thread.progress_updated.connect(self.update_progress)
        self.loading_thread.loading_complete.connect(self.show_main_content)
        self.loading_thread.error_occurred.connect(self.show_error)
        self.loading_thread.start()
    
    def update_progress(self, value):
        self.progress_bar.setValue(value)
    
    def show_error(self, error_msg):
        self.splash_logo.setText(error_msg)
        self.splash_logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
    
    def show_main_content(self):
        self.df = self.loading_thread.df
        required_columns = ["Name", "Number", "Email"]
        missing_columns = [col for col in required_columns if col not in self.df.columns]
        if missing_columns:
            logger.error(f"Missing columns in Excel file: {missing_columns}")
            self.show_error(f"Error: Columns not found in the file: {', '.join(missing_columns)}")
            return
        self.init_main_ui()
        
        self.splash_widget.deleteLater()
        self.setCentralWidget(self.main_widget)
    
    def init_main_ui(self):
        self.main_widget = QWidget()
        main_layout = QVBoxLayout(self.main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        self.create_title_bar(main_layout)
        
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(15, 15, 15, 15)
        
        self.uhb_logo_label = QLabel()
        try:
            pixmap = QPixmap("assets/icons/UHBE_logo.png")
            self.uhb_logo_label.setPixmap(pixmap)
            self.uhb_logo_label.setScaledContents(True)
            self.uhb_logo_label.setFixedSize(300, 85)
        except:
            logger.error("Logo file 'assets/icons/UHBE_logo.png' not found.")
            self.uhb_logo_label.setText("UHB Logo")
        
        self.uhb_logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        content_layout.addWidget(self.uhb_logo_label)
        
        self.title_label = QLabel("UHB Phone Directory")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setStyleSheet("""
            QLabel {
                background-color: #8c321e;
                color: white;
                font-size: 25px;
                font-weight: bold;
                border-radius: 25px;
                padding: 15px;
                margin: 10px 20px;
            }
        """)
        content_layout.addWidget(self.title_label)
        
        self.create_search_frame(content_layout)
        self.create_results_tree(content_layout)
        
        self.status_label = QLabel("E-Learning and Digital Transformation")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("""
            QLabel {
                background-color: #ecf0f1;
                color: #7f8c8d;
                font-size: 16px;
                border-radius: 10px;
                padding: 8px;
                margin: 5px 0px;
            }
        """)
        content_layout.addWidget(self.status_label)
        
        main_layout.addWidget(content_widget)
        self.update_tree()
    
    def create_title_bar(self, main_layout):
        self.title_bar = QFrame()
        self.title_bar.setFixedHeight(30)
        self.title_bar.setStyleSheet("background-color: #f0f0f0;")
        
        title_layout = QHBoxLayout(self.title_bar)
        title_layout.setContentsMargins(10, 5, 5, 5)
        
        try:
            icon_label = QLabel()
            pixmap = QPixmap("assets/icons/icon.png")
            icon_label.setPixmap(pixmap)
            icon_label.setScaledContents(True)
            icon_label.setFixedSize(21, 21)
            title_layout.addWidget(icon_label)
        except:
            logger.error("Icon file 'assets/icons/icon.png' not found.")
            
        title_layout.addStretch()
        
        title_text = QLabel("UHB Phone Directory")
        title_text.setStyleSheet("color: #340B01; font-weight: bold; font-size: 16px;")
        title_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_layout.addWidget(title_text)
        
        title_layout.addStretch()
        
        self.minimize_button = QPushButton("▼")
        self.minimize_button.setFixedSize(30, 20)
        self.minimize_button.setStyleSheet("""
            QPushButton {
                font-family: Segoe UI;
                background-color: #d3d3d3;
                color: #7f8c8d;
                border: none;
                border-radius: 5px;
                font-size: 13px;
            }
            QPushButton:hover { background-color: #e0e0e0; }
        """)
        self.minimize_button.clicked.connect(self.minimize_to_bar)
        title_layout.addWidget(self.minimize_button)
        
        close_button = QPushButton("✕")
        close_button.setFixedSize(30, 20)
        close_button.setStyleSheet("""
            QPushButton {
                font-family: Segoe UI;
                background-color: #8c321e;
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 13px;
            }
            QPushButton:hover { background-color: #be3415; }
        """)
        close_button.clicked.connect(self.close)
        title_layout.addWidget(close_button)
        
        main_layout.addWidget(self.title_bar)
    
    def create_search_frame(self, content_layout):
        search_frame = QFrame()
        search_frame.setStyleSheet("""
            QFrame {
                background-color: #e0e0e0;
                border-radius: 20px;
                padding: 5px;
            }
        """)
        
        search_layout = QHBoxLayout(search_frame)
        search_layout.setContentsMargins(1, 1, 1, 1)
            
        self.search_entry = QLineEdit()
        self.search_entry.setPlaceholderText("Search by name or number...")
        self.search_entry.setFixedSize(290, 35)
        self.search_entry.setStyleSheet("""
            QLineEdit {
                border: none;
                border-radius: 15px;
                padding: 8px;
                font-size: 18px;
                background-color: white;
                color: black;
            }
        """)
        self.search_entry.textChanged.connect(self.update_tree)
        search_layout.addWidget(self.search_entry)
        search_layout.addStretch()
        self.setup_shortcuts()

        try:
            search_icon = QLabel()
            pixmap = QPixmap("assets/icons/search_icon.png")
            search_icon.setPixmap(pixmap)
            search_icon.setScaledContents(True)
            search_icon.setFixedSize(35, 35)
            search_layout.addWidget(search_icon)
        except:
            logger.error("Search icon file 'assets/icons/search_icon.png' not found.")
        
        content_layout.addWidget(search_frame)
    
    def setup_shortcuts(self):
        select_all = QShortcut(QKeySequence.StandardKey.SelectAll, self.search_entry)
        select_all.activated.connect(self.search_entry.selectAll)
        copy = QShortcut(QKeySequence.StandardKey.Copy, self.search_entry)
        copy.activated.connect(self.search_entry.copy)
        paste = QShortcut(QKeySequence.StandardKey.Paste, self.search_entry)
        paste.activated.connect(self.search_entry.paste)
        cut = QShortcut(QKeySequence.StandardKey.Cut, self.search_entry)
        cut.activated.connect(self.search_entry.cut)
    
    def create_results_tree(self, content_layout):
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Name", "Number"])
        self.tree.setRootIsDecorated(False)
        self.tree.setAlternatingRowColors(True)
        self.tree.setHeaderHidden(True)
        
        header = self.tree.header()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        header.resizeSection(0, 260)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        header.resizeSection(1, 50)
        
        self.tree.setStyleSheet("""
            QTreeWidget {
                background-color: white;
                color: #340B01;
                font-size: 20px;
                border-radius: 15px;
                border: 2px solid #e0e0e0;
                padding: 5px;
                outline: none;
            }
            QTreeWidget::item {
                height: 35px;
                padding: 5px;
                border-bottom: 1px solid #f0f0f0;
            }
            QTreeWidget::item:hover {
                background-color: #8c321e;
                color: white;
            }
            QTreeWidget::item:selected {
                background-color: #8c321e;
                color: white;
            }
            QTreeWidget QScrollBar:vertical {
                background: #ffffff;
                width: 8px;
                border: none;
                margin-top: 5px;
                margin-bottom: 5px;
            }
            QTreeWidget QScrollBar::handle:vertical {
                background: #7f8c8d;
                min-height: 20px;
                border-radius: 4px;
            }
            QTreeWidget QScrollBar::handle:vertical:hover {
                background: #8c321e;
            }
            QTreeWidget QScrollBar::add-line:vertical, 
            QTreeWidget QScrollBar::sub-line:vertical {
                background: none;
                height: 0px;
            }
            QTreeWidget QScrollBar::add-page:vertical, 
            QTreeWidget QScrollBar::sub-page:vertical {
                background: transparent;
            }
        """)
        
        self.tree.itemClicked.connect(self.show_business_card)
        content_layout.addWidget(self.tree, 1)
    
    def show_business_card(self, item, column):
        if self.df is not None:
            try:
                number = item.text(1)
                person_data = self.df[self.df['Number'].astype(str) == str(number)]
                if not person_data.empty:
                    data = person_data.iloc[0].to_dict()
                    logger.debug(f"Selected person data: {data}")
                    dialog = BusinessCardDialog(data, self)
                    dialog.exec()
                else:
                    logger.warning(f"No data found for number: {number}")
                    self.status_label.setText(f"Error: No data for number {number}")
                    QMessageBox.warning(self, "Error", f"No data for number {number}")
            except KeyError as e:
                logger.error(f"Column not found in DataFrame: {e}")
                self.status_label.setText(f"Error: Field not found in data: {e}")
                QMessageBox.critical(self, "Error", f"Field not found in data: {e}")
    
    def update_tree(self):
        if self.df is None:
            return
            
        search_term = self.search_entry.text().strip().lower()
        
        try:
            if search_term:
                filtered_df = self.df[
                    self.df['Name'].str.lower().str.contains(search_term, na=False, regex=False) |
                    self.df['Number'].astype(str).str.contains(search_term, na=False, regex=False)
                ]
            else:
                filtered_df = self.df
            
            self.tree.clear()
            
            for _, row in filtered_df.iterrows():
                item = QTreeWidgetItem([str(row["Name"]), str(row["Number"])])
                self.tree.addTopLevelItem(item)
        except KeyError as e:
            logger.error(f"Error updating tree: Column not found - {e}")
            self.status_label.setText(f"Error: Please check column names in Excel file ({e})")
        except Exception as e:
            logger.error(f"Unexpected error in update_tree: {e}")
            self.status_label.setText(f"Error: Failed to update the list ({e})")
    
    def minimize_to_bar(self):
        if not self.is_minimized:
            self.original_geometry = self.geometry()
            
            for widget in self.main_widget.findChildren(QWidget):
                if widget != self.title_bar and widget.parent() == self.main_widget:
                    widget.hide()
            
            layout = self.main_widget.layout()
            layout.setAlignment(Qt.AlignmentFlag.AlignTop)

            self.animation = QPropertyAnimation(self, b"geometry")
            self.animation.setDuration(300)
            self.animation.setStartValue(self.geometry())
            
            bar_height = 30
            target_y = self.screen_height - bar_height
            end_geometry = QRect(0, target_y, 350, bar_height)
            self.animation.setEndValue(end_geometry)
            self.animation.setEasingCurve(QEasingCurve.Type.OutCubic)
            
            self.animation.finished.connect(self.minimize_finished)
            self.animation.start()
    
    def minimize_finished(self):
        self.minimize_button.setText("▲")
        self.minimize_button.clicked.disconnect()
        self.minimize_button.clicked.connect(self.restore_window)
        self.is_minimized = True
    
    def restore_window(self):
        if self.is_minimized:
            self.animation = QPropertyAnimation(self, b"geometry")
            self.animation.setDuration(300)
            self.animation.setStartValue(self.geometry())
            self.animation.setEndValue(self.original_geometry)
            self.animation.setEasingCurve(QEasingCurve.Type.OutCubic)
            
            self.animation.finished.connect(self.restore_finished)
            self.animation.start()
    
    def restore_finished(self):
        for widget in self.main_widget.findChildren(QWidget):
            if widget != self.title_bar and widget.parent() == self.main_widget:
                widget.show()
        
        self.minimize_button.setText("▼")
        self.minimize_button.clicked.disconnect()
        self.minimize_button.clicked.connect(self.minimize_to_bar)
        self.is_minimized = False