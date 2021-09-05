import sys
import os

import PySide2
from PySide2.QtCore import *
from PySide2.QtWidgets import *

class DirectoryTreeView(QTreeView):
    """
    Treeview file system UI
    default path: 프로젝트 메뉴에서 사용자가 설정한 폴더 경로
    """
    def __init__(self):
        QTreeView.__init__(self)        
        self.model = QFileSystemModel()

        self.setModel(self.model)
        self.setRootIndex(self.model.index(''))
        self.model.setReadOnly(False)

        self.setSelectionMode(self.SingleSelection)
        self.setDragDropMode(QAbstractItemView.InternalMove)
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)

    def dragEnterEvent(self, event):
        """
        파일을 drag 할 수 있게 함
        """
        m = event.mimeData()
        if m.hasUrls():
            for url in m.urls():
                if url.isLocalFile():
                    event.accept()
                    return
        event.ignore()

    def dropEvent(self, event):
        """
        drag 한 파일의 경로를 output합니다.
        """
        if event.source():
            QTreeView.dropEvent(self, event)
        else:
            ix = self.indexAt(event.pos())
            if not self.model().isDir(ix):
                ix = ix.parent()
            pathDir = self.model().filePath(ix)
            m = event.mimeData()
            if m.hasUrls():
                urlLocals = [url for url in m.urls() if url.isLocalFile()]
                accepted = False
                for urlLocal in urlLocals:
                    path = urlLocal.toLocalFile()
                    info = QFileInfo(path)
                    n_path = QDir(pathDir).filePath(info.fileName())
                    o_path = info.absoluteFilePath()
                    if n_path == o_path:
                        continue
                    if info.isDir():
                        QDir().rename(o_path, n_path)
                    else:
                        qfile = QFile(o_path)
                        if QFile(n_path).exists():
                            n_path += "(copy)"
                        qfile.rename(n_path)
                    accepted = True
                if accepted:
                    event.acceptProposedAction()

    # 프로젝트 바꿀 시 경로 반영
    def change_root_index(self, path):
        self.model.setRootPath(path)
        self.setRootIndex(self.model.index(path))


sys.path.append(os.path.abspath(os.path.dirname(__file__) + "\\..\\"))
dirname = os.path.dirname(PySide2.__file__)
plugin_path = os.path.join(dirname, 'plugins', 'platforms')
os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = plugin_path


if __name__ == '__main__':
    app = QApplication(sys.argv)

    mainWindow = DirectoryTreeView()
    mainWindow.show()

    app.exec_()