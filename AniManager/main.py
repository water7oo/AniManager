from PyQt5.QtWidgets import QFileDialog, QWidget, QMainWindow, QApplication, QListWidget, QTreeView, QInputDialog, QMessageBox, QVBoxLayout, QFrame

from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import pyqtSignal, Qt, QSettings
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QIcon
from pathlib import Path
import sys, os, json, shutil, datetime, pytz, time
from file_viewer import FileSystemView


class invoiceGen(QMainWindow):

    def __init__(self):
        super(invoiceGen,self).__init__()
        uic.loadUi('AniManager/invoice.ui', self)


class folderConfig(QMainWindow):
    jsonLoaded = pyqtSignal(dict)

    def __init__(self):
        super(folderConfig,self).__init__()
        uic.loadUi('AniManager/folderLoader.ui',self)
        self.setWindowTitle('Configure Work Folder')
        # self.setWindowIcon(QIcon())
        
        self.settings = QSettings('AniManager','folderManager' )

        self.directory = self.directoryEntry
        self.tempdirectory = self.directoryEntry_2
        self.targetdirectory = self.directoryEntry_3
        self.animTempDirectory = self.directoryEntry_4


        self.openDir = self.openDirectoryBtn
        self.openDir2 = self.openDirectoryBtn_2
        self.openDir3 = self.openDirectoryBtn_3
        self.openDir4 = self.openDirectoryBtn_4

        self.multiAddBtn = self.multiFolderAdd

        savedEntry1 = self.settings.value('saved word', type=str)
        self.directory.setText(savedEntry1)

        self.addFolderBtn = self.findChild(QtWidgets.QPushButton, 'addFolderBtn')

        self.addFolderBtn.clicked.connect(self.add_tempFolders)
        self.openDir.clicked.connect((lambda: self._open_folder_dialog(self.directory)))
        self.openDir2.clicked.connect((lambda: self._open_folder_dialog(self.tempdirectory)))
        self.openDir3.clicked.connect(lambda: self._open_folder_dialog(self.targetdirectory))
        self.openDir4.clicked.connect(lambda: self._open_file_dialog(self.animTempDirectory))
        self.multiAddBtn.clicked.connect(self.addMultiFiles)

        
        dirPath = self.directory.text()

        #  trying to implement text field restoration when closing th window
        if not os.path.exists(dirPath):
            dirPath = os.getcwd()
            self.directory.setText(dirPath)




        self.file_widget = FileSystemView(dirPath)
        fileContainer = self.findChild(QWidget, 'fileViewerContainer')

        if fileContainer:
            if fileContainer.layout() is not None:
                fileContainer.layout().addWidget(self.file_widget)
            else:
                print("no container")
                layout = QVBoxLayout(fileContainer)
                layout.addWidget(self.file_widget)
        else:
            print("no container found")

        self.directory.textChanged.connect(self.on_directory_changed)
 

    def _open_folder_dialog(self, line_edit):

            dir_path = QFileDialog.getExistingDirectory(self, "Select Directory", line_edit.text())
            if dir_path:
                line_edit.setText(dir_path)

                if line_edit == self.directory:
                    self.update_file_viewer(dir_path)

    def _open_file_dialog(self, line_edit):

            dir_path, _ = QFileDialog.getOpenFileName(self, 'Select Animation File', line_edit.text(), filter='', options=QFileDialog.Options())
            if dir_path:
                line_edit.setText(dir_path)

                if line_edit == self.directory:
                    self.update_file_viewer(dir_path)

    def on_directory_changed(self, path):

            if os.path.exists(path):
                self.update_file_viewer(path)

    def update_file_viewer(self, path):
  
            if hasattr(self.file_widget, 'setRootPath'):
                self.file_widget.setRootPath(path)

    def add_tempFolders(self):
            work_dir = self.directoryEntry.text()
            temp_dir = self.directoryEntry_2.text()
            projectName = self.showName.text()
            episodeNum = self.episodeNum.text()

            if not work_dir or not temp_dir:
                return

            if not os.path.exists(temp_dir) or not os.path.exists(work_dir):
                return

            try:
                for item in os.listdir(temp_dir):
                    source_path = os.path.join(temp_dir, item)

                    if os.path.isdir(source_path):

                        target_path = os.path.join(work_dir, projectName, episodeNum)
                        shutil.copytree(source_path, target_path, dirs_exist_ok=True)

                    else:

                        shutil.copy2(source_path, target_path)
                        
                print("All files and folders copied recursively successfully!")
                
            except Exception as e:
                print(f"Error copying files and folders: {e}")

    def addMultiFiles(self):
        self.currDir = self.directoryEntry_3.text()
        self.cutPrefixText = self.cutPrefix.text()
        self.cutSuffixText = self.cutSuffix.text()
        self.startingNum = self.startingFolderNum.value()
        tempFilePath = self.animTempDirectory.text()

        amount = self.cutAmount.value()

        if not os.path.isdir(self.currDir):
            return

        tempFileName = os.path.basename(tempFilePath)
        tempFileNameEXT = Path(tempFileName).suffix
        print(tempFileNameEXT)

        for i in range(amount):
            # give user the option for long form or short form (for now long form)
            folderName = f"{self.cutPrefixText}c{self.startingNum + i}{self.cutSuffixText}"
            mainFolder = os.path.join(self.currDir, folderName)


            os.makedirs(mainFolder, exist_ok=True)

            if os.path.isfile(tempFilePath):

                animTempFileName = f"{self.cutPrefixText}c{self.startingNum + i}{self.cutSuffixText}{tempFileNameEXT}"
                destination = os.path.join(mainFolder, animTempFileName)
                shutil.copy(tempFilePath, destination)

    
                



    def addFolder(self):
        defaultText = self.directoryLabel.text()
        if self.directoryEntry.text() != "":
            print("Folder Added")
            os.chdir(self.directoryEntry.text())
            os.mkdir('added_folder')
           


            self.directoryLabel.setText("Directory Set")
        else:
            print("please select a folder directory")
            self.directoryLabel.setText(defaultText)

    def saveEvent(self, event):
        self.settings.setValue('directory', self.directory.text())
        event.accept()

        
    def make_dir_structure(self):
        """Creates folders recursively based on your metadata JSON schema."""
        base_dir_str = self.directoryEntry.text()

        if not base_dir_str:
            print("Please select a target directory first.")
            return

        if not self.loaded_json_data:
            print("No JSON configuration loaded yet.")
            return

        base_path = Path(base_dir_str)

        def parse_node(current_path, node):
            """Recursively reads the node schema and creates directories."""
            folder_name = node.get("rootFileName") or node.get("fileName")
            
            if not folder_name:
                return
            target_path = current_path / folder_name
            target_path.mkdir(parents=True, exist_ok=True)

            children = node.get("children", [])
            for child in children:
                parse_node(target_path, child)

        try:
            parse_node(base_path, self.loaded_json_data)
            print("Directory structure successfully created!")
            self.directoryLabel.setText("Structure created successfully!")
        except Exception as e:
            print(f"Failed to create directory structure: {e}")


            

class mainManager(QMainWindow):
    def __init__(self):
        super(mainManager,self).__init__()
        uic.loadUi('AniManager/main.ui', self)
        self.w = None
        self.loaded_json_data = None
        self.setWindowTitle('AniManager')
        self.setWindowIcon(QIcon('AniManager\winIcon.png'))

        
        self.statusBar = self.statusBar()

        self.statusBar.addWidget(self.displayTime)
        self.convertDisplayTime()


        self.folderConfigBtn = self.findChild(QtWidgets.QPushButton, 'configureFolderBtn')


 
    
        self.invoiceGenBtn.clicked.connect(self.showInvoiceGen)
        self.folderConfigBtn.clicked.connect(self.showFolderConfig)



        self.show()


    def showInvoiceGen(self, checked):
        self.w = invoiceGen()
        self.w.show()
        print("Initializing Invoice Generator")

    def showFolderConfig(self, checked):
        self.w = folderConfig()
        self.w.jsonLoaded.connect(self.handle_loaded_json)
        self.w.show()
        print("Initializing Folder config")



    # while loop is preventing the rest of the program from loading
    def convertDisplayTime(self):
        # while True:

            currTime = datetime.datetime.now()
            tz = pytz.timezone('US/Eastern')
            dt = tz.localize(currTime)
            new_tz = pytz.timezone('Japan')

            converted = dt.astimezone(new_tz).strftime("%a %m/%d/%y %H:%M%p")
            self.displayTime.setText(str(converted))
            print(f"  {converted}" , end="\r")
            # time.sleep(1)


    def handle_loaded_json(self, data):
        self.loaded_json_data = data

        


        


app = QtWidgets.QApplication(sys.argv)
w = mainManager()
w.show()
app.exec_()
