import sys, os, shutil
from PyQt5.QtWidgets import QApplication, QWidget, QTreeView, QFileSystemModel, QVBoxLayout, QSplitter, QMenu, QInputDialog, QMessageBox
from PyQt5.QtCore import QModelIndex, Qt

class FileSystemView(QWidget):
	def __init__(self, dirPath):
		super().__init__()
		appWidth = 200
		appHeight = 300
		self.setWindowTitle('File System Viewer')
		self.setGeometry(20, 300, appWidth, appHeight)


		self.model = QFileSystemModel()
		self.model.setRootPath(dirPath)
		self.tree =  QTreeView()
		self.model.setReadOnly(False)

		self.tree.setModel(self.model)
		self.tree.setRootIndex(self.model.index(dirPath))
		self.tree.setColumnWidth(0, 250)
		self.tree.setAlternatingRowColors(True)

		self.tree.setContextMenuPolicy(Qt.CustomContextMenu)
		self.tree.customContextMenuRequested.connect(self.open_context_menu)
		layout = QVBoxLayout()
		layout.addWidget(self.tree)
		self.setLayout(layout)

	def open_context_menu(self, position):
			index = self.tree.indexAt(position)
			menu = QMenu(self)

			new_folder_action = menu.addAction("New Folder")
			rename_action = menu.addAction("Rename")
			delete_action = menu.addAction("Delete")

			action = menu.exec_(self.tree.viewport().mapToGlobal(position))

			if action == new_folder_action:
				self.create_new_folder(index)
			elif action == rename_action:
				self.rename_item(index)
			elif action == delete_action:
				self.delete_item(index)

	def create_new_folder(self, index):
			"""Creates a new folder inside the selected directory."""
			if not index.isValid():

				target_path = self.model.rootPath()
			else:
				target_path = self.model.filePath(index)

				if os.path.isfile(target_path):
					target_path = os.path.dirname(target_path)

			folder_name, ok = QInputDialog.getText(self, "New Folder", "Enter folder name:")
			if ok and folder_name:
				new_folder_path = os.path.join(target_path, folder_name)
				try:
					os.makedirs(new_folder_path, exist_ok=False)
				except Exception as e:
					QMessageBox.warning(self, "Error", f"Could not create folder:\n{str(e)}")	

	def rename_item(self, index):
			"""Renames the selected file or folder."""
			if not index.isValid():
				return
			
			old_path = self.model.filePath(index)
			old_name = os.path.basename(old_path)
			
			new_name, ok = QInputDialog.getText(self, "Rename", "Enter new name:", text=old_name)
			if ok and new_name and new_name != old_name:
				parent_dir = os.path.dirname(old_path)
				new_path = os.path.join(parent_dir, new_name)
				try:
					os.rename(old_path, new_path)
				except Exception as e:
					QMessageBox.warning(self, "Error", f"Could not rename:\n{str(e)}")

	def delete_item(self, index):
			"""Deletes the selected file or folder (recursively if folder)."""
			if not index.isValid():
				return
			
			path = self.model.filePath(index)
			name = os.path.basename(path)
			
			confirm = QMessageBox.question(
				self, "Confirm Delete", 
				f"Are you sure you want to delete '{name}'?",
				QMessageBox.Yes | QMessageBox.No, QMessageBox.No
			)
			
			if confirm == QMessageBox.Yes:
				try:
					if os.path.isdir(path):
						shutil.rmtree(path)  
					else:
						os.remove(path)     
				except Exception as e:
					QMessageBox.warning(self, "Error", f"Could not delete:\n{str(e)}")

	def setRootPath(self, path):
		if os.path.exists(path):
			self.model.setRootPath(path)
			self.tree.setRootIndex(self.model.index(path))
		
if __name__ == '__main__':
	app = QApplication(sys.argv)
	dirPath = r''
	demo = FileSystemView(dirPath)
	demo.show()
	sys.exit(app.exec_())