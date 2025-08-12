import sys
import os
import re

from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QFileDialog,
    QGraphicsView,
    QGraphicsScene,
    QGraphicsPixmapItem,
    QGraphicsPathItem,
    QGraphicsRectItem
)

from PyQt6.QtGui import (
    QImage,
    QPixmap,
    QColor,
    QPainterPath,
    QPen,
    QCursor
)

from PyQt6.QtCore import (
    Qt,
    QPointF,
    QRectF
)

from PyQt6.QtSvg import QSvgRenderer

import numpy as np

from ui_AlignRef import Ui_MainWindow


from datetime import datetime
import shutil
from xml.etree import ElementTree as ET

from collections import defaultdict

from PyQt6.QtGui import QShortcut, QKeySequence

from PIL import Image, ImageOps
import pydicom
import time

import csv


import cv2

from pydicom.dataset import Dataset, FileDataset





    
def extract_all_numbers(s):
    return [int(num) for num in re.findall(r'\d+', s)]





class CustomGraphicsView(QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setScene(QGraphicsScene(self))
        
        

    def wheelEvent(self, event):
        modifiers = QApplication.keyboardModifiers()
        delta = event.angleDelta().y()
        if modifiers == Qt.KeyboardModifier.ControlModifier:
            self.scale(1.25 if delta > 0 else 0.8, 1.25 if delta > 0 else 0.8)
        elif modifiers == Qt.KeyboardModifier.ShiftModifier:
            self.horizontalScrollBar().setValue(
                self.horizontalScrollBar().value() - delta
            )
        elif modifiers == Qt.KeyboardModifier.NoModifier:
            self.verticalScrollBar().setValue(
                self.verticalScrollBar().value() - delta
            )
        event.accept()



class ResizableRectItem(QGraphicsRectItem):
    handle_size = 8  # ハンドル（リサイズ用小さい四角）のサイズ

    def __init__(self, rect, main_window=None):
        super().__init__(rect)
        self.main_window = main_window
        self.setFlags(
            QGraphicsRectItem.GraphicsItemFlag.ItemIsMovable |
            QGraphicsRectItem.GraphicsItemFlag.ItemIsSelectable |
            QGraphicsRectItem.GraphicsItemFlag.ItemSendsGeometryChanges
        )
        self.setPen(QPen(QColor('red'), 2, Qt.PenStyle.DashLine))
        
        # ハンドル位置（四隅 + 辺の中央 ＝ 全8か所）
        self.handles = {
            'top_left': QRectF(0, 0, self.handle_size, self.handle_size),
            'top_right': QRectF(0, 0, self.handle_size, self.handle_size),
            'bottom_left': QRectF(0, 0, self.handle_size, self.handle_size),
            'bottom_right': QRectF(0, 0, self.handle_size, self.handle_size),
            'top_mid': QRectF(0, 0, self.handle_size, self.handle_size),
            'bottom_mid': QRectF(0, 0, self.handle_size, self.handle_size),
            'left_mid': QRectF(0, 0, self.handle_size, self.handle_size),
            'right_mid': QRectF(0, 0, self.handle_size, self.handle_size)
        }

        
        
        

        self.active_handle = None
        self.update_handles()

    
                
    def update_handles(self):
        rect = self.rect()
        self.handles['top_left'].moveTopLeft(rect.topLeft())
        self.handles['top_right'].moveTopRight(rect.topRight())
        self.handles['bottom_left'].moveBottomLeft(rect.bottomLeft())
        self.handles['bottom_right'].moveBottomRight(rect.bottomRight())
        self.handles['top_mid'].moveCenter(QPointF((rect.left() + rect.right()) / 2, rect.top()))
        self.handles['bottom_mid'].moveCenter(QPointF((rect.left() + rect.right()) / 2, rect.bottom()))
        self.handles['left_mid'].moveCenter(QPointF(rect.left(), (rect.top() + rect.bottom()) / 2))
        self.handles['right_mid'].moveCenter(QPointF(rect.right(), (rect.top() + rect.bottom()) / 2))



    def paint(self, painter, option, widget=None):
        super().paint(painter, option, widget)

        # ハンドルを描画
        painter.setBrush(QColor('white'))
        painter.setPen(QPen(QColor('black')))
        for handle in self.handles.values():
            painter.drawRect(handle)


    
    def mousePressEvent(self, event):
        pos = event.pos()
        self.active_handle = None
        for name, handle_rect in self.handles.items():
            if handle_rect.contains(pos):
                self.active_handle = name
                break
        super().mousePressEvent(event)


    
    def mouseReleaseEvent(self, event):
        self.active_handle = None
        super().mouseReleaseEvent(event)  # ✅ 最初に！
    
        if self.main_window:
            self.main_window.crop_box_global_rect = self.rect()
            
            self.main_window.display_current_image()



    def mouseMoveEvent(self, event):
        if self.active_handle:
            self.resize_rect(event.pos())
            self.update_handles()
        else:
            super().mouseMoveEvent(event)
        
    def resize_rect(self, pos):
        rect = self.rect()
    
        if self.active_handle == 'top_left':
            rect.setTopLeft(pos)
        elif self.active_handle == 'top_right':
            rect.setTopRight(pos)
        elif self.active_handle == 'bottom_left':
            rect.setBottomLeft(pos)
        elif self.active_handle == 'bottom_right':
            rect.setBottomRight(pos)
        elif self.active_handle == 'top_mid':
            rect.setTop(pos.y())
        elif self.active_handle == 'bottom_mid':
            rect.setBottom(pos.y())
        elif self.active_handle == 'left_mid':
            rect.setLeft(pos.x())
        elif self.active_handle == 'right_mid':
            rect.setRight(pos.x())
    
        # ✅ これを追加！
        self.prepareGeometryChange()
        self.setRect(rect.normalized())







class Main(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()

        self.setupUi(self)
        
        self.combo_canvas_bg.currentTextChanged.connect(lambda color: setattr(self, 'canvas_bg_color', color))
        self.canvas_bg_color = self.combo_canvas_bg.currentText()
        
        self.crop_box_coords = None  # (x1, y1, x2, y2)
        self.original_images_backup = {}  # Undo用に元画像をバックアップ

        self.box_mode = False
        self.box_points = []   
        self.temp_box_item = None
        self.last_box_prompt = None
        self.stored_boxes = []
        
        self.crop_mode = False
        self.crop_box_points = []
        self.crop_box_coords = None
        self.current_crop_rect_item = None
        
        
        self.btn_start_crop.clicked.connect(self.start_crop_mode)
        self.btn_clear_crop_box.clicked.connect(self.clear_crop_box)
        self.btn_apply_crop.clicked.connect(self.apply_crop)
    
        
        self.btn_undo_crop.clicked.connect(self.undo_crop)
        
        self.btn_export_aligned.clicked.connect(self.export_aligned_images)

        self.resized_images_cache = {}  #画像読み込み・キャンバス調整済み画像を格納する辞書　初期化
        self.image_paths = {}
        self.image_sizes = {}
        
        self.canvas_width = 0
        self.canvas_height = 0
        
        self.recording_position = False
        self.initial_transform = None  # QTransform
        self.current_translation = QPointF(0, 0)
        self.current_rotation_deg = 0.0

        self.image_pristine = True
        self.ignore_spinbox_change = False
        
        # 一括トラッキング用
        self.batch_object_data = []  # 各オブジェクトの情報を辞書形式で保持
        self.box_per_frame = {}  # 例: {0: ((x1,y1), (x2,y2)), 1: ((x1,y1), (x2,y2)), ...}
        self.installEventFilter(self)

        # ✅ graphicsView を CustomGraphicsView に差し替え
        layout = self.central_widget.layout()
        index = layout.indexOf(self.graphicsView)
        layout.removeWidget(self.graphicsView)
        self.graphicsView.deleteLater()

        self.graphicsView = CustomGraphicsView()
        layout.insertWidget(index, self.graphicsView)

        # ✅ Scene を作成
        self.scene = QGraphicsScene()
        self.graphicsView.setScene(self.scene)

        self.btn_load_images.clicked.connect(self.load_image_folder)
        self.btn_expand_canvas.clicked.connect(self.expand_canvas_and_reload)
        self.btn_fit_to_window.clicked.connect(self.fit_view_to_window)
                
        self.btn_prev_image.clicked.connect(self.overlay_previous_image)
        self.btn_next_image.clicked.connect(self.overlay_next_image)
        self.btn_clear_overlay.clicked.connect(self.clear_overlay)
        
        self.btn_start_record_position.clicked.connect(self.start_recording_position)
        self.btn_end_record_position.clicked.connect(self.finish_recording_position)
        self.btn_cancel_record_position.clicked.connect(self.cancel_recording_position)
                
        self.btn_set_pos_start.clicked.connect(self.set_position_start)
        self.btn_set_pos_end.clicked.connect(self.set_position_end)
        self.btn_apply_pos_rotation.clicked.connect(self.apply_recorded_position_to_range)
        
        self.btn_cancel_apply_pos.clicked.connect(self.cancel_applied_position)
        
        
        #Undo Redoのための変数
        self.undo_stack = {}  # 例: {'0001': [svg_text_before_edit, ...]}


        # ✅ 状態保持
        self.image_paths = {}
        self.mask_paths = {}
        self.current_index = 0

        self.graphicsView.viewport().installEventFilter(self)



        
        self.modified_svg_trees = {}
        self.path_elements_by_color = {}
        
        self.pixmap_cache = {}        # 画像キャッシュ
        self.svg_renderer_cache = {}  # SVGレンダリングキャッシュ
        
        
        now = datetime.now().strftime("%Y%m%d_%H%M%S")
        # self.output_mask_dir = os.path.join(os.getcwd(), f"masks_{now}")
        # os.makedirs(self.output_mask_dir, exist_ok=True)
        self.default_output_dir = os.getcwd()
        
        self.redo_stack = defaultdict(list)  # 🔁 Redoline用のスタック（画像ごと）
        
        self.calibration_mode = False
        self.calibration_points = []
        
        # self.mm_per_px = 1.0  # 初期値：1px = 1mm
        # self.z_spacing_mm = 1.0
        
        self.mm_per_px = None
        self.z_spacing_mm = None
        
        # self.interpolation_factor = 2  # Z方向の線形補完の倍率
        
        # 🔽 マウス移動を検知するために必要
        self.graphicsView.setMouseTracking(True)
        self.graphicsView.viewport().setMouseTracking(True)
        
        # 🔽 キャリブレーション用初期化
        self.temp_line_item = None
        self.calibration_points = []
    
        undo_shortcut = QShortcut(QKeySequence("Ctrl+Z"), self)
        undo_shortcut.activated.connect(self.smart_undo)
    
   
        self.label_status.setText("Ready.")
        
        self.loaded_images = {}  # 🔧 画像読み込み管理用の辞書
        

        
        self.overlay_image_item = None  # ← 重ねる画像表示用
        self.crop_box_per_frame = {}  # ← 画像キーごとの赤枠情報を保持
        self.crop_box_global_rect = None  # ✅ これを追加！
        
        self.expand_count = 0
 

    

    def load_image_folder(self):
        
        import pathlib
    
        folder = QFileDialog.getExistingDirectory(self, "Select Image Folder")
        if not folder:
            return
                
        input_folder = pathlib.Path(folder)
        self.input_folder_name = input_folder.name        
    
        # ✅ Canvas 背景色
        canvas_color_raw = self.combo_canvas_bg.currentText()
        print(f"[DEBUG] selected_color raw: {canvas_color_raw}")
        canvas_color = canvas_color_raw.lower()
        fill_rgb = (255, 255, 255) if canvas_color == "white" else (0, 0, 0)
    
        input_folder = pathlib.Path(folder)
        jpg_folder = pathlib.Path(os.getcwd()) / f"{input_folder.name}jpg"
    
        valid_exts = {".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp", ".dcm"}
        self.image_paths = {}
        self.image_sizes = {}
        self.resized_images_cache = {}
    
        max_width = 0
        max_height = 0
    
        # 1st pass: サイズ確認
        for filename in sorted(os.listdir(folder)):
            ext = pathlib.Path(filename).suffix.lower()
            if ext not in valid_exts:
                continue
    
            input_path = os.path.join(folder, filename)
            try:
                if ext == ".dcm":
                    ds = pydicom.dcmread(input_path)
                    arr = ds.pixel_array
                    arr = self._normalize_grayscale(arr)
                    image = Image.fromarray(arr).convert("RGB")
                else:
                    image = Image.open(input_path).convert("RGB")
    
                max_width = max(max_width, image.width)
                max_height = max(max_height, image.height)
            except Exception as e:
                print(f"[WARN] Failed to process {filename} during size check: {e}")
    
        self.canvas_width = max_width
        self.canvas_height = max_height
    
        # 2nd pass: パディング → 保存
        for i, filename in enumerate(sorted(os.listdir(folder))):
            ext = pathlib.Path(filename).suffix.lower()
            if ext not in valid_exts:
                continue
    
            input_path = os.path.join(folder, filename)
            key = f"{i+1:04}"
            output_jpg_path = os.path.join(jpg_folder, f"image{key}.jpg")
    
            if not jpg_folder.exists():
                jpg_folder.mkdir(exist_ok=True)
    
            try:
                if ext == ".dcm":
                    ds = pydicom.dcmread(input_path)
                    arr = ds.pixel_array
                    arr = self._normalize_grayscale(arr)
                    image = Image.fromarray(arr).convert("RGB")
                else:
                    image = Image.open(input_path).convert("RGB")
    
                delta_w = max_width - image.width
                delta_h = max_height - image.height
                padding = (
                    delta_w // 2,
                    delta_h // 2,
                    delta_w - delta_w // 2,
                    delta_h - delta_h // 2,
                )
    
                image_padded = ImageOps.expand(image, padding, fill=fill_rgb)
                self.resized_images_cache[key] = image_padded
                image_padded.save(output_jpg_path, "JPEG")
    
                self.image_paths[key] = output_jpg_path
                self.image_sizes[key] = image_padded.size
    
            except Exception as e:
                print(f"[WARN] Failed to process {filename}: {e}")
    
        self.label_status.setText(f"Loaded {len(self.image_paths)} images (converted to JPG, unified canvas).")
        self.current_index = 0
    
        # ✅ DICOM 情報保存（必要な場合のみ）
        dcm_paths = [os.path.join(folder, f) for f in sorted(os.listdir(folder)) if f.lower().endswith(".dcm")]
        if dcm_paths:
            try:
                ds = pydicom.dcmread(dcm_paths[0])
    
                width = int(getattr(ds, "Columns", 0))
                height = int(getattr(ds, "Rows", 0))
                depth = len(dcm_paths)
    
                pixel_spacing = getattr(ds, "PixelSpacing", ["", ""])
                slice_thickness = getattr(ds, "SliceThickness", "")
                image_position = getattr(ds, "ImagePositionPatient", ["", "", ""])
    
                volume_table = [
                    ["Width", "Height", "Depth"],
                    [str(width), str(height), str(depth)],
                    ["X Spacing", "Y Spacing", "Z Spacing"],
                    [str(pixel_spacing[0]), str(pixel_spacing[1]), str(slice_thickness)],
                    ["X Origin", "Y Origin", "Z Origin"],
                    [str(image_position[0]), str(image_position[1]), str(image_position[2])]
                ]
    
                self.mm_per_px = float(pixel_spacing[0]) if pixel_spacing[0] else None
                self.z_spacing_mm = float(slice_thickness) if slice_thickness else None
    
                csv_filename = f"{input_folder.name}_volinf.csv"
                csv_path = os.path.join(os.getcwd(), csv_filename)
    
                with open(csv_path, "w", newline="", encoding="utf-8") as f:
                    writer = csv.writer(f)
                    writer.writerows(volume_table)
    
                print(f"[INFO] Volume info saved to: {csv_path}")
            except Exception as e:
                print(f"[WARN] Failed to extract volume info: {e}")
    
        self.image_pristine = True
        
            
        # ✅ 元画像の保持（ここが今回の追加ポイント）
        self.original_images = {}
        for key, path in self.image_paths.items():
            self.original_images[key] = Image.open(path).convert("RGB")        
        
        
        self.display_current_image()
        # self.label_status.setText("✅ Images loaded.")
        self.fit_view_to_window()
        self.label_status.setText("✅ Images loaded. Use ↓↑, F/R, or J/U to switch images.")


    
    
    
    
        # ✅ 位置合わせ済み一時ファイルの記録を初期化
        self.transformed_image_paths = {}
        



    


        
    def expand_canvas_and_reload(self):
        from PIL import Image
        import os
    
        if not self.image_paths:
            self.label_status.setText("⚠ No images loaded.")
            return
        
        QApplication.processEvents()  # 🔸 ComboBoxの選択反映を強制
    
        # 🔹 UIから背景色取得（"White" or "Black"）
        selected_color = self.combo_canvas_bg.currentText().lower()
        print(f"[DEBUG] selected_color raw: {self.combo_canvas_bg.currentText()}")
        color_map = {
            "white": (255, 255, 255),
            "black": (0, 0, 0)
        }
        fill_rgb = color_map.get(selected_color, (255, 255, 255))  # デフォルト白
        print(f"[DEBUG] fill_rgb = {fill_rgb}")
    
        # 出力ディレクトリ作成
        expanded_dir = os.path.join(os.getcwd(), "expanded_canvas")
        os.makedirs(expanded_dir, exist_ok=True)
        print(f"[DEBUG] Output folder created at: {expanded_dir}")
    
        new_image_paths = {}
        new_image_sizes = {}
        new_cache = {}
    
        for key, path in self.image_paths.items():
            print(f"[DEBUG] Processing image key = {key}, path = {path}")
            img = Image.open(path).convert("RGB")
            new_width = img.width + 200
            new_height = img.height + 200
            print(f"[DEBUG] New canvas size: {new_width}x{new_height}")
    
            # 指定背景色のキャンバスを生成し、中央に貼り付け
            background = Image.new("RGB", (new_width, new_height), fill_rgb)
            background.paste(img, (100, 100))  # 上下左右 100px
    
            new_path = os.path.join(expanded_dir, f"expanded_{key}.jpg")
            background.save(new_path)
            print(f"[DEBUG] Saved expanded image to: {new_path}")
    
            new_image_paths[key] = new_path
            new_image_sizes[key] = background.size
            new_cache[key] = background
    
        # データ更新
        self.image_paths = new_image_paths
        self.image_sizes = new_image_sizes
        self.resized_images_cache = new_cache
        self.canvas_width += 200
        self.canvas_height += 200
        print(f"[DEBUG] Canvas updated: width={self.canvas_width}, height={self.canvas_height}")
    
        self.display_current_image()
        self.label_status.setText("✅ Canvas expanded by 100px on all sides.")
        self.expand_count += 1
        self.fit_view_to_window()

    
    def fit_view_to_window(self):
        self.graphicsView.fitInView(self.scene.itemsBoundingRect(), Qt.AspectRatioMode.KeepAspectRatio)
        self.label_status.setText("✅ View fitted to window.")


    
    def overlay_previous_image(self):
        # 既存のオーバーレイがあれば削除
        if self.overlay_image_item:
            self.scene.removeItem(self.overlay_image_item)
            self.overlay_image_item = None
    
        # 前の画像が存在するかチェック
        prev_index = self.current_index - 1
        if prev_index < 0:
            self.label_status.setText("⚠ No previous image.")
            return
    
        prev_key = f"{prev_index+1:04}"
        if prev_key not in self.image_paths:
            self.label_status.setText("⚠ Previous image not found.")
            return
    
        # 画像読み込みと変換
        img = Image.open(self.image_paths[prev_key]).convert("RGBA")
        data = img.tobytes("raw", "RGBA")
        qimg = QImage(data, img.width, img.height, QImage.Format.Format_RGBA8888)
        pixmap = QPixmap.fromImage(qimg)
    
        # シーンにオーバーレイとして追加
        self.overlay_image_item = self.scene.addPixmap(pixmap)
        self.overlay_image_item.setZValue(10)
        self.overlay_image_item.setOpacity(0.5)  # 半透明
    
        self.label_status.setText("🟡 Previous image overlayed.")



    
    def overlay_next_image(self):
        # 先に既存のオーバーレイを削除
        if self.overlay_image_item:
            self.scene.removeItem(self.overlay_image_item)
            self.overlay_image_item = None
    
        # ✅ 次のインデックスとキーを定義
        next_index = self.current_index + 1
        next_key = f"{next_index+1:04}"
    
        if next_key not in self.image_paths:
            self.label_status.setText("⚠ Next image not found.")
            return
    
        # 画像読み込み
        img = Image.open(self.image_paths[next_key]).convert("RGBA")
        data = img.tobytes("raw", "RGBA")
        qimg = QImage(data, img.width, img.height, QImage.Format.Format_RGBA8888)
        pixmap = QPixmap.fromImage(qimg)
    
        self.overlay_image_item = self.scene.addPixmap(pixmap)
        self.overlay_image_item.setZValue(10)
        self.overlay_image_item.setOpacity(0.5)
    
        self.label_status.setText("🟢 Next image overlayed.")




    
    def clear_overlay(self):
        if self.overlay_image_item:
            self.scene.removeItem(self.overlay_image_item)
            self.overlay_image_item = None
            self.label_status.setText("Overlay cleared.")

            

    
    def start_recording_position(self):
        # すでに存在する仮画像があれば削除
        if hasattr(self, 'position_preview_item') and self.position_preview_item:
            
            
            
            # self.scene.removeItem(self.position_preview_item)
            if hasattr(self, 'position_preview_item') and self.position_preview_item:
                try:
                    if self.position_preview_item.scene():  # まだ生きているなら
                        self.scene.removeItem(self.position_preview_item)
                except RuntimeError:
                    print("[WARN] position_preview_item already deleted")
                self.position_preview_item = None
            
            
            
            self.position_preview_item = None
    
        # 現在の画像を仮画像として複製
        key = f"{self.current_index+1:04}"
        img_path = self.image_paths.get(key)
        if not img_path:
            self.label_status.setText("⚠ No image loaded.")
            return
    
        img = Image.open(img_path).convert("RGBA")
        qimg = QImage(img.tobytes("raw", "RGBA"), img.width, img.height, QImage.Format.Format_RGBA8888)
        pixmap = QPixmap.fromImage(qimg)
    
        self.position_preview_item = self.scene.addPixmap(pixmap)
        self.position_preview_item.setZValue(5)
        self.position_preview_item.setOpacity(1.0)  # 少し透過でもOK
        # self.position_preview_item.setTransformOriginPoint(pixmap.rect().center())
        center_point = QPointF(pixmap.rect().center())
        self.position_preview_item.setTransformOriginPoint(center_point)
    
        # 移動・回転ログの初期化
        self.position_dx = 0
        self.position_dy = 0
        self.position_angle = 0.0
    
        # self.label_status.setText("🔴 Position recording started.")
        # 🔽 ステータス表示（ショートカット説明付き）
        self.label_status.setText(
            "🔴 Position recording started. ⬆⬇⬅➡ / WASD / OKL;: Move  |  Q/I: Rotate Left  |  E/P: Rotate Right"
        )
    
        
    def translate_preview(self, dx, dy):
        if hasattr(self, 'position_preview_item') and self.position_preview_item:
            self.position_preview_item.moveBy(dx, dy)
            self.position_dx += dx
            self.position_dy += dy
    
    def rotate_preview(self, angle_deg):
        if hasattr(self, 'position_preview_item') and self.position_preview_item:
            self.position_preview_item.setRotation(
                self.position_preview_item.rotation() + angle_deg
            )
            self.position_angle += angle_deg

    
    def finish_recording_position(self):
        if not hasattr(self, 'position_preview_item') or self.position_preview_item is None:
            self.label_status.setText("⚠ No preview to record.")
            return
    
        # 記録値を保存
        self.recorded_position_transform = {
            'dx': self.position_dx,
            'dy': self.position_dy,
            'angle_deg': self.position_angle
        }
    
        # プレビュー削除
        self.scene.removeItem(self.position_preview_item)
        self.position_preview_item = None
        
        self.clear_overlay()  # 🔸ここを追加**
    
        self.label_status.setText(
            f"✅ Recorded Δx={self.position_dx}, Δy={self.position_dy}, Δθ={self.position_angle:.1f}°"
        )




    
    def cancel_recording_position(self):
        if hasattr(self, 'position_preview_item') and self.position_preview_item:
            self.scene.removeItem(self.position_preview_item)
            self.position_preview_item = None
            self.label_status.setText("❌ Position recording canceled.")
        else:
            self.label_status.setText("ℹ️ No active position preview to cancel.")



    def set_position_start(self):
        self.position_range_start_index = self.current_index
        print(f"[DEBUG] Set Position Start: frame {self.position_range_start_index + 1}")
        self.label_status.setText(f"📍 Position Start set at frame {self.position_range_start_index + 1}")
    
    def set_position_end(self):
        self.position_range_end_index = self.current_index
        print(f"[DEBUG] Set Position Start: frame {self.position_range_start_index + 1}")
        self.label_status.setText(f"📍 Position End set at frame {self.position_range_end_index + 1}")


        
    
    def apply_transform(self, img_path, dx, dy, angle_deg, canvas_size):
        img = Image.open(img_path).convert("RGBA")
        img_rotated = img.rotate(-angle_deg, resample=Image.BICUBIC, expand=True)  # ← ここを修正
        
        bg = Image.new("RGBA", canvas_size, (255, 255, 255, 0))
        cx = (canvas_size[0] - img_rotated.width) // 2 + dx
        cy = (canvas_size[1] - img_rotated.height) // 2 + dy
        bg.paste(img_rotated, (cx, cy), img_rotated)
        
        return bg.convert("RGB")

    
    def apply_recorded_position_to_range(self):
        # 🔹 apply前に状態をバックアップ
        self.aligned_image_paths_backup = self.image_paths.copy()
        self.aligned_image_sizes_backup = self.image_sizes.copy()
        self.aligned_cache_backup = self.resized_images_cache.copy()
        
        
        if not hasattr(self, 'recorded_position_transform'):
            self.label_status.setText("⚠ No recorded position to apply.")
            return
        
        if not hasattr(self, 'position_range_start_index') or not hasattr(self, 'position_range_end_index'):
            self.label_status.setText("⚠ Position start/end not set.")
            return
    
        dx = self.recorded_position_transform['dx']
        dy = self.recorded_position_transform['dy']
        angle_deg = self.recorded_position_transform['angle_deg']
        canvas_size = (self.canvas_width, self.canvas_height)
    
        output_dir = os.path.join(os.getcwd(), "position_applied")
        os.makedirs(output_dir, exist_ok=True)
    
        start = min(self.position_range_start_index, self.position_range_end_index)
        end = max(self.position_range_start_index, self.position_range_end_index)
    
        for i in range(start, end + 1):
            key = f"{i+1:04}"
            if key not in self.image_paths:
                continue
            input_path = self.image_paths[key]
            result = self.apply_transform(input_path, dx, dy, angle_deg, canvas_size)
    
            output_path = os.path.join(output_dir, f"posapplied_{key}.jpg")
            result.save(output_path)
    
            self.image_paths[key] = output_path
            self.resized_images_cache[key] = result
            self.image_sizes[key] = result.size
            
        
    
        self.display_current_image()
        self.transformed_images = self.resized_images_cache.copy()
        self.label_status.setText(f"✅ Applied transform to frames {start+1} to {end+1}")
        

    
    def cancel_applied_position(self):
        if not hasattr(self, "aligned_image_paths_backup"):
            self.label_status.setText("⚠ No applied result to cancel.")
            return
    
        # 元の状態に復元
        self.image_paths = self.aligned_image_paths_backup.copy()
        self.image_sizes = self.aligned_image_sizes_backup.copy()
        self.resized_images_cache = self.aligned_cache_backup.copy()
    
        del self.aligned_image_paths_backup
        del self.aligned_image_sizes_backup
        del self.aligned_cache_backup
    
        self.label_status.setText("⛔ Applied position canceled.")
        self.display_current_image()






    
    def start_crop_mode(self):
        # クロップモードとして box_mode を再利用
        self.box_mode = True
        self.crop_box_points = []  # ✅ 統一された変数名を使用
        print("[DEBUG] start_crop_mode called")
    
        # クロスヘア仮線の初期化
        self.temp_crosshair_hline = None
        self.temp_crosshair_vline = None        
    
        # 仮のボックスがあれば削除
        if hasattr(self, "temp_box_item") and self.temp_box_item:
            self.scene.removeItem(self.temp_box_item)
            self.temp_box_item = None
    
        # クロップ用ボックスも削除
        if hasattr(self, "current_crop_rect_item"):
            try:
                if self.current_crop_rect_item is not None and self.current_crop_rect_item.scene() is not None:
                    self.scene.removeItem(self.current_crop_rect_item)
            except RuntimeError:
                print("[WARN] current_crop_rect_item already deleted.")
            self.current_crop_rect_item = None
    
        # セグメント系の残骸があればクリア（今後不要なら削除してもOK）
        self.last_box_prompt = None
        self.last_used_box_px = None
        self.box_per_frame.clear()
    
        self.label_status.setText("Click top-left and bottom-right corners to set crop box.")

    
    def clear_crop_box(self):
        # 現在のクロップボックス表示を削除
        if hasattr(self, "current_crop_rect_item") and self.current_crop_rect_item:
            try:
                if self.current_crop_rect_item.scene():
                    self.scene.removeItem(self.current_crop_rect_item)
            except RuntimeError:
                print("[WARN] current_crop_rect_item already deleted.")
            self.current_crop_rect_item = None
    
        # 仮ボックスも削除
        if hasattr(self, "temp_box_item") and self.temp_box_item:
            self.scene.removeItem(self.temp_box_item)
            self.temp_box_item = None
    
        # 内部状態を初期化
        self.crop_box_coords = None
        self.crop_box_points = []
        self.box_per_frame.clear()  # 必要に応じて残してもOK
        key = self.get_current_image_key()
        if key in self.crop_box_per_frame:
            del self.crop_box_per_frame[key]
        
        # ✅ 全画像共通のクロップ枠もクリア
        self.crop_box_global_rect = None
        
        self.label_status.setText("Crop box cleared.")




        
    
    def apply_crop(self):
        if not self.current_crop_rect_item:
            self.label_status.setText("⚠ No crop box set.")
            return
            
        # 🔸 scene座標から矩形取得
        scene_rect = self.current_crop_rect_item.sceneBoundingRect()
        x1_scene = int(scene_rect.left())
        y1_scene = int(scene_rect.top())
        x2_scene = int(scene_rect.right())
        y2_scene = int(scene_rect.bottom())
        
        # 🔸 どの画像がクロップ対象か決定（transformed → processed → original）
        if hasattr(self, "transformed_images") and self.transformed_images:
            source_images = self.transformed_images
        elif hasattr(self, "processed_images") and self.processed_images:
            source_images = self.processed_images
        else:
            source_images = self.original_images
        
        # 🔸 expand補正：originalを使ってるときだけ補正が必要
        if source_images is self.original_images:
            expand_px = 100 * self.expand_count
            x1_scene -= expand_px
            x2_scene -= expand_px
            y1_scene -= expand_px
            y2_scene -= expand_px
        
        box = (min(x1_scene, x2_scene), min(y1_scene, y2_scene), max(x1_scene, x2_scene), max(y1_scene, y2_scene))

        

        # 🔸 仮画像を新たに生成
        self.processed_images = {}
        for key, img in source_images.items():
            img_w, img_h = img.size
            crop_box = (
                max(0, min(box[0], img_w)),
                max(0, min(box[1], img_h)),
                max(0, min(box[2], img_w)),
                max(0, min(box[3], img_h)),
            )
            cropped = img.crop(crop_box)
            self.processed_images[key] = cropped

    
        self.image_sizes = {k: v.size for k, v in self.processed_images.items()}
        self.canvas_width, self.canvas_height = self.processed_images[self.get_current_image_key()].size
        self.display_current_image()
        self.label_status.setText("✅ Cropped working images (originals untouched).")
    
        # ✅ クロップ枠（赤枠）をシーンから削除
        if self.current_crop_rect_item and self.current_crop_rect_item.scene():
            self.scene.removeItem(self.current_crop_rect_item)
        self.current_crop_rect_item = None
    
        # ✅ 全画像共通の赤枠もリセット
        self.crop_box_global_rect = None
    
        # ✅ ボックス点もクリア
        self.box_points = []
        self.expand_count = 0  # クロップ後に expand オフセットをリセット（任意）
        self.transformed_images = None


        print(f"[DEBUG] Using {'original' if source_images is self.original_images else 'processed'} images for crop")
        print(f"[DEBUG] Cropping box: {box}")

    



    
    def undo_crop(self):
        if not self.original_images_backup:
            self.label_status.setText("⚠ Nothing to undo.")
            return
    
        for key, img in self.original_images_backup.items():
            img.save(self.image_paths[key])  # 元の画像に戻す
    
        self.scene.clear()
        self.display_current_image()
        self.original_images_backup.clear()
        self.label_status.setText("✅ Crop undone, original images restored.")







    
    def export_aligned_images(self):
        if not hasattr(self, "resized_images_cache") or not self.resized_images_cache:
            self.label_status.setText("⚠ No aligned images to export.")
            return
    
        # 出力形式取得
        fmt = self.combo_export_format.currentText().lower()
        extension = "dcm" if fmt == "dcm" else fmt.lower()
        
        # PILが受け入れる形式に変換
        format_map = {
            "jpg": "JPEG",
            "jpeg": "JPEG",
            "png": "PNG",
            "bmp": "BMP",
            "tiff": "TIFF"
        }
        save_format = format_map.get(fmt, fmt.upper())
        
        
        
        # 元フォルダ名とタイムスタンプで出力先を構成
        # timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        input_folder_name = getattr(self, "input_folder_name", "aligned")  # 事前に保存しておくと便利
        export_dir_name = f"{input_folder_name}_aligned_{timestamp}"
        target_dir = os.path.join(os.getcwd(), export_dir_name)
        os.makedirs(target_dir, exist_ok=True)
    
        images_to_export = self.processed_images if hasattr(self, "processed_images") and self.processed_images else self.resized_images_cache
        
        for key, img in images_to_export.items():    
            # filename = f"aligned_{key}.{extension}"
            filename = f"image{key}.{extension}"
            save_path = os.path.join(target_dir, filename)
    
            try:
                if fmt == "dcm":
                    arr = np.array(img.convert("L"))  # DICOMは通常モノクロ
                    ds = FileDataset(save_path, {}, file_meta=Dataset(), preamble=b"\0" * 128)
                    ds.Modality = 'OT'  # Other
                    ds.ContentDate = datetime.now().strftime('%Y%m%d')
                    ds.ContentTime = time.strftime('%H%M%S')
                    ds.Rows, ds.Columns = arr.shape
                    ds.SamplesPerPixel = 1
                    ds.PhotometricInterpretation = "MONOCHROME2"
                    ds.BitsStored = 8
                    ds.BitsAllocated = 8
                    ds.HighBit = 7
                    ds.PixelRepresentation = 0
                    ds.PixelData = arr.tobytes()
                    ds.save_as(save_path)
                else:
                    img.save(save_path, format=save_format)
    
            except Exception as e:
                print(f"[ERROR] Failed to save {save_path}: {e}")
    
        self.label_status.setText(f"✅ Exported images as {fmt.upper()} to: {target_dir}")























    
        
    def smart_undo(self):
        key = self.get_current_image_key()
    
        # ① 手描きパスのUndo（最優先）
        if key in self.drawn_paths_per_image and self.drawn_paths_per_image[key]:
            self.undo_last_path()
            print("[INFO] Ctrl+Z → undo_last_drawn_path done")
            return
    
        # ② 通常の1画像Undo（先にチェック）
        if key in self.undo_stack and self.undo_stack[key]:
            self.undo_edit(key)
            print("[INFO] Ctrl+Z → undo_svg_edit done")
            return
    
        # ③ 全画像対象のUndo（key="__global__" を渡す！）
        if "__global__" in self.undo_stack and self.undo_stack["__global__"]:
            self.undo_edit("__global__")
            print("[INFO] Ctrl+Z → undo_global_svg_edit done")
            return
    
        # ④ それでも何もなければ
        self.label_status.setText("Nothing to undo.")
        print("[INFO] Ctrl+Z → nothing to undo")





        

    def get_current_image_key(self):
        """現在の画像インデックスからキー（ファイル名）を取得"""
        keys = list(self.image_paths.keys())
        if 0 <= self.current_index < len(keys):
            return keys[self.current_index]
        return None






    





    #黒背景を消すための
    def _normalize_color(self, fill, style):
        def rgb_to_hex(rgb_str):
            match = re.match(r'rgb\((\d+),\s*(\d+),\s*(\d+)\)', rgb_str)
            if match:
                r, g, b = map(int, match.groups())
                return f'#{r:02x}{g:02x}{b:02x}'
            return rgb_str.strip().lower()
    
        color = ""
        if style and "fill:" in style:
            match = re.search(r'fill:([^;"]+)', style)
            if match:
                color = match.group(1).strip().lower()
        elif fill:
            color = fill.strip().lower()
    
        if color.startswith("rgb"):
            return rgb_to_hex(color)
        return color
    
    def _find_parent(self, root, target):
        for parent in root.iter():
            if target in list(parent):
                return parent
        return None





            

    def load_files_from_folder(self, folder, extensions):
        files = {}
        for file in sorted(os.listdir(folder)):
            if any(file.lower().endswith(ext) for ext in extensions):
                key = os.path.splitext(file)[0][-4:]  # 末尾4桁（例：0001）
                files[key] = os.path.join(folder, file)
        return files


    

                
    def display_current_image(self):
        # 🔄 オーバーレイは画像切り替え時に削除
        if self.overlay_image_item:
            self.scene.removeItem(self.overlay_image_item)
            self.overlay_image_item = None


        if not self.image_paths:
            return
    
        key = f"{self.current_index + 1:04}"
        filename = os.path.basename(self.image_paths.get(key, "N/A"))
        self.label_status.setText(f"Displaying {filename} ({self.current_index + 1}/{len(self.image_paths)})")
    
        # 🧠 現在の表示状態を保持
        current_transform = self.graphicsView.transform()
        h_value = self.graphicsView.horizontalScrollBar().value()
        v_value = self.graphicsView.verticalScrollBar().value()
    
        self.scene.clear()
    
        # 統一されたキャンバスサイズの画像を使用
        # img_pil = self.resized_images_cache[key]
        if hasattr(self, "processed_images") and key in self.processed_images:
            img_pil = self.processed_images[key]
        else:
            img_pil = self.resized_images_cache[key]
        
        
        
        img_np = np.array(img_pil.convert("RGB"))
        h, w, ch = img_np.shape
        bytes_per_line = ch * w
        qimage = QImage(img_np.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
        pixmap = QPixmap.fromImage(qimage)
    
        pixmap_item = QGraphicsPixmapItem(pixmap)
        pixmap_item.setPos(0, 0)
        self.scene.addItem(pixmap_item)
    
        # SVGマスクを表示
        if key in self.mask_paths:
            from xml.etree import ElementTree as ET
            from io import BytesIO
            from PyQt6.QtGui import QPainter
    
            tree = ET.parse(self.mask_paths[key])
            root = tree.getroot()
    
            hex_colors = [f'#{r:02x}{g:02x}{b:02x}' for (r, g, b) in self.color_labels]
    
            for elem in list(root.iter()):
                fill = elem.attrib.get("fill", "")
                style = elem.attrib.get("style", "")
    
                if not fill and "fill:" in style:
                    match = re.search(r'fill:([^;\"]+)', style)
                    if match:
                        fill = match.group(1).strip()
    
                fill_lower = fill.lower() if fill else ""
    
                for i, hex_str in enumerate(hex_colors):
                    if fill_lower == hex_str:
                        visible = self.checkboxes[i].isChecked()
                        if not visible:
                            elem.attrib["display"] = "none"
                        break
    
            svg_bytes = BytesIO()
            tree.write(svg_bytes, encoding='utf-8')
            svg_bytes.seek(0)
    
            renderer = QSvgRenderer(svg_bytes.read())
    
            image = QImage(w, h, QImage.Format.Format_ARGB32)
            image.fill(0)
            painter = QPainter(image)
            renderer.render(painter)
            painter.end()
    
            svg_pixmap = QPixmap.fromImage(image)
            svg_item = QGraphicsPixmapItem(svg_pixmap)
            svg_item.setOpacity(0.3)
            svg_item.setZValue(1)
            self.scene.addItem(svg_item)
    
        self.graphicsView.setSceneRect(0, 0, self.canvas_width, self.canvas_height)
        self.graphicsView.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.graphicsView.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorViewCenter)
        self.graphicsView.setTransform(current_transform)
    
        self.graphicsView.horizontalScrollBar().setValue(h_value)
        self.graphicsView.verticalScrollBar().setValue(v_value)

    
        # クロップ用ボックス再表示
        if self.crop_box_coords:
            x1, y1, x2, y2 = self.crop_box_coords
            rect = QRectF(QPointF(x1, y1), QPointF(x2, y2))
    
            if hasattr(self, 'current_crop_rect_item') and self.current_crop_rect_item:
                self.scene.removeItem(self.current_crop_rect_item)
    
            self.current_crop_rect_item = ResizableRectItem(rect)
            self.scene.addItem(self.current_crop_rect_item)
    
        # # このフレームにボックスがあれば再表示
        # if self.current_index in self.box_per_frame:
        #     p1, p2 = self.box_per_frame[self.current_index]
        #     rect = QRectF(p1, p2).normalized()
        #     box_item = QGraphicsRectItem(rect)
        #     box_item.setPen(QPen(Qt.GlobalColor.red, 2))
        #     box_item.setZValue(10)
        #     self.scene.addItem(box_item)
    
        # グレースケール画像（OpenCV）をスナップ用にセット
        gray_path = self.image_paths[key]
        gray = cv2.imread(gray_path, cv2.IMREAD_GRAYSCALE)
        self.graphicsView.gray_image = gray            
                            
        # ✅ 画像に対応するクロップボックスを再描画
        key = self.get_current_image_key()
        if key in self.crop_box_per_frame:
            rect = self.crop_box_per_frame[key]
            self.current_crop_rect_item = ResizableRectItem(rect)
            self.scene.addItem(self.current_crop_rect_item)
            
        # ✅ 全画像で共通のクロップ枠があれば描画
        if self.crop_box_global_rect:
            # self.current_crop_rect_item = ResizableRectItem(self.crop_box_global_rect)
            self.current_crop_rect_item = ResizableRectItem(self.crop_box_global_rect, main_window=self)

            self.current_crop_rect_item.setPen(QPen(Qt.GlobalColor.red, 2))
            self.current_crop_rect_item.setZValue(10)
            self.scene.addItem(self.current_crop_rect_item)
        








        

        
    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, "scene") and self.scene and not self.scene.itemsBoundingRect().isNull():
            self.graphicsView.resetTransform()
            self.graphicsView.fitInView(self.scene.itemsBoundingRect(), Qt.AspectRatioMode.KeepAspectRatio)
                
    
    

    def eventFilter(self, source, event):

        if event.type() == event.Type.KeyPress:
            key = event.key()
        
            if key in (Qt.Key.Key_PageDown, Qt.Key.Key_F, Qt.Key.Key_J):
                if self.current_index + 1 < len(self.image_paths):
                  
                    
                    self.current_index += 1
                    self.image_pristine = False  # 🔸 操作フラグをオフ
                    self.display_current_image()
                return True
        
            elif key in (Qt.Key.Key_PageUp, Qt.Key.Key_R, Qt.Key.Key_U):
                if self.current_index > 0:
                 
                    
                    self.current_index -= 1
                    self.image_pristine = False  # 🔸 操作フラグをオフ
                    self.display_current_image()
                return True
            
          
            
            # 🔁 左回転（Q または I）
            elif key in (Qt.Key.Key_Q, Qt.Key.Key_I):
                self.rotate_preview(-0.1)
                return True
            
            # 🔁 右回転（E または P）
            elif key in (Qt.Key.Key_E, Qt.Key.Key_P):
                self.rotate_preview(+0.1)
                return True
            
            # ⬆ 上に移動（W, O, ↑）
            elif key in (Qt.Key.Key_W, Qt.Key.Key_O, Qt.Key.Key_Up):
                self.translate_preview(0, -1)
                return True
            
            # ⬇ 下に移動（S, L, ↓）
            elif key in (Qt.Key.Key_S, Qt.Key.Key_L, Qt.Key.Key_Down):
                self.translate_preview(0, 1)
                return True
            
            # ⬅ 左に移動（A, K, ←）
            elif key in (Qt.Key.Key_A, Qt.Key.Key_K, Qt.Key.Key_Left):
                self.translate_preview(-1, 0)
                return True
            
            # ➡ 右に移動（D, ;, →）
            elif key in (Qt.Key.Key_D, Qt.Key.Key_Semicolon, Qt.Key.Key_Right):
                self.translate_preview(1, 0)
                return True
            


    
        elif event.type() == event.Type.Wheel and source == self.graphicsView.viewport():
            event.accept()
    
            modifiers = QApplication.keyboardModifiers()
            delta = event.angleDelta().y()
    
            if modifiers == Qt.KeyboardModifier.ControlModifier:
                factor = 1.25 if delta > 0 else 0.8
                self.graphicsView.scale(factor, factor)
                return True
    
            elif modifiers == Qt.KeyboardModifier.ShiftModifier:
                hbar = self.graphicsView.horizontalScrollBar()
                hbar.setValue(hbar.value() - delta)
                return True
    
            elif modifiers == Qt.KeyboardModifier.NoModifier:
                vbar = self.graphicsView.verticalScrollBar()
                vbar.setValue(vbar.value() - delta)
                return True
    
           
        
        elif event.type() == event.Type.MouseMove and source == self.graphicsView.viewport():
        
            # 🔍 共通デバッグ出力
            # print(f"[DEBUG] MouseMove: box_mode={self.box_mode}, box_points={len(self.box_points)}, calibration_mode={self.calibration_mode}, calibration_points={len(self.calibration_points)}")
        
            # ✅ ボックスモードで2点目をまだ選んでいないとき
            if self.box_mode and len(self.box_points) == 1:
                p1 = self.box_points[0]
                p2 = self.graphicsView.mapToScene(event.pos())
        
                if self.temp_box_item:
                    self.scene.removeItem(self.temp_box_item)
                    self.temp_box_item = None
        
                rect = QRectF(p1, p2).normalized()
                self.temp_box_item = QGraphicsRectItem(rect)
                self.temp_box_item.setPen(QPen(Qt.GlobalColor.red, 2, Qt.PenStyle.DashLine))
                self.scene.addItem(self.temp_box_item)
        
                return True
        
        
            # ✅ ボックスモードでまだ最初の点を選んでいないとき（クロスヘア）
            if self.box_mode and len(self.box_points) < 1:
                
                
                        
                
                # クロスヘア描画（MouseMove）
                scene_pos = self.graphicsView.mapToScene(event.pos())
                self.current_crosshair_pos = scene_pos  # ← 🔴 追加！
                
                x, y = scene_pos.x(), scene_pos.y()
                
                # 以前のクロスヘアを削除
                if hasattr(self, "temp_crosshair_hline") and self.temp_crosshair_hline:
                    self.scene.removeItem(self.temp_crosshair_hline)
                if hasattr(self, "temp_crosshair_vline") and self.temp_crosshair_vline:
                    self.scene.removeItem(self.temp_crosshair_vline)
                
                scene_rect = self.graphicsView.sceneRect()
                
                # 🔽 右方向にだけ伸びる水平線（左端がマウス位置）
                hline_path = QPainterPath()
                hline_path.moveTo(x, y)
                hline_path.lineTo(scene_rect.right(), y)
                
                self.temp_crosshair_hline = QGraphicsPathItem(hline_path)
                self.temp_crosshair_hline.setPen(QPen(Qt.GlobalColor.red, 2, Qt.PenStyle.SolidLine))
                self.temp_crosshair_hline.setZValue(999)
                self.scene.addItem(self.temp_crosshair_hline)
                
                # 🔽 下方向にだけ伸びる垂直線（上端がマウス位置）
                vline_path = QPainterPath()
                vline_path.moveTo(x, y)
                vline_path.lineTo(x, scene_rect.bottom())
                
                self.temp_crosshair_vline = QGraphicsPathItem(vline_path)
                self.temp_crosshair_vline.setPen(QPen(Qt.GlobalColor.red, 2, Qt.PenStyle.SolidLine))
                self.temp_crosshair_vline.setZValue(999)
                self.scene.addItem(self.temp_crosshair_vline)
        
        
        
                return True
        
            # ✅ キャリブレーション線の仮表示
            if self.calibration_mode and len(self.calibration_points) == 1:
                p1 = self.calibration_points[0]
                p2 = self.graphicsView.mapToScene(event.pos())
        
                if hasattr(self, "temp_line_item") and self.temp_line_item:
                    self.scene.removeItem(self.temp_line_item)
        
                path = QPainterPath()
                path.moveTo(p1)
                path.lineTo(p2)
                self.temp_line_item = QGraphicsPathItem(path)
                self.temp_line_item.setPen(QPen(Qt.GlobalColor.magenta, 1, Qt.PenStyle.DashLine))
                self.scene.addItem(self.temp_line_item)
        
                return True

        
        elif event.type() == event.Type.MouseButtonPress and event.button() == Qt.MouseButton.LeftButton:
            # ✅ マウスカーソルの現在位置を scene 座標に変換（ズレ防止）
            scene_pos = self.graphicsView.mapToScene(
                self.graphicsView.viewport().mapFromGlobal(QCursor.pos())
            )
        
            # 🔹 キャリブレーションモード
            if self.calibration_mode:
                self.calibration_points.append(scene_pos)
        
                if len(self.calibration_points) == 2:
                    p1, p2 = self.calibration_points
        
                    # 確定線
                    path = QPainterPath()
                    path.moveTo(p1)
                    path.lineTo(p2)
                    line_item = QGraphicsPathItem(path)
                    line_item.setPen(QPen(Qt.GlobalColor.magenta, 2))
                    self.scene.addItem(line_item)

     

                    # 仮線削除
                    if hasattr(self, "temp_line_item") and self.temp_line_item:
                        self.scene.removeItem(self.temp_line_item)
                        self.temp_line_item = None

                    px_length = ((p1.x() - p2.x()) ** 2 + (p1.y() - p2.y()) ** 2) ** 0.5
                    real_length_mm = self.spin_mm_input.value()
                    self.mm_per_px = real_length_mm / px_length if px_length != 0 else 1.0
                    self.z_spacing_mm = self.spin_z_interval.value()

                    self.label_status.setText(
                        f"Calibration complete: {px_length:.2f}px = {real_length_mm:.2f}mm → 1px = {self.mm_per_px:.4f} mm, Z spacing = {self.z_spacing_mm:.4f} mm"
                    )
                    self.save_calibration_to_csv()

                    self.calibration_mode = False
                    self.calibration_points = []

                return True

            # 🔹 ボックスプロンプトモード
            if self.box_mode:
                # self.box_points.append(scene_pos)

                                                        
                if self.box_mode:
                    if len(self.box_points) == 0:
                        # ✅ 1点目はクロスヘア（狙った位置）
                        if hasattr(self, "current_crosshair_pos"):
                            self.box_points.append(self.current_crosshair_pos)
                        else:
                            self.box_points.append(self.graphicsView.mapToScene(event.pos()))
                
                    elif len(self.box_points) == 1:
                        # ✅ 2点目は必ずクリック位置（誤差を防ぐため）
                        # scene_pos = self.graphicsView.mapToScene(event.pos())
                        scene_pos = self.graphicsView.mapToScene(self.graphicsView.viewport().mapFromGlobal(QCursor.pos()))

                
                        # 🔽 念のため：クリック時にも crosshair_pos を更新（マウスが動いてない場合）
                        self.current_crosshair_pos = scene_pos
                
                        self.box_points.append(scene_pos)



                # 1点目クリック後 → クロスヘア削除
                if len(self.box_points) == 1:
                    if hasattr(self, "temp_crosshair_hline") and self.temp_crosshair_hline:
                        self.scene.removeItem(self.temp_crosshair_hline)
                        self.temp_crosshair_hline = None
                    if hasattr(self, "temp_crosshair_vline") and self.temp_crosshair_vline:
                        self.scene.removeItem(self.temp_crosshair_vline)
                        self.temp_crosshair_vline = None

                # 2点目クリック → ボックス確定
                elif len(self.box_points) == 2:
                    p1, p2 = self.box_points
                    rect = QRectF(p1, p2).normalized()
                
                    if hasattr(self, 'confirmed_box_item') and self.confirmed_box_item:
                        self.scene.removeItem(self.confirmed_box_item)
                
                    # ✅ 先に確定ボックスを追加                
                    
                    # ✅ ResizableRectItem を current_crop_rect_item に代入（apply_crop で使うため）
                    if hasattr(self, 'current_crop_rect_item') and self.current_crop_rect_item:
                        self.scene.removeItem(self.current_crop_rect_item)
                    
                    self.current_crop_rect_item = ResizableRectItem(rect)
                    self.current_crop_rect_item.setPen(QPen(Qt.GlobalColor.red, 2))
                    self.current_crop_rect_item.setZValue(10)  # 必要なら重ね順設定
                    self.scene.addItem(self.current_crop_rect_item)

                    # ✅ ResizableRectItem を current_crop_rect_item に代入（apply_crop で使うため）
                    if hasattr(self, 'current_crop_rect_item') and self.current_crop_rect_item:
                        self.scene.removeItem(self.current_crop_rect_item)
                    
                    self.current_crop_rect_item = ResizableRectItem(rect)
                    self.current_crop_rect_item.setPen(QPen(Qt.GlobalColor.red, 2))
                    self.current_crop_rect_item.setZValue(10)
                    self.scene.addItem(self.current_crop_rect_item)
                    
                    self.crop_box_global_rect = rect  # ✅ 全画像共通の赤枠として保存
                    
                    # # ✅ ここで保存！画像ごとの赤枠を記録
                    # key = self.get_current_image_key()
                    # self.crop_box_per_frame[key] = rect
                
                    # ✅ 仮ボックスがあれば削除
                    if self.temp_box_item:
                        self.scene.removeItem(self.temp_box_item)
                        self.temp_box_item = None
                
                    # ✅ 終了処理
                    self.box_mode = False
                    width = self.graphicsView.sceneRect().width()
                    height = self.graphicsView.sceneRect().height()
                    top_left = (p1.x() / width * 100, p1.y() / height * 100)
                    bottom_right = (p2.x() / width * 100, p2.y() / height * 100)
                    self.last_box_prompt = (top_left, bottom_right)
                    self.last_used_box_px = ((p1.x(), p1.y()), (p2.x(), p2.y()))
                    self.label_status.setText(f"Box set: {top_left} → {bottom_right}")
                    self.last_used_box_index = self.current_index  # ✅ ボックスを置いたフレーム番号を記録
                    # ✅ フレームに応じて保存
                    self.box_per_frame[self.current_index] = ((p1, p2))

                    self.box_points = []
                                                        
                    if len(self.box_points) >= 2:
                        print(f"[DEBUG] point1: ({self.box_points[0].x():.2f}, {self.box_points[0].y():.2f})")
                        print(f"[DEBUG] point2: ({self.box_points[1].x():.2f}, {self.box_points[1].y():.2f})")

                    

                return True

    
        return super().eventFilter(source, event)


    
            
    
    
    def save_calibration_to_csv(self):
        import csv
        from pathlib import Path
    
        if self.mm_per_px is None or self.z_spacing_mm is None:
            print("[WARN] Calibration values not set")
            return
    
        try:
            first_img_path = self.image_paths.get("0001") or list(self.image_paths.values())[0]
            img = Image.open(first_img_path)
            width, height = img.width, img.height
        except Exception as e:
            print(f"[WARN] Failed to get image size: {e}")
            width, height = 0, 0
    
        depth = len(self.image_paths)
    
        volume_table = [
            ["Width", "Height", "Depth"],
            [str(width), str(height), str(depth)],
            ["X Spacing", "Y Spacing", "Z Spacing"],
            [str(self.mm_per_px), str(self.mm_per_px), str(self.z_spacing_mm)],
            ["X Origin", "Y Origin", "Z Origin"],
            ["0", "0", "0"]
        ]
    
        
        input_folder_name = Path(self.image_paths.get("0001") or list(self.image_paths.values())[0]).parent.name
        csv_filename = f"{input_folder_name}_volinf.csv"
        # csv_path = Path(self.output_mask_dir).parent / csv_filename
        csv_path = Path(self.default_output_dir) / csv_filename

    
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerows(volume_table)
    
        print(f"[INFO] Calibration info saved to: {csv_path}")

        


            
    def save_svg_state_for_undo(self, key=None):
        """
        SVGの状態をUndo用に保存。
        - key を指定：そのキーのみ保存
        - key を None：全mask_paths分のsnapshotを保存
        """
        if key is None:
            # 一括保存（全画像）
            snapshot = {}
            for k, path in self.mask_paths.items():
                if os.path.exists(path):
                    with open(path, "r", encoding="utf-8") as f:
                        snapshot[k] = f.read()
            if snapshot:
                self.undo_stack.setdefault("__global__", []).append(snapshot)
                self.redo_stack["__global__"] = []
        else:
            # 単一キーの保存（従来の動作）
            if key not in self.mask_paths:
                return
            path = self.mask_paths[key]
            with open(path, "r", encoding="utf-8") as f:
                svg_text = f.read()
            self.undo_stack.setdefault(key, []).append(svg_text)
            self.redo_stack[key] = []
        
        



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Main()
    app.installEventFilter(window)  # ← ここでアプリケーション全体にフィルターを適用
    window.show()
    sys.exit(app.exec())

