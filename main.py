import sys
import os
import shutil
import json
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QFileDialog, QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, QSlider, QHBoxLayout
from PyQt6.QtGui import QPixmap, QDragEnterEvent, QDropEvent, QPalette, QColor
from PyQt6.QtCore import Qt
import subprocess

class MusicPlayer(QWidget):
    def __init__(self):
        super().__init__()

        self.init_ui()
        self.music_file = None
        self.album_folder = None
        self.album_cfg = "album.cfg"
        self.media_process = None

    def init_ui(self):
        self.setAcceptDrops(True)
        layout = QVBoxLayout()

        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor(30, 30, 30))
        self.setPalette(palette)

        self.label = QLabel("Drag and drop a music file or folder here")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setStyleSheet("color: red; font-size: 16px; border: 2px dashed red; padding: 10px;")

        self.open_button = QPushButton("Open File/Folder")
        self.open_button.setStyleSheet("background-color: red; color: white;")
        self.open_button.clicked.connect(self.open_file_folder)

        self.image_display = QGraphicsView()
        self.scene = QGraphicsScene()
        self.image_display.setScene(self.scene)

        self.play_button = QPushButton("Play")
        self.play_button.setStyleSheet("background-color: red; color: white;")
        self.play_button.clicked.connect(self.play_music)

        self.stop_button = QPushButton("Stop")
        self.stop_button.setStyleSheet("background-color: red; color: white;")
        self.stop_button.clicked.connect(self.stop_music)

        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(50)
        self.volume_slider.setStyleSheet("color: red;")
        self.volume_slider.valueChanged.connect(self.change_volume)

        controls_layout = QHBoxLayout()
        controls_layout.addWidget(self.play_button)
        controls_layout.addWidget(self.stop_button)
        controls_layout.addWidget(self.volume_slider)

        layout.addWidget(self.label)
        layout.addWidget(self.open_button)
        layout.addWidget(self.image_display)
        layout.addLayout(controls_layout)

        self.setLayout(layout)
        self.setWindowTitle("CassetteXpress")
        self.resize(800, 600)

    def open_file_folder(self):
        path = QFileDialog.getExistingDirectory(self, "Select Folder")

        if path:
            self.album_folder = path
            self.label.setText(f"Loaded folder: {path}")

            if not os.path.exists(os.path.join(path, self.album_cfg)):
                self.create_album_cfg()

            self.play_music()

    def create_album_cfg(self):
        cfg_path = os.path.join(self.album_folder, self.album_cfg)
        with open(cfg_path, 'w') as f:
            json.dump({}, f)

    def play_music(self):
        self.stop_music()

        music_files = [f for f in os.listdir(self.album_folder) if f.endswith(('.mp3', '.wav', '.flac'))]

        if music_files:
            self.music_file = os.path.join(self.album_folder, music_files[0])
            self.label.setText(f"Now Playing: {self.music_file}")

            self.media_process = subprocess.Popen(["ffplay", "-nodisp", "-autoexit", "-volume", str(self.volume_slider.value()), self.music_file], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            self.load_visual()

    def stop_music(self):
        if self.media_process:
            self.media_process.kill()
            self.media_process = None

    def change_volume(self, value):
        if self.media_process:
            self.media_process.kill()
            self.play_music()

    def load_visual(self):
        cfg_path = os.path.join(self.album_folder, self.album_cfg)

        with open(cfg_path, 'r') as f:
            album_data = json.load(f)

        visual_file = album_data.get(os.path.basename(self.music_file))

        if visual_file and os.path.exists(os.path.join(self.album_folder, visual_file)):
            image_path = os.path.join(self.album_folder, visual_file)
            pixmap = QPixmap(image_path)
            self.scene.clear()
            self.scene.addItem(QGraphicsPixmapItem(pixmap))

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()

            if os.path.isfile(file_path) and file_path.lower().endswith(('.png', '.jpg', '.gif', '.mp4')):
                self.assign_visual(file_path)

    def assign_visual(self, visual_path):
        visual_name = os.path.basename(visual_path)
        dest_path = os.path.join(self.album_folder, visual_name)

        if not os.path.exists(dest_path):
            shutil.copy(visual_path, dest_path)

        cfg_path = os.path.join(self.album_folder, self.album_cfg)

        with open(cfg_path, 'r') as f:
            album_data = json.load(f)

        album_data[os.path.basename(self.music_file)] = visual_name

        with open(cfg_path, 'w') as f:
            json.dump(album_data, f, indent=4)

        self.load_visual()

    def closeEvent(self, event):
        self.stop_music()
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    player = MusicPlayer()
    player.show()
    sys.exit(app.exec())