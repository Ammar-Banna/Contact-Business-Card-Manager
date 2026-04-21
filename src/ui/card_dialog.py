import os
import subprocess
import tempfile
import logging
from PyQt6.QtPrintSupport import QPrinter
from PyQt6.QtWidgets import QDialog, QFrame, QPushButton, QLabel, QGraphicsDropShadowEffect, QApplication, QFileDialog, QMessageBox
from PyQt6.QtCore import Qt, QPoint, QRectF, QSize, QSizeF, QUrl, QPropertyAnimation
from PyQt6.QtGui import QColor, QDesktopServices, QGuiApplication, QPageSize, QPainter, QPixmap, QIcon, QFontDatabase
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas

logger = logging.getLogger(__name__)
drag_pos = None

class BusinessCardDialog(QDialog):
    def __init__(self, data, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Business Card")
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.p = 14
        self.setStyleSheet(f"""
            #bottomButtons {{
                font-size: {self.p}px;
                font-weight: bold;
                color: white;
                background-color: #7c321e;
            }}
            #bottomButtons:hover {{
                background-color: #9c321e;
            }}
            #bottomButtons:pressed {{
                background-color: #6c321e;
            }}
            QToolTip {{
                color: white;
                background-color: #2c2c2c; 
            }}
        """)
        
        font_id = QFontDatabase.addApplicationFont("assets/fonts/cocon-next-arabic.ttf")
        if font_id != -1:
            font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
        else:
            font_family = "Arial"
        
        self.setFixedSize(38*self.p, 32*self.p)
        
        screen = QApplication.primaryScreen().availableGeometry()
        self.move((screen.width() - self.width()) // 2, (screen.height() - self.height()) // 2)

        self.copy_frame = QFrame(self)
        self.share_button = QPushButton(self)
        self.print_frame = QFrame(self)
        self.export_frame = QFrame(self)
        
        self.card = QFrame(self)
        self.card.setObjectName("mainCard")
        self.card.setStyleSheet(f"""
            #mainCard {{
                background: qlineargradient(
                    x1:0, y1:0, x2:0, y2:1,
                    stop:0 white,
                    stop:0.8 white,
                    stop:0.8001 #8c321e,
                    stop:1 #8c321e
                );
            }}
            QWidget {{
                background: transparent;
            }}
        """)
        self.card.resize(36*self.p, 20*self.p)
        self.card.move((self.width() - self.card.width()) // 2, 0)
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setXOffset(0)
        shadow.setYOffset(5)
        shadow.setColor(QColor(0, 0, 0, 150))
        self.card.setGraphicsEffect(shadow)

        self.logo_label = QLabel(self.card)
        try:
            pixmap = QPixmap("assets/icons/UHB_logo.png")
            self.logo_label.setPixmap(pixmap)
        except Exception as e:
            logger.error(f"Logo file 'assets/icons/UHB_logo.png' not found: {e}")
            self.logo_label.setText("University Logo")
        self.logo_label.setFixedSize(14*self.p, 12*self.p)
        self.logo_label.setScaledContents(True)
        self.logo_label.move(self.card.width() - self.logo_label.width() - self.p, self.p*2)

        self.close_button = QPushButton(self)
        self.close_button.setText("✕")
        self.close_button.setFixedSize((self.p//2)*3, (self.p//2)*3)
        self.close_button.setStyleSheet(f"""
            QPushButton {{
                font-family: Segoe UI;
                background-color: lightgray;
                color: white;
                border: none;
                border-radius: {(self.p//2)*3 // 2}px;
                font-size: {(self.p//3)*2}px;
            }}
            QPushButton:hover {{
                background-color: #e0e0e0;
            }}
        """)
        self.close_button.move(self.card.width() - self.close_button.width() - (self.p//2), (self.p//2))
        self.close_button.clicked.connect(self.close)

        self.name_label = QLabel(self.card)
        self.name_label.setText(data.get("Name", "N/A"))
        self.name_label.setStyleSheet(f"color: #8c321e; font-size: {self.p+self.p}px; font-weight: bold; font-family: '{font_family}';")
        self.name_label.adjustSize()
        self.name_label.move(self.p * 2, self.p*2)

        self.email_icon_label = QLabel(self.card)
        try:
            pixmap = QPixmap("assets/icons/email_icon.png")
            self.email_icon_label.setPixmap(pixmap)
        except:
            self.email_icon_label.setText("✉️")
        self.email_icon_label.setFixedSize(self.p+self.p, self.p+self.p)
        self.email_icon_label.setScaledContents(True)
        self.email_icon_label.move(self.p * 2, self.name_label.y() + self.name_label.height() + self.p)

        self.email_label = QLabel(self.card)
        email_text = data.get("Email", "N/A")
        self.email_label.setText(email_text)
        self.email_label.setStyleSheet(f"color: #8c321e; font-size: {(self.p/2)+self.p}px; font-family: '{font_family}';")
        self.email_label.adjustSize()
        self.email_label.move(self.email_icon_label.x() + self.email_icon_label.width() + self.p, 
                              self.name_label.y() + self.name_label.height() + self.p)
        self.email_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextBrowserInteraction)
        self.email_label.setCursor(Qt.CursorShape.PointingHandCursor)
        def open_email(event):
            QDesktopServices.openUrl(QUrl(f"mailto:{self.email_label.text()}"))
            self.close()
        self.email_label.mousePressEvent = open_email

        self.phone_icon_label = QLabel(self.card)
        try:
            pixmap = QPixmap("assets/icons/phone_icon.png")
            self.phone_icon_label.setPixmap(pixmap)
        except:
            self.phone_icon_label.setText("📞")
        self.phone_icon_label.setFixedSize(self.p+self.p, self.p+self.p)
        self.phone_icon_label.setScaledContents(True)
        self.phone_icon_label.move(self.p * 2, self.email_icon_label.y() + self.email_icon_label.height() + self.p)

        self.phone_label = QLabel(self.card)
        phone_text = data.get("Phone", "N/A")
        self.phone_label.setText(phone_text)
        self.phone_label.setStyleSheet(f"color: #8c321e; font-size: {(self.p/2)+self.p}px; font-family: '{font_family}';")
        self.phone_label.adjustSize()
        self.phone_label.move(self.phone_icon_label.x() + self.phone_icon_label.width() + self.p, 
                              self.email_icon_label.y() + self.email_icon_label.height() + self.p)
        self.phone_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextBrowserInteraction)
        self.phone_label.setCursor(Qt.CursorShape.PointingHandCursor)
        def open_whatsapp(event):
            number = self.phone_label.text().replace("+", "").replace(" ", "")
            whatsapp_path = os.path.expandvars(r"%LocalAppData%\WhatsApp\WhatsApp.exe")
            if os.path.exists(whatsapp_path):
                subprocess.Popen([whatsapp_path])
            else:
                QDesktopServices.openUrl(QUrl(f"https://wa.me/{number}"))
            self.close()
        self.phone_label.mousePressEvent = open_whatsapp
            
        self.telephone_icon_label = QLabel(self.card)
        try:
            pixmap = QPixmap("assets/icons/telephone_icon.png")
            self.telephone_icon_label.setPixmap(pixmap)
        except:
            self.telephone_icon_label.setText("☎️")
        self.telephone_icon_label.setFixedSize(self.p+self.p, self.p+self.p)
        self.telephone_icon_label.setScaledContents(True)
        self.telephone_icon_label.move(self.p * 2, self.phone_icon_label.y() + self.phone_icon_label.height() + self.p)

        self.telephone_label = QLabel(self.card)
        self.telephone_label.setText("+966 13 720 " + str(data.get("Number", "N/A")))
        self.telephone_label.setStyleSheet(f"color: #8c321e; font-size: {(self.p/2)+self.p}px; font-family: '{font_family}';")
        self.telephone_label.adjustSize()
        self.telephone_label.move(self.telephone_icon_label.x() + self.telephone_icon_label.width() + self.p, 
                                  self.phone_icon_label.y() + self.phone_icon_label.height() + self.p)
        
        self.department = QLabel(self.card)
        self.department.setText(data.get("Department", "N/A"))
        self.department.setStyleSheet(f"color: white; font-size: {(self.p/2)+self.p}px; font-family: '{font_family}';")
        self.department.adjustSize()
        self.department.move((self.card.width() - self.department.width()) // 2, 
                           self.card.height() - self.department.height() - self.p)
        
        self.setup_print_frame()
        self.setup_share_button()
        self.setup_export_frame()
        self.setup_copy_frame()

    def setup_print_frame(self):
        self.print_frame.setFixedSize(7*self.p, 12*self.p)
        self.print_frame.move(self.p*2, 11*self.p)
        self.print_frame.setStyleSheet(f"QFrame {{ background-color: #7c321e; border-radius: {self.p}px; }}")

        self.print_button = QPushButton(self.print_frame)
        self.print_button.setObjectName("bottomButtons")
        self.print_button.setIcon(QIcon("assets/icons/print_icon.png"))
        self.print_button.setIconSize(QSize(self.p*2, self.p*2))
        self.print_button.setFixedSize(7*self.p, 3*self.p)
        self.print_button.move(0, 9*self.p)
        self.print_button.setStyleSheet(f"QPushButton {{border-bottom-left-radius: {self.p}px; border-bottom-right-radius: {self.p}px;}}")
        self.print_button.setToolTip("Print")
        self.print_button.clicked.connect(lambda: self.move_frame(self.print_frame, 11*self.p, 17*self.p))

        self.print_as_A4_button = QPushButton(self.print_frame)
        self.print_as_A4_button.setObjectName("bottomButtons")
        self.print_as_A4_button.setText("A4")
        self.print_as_A4_button.setFixedSize(7*self.p, 3*self.p)
        self.print_as_A4_button.move(0, 6*self.p)
        self.print_as_A4_button.setToolTip("Print A4 size paper")
        self.print_as_A4_button.clicked.connect(lambda: self.print_card("A4"))

        self.print_as_card_button = QPushButton(self.print_frame)
        self.print_as_card_button.setObjectName("bottomButtons")
        self.print_as_card_button.setText("Card")
        self.print_as_card_button.setFixedSize(7*self.p, 3*self.p)
        self.print_as_card_button.move(0, 3*self.p)
        self.print_as_card_button.setToolTip("Print 9x5 size card")
        self.print_as_card_button.clicked.connect(lambda: self.print_card("Card"))

    def setup_share_button(self):
        self.share_button.setObjectName("bottomButtons")
        self.share_button.setIcon(QIcon("assets/icons/share_icon.png"))
        self.share_button.setIconSize(QSize(self.p*2, self.p*2))
        self.share_button.setFixedSize(7*self.p, 5*self.p)
        self.share_button.move(self.p*11, 18*self.p)
        self.share_button.setStyleSheet(f"""
            QPushButton {{
                background-color: #7c321e;
                border-radius: {self.p}px;
                padding-top: {self.p*2}px;
            }}
            QPushButton:hover {{ background-color: #9c321e; }}
            QPushButton:pressed {{ background-color: #6c321e; }}
        """)
        self.share_button.setToolTip("Share")
        self.share_button.clicked.connect(self.share_card)

    def setup_export_frame(self):
        self.export_frame.setFixedSize(7*self.p, 15*self.p)
        self.export_frame.move(self.p*20, 8*self.p)
        self.export_frame.setStyleSheet(f"QFrame {{ background-color: #7c321e; border-radius: {self.p}px; }}")

        self.export_button = QPushButton(self.export_frame)
        self.export_button.setObjectName("bottomButtons")
        self.export_button.setIcon(QIcon("assets/icons/export_icon.png"))
        self.export_button.setIconSize(QSize(self.p*2, self.p*2))
        self.export_button.setFixedSize(7*self.p, 3*self.p)
        self.export_button.move(0, 12*self.p)
        self.export_button.setStyleSheet(f"QPushButton {{border-bottom-left-radius: {self.p}px; border-bottom-right-radius: {self.p}px;}}")
        self.export_button.setToolTip("Export")
        self.export_button.clicked.connect(lambda: self.move_frame(self.export_frame, 8*self.p, 17*self.p))

        self.export_as_image_button = QPushButton(self.export_frame)
        self.export_as_image_button.setObjectName("bottomButtons")
        self.export_as_image_button.setText("Image")
        self.export_as_image_button.setFixedSize(7*self.p, 3*self.p)
        self.export_as_image_button.move(0, 9*self.p)
        self.export_as_image_button.setToolTip("Export as PNG image")
        self.export_as_image_button.clicked.connect(self.export_as_image)

        self.export_as_A4_pdf_button = QPushButton(self.export_frame)
        self.export_as_A4_pdf_button.setObjectName("bottomButtons")
        self.export_as_A4_pdf_button.setText("A4")
        self.export_as_A4_pdf_button.setFixedSize(7*self.p, 3*self.p)
        self.export_as_A4_pdf_button.move(0, 6*self.p)
        self.export_as_A4_pdf_button.setToolTip("Export as A4 size PDF")
        self.export_as_A4_pdf_button.clicked.connect(lambda: self.export_as_pdf((21*cm, 29.7*cm), "A4"))

        self.export_as_card_pdf_button = QPushButton(self.export_frame)
        self.export_as_card_pdf_button.setObjectName("bottomButtons")
        self.export_as_card_pdf_button.setText("Card")
        self.export_as_card_pdf_button.setFixedSize(7*self.p, 3*self.p)
        self.export_as_card_pdf_button.move(0, 3*self.p)
        self.export_as_card_pdf_button.setToolTip("Export as 9x5 size PDF")
        self.export_as_card_pdf_button.clicked.connect(lambda: self.export_as_pdf((9*cm, 5*cm), "Card"))

    def setup_copy_frame(self):
        self.copy_frame.setFixedSize(7*self.p, 15*self.p)
        self.copy_frame.move(self.p*29, 8*self.p)
        self.copy_frame.setStyleSheet(f"QFrame {{ background-color: #7c321e; border-radius: {self.p}px; }}")

        self.copy_button = QPushButton(self.copy_frame)
        self.copy_button.setObjectName("bottomButtons")
        self.copy_button.setIcon(QIcon("assets/icons/copy_icon.png"))
        self.copy_button.setIconSize(QSize(self.p*2, self.p*2))
        self.copy_button.setFixedSize(7*self.p, 3*self.p)
        self.copy_button.move(0, 12*self.p)
        self.copy_button.setStyleSheet(f"QPushButton {{border-bottom-left-radius: {self.p}px; border-bottom-right-radius: {self.p}px;}}")
        self.copy_button.setToolTip("Copy")
        self.copy_button.clicked.connect(lambda: self.move_frame(self.copy_frame, 8*self.p, 17*self.p))

        self.copy_email_button = QPushButton(self.copy_frame)
        self.copy_email_button.setObjectName("bottomButtons")
        self.copy_email_button.setText("Email")
        self.copy_email_button.setFixedSize(7*self.p, 3*self.p)
        self.copy_email_button.move(0, 9*self.p)
        self.copy_email_button.setToolTip("Copy email to clipboard")
        self.copy_email_button.clicked.connect(self.copy_email_to_clipboard)

        self.copy_number_button = QPushButton(self.copy_frame)
        self.copy_number_button.setObjectName("bottomButtons")
        self.copy_number_button.setText("Number")
        self.copy_number_button.setFixedSize(7*self.p, 3*self.p)
        self.copy_number_button.move(0, 6*self.p)
        self.copy_number_button.setToolTip("Copy number to clipboard")
        self.copy_number_button.clicked.connect(self.copy_phone_to_clipboard)

        self.copy_card_button = QPushButton(self.copy_frame)
        self.copy_card_button.setObjectName("bottomButtons")
        self.copy_card_button.setText("Card")
        self.copy_card_button.setFixedSize(7*self.p, 3*self.p)
        self.copy_card_button.move(0, 3*self.p)
        self.copy_card_button.setToolTip("Copy card as image to clipboard")
        self.copy_card_button.clicked.connect(self.copy_frame_to_clipboard)

    def mousePressEvent(self, event):
        global drag_pos
        if event.button() == Qt.MouseButton.LeftButton:
            drag_pos = event.globalPosition().toPoint() - self.pos()
            event.accept()

    def mouseMoveEvent(self, event):
        global drag_pos
        if drag_pos is not None and event.buttons() & Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - drag_pos)
            event.accept()

    def mouseReleaseEvent(self, event):
        global drag_pos
        drag_pos = None
        event.accept()

    def move_frame(self, frame, start_y, end_y):
        current_y = frame.y()
        if current_y == start_y:
            start_pos = QPoint(frame.x(), start_y)
            end_pos = QPoint(frame.x(), end_y)
        else:
            start_pos = QPoint(frame.x(), end_y)
            end_pos = QPoint(frame.x(), start_y)
        animation = QPropertyAnimation(frame, b"pos")
        animation.setDuration(70)
        animation.setStartValue(start_pos)
        animation.setEndValue(end_pos)
        animation.start()
        self.animation = animation

    def print_card(self, size_type):
        try:
            pixmap = self.card.grab()
            printer = QPrinter(QPrinter.PrinterMode.HighResolution)
            if size_type == "A4":
                page_size = QPageSize(QSizeF(210, 297), QPageSize.Unit.Millimeter)
                printer.setPageSize(page_size)
            else:
                card_size = QPageSize(QSizeF(90, 50), QPageSize.Unit.Millimeter)
                printer.setPageSize(card_size)
            
            painter = QPainter()
            if not painter.begin(printer):
                raise RuntimeError("Failed to start printing process")
            
            resolution = printer.resolution()
            cm_to_points = 28.35
            scale_factor = resolution / 72.0
            
            page_rect = printer.pageRect(QPrinter.Unit.DevicePixel)
            card_ratio = pixmap.width() / pixmap.height()
            
            if size_type == "A4":
                card_width = 9 * cm_to_points * scale_factor
                card_height = card_width / card_ratio
                x = 1 * cm_to_points * scale_factor
                y = 1 * cm_to_points * scale_factor
            else:
                card_width = page_rect.width()
                card_height = page_rect.height()
                x = 0
                y = 0
            
            target_rect = QRectF(x, y, card_width, card_height)
            source_rect = QRectF(0, 0, pixmap.width(), pixmap.height())
            painter.drawPixmap(target_rect, pixmap, source_rect)
            
            painter.end()
        except Exception as e:
            QMessageBox.critical(self, "Printing Error", f"An error occurred while trying to print: {str(e)}")

    def share_card(self):
        pixmap = self.card.grab()
        temp_dir = tempfile.gettempdir()
        temp_file_path = os.path.join(temp_dir, "business_card_share.png")

        if os.path.exists(temp_file_path):
            try:
                os.remove(temp_file_path)
            except Exception as e:
                logger.error(f"Failed to delete old file: {e}")

        pixmap.save(temp_file_path)
        try:
            if os.name == 'nt':
                subprocess.run(['start', '', temp_file_path], shell=True)
            elif os.name == 'posix':
                subprocess.run(['open', temp_file_path] if os.uname().sysname == 'Darwin' else ['xdg-open', temp_file_path])
        except Exception as e:
            logger.error(f"An error occurred while opening the image: {e}")
        self.close()

    def export_as_image(self):
        try:
            file_path, _ = QFileDialog.getSaveFileName(self, "Save Image", "", "PNG Files (*.png)")
            if file_path:
                if not file_path.endswith(".png"):
                    file_path += ".png"
                pixmap = self.card.grab()
                if pixmap.isNull():
                    raise ValueError("Failed to capture card image")
                pixmap.save(file_path, "PNG")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to export image: {str(e)}")

    def export_as_pdf(self, page_size, size_name):
        temp_image = None
        try:
            file_path, _ = QFileDialog.getSaveFileName(self, f"Save PDF ({size_name})", "", "PDF Files (*.pdf)")
            if file_path:
                if not file_path.endswith(".pdf"):
                    file_path += ".pdf"
                temp_image = "temp_card.png"
                pixmap = self.card.grab()
                if pixmap.isNull():
                    raise ValueError("Failed to capture card appearance")
                pixmap.save(temp_image, "PNG")
                c = canvas.Canvas(file_path, pagesize=page_size)
                img_width, img_height = pixmap.width(), pixmap.height()
                if img_width == 0 or img_height == 0:
                    raise ValueError("Invalid card dimensions")
                y = page_size[1] - (5 * cm)
                c.drawImage(temp_image, 0, y, (img_width // img_width) * (9 * cm), (img_height // img_height) * (5 * cm))
                c.showPage()
                c.save()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to export PDF file: {str(e)}")
        finally:
            if temp_image and os.path.exists(temp_image):
                try:
                    os.remove(temp_image)
                except Exception as e:
                    logger.error(f"Failed to remove temporary file: {e}")

    def copy_email_to_clipboard(self):
        clipboard = QGuiApplication.clipboard()
        clipboard.setText(self.email_label.text())

    def copy_phone_to_clipboard(self):
        clipboard = QGuiApplication.clipboard()
        clipboard.setText(self.phone_label.text())

    def copy_frame_to_clipboard(self):
        pixmap = self.card.grab()
        clipboard = QGuiApplication.clipboard()
        clipboard.setPixmap(pixmap)