import time
import logging
import pandas as pd
from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtWidgets import QApplication

logger = logging.getLogger(__name__)

class LoadingThread(QThread):
    progress_updated = pyqtSignal(int)
    loading_complete = pyqtSignal()
    error_occurred = pyqtSignal(str)
    
    def run(self):
        try:
            logger.debug("Starting background loading...")
            self.progress_updated.emit(0)
            QApplication.processEvents()
            
            tasks = [
                ("Loading Excel file", self.load_excel),
                ("Initializing resources", self.init_resources),
                ("Setting up UI components", self.setup_components),
            ]
            
            for i, (task_name, task) in enumerate(tasks, 1):
                logger.debug(f"Executing task {i}/{len(tasks)}: {task_name}")
                if i == 1:
                    self.df = task()
                else:
                    task()
                self.progress_updated.emit(int((i / len(tasks)) * 100))
                time.sleep(0.05)
            
            logger.debug(f"Excel columns: {list(self.df.columns)}")
            self.loading_complete.emit()
            
        except FileNotFoundError as e:
            logger.error(f"Error loading resource: {e}")
            self.error_occurred.emit("Error: File not found")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            self.error_occurred.emit("Error: Loading failed")
    
    def load_excel(self):
        df = pd.read_excel('data/Phone directory.xlsx')
        df.columns = df.columns.str.strip()
        return df
    
    def init_resources(self):
        time.sleep(0.2)
    
    def setup_components(self):
        pass