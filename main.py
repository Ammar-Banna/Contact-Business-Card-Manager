import sys
import logging
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFontDatabase, QFont
from PyQt6.QtCore import Qt
from src.ui.main_window import PhoneDirectoryApp

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    sys.argv += ['-style', 'windowsvista']
    app = QApplication(sys.argv)
    
    font_id = QFontDatabase.addApplicationFont("assets/fonts/cocon-next-arabic.ttf")
    if font_id != -1:
        font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
        app.setFont(QFont(font_family, 10))
        
    app.setApplicationName("UHB Phone Directory")
    app.setOrganizationName("UHB")
    
    app.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
    
    window = PhoneDirectoryApp()
    window.show()
    app.processEvents()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()