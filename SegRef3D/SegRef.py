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
    QCheckBox
)

from PyQt6.QtSvgWidgets import QGraphicsSvgItem

from PyQt6.QtGui import (
    QPixmap,
    QPainterPath,
    QPen,
    QPainter, 
    QMouseEvent,
    QImage,
    QColor
)

from PyQt6.QtCore import Qt, QPointF
from PyQt6.QtSvg import QSvgRenderer

import numpy as np

from ui_SegRef import Ui_MainWindow

from svgpathtools import parse_path

from datetime import datetime
import shutil
from xml.etree import ElementTree as ET

from collections import defaultdict

from PyQt6.QtGui import QShortcut, QKeySequence

import pydicom
from PIL import Image

import csv

from PyQt6.QtCore import QRectF
from PyQt6.QtWidgets import QGraphicsRectItem

from sam2_interface import SAM2Interface
from PyQt6.QtGui import QPainterPath
from PyQt6.QtGui import QCursor


import cv2
import subprocess

import torch
import time

from trimesh.smoothing import filter_laplacian  # ✅ 追加

    
def extract_all_numbers(s):
    return [int(num) for num in re.findall(r'\d+', s)]

def create_video_from_images(image_paths, output_path, fps=5):
    if not image_paths:
        raise ValueError("No images provided to create video.")

    # 最初の画像のサイズを取得
    first_image = cv2.imread(image_paths[0])
    height, width, _ = first_image.shape

    # 動画ファイルを作成
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    for path in image_paths:
        img = cv2.imread(path)
        if img is None:
            raise ValueError(f"Failed to load image {path}")
        out.write(img)

    out.release()


def get_ffmpeg_path():
    if getattr(sys, 'frozen', False):
        # exeとしてビルド後の実行（PyInstaller環境）
        base_path = sys._MEIPASS if hasattr(sys, "_MEIPASS") else os.path.dirname(sys.executable)
    else:
        # 通常のPythonスクリプト実行
        base_path = os.path.dirname(os.path.abspath(__file__))
    
    ffmpeg_path = os.path.join(base_path, "ffmpeg_bin", "ffmpeg.exe")
    if not os.path.exists(ffmpeg_path):
        raise FileNotFoundError(f"ffmpeg.exe not found at {ffmpeg_path}")
    
    return ffmpeg_path

# グローバル定数として取得
FFMPEG_PATH = get_ffmpeg_path()



class CustomGraphicsView(QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setScene(QGraphicsScene(self))
        self.drawing = False
        self.current_path = None
        self.paths = []  # 各画像ごとに後で辞書化予定

        # ✅ ペン色とペン本体
        self.pen_color = Qt.GlobalColor.gray  # ← pen_color を定義
        self.pen = QPen(self.pen_color, 2)    # ← それを使って QPen を作成
        
        self.draw_mode = 'free'  # ← モード（free or click）
        self.click_points = []   # clickモードで使用する座標のリスト
        self.current_path_item = None  # clickモード用

        self.save_callback = None  # ✅ コールバック追加 
        
        self.temp_preview_item = None  # 仮のスムージングプレビュー用
        
        self.gray_image = None  # グレースケール画像（スナップ用）



        
  
        
    def create_smooth_path(self, points):
        if len(points) < 2:
            return QPainterPath()
    
        path = QPainterPath(points[0])
    
        def control_points(p0, p1, p2, p3):
            c1 = QPointF(p1.x() + (p2.x() - p0.x()) / 6.0,
                         p1.y() + (p2.y() - p0.y()) / 6.0)
            c2 = QPointF(p2.x() - (p3.x() - p1.x()) / 6.0,
                         p2.y() - (p3.y() - p1.y()) / 6.0)
            return c1, c2
    
        if len(points) == 2:
            path.lineTo(points[1])
            return path
    
        # 仮想の前点 p_{-1}
        p_minus = QPointF(2 * points[0].x() - points[1].x(),
                          2 * points[0].y() - points[1].y())
    
        # 最初の区間
        c1, c2 = control_points(p_minus, points[0], points[1], points[2])
        path.cubicTo(c1, c2, points[1])
    
        # 中間の区間
        for i in range(1, len(points) - 2):
            c1, c2 = control_points(points[i - 1], points[i], points[i + 1], points[i + 2])
            path.cubicTo(c1, c2, points[i + 1])
    
        # 仮想の後点 p_{n+1}
        p_last = points[-1]
        p_before_last = points[-2]
        p_plus = QPointF(2 * p_last.x() - p_before_last.x(),
                         2 * p_last.y() - p_before_last.y())
    
        # 最後の区間
        c1, c2 = control_points(points[-3], points[-2], points[-1], p_plus)
        path.cubicTo(c1, c2, points[-1])
    
        return path





        

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



    
    def snap_to_edge_wrapper(self, scene_pos):
        import cv2
        import numpy as np
    
        if not hasattr(self, 'gray_image') or self.gray_image is None:
            return scene_pos  # 元画像がなければそのまま
    
        # scene 座標から image 座標に変換
        x = int(scene_pos.x())
        y = int(scene_pos.y())
    
        window_size = 15
        img = self.gray_image
        h, w = img.shape
        half = window_size // 2
    
        x_min = max(0, x - half)
        x_max = min(w, x + half)
        y_min = max(0, y - half)
        y_max = min(h, y + half)
    
        crop = img[y_min:y_max, x_min:x_max]
        edges = cv2.Canny(crop, 50, 150)
    
        if np.count_nonzero(edges) == 0:
            return scene_pos  # エッジなしなら補正しない
    
        ys, xs = np.where(edges > 0)
        xs_global = xs + x_min
        ys_global = ys + y_min
    
        distances = (xs_global - x) ** 2 + (ys_global - y) ** 2
        min_idx = np.argmin(distances)
        snapped_x = int(xs_global[min_idx])
        snapped_y = int(ys_global[min_idx])
    
        return QPointF(snapped_x, snapped_y)

     
    def undo_last_click_point(self):
        if self.draw_mode in ['click', 'click_snap'] and self.click_points:
            self.click_points.pop()  # 最後の点を削除
    
            if len(self.click_points) >= 2:
                smooth_path = self.create_smooth_path(self.click_points)
                self.current_path_item.setPath(smooth_path)
            elif len(self.click_points) == 1:
                self.current_path = QPainterPath(self.click_points[0])
                self.current_path_item.setPath(self.current_path)
            else:
                # すべて削除されたらパスを消去
                if self.current_path_item:
                    self.scene().removeItem(self.current_path_item)
                    self.current_path_item = None
                    self.current_path = None
    
            # 仮プレビューも消す
            if self.temp_preview_item:
                self.scene().removeItem(self.temp_preview_item)
                self.temp_preview_item = None
    
            self.scene().update()
   

    
    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            scene_pos = self.mapToScene(event.pos())
    
            if self.draw_mode == 'free':
                self.drawing = True
                self.current_path = QPainterPath(scene_pos)
                self.current_path_item = QGraphicsPathItem()
                self.current_path_item.setPen(self.pen)
                self.current_path_item.setPath(self.current_path)
                self.scene().addItem(self.current_path_item)
    
            elif self.draw_mode in ('click', 'click_snap'):
                # ▶ snap モードのときは座標を補正
                if self.draw_mode == 'click_snap':
                    snapped_scene_pos = self.snap_to_edge_wrapper(scene_pos)
                    self.click_points.append(snapped_scene_pos)
                else:
                    self.click_points.append(scene_pos)
    
                if len(self.click_points) == 1:
                    self.current_path = QPainterPath(self.click_points[0])
                    self.current_path_item = QGraphicsPathItem()
                    self.current_path_item.setPen(self.pen)
                    self.scene().addItem(self.current_path_item)
                else:
                    smooth_path = self.create_smooth_path(self.click_points)
                    self.current_path_item.setPath(smooth_path)
    
                # 仮プレビューの削除
                if self.temp_preview_item:
                    self.scene().removeItem(self.temp_preview_item)
                    self.temp_preview_item = None
    
            event.accept()



                
    def mouseMoveEvent(self, event: QMouseEvent):
        scene_pos = self.mapToScene(event.pos())
    
        # ✅ freeモード（従来の手描き）
        if self.draw_mode == 'free' and self.drawing and self.current_path:
            self.current_path.lineTo(scene_pos)
            self.current_path_item.setPath(self.current_path)
    
        # ✅ clickモード（仮のスムーズ曲線プレビュー）
        # elif self.draw_mode == 'click' and len(self.click_points) >= 1:
        elif self.draw_mode in ('click', 'click_snap') and len(self.click_points) >= 1:

            temp_points = self.click_points + [scene_pos]
            smooth_path = self.create_smooth_path(temp_points)
    
            # 🔒 temp_preview_item の存在と有効性をチェック
            if self.temp_preview_item:
                if self.temp_preview_item.scene() is not None:
                    self.temp_preview_item.setPath(smooth_path)
                else:
                    print("[WARN] temp_preview_item is deleted or invalid")
                    self.temp_preview_item = None
    
            if not self.temp_preview_item:
                self.temp_preview_item = QGraphicsPathItem()
                self.temp_preview_item.setPen(QPen(Qt.GlobalColor.gray, 1, Qt.PenStyle.DashLine))  # 仮表示は点線で
                self.temp_preview_item.setPath(smooth_path)
                self.scene().addItem(self.temp_preview_item)
    
        event.accept()
            

    
    def finalize_click_drawing(self):
        if self.click_points and self.current_path_item:
            smooth_path = self.create_smooth_path(self.click_points)
            smooth_path.closeSubpath()
            self.current_path_item.setPath(smooth_path)
            self.paths.append(self.current_path_item)
    
            if self.save_callback:
                self.save_callback(smooth_path)
    
            if self.temp_preview_item:
                self.scene().removeItem(self.temp_preview_item)
                self.temp_preview_item = None
    
            self.click_points = []
            self.current_path = None
            self.current_path_item = None
            self.scene().update()

                
    def mouseReleaseEvent(self, event: QMouseEvent):
        if self.draw_mode == 'free':
            if event.button() == Qt.MouseButton.LeftButton and self.drawing:
                self.drawing = False
                path = self.current_path_item.path()
                path.closeSubpath()
                self.current_path_item.setPath(path)
                self.paths.append(self.current_path_item)
                if self.save_callback:
                    self.save_callback(self.current_path_item.path())
                self.scene().update()
    
        elif self.draw_mode in ['click', 'click_snap']:
            if event.button() == Qt.MouseButton.RightButton:
                self.finalize_click_drawing()  # ← 共通処理に置き換え
    
        event.accept()



    # def mouseReleaseEvent(self, event: QMouseEvent):
    #     if self.draw_mode == 'free':
    #         if event.button() == Qt.MouseButton.LeftButton and self.drawing:
    #             self.drawing = False
    #             path = self.current_path_item.path()
    #             path.closeSubpath()
    #             self.current_path_item.setPath(path)
    #             self.paths.append(self.current_path_item)
    #             if self.save_callback:
    #                 self.save_callback(self.current_path_item.path())
    #             self.scene().update()
    

    #     elif self.draw_mode == 'click':
    #         if event.button() == Qt.MouseButton.RightButton:
    #             if self.click_points and self.current_path_item:
    #                 # ✅ 点列をスムージングしたパスに置き換える
    #                 smooth_path = self.create_smooth_path(self.click_points)
    #                 smooth_path.closeSubpath()
    #                 self.current_path_item.setPath(smooth_path)
    #                 self.paths.append(self.current_path_item)
    #                 if self.save_callback:
    #                     self.save_callback(smooth_path)
        
    #                 # ✅ 🔽 ここに仮プレビュー削除を追加
    #                 if self.temp_preview_item:
    #                     self.scene().removeItem(self.temp_preview_item)
    #                     self.temp_preview_item = None        
        
    #                 self.click_points = []
    #                 self.current_path = None
    #                 self.current_path_item = None
    #                 self.scene().update()

        
    #     elif self.draw_mode == 'click_snap':
    #         if event.button() == Qt.MouseButton.RightButton:
    #             if self.click_points and self.current_path_item:
    #                 smooth_path = self.create_smooth_path(self.click_points)
    #                 smooth_path.closeSubpath()
    #                 self.current_path_item.setPath(smooth_path)
    #                 self.paths.append(self.current_path_item)
    #                 if self.save_callback:
    #                     self.save_callback(smooth_path)
        
    #                 if self.temp_preview_item:
    #                     self.scene().removeItem(self.temp_preview_item)
    #                     self.temp_preview_item = None
        
    #                 self.click_points = []
    #                 self.current_path = None
    #                 self.current_path_item = None
    #                 self.scene().update()

        event.accept()


class SegRefMain(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        

        self.image_pristine = True
        self.ignore_spinbox_change = False
        
        # 🔽 Box Prompt用（SAM2統合のため）
        self.box_mode = False
        self.box_points = []
        self.temp_box_item = None
        self.last_box_prompt = None
        self.stored_boxes = []
        # 一括トラッキング用
        self.batch_object_data = []  # 各オブジェクトの情報を辞書形式で保持
        self.box_per_frame = {}  # 例: {0: ((x1,y1), (x2,y2)), 1: ((x1,y1), (x2,y2)), ...}


        
        self.setupUi(self)
    
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

        # ✅ チェックボックスのイベント接続
        for checkbox in self.checkboxes:
            checkbox.stateChanged.connect(self.display_current_image)

        # ✅ ボタンイベント
                
        # self.btn_export_target_mask.clicked.connect(
        #     lambda: self.export_target_object_as_mask(
        #         target_index=self.combo_target_object.currentIndex()
        #     )
        # )  #実験用
        
        
        
        self.btn_load_images.clicked.connect(self.load_image_folder)
        self.btn_thin_images.clicked.connect(self.thin_images_and_reload)

        
        self.btn_load_masks.clicked.connect(self.load_mask_folder)
        self.btn_save_svg_as.clicked.connect(self.save_svg_as)



        
        self.spin_threshold_min.valueChanged.connect(self.on_threshold_spinbox_changed)
        self.spin_threshold_max.valueChanged.connect(self.on_threshold_spinbox_changed)

        self.combo_threshold_preset.currentTextChanged.connect(self.apply_threshold_preset)


        self.btn_extract_threshold.clicked.connect(self.extract_by_threshold)
        # self.btn_otsu_threshold.clicked.connect(self.on_set_min_threshold_by_otsu)







        self.btn_undo.clicked.connect(self.undo_last_path)
        self.btn_redo.clicked.connect(self.redo_last_path)
        self.btn_clear_current_path.clicked.connect(self.clear_current_path)
        self.btn_clear_all_paths.clicked.connect(self.clear_all_paths)        
        
        self.combo_color.currentTextChanged.connect(self.update_pen_color)
        self.combo_draw_mode.currentTextChanged.connect(self.change_draw_mode)
        

        
        
        self.btn_add_to_mask.clicked.connect(self.add_drawn_path_to_mask)
        self.btn_cut_from_mask.clicked.connect(self.cut_drawn_path_from_mask)
        self.btn_transfer_to_mask.clicked.connect(self.transfer_drawn_path_to_mask)
        self.btn_convert_color.clicked.connect(self.convert_object_color_across_svgs)
        self.btn_undo_edit.clicked.connect(self.smart_undo)
        self.btn_redo_edit.clicked.connect(self.redo_edit)
        self.btn_rescan_used_colors.clicked.connect(self.update_checkboxes_based_on_used_colors)

        self.btn_bring_to_front.clicked.connect(self.bring_selected_object_to_front)
        self.btn_send_to_back.clicked.connect(self.send_selected_object_to_back)
        
        
        
        # self.btn_remove_small_parts.clicked.connect(self.delete_small_parts_in_selected_object)
        self.btn_remove_small_parts.clicked.connect(self.on_remove_small_parts)
        self.btn_delete_current_only.clicked.connect(self.delete_selected_object_from_current_image)
        self.btn_delete_object.clicked.connect(self.delete_selected_object)
        self.btn_undo_delete.clicked.connect(self.smart_undo)


        
        # self.btn_export_grayscale_png.clicked.connect(self.export_all_svgs_to_grayscale_png)
        self.btn_export_tiff.clicked.connect(self.export_all_svgs_to_grayscale_tiff)
        self.btn_export_tiff_reversed.clicked.connect(self.export_all_svgs_to_grayscale_tiff_reversed)
        
        self.btn_draw_calibration_line.clicked.connect(self.start_calibration)
        self.btn_export_stl_colorwise.clicked.connect(self.export_colorwise_stl_with_scale)
        self.btn_export_volume_csv.clicked.connect(self.export_colorwise_volumes_to_csv)




        #Undo Redoのための変数
        self.undo_stack = {}  # 例: {'0001': [svg_text_before_edit, ...]}
        self.redo_stack = {}


        # ✅ 状態保持
        self.image_paths = {}
        self.mask_paths = {}
        self.current_index = 0

        self.graphicsView.viewport().installEventFilter(self)

        # ✅ 線データ保持
        self.drawn_paths_per_image = {}
        self.graphicsView.save_callback = self.save_drawn_path
        
        self.color_labels = self.color_labels
        
        self.modified_svg_trees = {}
        self.path_elements_by_color = {}
        
        self.pixmap_cache = {}        # 画像キャッシュ
        self.svg_renderer_cache = {}  # SVGレンダリングキャッシュ
        
        self.drawn_paths_per_image = {}  # 画像キー → [(QPainterPath, モード)] の辞書
        
        now = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.output_mask_dir = os.path.join(os.getcwd(), f"masks_{now}")
        os.makedirs(self.output_mask_dir, exist_ok=True)
        
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
    
        self.sam2_interface = SAM2Interface()
        self.sam2_enabled = self.sam2_interface.has_cuda  # ✅ GPU使用可否の判定

        if not self.sam2_enabled:
            self.label_status.setText("⚠ SAM2 is disabled (requires NVIDIA GPU + CUDA + PyTorch).")

            # SAM2関連のボタンをリストアップ
            sam_buttons = [
                self.btn_run_sam2,
                self.btn_set_box_prompt,
                self.btn_clear_box,
                self.btn_set_tracking_start,
                self.btn_set_tracking_end,
                self.btn_add_object_prompt,
                self.btn_batch_tracking,
                self.btn_run_tracking,
                self.btn_prepare_tracking,
            ]

            # ボタンを無効化し、クリック時にはステータスメッセージを出すようにする
            for btn in sam_buttons:
                try:
                    btn.clicked.disconnect()
                except TypeError:
                    pass
                btn.setEnabled(False)  # ✅ グレーアウト
                btn.setStyleSheet("color: gray; background-color: lightgray;")  # ✅ 見た目もグレーアウト
                btn.clicked.connect(lambda _, b=btn: self.label_status.setText(
                    f"⚠ '{b.text()}' is only available on systems with NVIDIA GPU + CUDA + PyTorch."))
        
        
        self.label_status.setText("Ready.")
        
        self.loaded_images = {}  # 🔧 画像読み込み管理用の辞書
        
        self.btn_set_box_prompt.clicked.connect(self.start_box_prompt_mode)
        self.btn_run_sam2.clicked.connect(self.run_sam2_segmentation)
        self.btn_clear_box.clicked.connect(self.clear_box)
                        
        self.tracking_start_index = None
        self.tracking_end_index = None
        self.btn_prepare_tracking.clicked.connect(self.prepare_tracking_frames)
        self.btn_set_tracking_start.clicked.connect(self.set_tracking_start)
        self.btn_set_tracking_end.clicked.connect(self.set_tracking_end)
        self.btn_run_tracking.clicked.connect(self.run_tracking)
        self.btn_add_object_prompt.clicked.connect(self.add_object_prompt_for_batch)
        self.btn_batch_tracking.clicked.connect(self.run_batch_tracking)
        
        #オーバーラップの検出
        self.btn_extract_overlap.clicked.connect(self.on_extract_overlap_clicked)
        self.btn_extract_overlap_all.clicked.connect(self.on_extract_overlap_clicked_all)  # ← 新関数に接続



    
    
    import re
    



    
    def thin_images_and_reload(self):
        if not self.image_pristine:
            self.label_status.setText("⚠ Please run thinning immediately after loading images, before any operations.")
            return

        

        
        
        factor = self.spin_thin_factor.value()
        if factor <= 1:
            self.label_status.setText("No thinning applied (factor = 1).")
            return
    
        now = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = os.path.join(os.getcwd(), f"thinned_images_{now}")
        os.makedirs(output_dir, exist_ok=True)
    
        # 🔽 数値列をすべて抽出し、naturalな並び順にソート
        image_items = sorted(
            self.image_paths.items(),
            key=lambda item: extract_all_numbers(item[0])
        )
    
        new_image_paths = {}
    
        for i, (key, path) in enumerate(image_items):
            if i % factor == 0:
                img = cv2.imread(path)
                if img is None:
                    continue
                new_name = f"{len(new_image_paths)+1:04d}.jpg"
                save_path = os.path.join(output_dir, new_name)
                cv2.imwrite(save_path, img)
                new_image_paths[new_name[:-4]] = save_path
    
        self.image_paths = new_image_paths
        self.current_index = 0
    
        if self.z_spacing_mm is not None:
            self.z_spacing_mm *= factor
    
        self.display_current_image()
        self.label_status.setText(f"✅ Thinned to every {factor} image(s). Total: {len(new_image_paths)} images.")
        
        
        
                
    def on_threshold_spinbox_changed(self):
        print("[DEBUG] spinbox changed")
        if self.ignore_spinbox_change:
            print("[DEBUG] Change ignored due to flag.")
            return
        print("[DEBUG] Set to Custom")
        if self.combo_threshold_preset.currentText() != "Custom":
            self.combo_threshold_preset.setCurrentText("Custom")
            
            


    
    import re
    
    def normalize_color(self, fill: str, style: str) -> str:
        import re
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





    
    
    def extract_object_mask_as_binary(self, key, object_index):
        """
        対象のSVGファイルから、指定されたオブジェクト番号のマスク領域をバイナリ画像として返す。
        """
        import cv2
        import numpy as np
        from PyQt6.QtGui import QImage, QPainter, QColor
        from PyQt6.QtCore import Qt
        from xml.etree import ElementTree as ET
    
        if key not in self.mask_paths:
            print(f"[WARN] No mask found for {key}")
            return None
    
        # ✅ 元画像サイズを使ってマスクサイズを決定
        if key not in self.image_paths:
            print(f"[WARN] No image path found for key: {key}")
            return None
    
        image_path = self.image_paths[key]
        img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        if img is None:
            print(f"[WARN] Failed to load image: {image_path}")
            return None
    
        height, width = img.shape
    
        # ✅ SVG 読み込み
        svg_path = self.mask_paths[key]
        tree = ET.parse(svg_path)
        root = tree.getroot()
    
        target_rgb = self.color_labels[object_index]
        target_hex = f'#{target_rgb[0]:02x}{target_rgb[1]:02x}{target_rgb[2]:02x}'
    
        image = QImage(width, height, QImage.Format.Format_Grayscale8)
        image.fill(0)
    
        painter = QPainter(image)
        painter.setBrush(QColor(255, 255, 255))
        painter.setPen(Qt.PenStyle.NoPen)
    
        for elem in root.iter("path"):
            fill = elem.attrib.get("fill", "").lower()
            if fill != target_hex:
                continue
    
            d_attr = elem.attrib.get("d")
            if not d_attr:
                continue
    
            path = self.svg_d_to_qpath(d_attr)
            painter.drawPath(path)
    
        painter.end()
    
        ptr = image.bits()
        ptr.setsize(image.width() * image.height())
        arr = np.array(ptr).reshape((image.height(), image.width()))
        return arr

                

        
    
    
    

    
    
    
    
    
    
    def apply_threshold_preset(self, preset_name):
        presets = {
            "CT Bone": (180, 255),
            "CT Soft Tissue": (80, 180),
            "CT Fat": (30, 80),
            "CT Air/Background": (0, 30),
            "MRI High Signal": (150, 255),
            "MRI Low Signal": (0, 60)
        }
    
        self.ignore_spinbox_change = True  # 🚫 一時的に変更検知を無視
    
        if preset_name in presets:
            min_val, max_val = presets[preset_name]
            self.spin_threshold_min.setValue(min_val)
            self.spin_threshold_max.setValue(max_val)
            self.label_status.setText(f"✅ Preset '{preset_name}' applied: Min={min_val}, Max={max_val}")
    



    
        elif preset_name == "Custom":
            self.label_status.setText("🛠 Custom mode: you can set thresholds manually.")
    
        else:
            self.label_status.setText("⚠ Unknown preset selected.")
    
        self.ignore_spinbox_change = False  # ✅ フラグ解除











    
    def svg_d_to_qpath(self, d_string):
        from PyQt6.QtGui import QPainterPath
        import re
    
        path = QPainterPath()
        tokens = re.findall(r"[-+]?\d*\.\d+|[-+]?\d+|[A-Za-z]", d_string)
        i = 0
        current_pos = None
        while i < len(tokens):
            cmd = tokens[i]
            if cmd == "M":
                x, y = float(tokens[i + 1]), float(tokens[i + 2])
                path.moveTo(x, y)
                current_pos = (x, y)
                i += 3
            elif cmd == "L":
                x, y = float(tokens[i + 1]), float(tokens[i + 2])
                path.lineTo(x, y)
                current_pos = (x, y)
                i += 3
            elif cmd == "Z":
                path.closeSubpath()
                i += 1
            else:
                i += 1
        return path




    
    def on_extract_overlap_clicked(self):
        key = self.get_current_image_key()
        if not key:
            self.label_status.setText("⚠ No image selected.")
            return
    
        idx1 = self.combo_overlap1.currentIndex()
        idx2 = self.combo_overlap2.currentIndex()
    
        if idx1 == idx2:
            self.label_status.setText("⚠ Please select two different objects.")
            return
    
        color1 = self.color_labels[idx1]
        color2 = self.color_labels[idx2]
    
        self.extract_overlap_between_objects(key, color1, color2)


    
    def extract_overlap_between_objects(self, key, color1_rgb, color2_rgb):
        if key not in self.mask_paths:
            print(f"[WARN] No SVG found for key {key}")
            return
    
        svg_path = self.mask_paths[key]
        tree = ET.parse(svg_path)
        root = tree.getroot()
    
        def rgb_to_hex(rgb):
            return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"
    
        color1_hex = rgb_to_hex(color1_rgb)
        color2_hex = rgb_to_hex(color2_rgb)
    
        path1 = QPainterPath()
        path2 = QPainterPath()
    
        for elem in root.iter("path"):
            fill = elem.attrib.get("fill", "").lower()
            if fill not in {color1_hex, color2_hex}:
                continue
    
            d = elem.attrib.get("d")
            if not d:
                continue
    
            qpath = self.svg_d_to_qpath(d)
            path_union = QPainterPath()
            for subpath in qpath.toSubpathPolygons():
                if subpath.size() >= 3:
                    sp = QPainterPath()
                    sp.moveTo(subpath[0])
                    for pt in subpath[1:]:
                        sp.lineTo(pt)
                    sp.closeSubpath()
                    path_union = path_union.united(sp)
    
            if fill == color1_hex:
                path1 = path1.united(path_union)
            elif fill == color2_hex:
                path2 = path2.united(path_union)
    
        intersection = path1.intersected(path2)
    
        if intersection.isEmpty():
            self.label_status.setText("⚠ No overlapping area found.")
            return
    
        item = QGraphicsPathItem(intersection)
        # item.setPen(QPen(Qt.GlobalColor.magenta, 2))
        item.setPen(QPen(self.graphicsView.pen_color, 2))  # ← ユーザー設定のペン色に統一
        item.setZValue(5)
        self.scene.addItem(item)
    
        # 保存（描画履歴）
        self.save_drawn_path_for_image(key, intersection)
        self.label_status.setText("✅ Overlap extracted and added to current image.")





    def on_extract_overlap_clicked_all(self):
        idx1 = self.combo_overlap1.currentIndex()
        idx2 = self.combo_overlap2.currentIndex()
    
        if idx1 == idx2:
            self.label_status.setText("⚠ Please select two different objects.")
            return
    
        color1 = self.color_labels[idx1]
        color2 = self.color_labels[idx2]
    
        self.save_svg_state_for_undo("__global__")  # Undoのために一括保存
    
        processed = 0
        for key in self.mask_paths.keys():
            self.extract_overlap_between_objects(key, color1, color2)
            processed += 1
    
        self.display_current_image()
        self.label_status.setText(f"✅ Overlap extraction completed for {processed} images.")

 

    
    # def change_draw_mode(self, mode):
    #     self.graphicsView.draw_mode = mode.lower()  # 'free' or 'click'
    #     self.label_status.setText(f"Draw mode: {mode}")
            
    def change_draw_mode(self, mode):
        if mode == "Click (Snap)":
            self.graphicsView.draw_mode = "click_snap"
        elif mode == "Click":
            self.graphicsView.draw_mode = "click"
        else:
            self.graphicsView.draw_mode = "free"
    
        self.label_status.setText(f"Draw mode: {self.graphicsView.draw_mode}")





    
    def start_box_prompt_mode(self):
        self.box_mode = True
        self.box_points = []
        print("[DEBUG] start_box_prompt_mode called")

            
        # クロスヘア仮線の初期化
        self.temp_crosshair_hline = None
        self.temp_crosshair_vline = None        
    
        # 以前の仮ボックスが残っていれば削除
        if hasattr(self, "temp_box_item") and self.temp_box_item:
            self.scene.removeItem(self.temp_box_item)
            self.temp_box_item = None
            
     

                    
        # 🔸 確定ボックス削除（実線のやつ）
        if hasattr(self, "confirmed_box_item"):
            try:
                if self.confirmed_box_item is not None and self.confirmed_box_item.scene() is not None:
                    self.scene.removeItem(self.confirmed_box_item)
            except RuntimeError:
                print("[WARN] confirmed_box_item has been already deleted.")
            self.confirmed_box_item = None
            
    
    
        # 🔸 保存済みのボックス情報もリセット
        self.last_box_prompt = None
        self.last_used_box_px = None
        
        # 🔸 すべてのフレームのボックス情報もクリア
        self.box_per_frame.clear()
    
        self.label_status.setText("Click top-left and bottom-right corners to set box.")
        
    
    def clear_box(self):
        # ✅ ボックスが表示されていれば削除
        if hasattr(self, "confirmed_box_item") and self.confirmed_box_item:
            self.scene.removeItem(self.confirmed_box_item)
            self.confirmed_box_item = None
    
        if hasattr(self, "temp_box_item") and self.temp_box_item:
            self.scene.removeItem(self.temp_box_item)
            self.temp_box_item = None
    
        # ✅ 状態を初期化
        self.box_points = []
        self.last_box_prompt = None
        self.last_used_box_px = None
        
        # ✅ すべてのフレーム上のボックス情報もクリア
        self.box_per_frame.clear()        
        
        self.label_status.setText("Box cleared.")






    
    def run_sam2_segmentation(self):
        key = self.get_current_image_key()
        if key is None or key not in self.image_paths:
            print("[WARN] No image loaded.")
            return
    
        if not self.last_box_prompt:
            print("[WARN] No box prompt set.")
            return
    
        image_path = self.image_paths[key]
        image_pil = Image.open(image_path).convert("RGB")
        image_np = np.array(image_pil)
    
        # pxに変換
        width, height = image_pil.size
        top_left_percent, bottom_right_percent = self.last_box_prompt
        x1 = top_left_percent[0] * width / 100
        y1 = top_left_percent[1] * height / 100
        x2 = bottom_right_percent[0] * width / 100
        y2 = bottom_right_percent[1] * height / 100
        box = ((x1, y1), (x2, y2))
    
        print(f"[INFO] Running SAM2 on box: {box}")
        
             
                    
        def update_progress(percent):
            bar_length = 20  # バーの長さ（文字数）
            filled_length = int(bar_length * percent // 100)
            bar = '█' * filled_length + '-' * (bar_length - filled_length)
            self.label_status.setText(f"SAM2 segmentation... |{bar}| {percent}%")
            QApplication.processEvents()

        
        result_mask = self.sam2_interface.run_segmentation(image_np, box, progress_callback=update_progress)
    
        # マスクから QPainterPath に変換して、描画＆保存
        qpath = self.sam2_interface.mask_to_qpath(result_mask)
                
        # ✅ パスの簡略化（曲線が多すぎる問題を軽減）
        qpath = qpath.simplified()
 
        
                
        # QGraphicsPathItem を作成（ペン設定も一致させる）
        path_item = QGraphicsPathItem()
        path_item.setPen(self.graphicsView.pen)  # ✅ タッチペン描画と同じペン設定
        path_item.setPath(qpath)
        self.scene.addItem(path_item)
        
        # save_drawn_path にも登録（Undo/Redo対応）
        self.save_drawn_path(qpath)
    
        print("[INFO] SAM2 segmentation done and added to drawing.")
        
        
        
        
        
        # 🔸 表示されている確定ボックス（赤線）を削除
        if hasattr(self, "confirmed_box_item"):
            try:
                if self.confirmed_box_item is not None and self.confirmed_box_item.scene() is not None:
                    self.scene.removeItem(self.confirmed_box_item)
            except RuntimeError:
                print("[WARN] confirmed_box_item has been already deleted.")
            self.confirmed_box_item = None
        

        
        # 🔸 フレームごとのボックス情報も削除
        if hasattr(self, "last_used_box_index") and self.last_used_box_index in self.box_per_frame:
            del self.box_per_frame[self.last_used_box_index]

        
        
        
        
        # ✅ 仮ボックス（マウス移動中の点線）を削除
        if self.temp_box_item:
            self.scene.removeItem(self.temp_box_item)
            self.temp_box_item = None
        
        self.display_current_image()

        # 🔁 run_tracking() 用にボックス(px)も保存
        self.last_used_box_px = box

        print("[DEBUG] result_mask shape:", result_mask.shape)
        print("[DEBUG] result_mask dtype:", result_mask.dtype)
        print("[DEBUG] result_mask unique values:", np.unique(result_mask))






    
    def prepare_tracking_frames(self):
        self.label_status.setText("📦 Preparing tracking frames...")
        QApplication.processEvents()
    
        video_dir = "./video_frames"
        if os.path.exists(video_dir):
            shutil.rmtree(video_dir)
        os.makedirs(video_dir)
    
        image_items = sorted(self.image_paths.items())  # ファイル名でソート
        total = len(image_items)
    
        for i, (name, path) in enumerate(image_items, 1):
            dst_filename = f"{i:04d}.jpg"
            dst_path = os.path.join(video_dir, dst_filename)
            shutil.copyfile(path, dst_path)
    
            # 🔁 進捗バー
            percent = int(i / total * 100)
            bar = "[" + "█" * (percent // 10) + " " * (10 - percent // 10) + "]"
            self.label_status.setText(f"📷 Preparing frames: {bar} {percent}%")
            QApplication.processEvents()
            time.sleep(0.01)
    
        self.label_status.setText("✅ Tracking frames ready.")


    
    def set_tracking_start(self):
        self.tracking_start_index = self.current_image_index
        self.label_status.setText(f"Tracking Start set at frame {self.tracking_start_index + 1}")
    
    def set_tracking_end(self):
        self.tracking_end_index = self.current_image_index
        self.label_status.setText(f"Tracking End set at frame {self.tracking_end_index + 1}")
    
    
    
        
    def hide_confirmed_box(self):
        if hasattr(self, "confirmed_box_item"):
            try:
                if self.confirmed_box_item and self.confirmed_box_item.scene():
                    self.scene.removeItem(self.confirmed_box_item)
            except RuntimeError:
                print("[WARN] confirmed_box_item has been already deleted.")
            self.confirmed_box_item = None  # 表示だけ消す。中身のbox情報は残す


    
    def run_tracking(self):
        # 🔎 チェック：開始・終了フレーム
        if not hasattr(self, 'tracking_start_index') or not hasattr(self, 'tracking_end_index'):
            self.label_status.setText("Please set both start and end frames for tracking.")
            return
    
        if self.tracking_start_index > self.tracking_end_index:
            self.label_status.setText("Tracking start frame must be before end frame.")
            return
    
        self.label_status.setText(f"Tracking will run from frame {self.tracking_start_index + 1} to {self.tracking_end_index + 1}.")
    
    
    
        # ✅ ボックスプロンプト（px単位）を使用
        if not hasattr(self, 'last_used_box_px'):
            self.label_status.setText("⚠ Box prompt not set. Please run SAM2 segmentation first.")
            return
        box = self.last_used_box_px
    
        # 🟡 ポイントプロンプト（任意）
        point = self.last_used_point if hasattr(self, 'last_used_point') else None




        
        video_dir = "./video_frames"
        if not os.path.exists(video_dir):
            self.label_status.setText("⚠ Please run 'Prepare Tracking Frames' first.")
            return
            
    
        # 🔄 推論状態初期化（順方向）
        self.label_status.setText("📷 Loading frames into SAM2... Please wait.")
        QApplication.processEvents()
        
        predictor = self.sam2_interface.predictor
        inference_state = predictor.init_state(video_path=video_dir)
        predictor.reset_state(inference_state)
    
        # 🧠 初期画像の読み込み（順方向）
        box_frame_index = self.last_used_box_index  # ✅ ボックスを置いたフレーム
        frame_idx = box_frame_index
        sample_image = np.array(Image.open(os.path.join(video_dir, f"{frame_idx + 1:04d}.jpg")))
        h, w = sample_image.shape[:2]
    
        # ボックスとポイントの変換
        x1, y1 = int(box[0][0]), int(box[0][1])
        x2, y2 = int(box[1][0]), int(box[1][1])
        box_arr = np.array([x1, y1, x2, y2], dtype=np.float32)
    
        if point:
            x_p, y_p = int(point[0]), int(point[1])
            points = np.array([[x_p, y_p]], dtype=np.float32)
            labels = np.array([1], dtype=np.int32)
        else:
            points = None
            labels = None
    
        # ▶ 順方向の初期マスク設定
        predictor.add_new_points_or_box(
            inference_state=inference_state,
            frame_idx=frame_idx,
            obj_id=1,
            points=points,
            labels=labels,
            box=box_arr
        )
    
        print("[DEBUG] Forward inference_state object_ids:", inference_state.get("obj_ids", "N/A"))
        print(f"[DEBUG] Using box: {box}")
        print(f"[DEBUG] Converted to array: {box_arr}")
    
        # # ▶ 伝播上限
        # frame_limit = self.tracking_end_index
        # video_segments = {}
        
        # # ▶ 進捗バー準備（順方向）
        # total_forward = frame_limit - self.tracking_start_index + 1
                
        # ▶ 伝播上限
        frame_limit = self.tracking_end_index
        video_segments = {}
        
        # ▶ 進捗バー準備（順方向）
        total_forward = frame_limit - box_frame_index + 1
        
        
        
        current_forward = 0
        
        
        
        
    
        # ▶ 順方向の伝播
        for out_frame_idx, out_obj_ids, out_mask_logits in predictor.propagate_in_video(inference_state):
            if out_frame_idx > frame_limit:
                break
            video_segments[out_frame_idx] = {
                out_obj_id: (out_mask_logits[i] > 0.0).squeeze().cpu().numpy()
                for i, out_obj_id in enumerate(out_obj_ids)
            }
    
            # 🌟 進捗バー表示（順方向）
            current_forward += 1
            percent = int(current_forward / total_forward * 100)
            bar = "[" + "█" * (percent // 10) + "-" * (10 - percent // 10) + "]"
            self.label_status.setText(f"▶ Forward tracking {bar} {percent}%")
            QApplication.processEvents()
        


    
        # reversed_frame_indices = list(range(self.tracking_end_index, self.tracking_start_index - 1, -1))
        reversed_frame_indices = list(range(box_frame_index, self.tracking_start_index - 1, -1))




        reversed_video_dir = "./video_frames_reversed"
        if os.path.exists(reversed_video_dir):
            shutil.rmtree(reversed_video_dir)
        os.makedirs(reversed_video_dir)
    
        # for i, idx in enumerate(reversed_frame_indices):
        #     src = os.path.join(video_dir, f"{idx + 1:04d}.jpg")  # ffmpeg -start_number 1 に対応
        #     # dst = os.path.join(reversed_video_dir, f"{i:04d}.jpg")
        #     # ✅ 修正：ffmpeg で読み込めるよう 0001.jpg からスタート
        #     dst = os.path.join(reversed_video_dir, f"{i + 1:04d}.jpg")
        #     shutil.copyfile(src, dst)
        
        #存在確認追加            
        for i, idx in enumerate(reversed_frame_indices):
            src = os.path.join(video_dir, f"{idx + 1:04d}.jpg")  # ffmpeg -start_number 1 に対応
            dst = os.path.join(reversed_video_dir, f"{i + 1:04d}.jpg")
            
            if os.path.exists(src):
                shutil.copyfile(src, dst)
            else:
                print(f"[WARN] Skipping missing frame: {src}")            
    
        # 🔧 修正箇所: reversed ディレクトリで推論初期化
        reversed_inference_state = predictor.init_state(video_path=reversed_video_dir)
        predictor.reset_state(reversed_inference_state)
    
        # 🔧 修正箇所: reversed 側の frame_idx=0 に初期マスク設定
        predictor.add_new_points_or_box(
            inference_state=reversed_inference_state,
            frame_idx=0,
            obj_id=1,
            points=points,
            labels=labels,
            box=box_arr
        )
    
        # 🔧 修正箇所: reversed 側の順方向伝播
        reversed_video_segments = {}
                
        # ▶ 進捗バー準備（逆方向）
        total_backward = len(reversed_frame_indices)
        current_backward = 0        
        
        for out_frame_idx, out_obj_ids, out_mask_logits in predictor.propagate_in_video(reversed_inference_state):
            reversed_video_segments[out_frame_idx] = {
                out_obj_id: (out_mask_logits[i] > 0.0).squeeze().cpu().numpy()
                for i, out_obj_id in enumerate(out_obj_ids)
            }    
         
            # 🌟 進捗バー表示（逆方向）
            current_backward += 1
            percent = int(current_backward / total_backward * 100)
            bar = "[" + "█" * (percent // 10) + "-" * (10 - percent // 10) + "]"
            self.label_status.setText(f"◀ Backward tracking {bar} {percent}%")
            QApplication.processEvents()
                
        # 🔧 修正箇所: reversed の結果を本来のフレームインデックスにマッピング（正確）
        # for i, orig_frame_idx in enumerate(reversed_frame_indices[::-1]):  # 順番を元に戻す
        #     if orig_frame_idx not in video_segments:
        #         video_segments[orig_frame_idx] = reversed_video_segments.get(i, {})
        
        # 🔧 正しいマッピング：reversed_frame_indices[i] → reversed_video_segments[i]
        for i, orig_frame_idx in enumerate(reversed_frame_indices[::-1]):
            # reversed_video_segments の中身は i = 0 が reversed_frame_indices[0] に対応しているので
            reversed_index = total_backward - 1 - i
            if orig_frame_idx not in video_segments:
                video_segments[orig_frame_idx] = reversed_video_segments.get(reversed_index, {})



        # ▶ マスク適用・保存
        frame_names = list(self.image_paths.keys())
    
        for frame_idx, frame_name in enumerate(frame_names):
            if frame_idx > frame_limit:
                break
    
            if frame_idx in video_segments:
                segment_masks = video_segments[frame_idx]
                for obj_id, mask in segment_masks.items():
                    print(f"[DEBUG] Frame {frame_idx}, Obj {obj_id}, mask type: {type(mask)}")
    
                    if mask is None or not isinstance(mask, np.ndarray) or mask.ndim != 2 or not np.any(mask):
                        print(f"[WARN] Skipping frame {frame_idx}, obj_id {obj_id}: invalid mask")
                        continue
    
                    qpath = self.sam2_interface.mask_to_qpath(mask)
                    # ✅ パスの簡略化（曲線が多すぎる問題を軽減）
                    qpath = qpath.simplified()
                    
                    key = f"{frame_idx + 1:04d}"  # ffmpeg に合わせたファイル名対応
    
                    # 既存の描画があれば削除
                    if key in self.drawn_paths_per_image:
                        del self.drawn_paths_per_image[key]
                        print(f"[INFO] Previous path for frame {key} deleted.")
    
                    self.save_drawn_path_for_image(key, qpath)
    
        # ▶ 状態更新
        
        self.label_status.setText("✅ Tracking completed and masks applied to selected frames.")

        

        
        # 🔸 表示されている確定ボックス（赤線）を削除
        if hasattr(self, "confirmed_box_item"):
            try:
                if self.confirmed_box_item is not None and self.confirmed_box_item.scene() is not None:
                    self.scene.removeItem(self.confirmed_box_item)
            except RuntimeError:
                print("[WARN] confirmed_box_item has been already deleted.")
            self.confirmed_box_item = None
        
        # 🔸 ボックスの情報をすべてリセット
        self.last_box_prompt = None
        self.last_used_box_px = None
        
        # 🔸 フレームごとのボックス情報も削除
        if hasattr(self, "last_used_box_index") and self.last_used_box_index in self.box_per_frame:
            del self.box_per_frame[self.last_used_box_index]

            
            
            


        self.last_used_box_px = None
        
        
        self.display_current_image()
        
        


    
    def add_object_prompt_for_batch(self):

        
        if not hasattr(self, 'last_used_box_px'):
            self.label_status.setText("⚠ Box prompt not set.")
            return
        if not hasattr(self, 'tracking_start_index') or not hasattr(self, 'tracking_end_index'):
            self.label_status.setText("⚠ Start and End frame must be set.")
            return
    
        box = self.last_used_box_px
        point = self.last_used_point if hasattr(self, 'last_used_point') else None
        start_frame = self.tracking_start_index
        end_frame = self.tracking_end_index
    
        if len(self.batch_object_data) >= 20:
            self.label_status.setText("⚠ Max 20 objects allowed.")
            return
    
        self.batch_object_data.append({
            "box": box,
            "point": point,
            "start": start_frame,
            "end": end_frame,
            "box_frame": self.last_used_box_index  # ✅ 新規追加
        })
    
        self.label_status.setText(f"🧩 Object {len(self.batch_object_data)} added (Frame {start_frame+1}–{end_frame+1})")
        



    
    def run_tracking_for_object(self, obj_id, box, point, start_frame, end_frame, box_frame):
        self.label_status.setText(f"📦 Tracking Object {obj_id}: Frame {start_frame+1}–{end_frame+1}")
        QApplication.processEvents()
    
        video_dir = "./video_frames"
        if not os.path.exists(video_dir):
            self.label_status.setText("⚠ Please run 'Prepare Tracking Frames' first.")
            return
    
        # 🔄 推論状態初期化（順方向）
        self.label_status.setText("📷 Loading frames into SAM2... Please wait.")
        QApplication.processEvents()
    
        predictor = self.sam2_interface.predictor
        inference_state = predictor.init_state(video_path=video_dir)
        predictor.reset_state(inference_state)
    
        # 初期画像の読み込み
        # frame_idx = start_frame
        frame_idx = box_frame

        sample_image = np.array(Image.open(os.path.join(video_dir, f"{frame_idx + 1:04d}.jpg")))
        h, w = sample_image.shape[:2]
    
        # ボックスとポイントの変換
        x1, y1 = int(box[0][0]), int(box[0][1])
        x2, y2 = int(box[1][0]), int(box[1][1])
        box_arr = np.array([x1, y1, x2, y2], dtype=np.float32)
    
        if point:
            x_p, y_p = int(point[0]), int(point[1])
            points = np.array([[x_p, y_p]], dtype=np.float32)
            labels = np.array([1], dtype=np.int32)
        else:
            points = None
            labels = None
    
        # 初期マスク指定
        predictor.add_new_points_or_box(
            inference_state=inference_state,
            frame_idx=frame_idx,
            obj_id=obj_id,
            points=points,
            labels=labels,
            box=box_arr
        )
    
        # frame_limit = end_frame
        # video_segments = {}
        # # total_forward = frame_limit - start_frame + 1
        # total_forward = end_frame - box_frame + 1

        # current_forward = 0
        
        # ▶ 伝播上限
        # frame_limit = self.tracking_end_index
        frame_limit = end_frame
        video_segments = {}
        
        # ▶ 進捗バー準備（順方向）
        total_forward = frame_limit - box_frame + 1
        current_forward = 0        
        
        
    
        for out_frame_idx, out_obj_ids, out_mask_logits in predictor.propagate_in_video(inference_state):
            if out_frame_idx > frame_limit:
                break
            video_segments[out_frame_idx] = {
                out_obj_id: (out_mask_logits[i] > 0.0).squeeze().cpu().numpy()
                for i, out_obj_id in enumerate(out_obj_ids)
            }
    
            current_forward += 1
            percent = int(current_forward / total_forward * 100)
            bar = "[" + "█" * (percent // 10) + "-" * (10 - percent // 10) + "]"
            self.label_status.setText(f"▶ Object {obj_id}: Forward {bar} {percent}%")
            QApplication.processEvents()
    
        # 逆方向
        # reversed_frame_indices = list(range(end_frame, start_frame - 1, -1))
        reversed_frame_indices = list(range(box_frame, start_frame - 1, -1))

        reversed_video_dir = "./video_frames_reversed"
        if os.path.exists(reversed_video_dir):
            shutil.rmtree(reversed_video_dir)
        os.makedirs(reversed_video_dir)
    
        for i, idx in enumerate(reversed_frame_indices):
            src = os.path.join(video_dir, f"{idx + 1:04d}.jpg")
            dst = os.path.join(reversed_video_dir, f"{i + 1:04d}.jpg")
            if os.path.exists(src):
                shutil.copyfile(src, dst)
            else:
                print(f"[WARN] Skipping missing frame: {src}")
    
        reversed_inference_state = predictor.init_state(video_path=reversed_video_dir)
        predictor.reset_state(reversed_inference_state)
    
        predictor.add_new_points_or_box(
            inference_state=reversed_inference_state,
            frame_idx=0,
            obj_id=obj_id,
            points=points,
            labels=labels,
            box=box_arr
        )
    
        reversed_video_segments = {}
        total_backward = len(reversed_frame_indices)
        current_backward = 0
    
        for out_frame_idx, out_obj_ids, out_mask_logits in predictor.propagate_in_video(reversed_inference_state):
            reversed_video_segments[out_frame_idx] = {
                out_obj_id: (out_mask_logits[i] > 0.0).squeeze().cpu().numpy()
                for i, out_obj_id in enumerate(out_obj_ids)
            }
    
            current_backward += 1
            percent = int(current_backward / total_backward * 100)
            bar = "[" + "█" * (percent // 10) + "-" * (10 - percent // 10) + "]"
            self.label_status.setText(f"◀ Object {obj_id}: Backward {bar} {percent}%")
            QApplication.processEvents()
    
        # # reversed → 正規順に戻す
        # for i, orig_frame_idx in enumerate(reversed_frame_indices[::-1]):
        #     reversed_index = total_backward - 1 - i  # ✅ 正しい順に戻す
        #     if orig_frame_idx not in video_segments:
        #         video_segments[orig_frame_idx] = reversed_video_segments.get(i, {})
            
        # ⬇ reversed_video_segments を正しい位置に統合する
        for out_frame_idx, masks in reversed_video_segments.items():
            # 対応する元のフレームインデックスを取得
            if out_frame_idx < len(reversed_frame_indices):
                orig_frame_idx = reversed_frame_indices[out_frame_idx]
                if orig_frame_idx not in video_segments:
                    video_segments[orig_frame_idx] = masks
    
    
        # マスク保存
        frame_names = list(self.image_paths.keys())
        for frame_idx, frame_name in enumerate(frame_names):
            if frame_idx > frame_limit:
                break
            if frame_idx in video_segments:
                segment_masks = video_segments[frame_idx]
                for seg_obj_id, mask in segment_masks.items():
                    if mask is None or not isinstance(mask, np.ndarray) or mask.ndim != 2 or not np.any(mask):
                        print(f"[WARN] Skipping frame {frame_idx}, obj_id {seg_obj_id}: invalid mask")
                        continue
                    qpath = self.sam2_interface.mask_to_qpath(mask)
                    # ✅ パスの簡略化（曲線が多すぎる問題を軽減）
                    qpath = qpath.simplified()
                    key = f"{frame_idx + 1:04d}"
    
                    if key in self.drawn_paths_per_image:
                        del self.drawn_paths_per_image[key]
                        print(f"[INFO] Previous path for frame {key} deleted.")
                    
                    # RGB → hex変換
                    def rgb_to_hex(rgb):
                        return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"
                    
                    # SVGファイルが存在するか確認
                    svg_path = self.mask_paths.get(key)
                    if svg_path and os.path.exists(svg_path):
                        try:
                            tree = ET.parse(svg_path)
                            root = tree.getroot()
                    
                            # QPainterPath → path d 文字列
                            polygons = qpath.toSubpathPolygons()
                            path_data = ""
                            for polygon in polygons:
                                if polygon.size() < 3:
                                    continue
                                path_data += "M " + " L ".join(f"{pt.x()},{pt.y()}" for pt in polygon) + " Z "
                    
                            # オブジェクトの色（obj_id）で fill 指定
                            obj_color_rgb = self.color_labels[obj_id - 1]  # 1-indexed
                            fill_color = rgb_to_hex(obj_color_rgb)
                    
                            new_elem = ET.Element("path")
                            new_elem.set("d", path_data.strip())
                            new_elem.set("fill", fill_color)
                            new_elem.set("stroke", "none")
                            new_elem.set("fill-rule", "evenodd")
                            root.append(new_elem)
                    
                            # 保存先を output_mask_dir に変更
                            save_path = os.path.join(self.output_mask_dir, os.path.basename(svg_path))
                            tree.write(save_path, encoding="utf-8")
                    
                            print(f"[INFO] Object {obj_id}: SVG path added to {save_path}")
                    
                            # UI再描画のため、drawn_paths にも qpath を保存
                            # self.drawn_paths_per_image[key] = [(qpath, fill_color)]
                            self.checkboxes[obj_id - 1].setChecked(True)
                    
                        except Exception as e:
                            print(f"[ERROR] Failed to write SVG path for {key}: {e}")


    
                    self.save_drawn_path_for_image(key, qpath)
    
        self.label_status.setText(f"✅ Object {obj_id}: Tracking complete.")
        self.clear_all_paths()



    
    def run_batch_tracking(self):
        if not self.batch_object_data:
            self.label_status.setText("⚠ No objects registered for batch tracking.")
            return
    
        for obj_idx, obj_info in enumerate(self.batch_object_data, 1):
            self.label_status.setText(f"🚀 Tracking object {obj_idx} (Frame {obj_info['start']+1}–{obj_info['end']+1})...")
            QApplication.processEvents()
    
            self.run_tracking_for_object(
                obj_id=obj_idx,
                box=obj_info["box"],
                point=obj_info["point"],
                start_frame=obj_info["start"],
                end_frame=obj_info["end"],
                box_frame=obj_info["box_frame"]  # ✅ これを追加
            )
    
        self.label_status.setText("✅ All batch tracking completed.")
                
        
                        
        # 🔸 表示されている確定ボックス（赤線）を削除
        if hasattr(self, "confirmed_box_item"):
            try:
                if self.confirmed_box_item is not None and self.confirmed_box_item.scene() is not None:
                    self.scene.removeItem(self.confirmed_box_item)
            except RuntimeError:
                print("[WARN] confirmed_box_item has been already deleted.")
            self.confirmed_box_item = None
        
        # 🔸 ボックスの情報をすべてリセット
        self.last_box_prompt = None
        self.last_used_box_px = None
        
        # 🔸 フレームごとのボックス情報をすべて削除（これが必要！）
        self.box_per_frame.clear()


            
            
        
        self.display_current_image()








        
    # def smart_undo(self):
    #     key = self.get_current_image_key()
    
    #     # ① 手描きパスのUndo（最優先）
    #     if key in self.drawn_paths_per_image and self.drawn_paths_per_image[key]:
    #         self.undo_last_path()
    #         print("[INFO] Ctrl+Z → undo_last_drawn_path done")
    #         return

    #     # ③ 通常の1画像Undo
    #     if key in self.undo_stack and self.undo_stack[key]:
    #         self.undo_edit(key)  # ← ✅ 明示的に現在の画像キーを指定
    #         print("[INFO] Ctrl+Z → undo_svg_edit done")
    #         return

    
    #     # ② 全画像対象のUndoがある場合
    #     if "__global__" in self.undo_stack and self.undo_stack["__global__"]:
    #         self.undo_edit("__global__")  # ← ✅ 修正
    #         print("[INFO] Ctrl+Z → undo_global_svg_edit done")
    #         return

    

    
    #     # ④ それでも何もなければ
    #     self.label_status.setText("Nothing to undo.")
    #     print("[INFO] Ctrl+Z → nothing to undo")
        
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



    def start_calibration(self):
        self.display_current_image()
        self.calibration_mode = True
        self.calibration_points = []
        self.label_status.setText("Click two points to draw calibration line.")

        

    def get_current_image_key(self):
        """現在の画像インデックスからキー（ファイル名）を取得"""
        keys = list(self.image_paths.keys())
        if 0 <= self.current_index < len(keys):
            return keys[self.current_index]
        return None



    def update_pen_color(self, color_name):
        if color_name == "Gray":
            color = Qt.GlobalColor.gray
        elif color_name == "White":
            color = Qt.GlobalColor.white
        elif color_name == "Black":
            color = Qt.GlobalColor.black
        else:
            color = Qt.GlobalColor.gray  # デフォルト fallback
    
        self.graphicsView.pen = QPen(color, 2)
        self.graphicsView.pen_color = color  # ✅ pen_colorも同期して更新

    


    
    def extract_by_threshold(self):
        if not self.image_paths:
            print("[WARN] No images loaded.")
            return
    
        min_val = self.spin_threshold_min.value()
        max_val = self.spin_threshold_max.value()
    
        current_key = self.get_current_image_key()
    
        for key, image_path in self.image_paths.items():
            try:
                image_pil = Image.open(image_path).convert("L")  # グレースケール
                image_np = np.array(image_pil)
    
                # 🎯 閾値処理
                mask = np.where((image_np >= min_val) & (image_np <= max_val), 255, 0).astype(np.uint8)
    
                # ✨ マスク → QPainterPath
                qpath = self.sam2_interface.mask_to_qpath(mask)
    
                # ✏ 現在表示中の画像には画面にも描画
                if key == current_key:
                    path_item = QGraphicsPathItem()
                    path_item.setPen(self.graphicsView.pen)  # タッチペンと同じ設定
                    path_item.setPath(qpath)
                    self.scene.addItem(path_item)
    
                # 💾 Undo/Redo & SVG対応
                # self.save_drawn_path(qpath, key_override=key)
                self.save_drawn_path_for_image(key, qpath)

    
                print(f"[INFO] Extracted mask from {image_path} (key: {key})")
    
            except Exception as e:
                print(f"[WARN] Failed to process {image_path}: {e}")
    
        self.label_status.setText(f"✅ Threshold extraction completed for all images.")
    






        
    def undo_last_path(self):
        key = f"{self.current_index + 1:04}"
        if key in self.drawn_paths_per_image and self.drawn_paths_per_image[key]:
            last_path = self.drawn_paths_per_image[key].pop()  # 最後のパスを取り出す
            self.redo_stack[key].append(last_path)             # 🔁 Redo用に保存
            self.display_current_image()
    
    def redo_last_path(self):
        key = self.get_current_image_key()
        if key in self.redo_stack and self.redo_stack[key]:
            restored_path = self.redo_stack[key].pop()
    
            # パス配列がなければ初期化
            if key not in self.drawn_paths_per_image:
                self.drawn_paths_per_image[key] = []
    
            self.drawn_paths_per_image[key].append(restored_path)
            self.display_current_image()
    
    def clear_current_path(self):
        key = self.get_current_image_key()
        if key in self.drawn_paths_per_image:
            self.drawn_paths_per_image[key] = []
            self.display_current_image()
    
    def clear_all_paths(self):
        for key in self.image_paths.keys():
            self.drawn_paths_per_image[key] = []
        self.display_current_image()

    # def clear_all_paths(self):
    #     key = f"{self.current_index + 1:04}"
    #     if key in self.drawn_paths_per_image:
    #         self.drawn_paths_per_image[key] = []
    #         self.display_current_image()




    
    def _create_empty_svg(self, svg_path, reference_image_path):
        from xml.etree.ElementTree import Element, SubElement, ElementTree
    
        # 画像サイズを取得
        with Image.open(reference_image_path) as img:
            width, height = img.size
    
        # SVGの基本構造を構築
        svg = Element("svg", xmlns="http://www.w3.org/2000/svg",
                      width=str(width), height=str(height),
                      viewBox=f"0 0 {width} {height}")
        tree = ElementTree(svg)
        tree.write(svg_path, encoding="utf-8", xml_declaration=True)
            
                
            
            
                    
    def _normalize_grayscale(self, array):
        arr = array.astype(np.float32)
        arr -= arr.min()
        arr /= (arr.max() + 1e-8)
        arr *= 255.0
        return arr.astype(np.uint8)
    
    
    
    
    def load_image_folder(self):
        import pathlib
    
        folder = QFileDialog.getExistingDirectory(self, "Select Image Folder")
        if not folder:
            return
    
        # 🔽 新しいフォルダを作成（元のフォルダ名 + jpg）
        # input_folder = pathlib.Path(folder)
        # jpg_folder = input_folder.parent / f"{input_folder.name}jpg"
        input_folder = pathlib.Path(folder)
        jpg_folder = pathlib.Path(os.getcwd()) / f"{input_folder.name}jpg"
        # jpg_folder.mkdir(exist_ok=True)
    
        # 🔽 対応拡張子（大文字も許容）
        valid_exts = {".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp", ".dcm"}
        self.image_paths = {}
        self.image_sizes = {}  # ✅ 追加：画像サイズ保存用
    
        # 🔽 変換処理
        for i, filename in enumerate(sorted(os.listdir(folder))):
            ext = pathlib.Path(filename).suffix.lower()
            if ext not in valid_exts:
                continue
    
            input_path = os.path.join(folder, filename)
            key = f"{i+1:04}"
            output_jpg_path = os.path.join(jpg_folder, f"image{key}.jpg")  # ✅ ← image0001.jpg形式に
                            
            try:
                if ext == ".dcm":
                    if not jpg_folder.exists():  # 🔑 必要になったタイミングで作成
                        jpg_folder.mkdir(exist_ok=True)
                    
                    # DICOM を JPEG に変換
                    ds = pydicom.dcmread(input_path)
                    arr = ds.pixel_array
                    arr = self._normalize_grayscale(arr)
                    image = Image.fromarray(arr).convert("RGB")
                    image.save(output_jpg_path, "JPEG")
                    self.image_paths[key] = output_jpg_path
                    self.image_sizes[key] = image.size  # ✅ サイズ記録
            
                elif ext == ".jpg":
                    # すでにJPEGならそのまま使う（再保存しない）
                    self.image_paths[key] = input_path
                    image = Image.open(input_path)
                    self.image_sizes[key] = image.size  # ✅ サイズ記録
            
                else:
                    if not jpg_folder.exists():  # 🔑 必要になったタイミングで作成
                        jpg_folder.mkdir(exist_ok=True)
                    # 他の画像形式はJPEGに変換して保存
                    image = Image.open(input_path).convert("RGB")
                    image.save(output_jpg_path, "JPEG")
                    self.image_paths[key] = output_jpg_path
                    self.image_sizes[key] = image.size  # ✅ サイズ記録
                
            except Exception as e:
                print(f"[WARN] Failed to process {filename}: {e}")
    
        self.label_status.setText(f"Loaded {len(self.image_paths)} images (converted to JPG).")
        self.current_index = 0
    
        # 🔽 output_mask_dir を初期化
        now = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.output_mask_dir = os.path.join(os.getcwd(), f"masks_{now}")
        os.makedirs(self.output_mask_dir, exist_ok=True)
    
        # 🔽 空のSVGを生成して mask_paths に登録
        for key, img_path in self.image_paths.items():
            svg_filename = f"mask{key}.svg"
            svg_path = os.path.join(self.output_mask_dir, svg_filename)
            self._create_empty_svg(svg_path, img_path)
            self.mask_paths[key] = svg_path
            
        # 🔽 代表となるDICOMを1枚探す（1番目でOK）
        dcm_paths = [os.path.join(folder, f) for f in sorted(os.listdir(folder)) if f.lower().endswith(".dcm")]
        if dcm_paths:
            try:
                # import pydicom
                ds = pydicom.dcmread(dcm_paths[0])
        
                width = int(getattr(ds, "Columns", 0))
                height = int(getattr(ds, "Rows", 0))
                depth = len(dcm_paths)
        
                pixel_spacing = getattr(ds, "PixelSpacing", ["", ""])
                slice_thickness = getattr(ds, "SliceThickness", "")
        
                image_position = getattr(ds, "ImagePositionPatient", ["", "", ""])
        
                # 🔽 表形式で出力
                volume_table = [
                    ["Width", "Height", "Depth"],
                    [str(width), str(height), str(depth)],
                    ["X Spacing", "Y Spacing", "Z Spacing"],
                    [str(pixel_spacing[0]), str(pixel_spacing[1]), str(slice_thickness)],
                    ["X Origin", "Y Origin", "Z Origin"],
                    [str(image_position[0]), str(image_position[1]), str(image_position[2])]
                ]
        
                # 🔽 値を保存しておく（STL生成で使用）
                self.mm_per_px = float(pixel_spacing[0]) if pixel_spacing[0] else None
                self.z_spacing_mm = float(slice_thickness) if slice_thickness else None        
        
                # 🔽 保存ファイル名：入力フォルダ名 + _volinf.csv
                csv_filename = f"{input_folder.name}_volinf.csv"
                csv_path = os.path.join(os.getcwd(), csv_filename)
        
                with open(csv_path, "w", newline="", encoding="utf-8") as f:
                    writer = csv.writer(f)
                    writer.writerows(volume_table)
        
                print(f"[INFO] Volume info saved to: {csv_path}")
            except Exception as e:
                print(f"[WARN] Failed to extract volume info: {e}")

        self.image_pristine = True
        self.display_current_image()
            
            
            


    
    def load_mask_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Mask Folder")
        if folder:
            self.mask_paths = self.load_files_from_folder(folder, [".svg"])
            self.label_status.setText(f"Loaded {len(self.mask_paths)} masks.")
            
            
            # 🔽 既存のself.output_mask_dirを使う（未定義なら新規作成）
            if not hasattr(self, "output_mask_dir") or not os.path.exists(self.output_mask_dir):
                now = datetime.now().strftime("%Y%m%d_%H%M%S")
                self.output_mask_dir = os.path.join(os.getcwd(), f"masks_{now}")
                os.makedirs(self.output_mask_dir, exist_ok=True)
            
    
            # 🔽 使用可能なRGB色リストをhexに変換（例: "#ff0000"）
            allowed_colors = {f"#{r:02x}{g:02x}{b:02x}" for r, g, b in self.color_labels}
    
            # 🔽 全てのマスクを処理
            for key, path in self.mask_paths.items():
                save_path = os.path.join(self.output_mask_dir, os.path.basename(path))
                shutil.copy2(path, save_path)
                self.mask_paths[key] = save_path  # 🔁 保存先を参照に切り替え
    
                # ➕ SVGファイルを読み込み、定義色以外の要素を削除
                try:
                    tree = ET.parse(save_path)
                    root = tree.getroot()
                    elements_to_remove = []
    
                    for elem in root.iter():
                        fill = elem.attrib.get("fill", "")
                        style = elem.attrib.get("style", "")
    
                        # fill属性またはstyle属性のfillから色を抽出
                        color = self._normalize_color(fill, style)
    
                        if color and color not in allowed_colors:
                            elements_to_remove.append(elem)
    
                    for elem in elements_to_remove:
                        parent = self._find_parent(root, elem)
                        if parent is not None:
                            parent.remove(elem)
    
                    tree.write(save_path, encoding="utf-8")
                except Exception as e:
                    print(f"[WARN] Failed to clean {save_path}: {e}")
    
            self.display_current_image()
            self.update_checkboxes_based_on_used_colors()


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


    
    def update_checkboxes_based_on_used_colors(self):
        used_colors = set()
    
        for svg_path in self.mask_paths.values():
            try:
                tree = ET.parse(svg_path)
                root = tree.getroot()
    
                for elem in root.iter():
                    fill = elem.attrib.get('fill')
                    if fill and fill.startswith('#'):
                        # hex → RGBタプルへ変換
                        r = int(fill[1:3], 16)
                        g = int(fill[3:5], 16)
                        b = int(fill[5:7], 16)
                        used_colors.add((r, g, b))
            except Exception as e:
                print(f"[WARN] Failed to parse {svg_path}: {e}")
                continue
    
        # チェックボックスを更新
        for i, color in enumerate(self.color_labels):
            checkbox = self.checkboxes[i]
            checkbox.setChecked(color in used_colors)


        
    def save_svg_as(self):
        folder_path = QFileDialog.getExistingDirectory(
            self, "Select Folder to Save SVGs"
        )
    
        if not folder_path:
            self.label_status.setText("Save canceled.")
            return
    
        count = 0
        for key, svg_path in self.mask_paths.items():
            if os.path.exists(svg_path):
                dst_path = os.path.join(folder_path, f"mask{key}.svg")
                shutil.copyfile(svg_path, dst_path)
                count += 1
    
        self.label_status.setText(f"{count} SVGs saved to: {folder_path}")






    def display_current_image(self):
        # # ✅ 途中描画を中断して初期化（click系）
        # if self.graphicsView.draw_mode in ['click', 'click_snap']:
        #     self.graphicsView.click_points = []
        #     if self.graphicsView.current_path_item:
        #         try:
        #             self.graphicsView.scene().removeItem(self.graphicsView.current_path_item)
        #         except RuntimeError:
        #             pass
        #         self.graphicsView.current_path_item = None
        #     if self.graphicsView.temp_preview_item:
        #         try:
        #             self.graphicsView.scene().removeItem(self.graphicsView.temp_preview_item)
        #         except RuntimeError:
        #             pass
        #         self.graphicsView.temp_preview_item = None



        # ✅ 現在の画像インデックスを記録
        self.current_image_index = self.current_index 
        
        # 🧠 現在の表示状態を保持
        current_transform = self.graphicsView.transform()
        h_value = self.graphicsView.horizontalScrollBar().value()
        v_value = self.graphicsView.verticalScrollBar().value()
    
        self.scene.clear()
    
        key = f"{self.current_index + 1:04}"
        filename = os.path.basename(self.image_paths.get(key, "N/A"))
        self.label_status.setText(f"Displaying {filename} ({self.current_index + 1}/{len(self.image_paths)})")
            
        # 🔹 画像（pixmap）キャッシュを利用
        if key in self.image_paths:
            if key not in self.pixmap_cache:
                self.pixmap_cache[key] = QPixmap(self.image_paths[key])
            pixmap = self.pixmap_cache[key]
            item = QGraphicsPixmapItem(pixmap)
            self.scene.addItem(item)
        
        if key in self.mask_paths:
            from xml.etree import ElementTree as ET
            from io import BytesIO
            
            from PyQt6.QtGui import QImage, QPainter
        
            tree = ET.parse(self.mask_paths[key])
            root = tree.getroot()
        
            hex_colors = [f'#{r:02x}{g:02x}{b:02x}' for (r, g, b) in self.color_labels]
        
            for elem in list(root.iter()):
                fill = elem.attrib.get("fill", "")
                style = elem.attrib.get("style", "")
        
                if not fill and "fill:" in style:
                    match = re.search(r'fill:([^;"]+)', style)
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
        
            pixmap = self.pixmap_cache.get(key)
            width = pixmap.width() if pixmap else 512
            height = pixmap.height() if pixmap else 512
        
            image = QImage(width, height, QImage.Format.Format_ARGB32)
            image.fill(0)
            painter = QPainter(image)
            renderer.render(painter)
            painter.end()
        
            svg_pixmap = QPixmap.fromImage(image)
            svg_item = QGraphicsPixmapItem(svg_pixmap)
            svg_item.setOpacity(0.3)
            svg_item.setZValue(1)
            self.scene.addItem(svg_item)

        self.graphicsView.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.graphicsView.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorViewCenter)
        
        # ⛔ fitInViewを呼ばない（リセットされるから）
        # self.graphicsView.resetTransform()
        self.graphicsView.setTransform(current_transform)  # ズームを戻す
    
        # スクロール位置を復元
        self.graphicsView.horizontalScrollBar().setValue(h_value)
        self.graphicsView.verticalScrollBar().setValue(v_value)
        
        pixmap = self.pixmap_cache[key]
        item = QGraphicsPixmapItem(pixmap)
        self.scene.addItem(item)
        self.scene.setSceneRect(QRectF(pixmap.rect()))

        
        
        
        
        # ✅ 描画済みの線を再表示
        key = f"{self.current_index + 1:04}"
        if key in self.drawn_paths_per_image:
            for path, color in self.drawn_paths_per_image[key]:
                path_item = QGraphicsPathItem(path)
                # path_item.setPen(QPen(color, 2))  # ✅ 保存された色で描画
                path_item.setPen(QPen(QColor(color), 2))  # ✅ colorがstrならQColorに変換
                self.scene.addItem(path_item)



                        
        # ✅ このフレームにボックスがあれば再表示
        if self.current_index in self.box_per_frame:
            p1, p2 = self.box_per_frame[self.current_index]
            rect = QRectF(p1, p2).normalized()
            box_item = QGraphicsRectItem(rect)
            box_item.setPen(QPen(Qt.GlobalColor.red, 2))
            box_item.setZValue(10)
            self.scene.addItem(box_item)
                    
        # ✅ グレースケール画像（OpenCV）をスナップ用にセット
        gray_path = self.image_paths[key]
        gray = cv2.imread(gray_path, cv2.IMREAD_GRAYSCALE)
        self.graphicsView.gray_image = gray            
            
            
                    
                


        

        
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
                    # ✅ 描画途中なら確定（切り替え前に！）
                    if self.graphicsView.draw_mode in ['click', 'click_snap']:
                        if self.graphicsView.click_points and self.graphicsView.current_path_item:
                            self.graphicsView.finalize_click_drawing()                    
                    
                    self.current_index += 1
                    self.image_pristine = False  # 🔸 操作フラグをオフ
                    self.display_current_image()
                return True
        
            elif key in (Qt.Key.Key_PageUp, Qt.Key.Key_R, Qt.Key.Key_U):
                if self.current_index > 0:
                    # ✅ 描画途中なら確定（切り替え前に！）
                    if self.graphicsView.draw_mode in ['click', 'click_snap']:
                        if self.graphicsView.click_points and self.graphicsView.current_path_item:
                            self.graphicsView.finalize_click_drawing()                    
                    
                    self.current_index -= 1
                    self.image_pristine = False  # 🔸 操作フラグをオフ
                    self.display_current_image()
                return True
            
            # 🔍 拡大：E
            elif key in (Qt.Key.Key_E, Qt.Key.Key_I, Qt.Key.Key_Plus, Qt.Key.Key_Equal):
                self.graphicsView.scale(1.25, 1.25)
                return True
    
            # 🔎 縮小：Q
            elif key in (Qt.Key.Key_Q, Qt.Key.Key_P, Qt.Key.Key_Minus):
                self.graphicsView.scale(0.8, 0.8)
                return True
                        
            elif key in (Qt.Key.Key_W, Qt.Key.Key_O, Qt.Key.Key_Up):
                self.graphicsView.verticalScrollBar().setValue(
                    self.graphicsView.verticalScrollBar().value() - 50  # 上へ
                )
                return True
            
            elif key in (Qt.Key.Key_S, Qt.Key.Key_L, Qt.Key.Key_Down):
                self.graphicsView.verticalScrollBar().setValue(
                    self.graphicsView.verticalScrollBar().value() + 50  # 下へ
                )
                return True
            
            elif key in (Qt.Key.Key_A, Qt.Key.Key_K, Qt.Key.Key_Left):
                self.graphicsView.horizontalScrollBar().setValue(
                    self.graphicsView.horizontalScrollBar().value() - 50  # 左へ
                )
                return True
            
            elif key in (Qt.Key.Key_D, Qt.Key.Key_Semicolon, Qt.Key.Key_Right):
                self.graphicsView.horizontalScrollBar().setValue(
                    self.graphicsView.horizontalScrollBar().value() + 50  # 右へ
                )
                return True
            
            # ✅ Tキーでクリック描画を確定
            elif key in (Qt.Key.Key_G, Qt.Key.Key_H):
                if self.graphicsView.draw_mode in ['click', 'click_snap']:
                    self.graphicsView.finalize_click_drawing()
                    return True            
                       
            elif key in (Qt.Key.Key_T, Qt.Key.Key_Y):
                if self.graphicsView.draw_mode in ['click', 'click_snap']:
                    self.graphicsView.undo_last_click_point()
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
                
                    # ✅ 先に確定ボックスを追加
                    self.confirmed_box_item = QGraphicsRectItem(rect)
                    self.confirmed_box_item.setPen(QPen(Qt.GlobalColor.red, 2))
                    self.confirmed_box_item.setZValue(10)  # 仮ボックスより上に描画したければ
                    self.scene.addItem(self.confirmed_box_item)
                
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
    
        # from datetime import datetime
        # folder_name = Path(self.output_mask_dir).name.replace("masks_", "")
        # csv_path = Path(self.output_mask_dir).parent / f"{folder_name}_volinf.csv"
        
        input_folder_name = Path(self.image_paths.get("0001") or list(self.image_paths.values())[0]).parent.name
        csv_filename = f"{input_folder_name}_volinf.csv"
        csv_path = Path(self.output_mask_dir).parent / csv_filename

    
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
        
        
        
        
                
                
    def undo_edit(self, key=None):
        if key is None:
            key = self.get_current_image_key()
    
        # 🔁 グローバルUndo（全画像対象の操作があれば優先）
        if key == "__global__" and self.undo_stack.get("__global__"):
            snapshot = self.undo_stack["__global__"].pop()
    
            # Redo用に現在の全状態を保存
            current_state = {}
            for k in snapshot:
                if k in self.mask_paths and os.path.exists(self.mask_paths[k]):
                    with open(self.mask_paths[k], "r", encoding="utf-8") as f:
                        current_state[k] = f.read()
            self.redo_stack.setdefault("__global__", []).append(current_state)
    
            # 復元
            for k, svg_text in snapshot.items():
                if k in self.mask_paths:
                    with open(self.mask_paths[k], "w", encoding="utf-8") as f:
                        f.write(svg_text)
    
            self.display_current_image()
            self.label_status.setText("Undo (all images) completed.")
            return
    
        # 🟨 通常Undo（1画像のみ）
        if key in self.undo_stack and self.undo_stack[key]:
            current_svg_path = self.mask_paths.get(key)
            if current_svg_path and os.path.exists(current_svg_path):
                # Redo用に現在状態を保存
                with open(current_svg_path, "r", encoding="utf-8") as f:
                    self.redo_stack.setdefault(key, []).append(f.read())
    
                # Undo復元
                previous_svg = self.undo_stack[key].pop()
                with open(current_svg_path, "w", encoding="utf-8") as f:
                    f.write(previous_svg)
    
                self.display_current_image()
                self.label_status.setText(f"Undo (image {key}) completed.")
            else:
                self.label_status.setText(f"SVG path not found for image {key}")
        else:
            self.label_status.setText("Nothing to undo.")
            
            
    
    # def redo_edit(self):
    #     key = self.get_current_image_key()
    #     if key in self.redo_stack and self.redo_stack[key]:
    #         current_svg_path = self.mask_paths[key]
    #         with open(current_svg_path, "r", encoding="utf-8") as f:
    #             self.undo_stack.setdefault(key, []).append(f.read())
    #         next_svg = self.redo_stack[key].pop()
    #         with open(current_svg_path, "w", encoding="utf-8") as f:
    #             f.write(next_svg)
    #         self.display_current_image()
    
    def redo_edit(self):
        key = self.get_current_image_key()
    
        # 🔁 グローバルRedo（全画像対象の操作）
        if "__global__" in self.redo_stack and self.redo_stack["__global__"]:
            snapshot = self.redo_stack["__global__"].pop()
    
            # Undo用に現在の全状態を保存
            current_state = {}
            for k in snapshot:
                if k in self.mask_paths and os.path.exists(self.mask_paths[k]):
                    with open(self.mask_paths[k], "r", encoding="utf-8") as f:
                        current_state[k] = f.read()
            self.undo_stack.setdefault("__global__", []).append(current_state)
    
            # 復元
            for k, svg_text in snapshot.items():
                if k in self.mask_paths:
                    with open(self.mask_paths[k], "w", encoding="utf-8") as f:
                        f.write(svg_text)
    
            self.display_current_image()
            self.label_status.setText("Redo (all images) completed.")
            return
    
        # 🟨 通常Redo（1画像のみ）
        if key in self.redo_stack and self.redo_stack[key]:
            current_svg_path = self.mask_paths[key]
            with open(current_svg_path, "r", encoding="utf-8") as f:
                self.undo_stack.setdefault(key, []).append(f.read())
            next_svg = self.redo_stack[key].pop()
            with open(current_svg_path, "w", encoding="utf-8") as f:
                f.write(next_svg)
            self.display_current_image()
            self.label_status.setText(f"Redo (image {key}) completed.")
        else:
            self.label_status.setText("Nothing to redo.")




    
    def save_drawn_path(self, path):
        key = self.get_current_image_key()

        # 🔒 パスを確実に閉じる
        if not path.isEmpty():
            path.closeSubpath()
    
        # パスの初期化（なければ）
        if key not in self.drawn_paths_per_image:
            self.drawn_paths_per_image[key] = []
    
        # 🔁 Redoスタックも初期化（Undo後の新規描画で履歴を消す）
        if key not in self.redo_stack:
            self.redo_stack[key] = []
        self.redo_stack[key].clear()
    
        # ペンの色付きでパスを保存
        self.drawn_paths_per_image[key].append((path, self.graphicsView.pen_color))



    def save_drawn_path_for_image(self, key, qpath):
        # 🔒 パスを確実に閉じる
        if not qpath.isEmpty():
            qpath.closeSubpath()

        if key not in self.drawn_paths_per_image:
            self.drawn_paths_per_image[key] = []
        self.drawn_paths_per_image[key].append((qpath, self.graphicsView.pen_color))
        print(f"[INFO] Drawn path added to frame: {key}")


    
    def redraw_paths(self):
        self.remove_all_path_items()
        key = self.get_current_image_key()
        if key in self.drawn_paths_per_image:
            for path, color in self.drawn_paths_per_image[key]:
                path_item = QGraphicsPathItem(path)
                pen = QPen(color, 2)
                path_item.setPen(pen)
                self.scene.addItem(path_item)
                self.graphicsView.path_items.append(path_item)





    #ベクターのみで簡潔するver    
    def add_drawn_path_to_mask(self):
        # self.save_svg_state_for_undo(self.get_current_image_key())
        # ✅ ループ前に一度だけ全画像の Undo 保存
        self.save_svg_state_for_undo()        
    
        from PyQt6.QtGui import QPainterPath
        from xml.etree import ElementTree as ET
    
        def parse_svg_path_to_qpath(d_attr):
            path = QPainterPath()
            tokens = re.findall(r"[-+]?\d*\.\d+|[-+]?\d+|[A-Za-z]", d_attr)
            i = 0
            while i < len(tokens):
                cmd = tokens[i]
                if cmd == "M":
                    x, y = float(tokens[i + 1]), float(tokens[i + 2])
                    path.moveTo(x, y)
                    i += 3
                elif cmd == "L":
                    x, y = float(tokens[i + 1]), float(tokens[i + 2])
                    path.lineTo(x, y)
                    i += 3
                elif cmd == "Z":
                    path.closeSubpath()
                    i += 1
                else:
                    i += 1
            return path
    
        def normalize_color(fill, style):
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
    
        def safe_remove(root, target_elem):
            for parent in root.iter():
                if target_elem in list(parent):
                    parent.remove(target_elem)
                    return True
            return False
    
        # 対象色を取得
        idx = self.combo_target_object.currentIndex()
        target_rgb = self.color_labels[idx]
        fill_color = f'#{target_rgb[0]:02x}{target_rgb[1]:02x}{target_rgb[2]:02x}'
    
        # 各画像についてループ
        for key, paths in self.drawn_paths_per_image.items():
            if not paths or key not in self.mask_paths:
                continue

            # self.save_svg_state_for_undo("__global__", key)  # ✅ keyごとに保存（__global__スタックに）
    
            svg_path = self.mask_paths.get(key)
            if not svg_path:
                print(f"[DEBUG] No SVG path found for key: {key}")
                continue
            print(f"[DEBUG] Processing SVG path: {svg_path}")
    
            tree = ET.parse(svg_path)
            root = tree.getroot()
    
            print(f"[DEBUG] SVG: {svg_path}")
            all_tags = [elem.tag for elem in root.iter()]
            print(f"[DEBUG] Found tags: {set(all_tags)}")
    
            # 既存パスと描画パスの統合
            combined_path = QPainterPath()
            for path, _ in paths:
                path.closeSubpath()
                combined_path.addPath(path)
            
            combined_path.setFillRule(Qt.FillRule.OddEvenFill)  # ✅ ここを追加！
    
            color_map = {}
            for elem in root.findall(".//path"):
                fill = normalize_color(elem.attrib.get("fill", ""), elem.attrib.get("style", ""))
                color_map.setdefault(fill, []).append(elem)





            
            from PyQt6.QtGui import QPainterPath
            
            # ✅ 描画されたパスを1つにまとめる
            combined_path = QPainterPath()
            for path, _ in paths:
                path.closeSubpath()
                combined_path.addPath(path)
            combined_path.setFillRule(Qt.FillRule.OddEvenFill)
            
            # ✅ SVGパスデータを生成
            polygons = combined_path.toSubpathPolygons()
            svg_path_data = ""
            for polygon in polygons:
                if polygon.size() < 3:
                    continue
                svg_path_data += "M " + " L ".join(f"{pt.x()},{pt.y()}" for pt in polygon) + " Z "
            
            # ✅ 現在選択中の色で追加（既存 path は削除しない）
            idx = self.combo_target_object.currentIndex()
            target_rgb = self.color_labels[idx]
            fill_color = f'#{target_rgb[0]:02x}{target_rgb[1]:02x}{target_rgb[2]:02x}'
            
            new_elem = ET.Element("path")
            new_elem.set("d", svg_path_data.strip())
            new_elem.set("fill", fill_color)
            new_elem.set("stroke", "none")
            new_elem.set("fill-rule", "evenodd")
            root.append(new_elem)
            
            
                
                
    
            # 保存
            original_name = os.path.basename(svg_path)
            save_path = os.path.join(self.output_mask_dir, original_name)
            tree.write(save_path, encoding="utf-8")
    
            # この画像の描画をクリア
            self.drawn_paths_per_image[key] = []
    
        self.display_current_image()
        # ✅ 対象オブジェクトを明示的に表示ONにする
        self.checkboxes[idx].setChecked(True)
    
   # #ラスタライズを介するパターン        
   #  def add_drawn_path_to_mask(self):
   #      from PyQt6.QtGui import QPainterPath
   #      from xml.etree import ElementTree as ET
    
   #      def normalize_color(fill, style):
   #          def rgb_to_hex(rgb_str):
   #              match = re.match(r'rgb\((\d+),\s*(\d+),\s*(\d+)\)', rgb_str)
   #              if match:
   #                  r, g, b = map(int, match.groups())
   #                  return f'#{r:02x}{g:02x}{b:02x}'
   #              return rgb_str.strip().lower()
    
   #          color = ""
   #          if style and "fill:" in style:
   #              match = re.search(r'fill:([^;"]+)', style)
   #              if match:
   #                  color = match.group(1).strip().lower()
   #          elif fill:
   #              color = fill.strip().lower()
    
   #          if color.startswith("rgb"):
   #              return rgb_to_hex(color)
   #          return color
    
   #      self.save_svg_state_for_undo()
    
   #      idx = self.combo_target_object.currentIndex()
   #      target_rgb = self.color_labels[idx]
   #      fill_color = f'#{target_rgb[0]:02x}{target_rgb[1]:02x}{target_rgb[2]:02x}'
    
   #      for key, paths in self.drawn_paths_per_image.items():
   #          if not paths or key not in self.mask_paths:
   #              continue
    
   #          svg_path = self.mask_paths[key]
   #          tree = ET.parse(svg_path)
   #          root = tree.getroot()
    
   #          # 🔸 描画パスを結合
   #          combined_path = QPainterPath()
   #          for path, _ in paths:
   #              path.closeSubpath()
   #              simplified = self.simplify_path(path)
   #              combined_path.addPath(simplified)
   #          combined_path.setFillRule(Qt.FillRule.OddEvenFill)
    
   #          # 🔸 ラスタライズしてバイナリマスク化
   #          width, height = self.image_sizes.get(key, (512, 512))
   #          binary_mask = self.rasterize_path_to_binary(combined_path, width, height)
    
   #          # 🔸 輪郭抽出
   #          contour_paths = self.extract_paths_from_binary(binary_mask)
    
   #          # 🔸 SVGに path を追加
   #          for path in contour_paths:
   #              svg_path_data = ""
   #              for polygon in path.toSubpathPolygons():
   #                  if polygon.size() < 3:
   #                      continue
   #                  svg_path_data += "M " + " L ".join(f"{pt.x()},{pt.y()}" for pt in polygon) + " Z "
    
   #              new_elem = ET.Element("path")
   #              new_elem.set("d", svg_path_data.strip())
   #              new_elem.set("fill", fill_color)
   #              new_elem.set("stroke", "none")
   #              new_elem.set("fill-rule", "evenodd")
   #              root.append(new_elem)
    
   #          # 🔸 保存
   #          save_path = os.path.join(self.output_mask_dir, os.path.basename(svg_path))
   #          tree.write(save_path, encoding="utf-8", xml_declaration=True)
   #          self.mask_paths[key] = save_path
    
   #          # 🔸 描画パスをクリア
   #          self.drawn_paths_per_image[key] = []
    
   #          if key == self.get_current_image_key():
   #              self.display_current_image()
   #              self.scene.update()
    
   #      self.display_current_image()
   #      self.scene.update()
   #      self.checkboxes[idx].setChecked(True)






    def qpath_to_svg_path(self, path: QPainterPath) -> str:
        """QPainterPath を SVG パス文字列に変換"""
        svg_parts = []
        for i in range(path.elementCount()):
            e = path.elementAt(i)
            cmd = "M" if i == 0 else "L"
            svg_parts.append(f"{cmd} {e.x:.2f} {e.y:.2f}")
        svg_parts.append("Z")
        return " ".join(svg_parts)






    def simplify_path(self, path: QPainterPath, tolerance: float = 2.0) -> QPainterPath:
        from PyQt6.QtGui import QPolygonF
        simplified = QPainterPath()
        polygon = path.toFillPolygon()
        if polygon:
            simplified.addPolygon(QPolygonF(polygon))
        return simplified

    def parse_svg_path_to_qpath(self, d_attr, step_size=5.0):
        from svgpathtools import parse_path
        import numpy as np
        from PyQt6.QtGui import QPainterPath

        path_obj = parse_path(d_attr)
        qpath = QPainterPath()
        for segment in path_obj:
            num = max(2, int(segment.length() // step_size))
            points = [segment.point(t) for t in np.linspace(0, 1, num)]
            for i, pt in enumerate(points):
                x, y = pt.real, pt.imag
                if i == 0 and qpath.isEmpty():
                    qpath.moveTo(x, y)
                else:
                    qpath.lineTo(x, y)
        return qpath






    
    def export_target_object_as_mask(self, target_index: int = 0):
        from PyQt6.QtGui import QImage, QPainter, QPixmap
        from PyQt6.QtSvg import QSvgRenderer
        from PyQt6.QtCore import Qt, QRectF
        from xml.etree import ElementTree as ET
        from io import BytesIO
        from datetime import datetime
        import os
        from copy import deepcopy  # ← 追加
    
        if not self.image_paths:
            print("[ERROR] No images loaded.")
            return
    
        key = list(self.image_paths.keys())[0]
        image_path = self.image_paths[key]
        svg_path = self.mask_paths[key]
    
        pixmap = QPixmap(image_path)
        width = pixmap.width()
        height = pixmap.height()
        if width == 0 or height == 0:
            print(f"[ERROR] Failed to get valid size from: {image_path}")
            return
    
        # 🎯 ターゲット色
        target_rgb = self.color_labels[target_index]
        target_hex = f'#{target_rgb[0]:02x}{target_rgb[1]:02x}{target_rgb[2]:02x}'.lower()
    
    
    
        
        # 🛠 SVG 読み込みとフィルター処理
        tree = ET.parse(svg_path)
        root = tree.getroot()
        
        match_count = 0
        target_elements = []
        
        for elem in list(root.iter()):
            fill = elem.attrib.get("fill", "")
            style = elem.attrib.get("style", "")
            color = self._normalize_color(fill, style)
        
            elem.attrib.pop("style", None)  # styleの影響を除去
        
            if color == target_hex:
                target_copy = deepcopy(elem)
                target_copy.set("fill", "#ffffff")  # 白に塗って最後に描画
                target_elements.append(target_copy)
                elem.set("fill", "#000000")  # 元の場所にも一応黒で残す
                match_count += 1
            else:
                elem.set("fill", "#000000")  # その他は黒塗り
        
        # ✅ 白いターゲット要素を最後に追加（前面に来る）
        for target_elem in target_elements:
            root.append(target_elem)
        
        print(f"[DEBUG] Matched {match_count} elements for target color {target_hex}")

    
    
    
        # 🔁 SVGラスタライズ処理
        svg_bytes = BytesIO()
        tree.write(svg_bytes, encoding='utf-8')
        svg_data = svg_bytes.getvalue()
    
        renderer = QSvgRenderer(svg_data)
        image = QImage(width, height, QImage.Format.Format_RGB32)
        image.fill(Qt.GlobalColor.black)
        image.fill(0)  # ✅ これが抜けていた！
    
        painter = QPainter()
        if painter.begin(image):
            painter.setRenderHint(QPainter.RenderHint.Antialiasing, False)
            painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, False)
            renderer.render(painter, QRectF(0, 0, width, height))  # ✅ 描画範囲明示
            painter.end()
        else:
            print("[ERROR] QPainter failed")
            return
    
        # 💾 保存
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        save_dir = os.path.join(os.getcwd(), f"target_mask_output_{timestamp}")
        os.makedirs(save_dir, exist_ok=True)
        save_path = os.path.join(save_dir, f"{key}_mask.tiff")
        image.save(save_path, "TIFF")
        print(f"[SAVED] Target mask saved to: {save_path}")



    
    def svg_object_to_binary_mask(self, key: str, target_index: int) -> np.ndarray:
        from PyQt6.QtGui import QImage, QPainter, QPixmap
        from PyQt6.QtSvg import QSvgRenderer
        from PyQt6.QtCore import Qt, QRectF
        from xml.etree import ElementTree as ET
        from io import BytesIO
        import numpy as np
        from copy import deepcopy
    
        if key not in self.image_paths or key not in self.mask_paths:
            print(f"[ERROR] Invalid key: {key}")
            return None
    
        image_path = self.image_paths[key]
        svg_path = self.mask_paths[key]
    
        pixmap = QPixmap(image_path)
        width = pixmap.width()
        height = pixmap.height()
        if width == 0 or height == 0:
            print(f"[ERROR] Failed to get valid size from: {image_path}")
            return None
    
        # 🎯 ターゲット色
        target_rgb = self.color_labels[target_index]
        target_hex = f'#{target_rgb[0]:02x}{target_rgb[1]:02x}{target_rgb[2]:02x}'.lower()
    
        # 🛠 SVG 読み込みと描画調整
        tree = ET.parse(svg_path)
        root = tree.getroot()
    
        target_elements = []
        match_count = 0
    
        for elem in list(root.iter()):
            fill = elem.attrib.get("fill", "")
            style = elem.attrib.get("style", "")
            color = self._normalize_color(fill, style)
    
            elem.attrib.pop("style", None)  # 副作用を除去
    
            if color == target_hex:
                target_copy = deepcopy(elem)
                target_copy.set("fill", "#ffffff")
                target_elements.append(target_copy)
                elem.set("fill", "#000000")
                match_count += 1
            else:
                elem.set("fill", "#000000")
    
        for target_elem in target_elements:
            root.append(target_elem)
    
        if match_count == 0:
            print(f"[WARN] No matching elements found for {target_hex}")
    
        # 🔁 SVG → QImage
        svg_bytes = BytesIO()
        tree.write(svg_bytes, encoding='utf-8')
        svg_data = svg_bytes.getvalue()
    
        renderer = QSvgRenderer(svg_data)
        image = QImage(width, height, QImage.Format.Format_RGB32)
        image.fill(Qt.GlobalColor.black)
        image.fill(0)
    
        painter = QPainter()
        if painter.begin(image):
            painter.setRenderHint(QPainter.RenderHint.Antialiasing, False)
            painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, False)
            renderer.render(painter, QRectF(0, 0, width, height))
            painter.end()
        else:
            print("[ERROR] QPainter failed")
            return None
    
        # 🔁 QImage → NumPy配列
        ptr = image.bits().asstring(image.width() * image.height() * 4)
        arr = np.frombuffer(ptr, dtype=np.uint8).reshape((height, width, 4))
        binary_mask = (arr[:, :, 0] + arr[:, :, 1] + arr[:, :, 2]) > 0  # 白部分だけTrue
    
        return binary_mask
    



       
    def rasterize_path_to_binary(self, path: QPainterPath, width: int, height: int) -> np.ndarray:
        from PyQt6.QtGui import QImage, QPainter
        from PyQt6.QtCore import Qt
        import numpy as np
    
        image = QImage(width, height, QImage.Format.Format_ARGB32)
        image.fill(Qt.GlobalColor.black)
    
        painter = QPainter(image)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, False)
        painter.setBrush(Qt.GlobalColor.white)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawPath(path)
        painter.end()
    
        # numpy配列に変換して白い部分を True に
        ptr = image.bits().asstring(image.width() * image.height() * 4)
        arr = np.frombuffer(ptr, dtype=np.uint8).reshape((image.height(), image.width(), 4))
        binary = arr[:, :, 0] > 0  # R成分が0より大きければ白
    
        return binary
    

    

    
    
    def extract_paths_from_binary(self, binary_mask: np.ndarray, min_area: float = 100.0) -> list:
        import cv2
        from PyQt6.QtGui import QPainterPath
        from PyQt6.QtCore import QPointF, Qt
    
        paths = []
    
        # ✅ OpenCV用に uint8 に変換（True→255、False→0）
        if binary_mask.dtype != np.uint8:
            binary_mask = (binary_mask > 0).astype(np.uint8) * 255
    
    
        
        contours, _ = cv2.findContours(binary_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
    
        combined_path = QPainterPath()
    
        for contour in contours:
            if len(contour) < 3:
                continue
    
            area = cv2.contourArea(contour)
            if area < min_area:
                continue
    
            sub_path = QPainterPath()
            sub_path.moveTo(QPointF(contour[0][0][0], contour[0][0][1]))
            for point in contour[1:]:
                x, y = point[0]
                sub_path.lineTo(QPointF(x, y))
            sub_path.closeSubpath()
            combined_path.addPath(sub_path)
    
        combined_path.setFillRule(Qt.FillRule.OddEvenFill)
        return [combined_path]  # ✅ 1つの複合パスとして返す


                
            
    def cut_drawn_path_from_mask(self):
        from PIL import Image
        from PyQt6.QtGui import QPainterPath, QPainterPathStroker
        from PyQt6.QtCore import QPointF, Qt
    
        def normalize_color(fill, style):
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
    
        def safe_remove(root, target_elem):
            for parent in root.iter():
                if target_elem in list(parent):
                    parent.remove(target_elem)
                    return True
            return False
    
        key_current = self.get_current_image_key()
        if not key_current or key_current not in self.drawn_paths_per_image:
            return
    
        self.save_svg_state_for_undo()
    
        idx = self.combo_target_object.currentIndex()
        target_rgb = self.color_labels[idx]
        fill_color = f'#{target_rgb[0]:02x}{target_rgb[1]:02x}{target_rgb[2]:02x}'
    
        for key, paths in self.drawn_paths_per_image.items():
            if not paths or key not in self.mask_paths:
                continue
    
            svg_path = self.mask_paths[key]
            tree = ET.parse(svg_path)
            root = tree.getroot()
    
            drawn_union = QPainterPath()
            for path, _ in paths:
                path.closeSubpath()
                simplified = self.simplify_path(path)
                drawn_union.addPath(simplified)
    
            drawn_union.setFillRule(Qt.FillRule.OddEvenFill)
    
            # 描画領域を画像化 → 輪郭再抽出（subtractedによる穴潰れ回避）
            width, height = self.image_sizes.get(key, (512, 512))
            # binary_mask = self.path_to_binary_image(drawn_union, width, height)
            binary_mask = self.rasterize_path_to_binary(drawn_union, width, height)

            # contour_paths = self.extract_paths_from_binary(binary_mask)
            contour_paths = self.extract_paths_from_binary(binary_mask, min_area=100.0)

    
            elements_to_process = list(root.iter())
    
            for elem in elements_to_process:
                tag = elem.tag.lower()
                fill = normalize_color(elem.attrib.get("fill", ""), elem.attrib.get("style", ""))
                if fill != fill_color:
                    continue
    
                if tag.endswith("path"):
                    d_attr = elem.attrib.get("d", "")
                    if not d_attr:
                        continue
                    try:
                        original_path = self.parse_svg_path_to_qpath(d_attr, step_size=5.0)
                        original_path.setFillRule(Qt.FillRule.OddEvenFill)
                    except Exception as e:
                        print(f"[DEBUG] Failed to parse path: {e}")
                        continue
  
    
  
                    
                    # 🔸 ターゲットインデックス取得
                    target_index = self.combo_target_object.currentIndex()
                    
                    # 🔸 SVGから特定オブジェクトのみレンダリングしてバイナリ化
                    original_binary = self.svg_object_to_binary_mask(key, target_index)
                    if original_binary is None:
                        print("[ERROR] Failed to generate binary mask.")
                        return
                    

                    
                    # 🔸 描画領域のバイナリマスク（これは path → image でOK）
                    # drawn_binary = self.path_to_binary_image(drawn_union, width, height)
                    drawn_binary = self.rasterize_path_to_binary(drawn_union, width, height)

                    
                    
                    
                    # # ✅ デバッグ出力
                    # cv2.imwrite("debug_original_binary.png", original_binary * 255)
                    # cv2.imwrite("debug_drawn_binary.png", drawn_binary * 255)

                    
                    # ✅ ラスター subtract
                    cut_result = original_binary & (~drawn_binary)
                    # cv2.imwrite("debug_cut_result.png", cut_result.astype(np.uint8) * 255)
                                        
                    # # 🔍 デバッグ用にラスター subtract 結果を保存（白＝残る部分）
                    # debug_cut_path = os.path.join(self.output_mask_dir, f"debug_cut_{os.path.basename(svg_path).replace('.svg', '.png')}")
                    # cv2.imwrite(debug_cut_path, cut_result * 255)  # 白黒で保存（uint8）
                    # print(f"[DEBUG] Saved cut_result image to: {debug_cut_path}")                    
                    
                    # 輪郭を再抽出
                    # cut_paths = self.extract_paths_from_binary(cut_result)
                    cut_paths = self.extract_paths_from_binary(cut_result, min_area=100.0)

                    
                    # 元の path 要素を削除
                    safe_remove(root, elem)
                    
                    # 抽出した path を SVG として追加
                    for path in cut_paths:
                        svg_path_data = ""
                        for polygon in path.toSubpathPolygons():
                            if polygon.size() < 3:
                                continue
                            svg_path_data += "M " + " L ".join(f"{pt.x()},{pt.y()}" for pt in polygon) + " Z "
                    
                        new_elem = ET.Element("path")
                        new_elem.set("d", svg_path_data.strip())
                        new_elem.set("fill", fill_color)
                        new_elem.set("stroke", "none")
                        new_elem.set("fill-rule", "evenodd")
                        root.append(new_elem)
    
    
    
    
    
    
            save_path = os.path.join(self.output_mask_dir, os.path.basename(svg_path))
            tree.write(save_path, encoding="utf-8", xml_declaration=True)
            self.mask_paths[key] = save_path
            self.drawn_paths_per_image[key] = []
    
            if key == key_current:
                self.display_current_image()
                self.scene.update()
    
        self.display_current_image()
        self.scene.update()        
        
        
    
                
    # def transfer_drawn_path_to_mask(self):
    #     # key = self.get_current_image_key()
    #     # self.save_svg_state_for_undo(key)
        
    #     # ✅ ループ前に一度だけ全画像の Undo 保存
    #     self.save_svg_state_for_undo()       

    #     from PyQt6.QtGui import QPainterPath
    #     from xml.etree import ElementTree as ET
    
    #     def normalize_color(fill, style):
    #         def rgb_to_hex(rgb_str):
    #             match = re.match(r'rgb\((\d+),\s*(\d+),\s*(\d+)\)', rgb_str)
    #             if match:
    #                 r, g, b = map(int, match.groups())
    #                 return f'#{r:02x}{g:02x}{b:02x}'
    #             return rgb_str.strip().lower()
    
    #         color = ""
    #         if style and "fill:" in style:
    #             match = re.search(r'fill:([^;"]+)', style)
    #             if match:
    #                 color = match.group(1).strip().lower()
    #         elif fill:
    #             color = fill.strip().lower()
    
    #         if color.startswith("rgb"):
    #             return rgb_to_hex(color)
    #         return color
    
    #     def parse_svg_path_to_qpath(d_attr, step_size=1.0):
    #         path_obj = parse_path(d_attr)
    #         qpath = QPainterPath()
    #         for segment in path_obj:
    #             num = max(2, int(segment.length() // step_size))
    #             points = [segment.point(t) for t in np.linspace(0, 1, num)]
    #             for i, pt in enumerate(points):
    #                 x, y = pt.real, pt.imag
    #                 if i == 0 and qpath.isEmpty():
    #                     qpath.moveTo(x, y)
    #                 else:
    #                     qpath.lineTo(x, y)
    #         return qpath
    
    #     def safe_remove(root, target_elem):
    #         for parent in root.iter():
    #             if target_elem in list(parent):
    #                 parent.remove(target_elem)
    #                 return True
    #         return False
    
    #     key_current = self.get_current_image_key()
    #     if not key_current or key_current not in self.drawn_paths_per_image:
    #         return
    
    #     # 元のオブジェクト色と、転送先オブジェクト色
    #     idx_src = self.combo_target_object.currentIndex()
    #     idx_dst = self.combo_transfer_target.currentIndex()
    #     src_rgb = self.color_labels[idx_src]
    #     dst_rgb = self.color_labels[idx_dst]
    #     src_color = f'#{src_rgb[0]:02x}{src_rgb[1]:02x}{src_rgb[2]:02x}'
    #     dst_color = f'#{dst_rgb[0]:02x}{dst_rgb[1]:02x}{dst_rgb[2]:02x}'
    
    #     for key, paths in self.drawn_paths_per_image.items():
    #         if not paths or key not in self.mask_paths:
    #             continue
    
    #         svg_path = self.mask_paths[key]
    #         tree = ET.parse(svg_path)
    #         root = tree.getroot()
    
    #         drawn_union = QPainterPath()
    #         for path, _ in paths:
    #             path.closeSubpath()
    #             drawn_union.addPath(path)
    #         drawn_union.setFillRule(Qt.FillRule.OddEvenFill)  # ✅ 穴対応

    #         print(f"[DEBUG] drawn_union is empty? {drawn_union.isEmpty()}")
    
    #         elements_to_process = list(root.iter())
    
    #         for elem in elements_to_process:
    #             tag = elem.tag.lower()
    #             fill = normalize_color(elem.attrib.get("fill", ""), elem.attrib.get("style", ""))
    #             if fill != src_color:
    #                 continue
    
    #             # polygon 処理
    #             if tag.endswith("polygon"):
    #                 points_str = elem.attrib.get("points", "").strip()
    #                 if not points_str:
    #                     continue
    #                 try:
    #                     points = [QPointF(float(x), float(y)) for x, y in (pt.split(",") for pt in points_str.split())]
    #                 except Exception as e:
    #                     print(f"[DEBUG] Failed to parse polygon points: {e}")
    #                     continue
    
    #                 polygon_path = QPainterPath()
    #                 if points:
    #                     polygon_path.moveTo(points[0])
    #                     for pt in points[1:]:
    #                         polygon_path.lineTo(pt)
    #                     polygon_path.closeSubpath()

    #                 # 🔧 修正ポイント①：交差部分を転送先色で追加
    #                 intersected = polygon_path.intersected(drawn_union)
                    
                    
                    
    #                 svg_path_data = ""
    #                 for polygon in intersected.toSubpathPolygons():
    #                     if polygon.size() < 3:
    #                         continue
    #                     svg_path_data += "M " + " L ".join(f"{pt.x()},{pt.y()}" for pt in polygon) + " Z "
    #                 new_elem = ET.Element("path")
    #                 new_elem.set("d", svg_path_data.strip())
    #                 new_elem.set("fill", dst_color)
    #                 new_elem.set("stroke", "none")
    #                 new_elem.set("fill-rule", "evenodd")
    #                 root.append(new_elem)

                        
    
    #                 # 🔧 修正ポイント②：差分を元の色で残す
    #                 subtracted = polygon_path.subtracted(drawn_union)
                    
                    
                                        
    #                 svg_path_data = ""
    #                 for polygon in subtracted.toSubpathPolygons():
    #                     if polygon.size() < 3:
    #                         continue
    #                     svg_path_data += "M " + " L ".join(f"{pt.x()},{pt.y()}" for pt in polygon) + " Z "
    #                 new_elem = ET.Element("path")
    #                 new_elem.set("d", svg_path_data.strip())
    #                 new_elem.set("fill", src_color)
    #                 new_elem.set("stroke", "none")
    #                 new_elem.set("fill-rule", "evenodd")
    #                 root.append(new_elem)

                    
                    
    
    #                 # 🔧 修正ポイント③：元の要素を削除
    #                 safe_remove(root, elem)



    
    #             # path 処理
    #             elif tag.endswith("path"):
    #                 d_attr = elem.attrib.get("d", "")
    #                 if not d_attr:
    #                     continue
    #                 try:
    #                     original_path = parse_svg_path_to_qpath(d_attr)
    #                 except Exception as e:
    #                     print(f"[DEBUG] Failed to parse path d attribute: {e}")
    #                     continue
                        
    #                 # 🔧 修正ポイント④：交差部分を転送先色で追加
    #                 intersected = original_path.intersected(drawn_union)
    #                 for polygon in intersected.toSubpathPolygons():
    #                     if polygon.size() < 3:
    #                         continue
    #                     points = [f"{pt.x()},{pt.y()}" for pt in polygon]
    #                     svg_path_data = "M " + " L ".join(points) + " Z"
                        
                        
                        
    #                     new_elem = ET.Element("path")
    #                     new_elem.set("d", svg_path_data)
    #                     new_elem.set("fill", dst_color)
    #                     new_elem.set("stroke", "none")
    #                     new_elem.set("fill-rule", "evenodd")

                        
                        
    #                     root.append(new_elem)
    
    #                 # 🔧 修正ポイント⑤：差分を元の色で残す
    #                 subtracted = original_path.subtracted(drawn_union)
    #                 for polygon in subtracted.toSubpathPolygons():
    #                     if polygon.size() < 3:
    #                         continue
    #                     points = [f"{pt.x()},{pt.y()}" for pt in polygon]
    #                     svg_path_data = "M " + " L ".join(points) + " Z"
                        
                        
    #                     new_elem = ET.Element("path")
    #                     new_elem.set("d", svg_path_data)
                        
                        
    #                     new_elem.set("fill", dst_color)
                        
    #                     # ✅ 修正: 元の色を使うべき
    #                     new_elem.set("fill", src_color)                        
    #                     new_elem.set("stroke", "none")
    #                     new_elem.set("fill-rule", "evenodd")
                        
                        
    #                     root.append(new_elem)
    
    #                 # 🔧 修正ポイント⑥：元の要素を削除
    #                 safe_remove(root, elem)                    
                    

    
    
    #         # 保存
    #         save_path = os.path.join(self.output_mask_dir, os.path.basename(svg_path))
    #         tree.write(save_path, encoding="utf-8")
    #         self.mask_paths[key] = save_path
    #         self.drawn_paths_per_image[key] = []

    #     self.update_checkboxes_based_on_used_colors()
    #     self.display_current_image()
    #     self.scene.update()
        
            
    def _add_contours_to_svg(self, binary_mask, color_hex, root):
        contours, hierarchy = cv2.findContours(binary_mask, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
        if hierarchy is None:
            return
    
        hierarchy = hierarchy[0]  # shape: (n_contours, 4)
    
        def contour_to_path(contour):
            points = [f"{pt[0][0]},{pt[0][1]}" for pt in contour]
            return "M " + " L ".join(points) + " Z"
    
        # 輪郭と階層構造から path を構築
        for i, (contour, hier) in enumerate(zip(contours, hierarchy)):
            if hier[3] != -1:
                continue  # 子輪郭（穴）は親のパスで処理されるのでスキップ
    
            # ✅ 親輪郭
            d = contour_to_path(contour)
    
            # ✅ 子（穴）を含める
            child_idx = hier[2]
            while child_idx != -1:
                d += " " + contour_to_path(contours[child_idx])
                child_idx = hierarchy[child_idx][0]
    
            new_elem = ET.Element("path")
            new_elem.set("d", d)
            new_elem.set("fill", color_hex)
            new_elem.set("stroke", "none")
            new_elem.set("fill-rule", "evenodd")  # ⬅️ これが穴を正しく扱うために必要
            root.append(new_elem)




    
    def transfer_drawn_path_to_mask(self):
        from xml.etree import ElementTree as ET
        from PyQt6.QtGui import QImage, QPainterPath
        from PyQt6.QtCore import Qt
        import numpy as np
        import cv2
        import os
    
        self.save_svg_state_for_undo()
    
        key_current = self.get_current_image_key()
        if not key_current or key_current not in self.drawn_paths_per_image:
            return
    
        idx_src = self.combo_target_object.currentIndex()
        idx_dst = self.combo_transfer_target.currentIndex()
        src_rgb = self.color_labels[idx_src]
        dst_rgb = self.color_labels[idx_dst]
        src_color = f'#{src_rgb[0]:02x}{src_rgb[1]:02x}{src_rgb[2]:02x}'
        dst_color = f'#{dst_rgb[0]:02x}{dst_rgb[1]:02x}{dst_rgb[2]:02x}'
    
        for key, paths in self.drawn_paths_per_image.items():
            if not paths or key not in self.mask_paths or key not in self.image_paths:
                continue
    
            image_path = self.image_paths[key]
            svg_path = self.mask_paths[key]
            pixmap = QPixmap(image_path)
            width, height = pixmap.width(), pixmap.height()
    
            if width == 0 or height == 0:
                print(f"[ERROR] Invalid image size for {key}")
                continue
    
            # 🎯 1. 元のマスクをバイナリ化
            mask_src = self.svg_object_to_binary_mask(key, idx_src).astype(np.uint8)
            if mask_src is None:
                continue
    
            # ✏ 2. 手描きパスをラスタライズ
            path_union = QPainterPath()
            for path, _ in paths:
                path.closeSubpath()
                path_union.addPath(path)
            path_union.setFillRule(Qt.FillRule.OddEvenFill)
            drawn_mask = self.rasterize_path_to_binary(path_union, width, height).astype(np.uint8)
    
            # ➕ 3. 転送部分（AND）・残存部分（差分）を計算
            intersected = cv2.bitwise_and(mask_src, drawn_mask)
            subtracted = cv2.bitwise_and(mask_src, cv2.bitwise_not(drawn_mask))
    
            # 🧼 4. 元のオブジェクト要素を削除
            tree = ET.parse(svg_path)
            root = tree.getroot()
            to_remove = []
            for elem in list(root.iter()):
                fill = elem.attrib.get("fill", "").strip().lower()
                style = elem.attrib.get("style", "")
                if self._normalize_color(fill, style) == src_color:
                    to_remove.append(elem)
            for elem in to_remove:
                root.remove(elem)
    
            # 🖌 5. 交差領域 → 転送先色で追加
            self._add_contours_to_svg(intersected, dst_color, root)
    
            # 🖌 6. 残存領域 → 元の色で追加
            self._add_contours_to_svg(subtracted, src_color, root)
    
            # 💾 7. 保存
            save_path = os.path.join(self.output_mask_dir, os.path.basename(svg_path))
            tree.write(save_path, encoding="utf-8")
            self.mask_paths[key] = save_path
            self.drawn_paths_per_image[key] = []
    
        self.update_checkboxes_based_on_used_colors()
        self.display_current_image()
        self.scene.update()
        
        


    
    def convert_object_color_across_svgs(self):
        from xml.etree import ElementTree as ET
    
        def normalize_color(fill, style):
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
    
        # 元のオブジェクト番号と変換先オブジェクト番号を取得
        idx_from = self.combo_convert_from.currentIndex()
        idx_to = self.combo_convert_to.currentIndex()
        color_from = f'#{self.color_labels[idx_from][0]:02x}{self.color_labels[idx_from][1]:02x}{self.color_labels[idx_from][2]:02x}'
        color_to   = f'#{self.color_labels[idx_to][0]:02x}{self.color_labels[idx_to][1]:02x}{self.color_labels[idx_to][2]:02x}'

        # 一括編集のためUndo保存（全SVG）
        self.save_svg_state_for_undo()  # ← ループの外に1回でOK！
    
        for key, svg_path in self.mask_paths.items():
            tree = ET.parse(svg_path)
            root = tree.getroot()
            changed = False
    
            for elem in root.iter():
                tag = elem.tag.lower()
                fill = normalize_color(elem.attrib.get("fill", ""), elem.attrib.get("style", ""))
                if fill == color_from:
                    elem.set("fill", color_to)
                    changed = True
    
            if changed:
                save_path = os.path.join(self.output_mask_dir, os.path.basename(svg_path))
                tree.write(save_path, encoding="utf-8")
                self.mask_paths[key] = save_path  # 更新
                print(f"[INFO] Converted in {os.path.basename(svg_path)}")
    
        self.display_current_image()
        self.scene.update()
        

    
    def bring_selected_object_to_front(self):
        self._reorder_svg_elements(bring_to_front=True)
    
    def send_selected_object_to_back(self):
        self._reorder_svg_elements(bring_to_front=False)
    
    def _reorder_svg_elements(self, bring_to_front=True):
        from xml.etree import ElementTree as ET
    
        def normalize_color(fill, style):
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
    
        # 対象オブジェクト色のRGBとHex取得（1回だけでOK）
        idx = self.combo_reorder_object.currentIndex()
        target_rgb = self.color_labels[idx]
        target_hex = f'#{target_rgb[0]:02x}{target_rgb[1]:02x}{target_rgb[2]:02x}'

        # 一括編集のためUndo保存（全SVG）
        self.save_svg_state_for_undo()  # ← ループの外に1回でOK！
    
        for key, svg_path in self.mask_paths.items():
            try:
                tree = ET.parse(svg_path)
                root = tree.getroot()
            except Exception as e:
                print(f"[ERROR] Failed to parse SVG ({key}): {e}")
                continue
    
            elements = list(root)
            matched = []
            unmatched = []
    
            for elem in elements:
                fill = normalize_color(elem.attrib.get("fill", ""), elem.attrib.get("style", ""))
                if fill == target_hex:
                    matched.append(elem)
                else:
                    unmatched.append(elem)
    
            if not matched:
                print(f"[INFO] No matching elements found in {key}.svg")
                continue
    
            root[:] = []
            if bring_to_front:
                root.extend(unmatched + matched)
            else:
                root.extend(matched + unmatched)
    
            save_path = os.path.join(self.output_mask_dir, os.path.basename(svg_path))
            tree.write(save_path, encoding="utf-8")
            self.mask_paths[key] = save_path
            print(f"[INFO] {'Brought to front' if bring_to_front else 'Sent to back'} in {key}.svg")
    
        self.display_current_image()
        self.scene.update()





    
    def save_all_modified_svgs(self, output_dir=None):
        import os
        for key, tree in self.modified_svg_trees.items():
            path = self.mask_paths.get(key)
            if not path:
                continue
            save_path = path if output_dir is None else os.path.join(output_dir, os.path.basename(path))
            tree.write(save_path, encoding="utf-8")
    
            


    
    def export_all_svgs_to_grayscale_tiff(self):
        from PyQt6.QtGui import QImage, QPainter, QPixmap
        from xml.etree import ElementTree as ET
        from io import BytesIO
        from datetime import datetime
        import os
        from PyQt6.QtWidgets import QApplication
    
        app = QApplication.instance()
        if app is None:
            app = QApplication([])
    
        if not QApplication.instance():
            print("[ERROR] No QApplication instance found")
            return
    
        if not self.image_paths:
            print("[ERROR] No images loaded.")
            return
    
        first_image_path = list(self.image_paths.values())[0]
        pixmap = QPixmap(first_image_path)
        width = pixmap.width()
        height = pixmap.height()
        if width == 0 or height == 0:
            print(f"[ERROR] Failed to get valid size from: {first_image_path}")
            return
    
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = os.path.join(os.getcwd(), f"tiff_output_{timestamp}")
        os.makedirs(output_dir, exist_ok=True)
    
        svg_dir = self.output_mask_dir
        svg_files = [f for f in os.listdir(svg_dir) if f.endswith(".svg")]
        if not svg_files:
            print("[ERROR] No SVG files found in:", svg_dir)
            return
        
    
        grayscale_values = [255, 248, 237, 226, 215, 204, 193, 182, 171, 160,
                            149, 138, 127, 116, 105, 94, 83, 72, 61, 50]
        rgb_to_gray = {
            f'#{r:02x}{g:02x}{b:02x}': f'#{v:02x}{v:02x}{v:02x}'
            for (r, g, b), v in zip(self.color_labels, grayscale_values)
        }
    
        for filename in svg_files:
            svg_path = os.path.join(svg_dir, filename)
            print(f"[DEBUG] Processing SVG path: {svg_path}")
            tree = ET.parse(svg_path)
            root = tree.getroot()
    
            for elem in root.iter():
                fill = elem.attrib.get("fill", "")
                style = elem.attrib.get("style", "")
                color = self._normalize_color(fill, style)
                if color in rgb_to_gray:
                    elem.set("fill", rgb_to_gray[color])
    
            svg_bytes = BytesIO()
            tree.write(svg_bytes, encoding='utf-8')
            svg_bytes.seek(0)
            renderer = QSvgRenderer(svg_bytes.read())
    
            # image = QImage(width, height, QImage.Format.Format_ARGB32)
            image = QImage(width, height, QImage.Format.Format_RGB32)  # ← ARGBでなくRGBにする
            image.fill(Qt.GlobalColor.black)  # 背景

            if image.isNull():
                print("[ERROR] QImage creation failed")
                continue
            image.fill(0)
    
            painter = QPainter()
            if not painter.begin(image):
                print(f"[ERROR] QPainter failed for {svg_path}")
                continue
            painter.setRenderHint(QPainter.RenderHint.Antialiasing, False)
            painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, False)

            renderer.render(painter)
            painter.end()
    
            save_path = os.path.join(output_dir, filename.replace(".svg", ".tiff"))
            image.save(save_path, "TIFF")
            print(f"[SAVED] {save_path}")
    
        print(f"[INFO] Exported {len(svg_files)} grayscale TIFF files to: {output_dir}")

    



    def export_all_svgs_to_grayscale_tiff_reversed(self):
        from PyQt6.QtGui import QImage, QPainter, QPixmap
        from xml.etree import ElementTree as ET
        from io import BytesIO
        from datetime import datetime
        import os
        from PyQt6.QtWidgets import QApplication
    
        app = QApplication.instance()
        if app is None:
            app = QApplication([])
    
        if not self.image_paths:
            print("[ERROR] No images loaded.")
            return
    
        first_image_path = list(self.image_paths.values())[0]
        pixmap = QPixmap(first_image_path)
        width = pixmap.width()
        height = pixmap.height()
        if width == 0 or height == 0:
            print(f"[ERROR] Failed to get valid size from: {first_image_path}")
            return
    
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = os.path.join(os.getcwd(), f"tiff_output_reversed_{timestamp}")
        os.makedirs(output_dir, exist_ok=True)
    
        svg_dir = self.output_mask_dir
        svg_files = sorted([f for f in os.listdir(svg_dir) if f.endswith(".svg")])
    
        if not svg_files:
            print("[ERROR] No SVG files found in:", svg_dir)
            return
    
        grayscale_values = [255, 248, 237, 226, 215, 204, 193, 182, 171, 160,
                            149, 138, 127, 116, 105, 94, 83, 72, 61, 50]
        rgb_to_gray = {
            f'#{r:02x}{g:02x}{b:02x}': f'#{v:02x}{v:02x}{v:02x}'
            for (r, g, b), v in zip(self.color_labels, grayscale_values)
        }
    
        reversed_files = list(reversed(svg_files))
        total = len(reversed_files)
    
        for i, filename in enumerate(reversed_files):
            svg_path = os.path.join(svg_dir, filename)
            print(f"[DEBUG] Processing SVG path: {svg_path}")
            tree = ET.parse(svg_path)
            root = tree.getroot()
    
            for elem in root.iter():
                fill = elem.attrib.get("fill", "")
                style = elem.attrib.get("style", "")
                color = self._normalize_color(fill, style)
                if color in rgb_to_gray:
                    elem.set("fill", rgb_to_gray[color])
    
            svg_bytes = BytesIO()
            tree.write(svg_bytes, encoding='utf-8')
            svg_bytes.seek(0)
            renderer = QSvgRenderer(svg_bytes.read())
    
            image = QImage(width, height, QImage.Format.Format_RGB32)
            image.fill(Qt.GlobalColor.black)
    
            if image.isNull():
                print("[ERROR] QImage creation failed")
                continue
    
            painter = QPainter()
            if not painter.begin(image):
                print(f"[ERROR] QPainter failed for {svg_path}")
                continue
            painter.setRenderHint(QPainter.RenderHint.Antialiasing, False)
            painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, False)
    
            renderer.render(painter)
            painter.end()
    
            save_filename = f"mask{i+1:04}.tiff"
            save_path = os.path.join(output_dir, save_filename)
            image.save(save_path, "TIFF")
            print(f"[SAVED] {save_path}")
    
        print(f"[INFO] Exported {total} TIFF files in reversed order to: {output_dir}")

    






    def on_remove_small_parts(self):
        threshold = self.spinbox_threshold.value()
        self.delete_small_parts_in_selected_object(min_area_threshold=threshold)


    

    def delete_small_parts_in_selected_object(self, min_area_threshold=None):
        if min_area_threshold is None:
            min_area_threshold = self.spinbox_threshold.value()  # ✅ UIから取得
            
        from xml.etree import ElementTree as ET
        from svgpathtools import parse_path
        from PyQt6.QtGui import QPainterPath
        import re
    
        def normalize_color(fill, style):
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
                return rgb_to_hex(color).lower()  # ✅ 小文字統一
            return color.lower()  # ✅ 小文字統一
    

            
        # def svg_d_to_qpath(d_string):
        #     path = QPainterPath()
        #     tokens = re.findall(r"[-+]?\d*\.\d+|[-+]?\d+|[A-Za-z]", d_string)
        #     i = 0
        #     current_pos = None
        #     while i < len(tokens):
        #         cmd = tokens[i]
        #         if cmd == "M":
        #             x, y = float(tokens[i + 1]), float(tokens[i + 2])
        #             path.moveTo(x, y)
        #             current_pos = (x, y)
        #             i += 3
        #         elif cmd == "L":
        #             x, y = float(tokens[i + 1]), float(tokens[i + 2])
        #             path.lineTo(x, y)
        #             current_pos = (x, y)
        #             i += 3
        #         elif cmd == "Z":
        #             path.closeSubpath()
        #             i += 1
        #         else:
        #             i += 1
        #     return path
    
    
    
    
    
        # 対象オブジェクト番号と色（hex）
        obj_index = self.combo_delete_object.currentIndex()
        target_rgb = self.color_labels[obj_index]
        target_hex = '#{:02x}{:02x}{:02x}'.format(*target_rgb).lower()

    
        deleted_count = 0
                
        # ✅ 一括編集のためUndo保存（全SVG）
        self.save_svg_state_for_undo("__global__")        
        for key, svg_path in self.mask_paths.items():
            # self.save_svg_state_for_undo(key)  # ✅ ここでUndo用バックアップを保存
            tree = ET.parse(svg_path)
            root = tree.getroot()
            parent_map = {c: p for p in root.iter() for c in p}
            changed = False
    
            for elem in list(root.iter()):

                tag = elem.tag
                if '}' in tag:
                    tag = tag.split('}', 1)[1]  # 名前空間を除去
                
                if tag.lower() != "path":
                    continue
            
    
                fill = normalize_color(elem.attrib.get("fill", ""), elem.attrib.get("style", ""))
                if fill != target_hex:
                    continue
    
                d = elem.attrib.get("d", "")
                if not d:
                    continue
     
                def polygon_area_from_points(points):
                    if len(points) < 3:
                        return 0.0
                    area = 0.0
                    for i in range(len(points)):
                        x1, y1 = points[i].x(), points[i].y()
                        x2, y2 = points[(i + 1) % len(points)].x(), points[(i + 1) % len(points)].y()
                        area += (x1 * y2 - x2 * y1)
                    return abs(area) / 2.0                
                
                
                # qpath = svg_d_to_qpath(d)
                qpath = self.svg_d_to_qpath(d)
                if not qpath:
                    continue
                
                polygons = qpath.toSubpathPolygons()
                total_area = sum(polygon_area_from_points(poly) for poly in polygons)
                
                print(f"[DEBUG] Area: {total_area:.2f} px² for object {obj_index+1}")
                
                
                
                
                
                
                # if total_area < min_area_threshold:
                #     parent = parent_map.get(elem)
                #     if parent is not None:
                #         parent.remove(elem)
                #         deleted_count += 1
                #         changed = True
                
                # 新しいパスデータを構築
                new_path_data = ""
                kept_count = 0
                for poly in polygons:
                    area = polygon_area_from_points(poly)
                    if area >= min_area_threshold:
                        kept_count += 1
                        new_path_data += "M " + " L ".join(f"{pt.x()},{pt.y()}" for pt in poly) + " Z "
                    else:
                        print(f"[DEBUG] Removed subpath with area {area:.2f} px² (below threshold)")
                
                if kept_count == 0:
                    # 全部小さくて削除された場合 → path要素自体を削除
                    parent = parent_map.get(elem)
                    if parent is not None:
                        parent.remove(elem)
                        deleted_count += 1
                        changed = True
                else:
                    # 一部でも残ったら、d属性を書き換え
                    elem.set("d", new_path_data.strip())
                    changed = True
                        
                        
                        
                        
    
            if changed:
                save_path = os.path.join(self.output_mask_dir, os.path.basename(svg_path))
                tree.write(save_path, encoding="utf-8")
                self.mask_paths[key] = save_path
                print(f"[INFO] Removed small parts of object {obj_index+1} in {os.path.basename(svg_path)}")
    
        self.display_current_image()
        self.scene.update()
        self.label_status.setText(f"Removed small parts of object {obj_index+1} from all SVGs. ({deleted_count} elements removed)")




    
    def delete_selected_object_from_current_image(self):
        # self.save_svg_state_for_undo("__global__")
        key = self.get_current_image_key()
        if key:
            self.save_svg_state_for_undo(key)
        
        
        
        from xml.etree import ElementTree as ET
        import re
        import os
    
        def normalize_color(fill, style):
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
    
        # 現在表示中の画像キーと対応SVG取得
        key = self.get_current_image_key()
        svg_path = self.mask_paths[key]
    
        # 削除対象の色を決定
        obj_index = self.combo_delete_object.currentIndex()
        target_rgb = self.color_labels[obj_index]
        target_hex = '#{:02x}{:02x}{:02x}'.format(*target_rgb)
    
        # SVGを読み込み、該当 path を削除
        tree = ET.parse(svg_path)
        root = tree.getroot()
        parent_map = {c: p for p in root.iter() for c in p}
        deleted_count = 0
    
        for elem in list(root.iter()):
            if not elem.tag.lower().endswith("path"):
                continue
    
            fill = normalize_color(elem.attrib.get("fill", ""), elem.attrib.get("style", ""))
            if fill == target_hex:
                parent = parent_map.get(elem)
                if parent is not None:
                    parent.remove(elem)
                    deleted_count += 1
    
        # 保存先に書き戻す
        save_path = os.path.join(self.output_mask_dir, os.path.basename(svg_path))
        tree.write(save_path, encoding="utf-8")
        self.mask_paths[key] = save_path
    
        # GUI更新
        self.display_current_image()
        self.scene.update()
        self.label_status.setText(f"Deleted object {obj_index+1} from {os.path.basename(svg_path)}. ({deleted_count} elements removed)")









    
    
    def delete_selected_object(self):
       
        from xml.etree import ElementTree as ET
        import re
        
        # ✅ 全画像Undo保存（ループ前に1回だけ！）
        self.save_svg_state_for_undo()    
        
        def normalize_color(fill, style):
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
    
        # オブジェクト番号（1〜20）を取得し、その色を決定
        obj_index = self.combo_delete_object.currentIndex()
        target_rgb = self.color_labels[obj_index]
        target_hex = '#{:02x}{:02x}{:02x}'.format(*target_rgb)
    
        deleted_count = 0
        for key, svg_path in self.mask_paths.items():
            # self.save_svg_state_for_undo(key)
            tree = ET.parse(svg_path)
            root = tree.getroot()
            parent_map = {c: p for p in root.iter() for c in p}
            changed = False
    
            for elem in list(root.iter()):
                tag = elem.tag.lower()
                if not tag.endswith("path"):
                    continue
    
                fill = normalize_color(elem.attrib.get("fill", ""), elem.attrib.get("style", ""))
                if fill == target_hex:
                    parent = parent_map.get(elem)
                    if parent is not None:
                        parent.remove(elem)
                        deleted_count += 1
                        changed = True
    
            if changed:
                save_path = os.path.join(self.output_mask_dir, os.path.basename(svg_path))
                tree.write(save_path, encoding="utf-8")
                self.mask_paths[key] = save_path  # 更新
                print(f"[INFO] Deleted object {obj_index+1} from {os.path.basename(svg_path)}")
    
        self.display_current_image()
        self.scene.update()
        self.label_status.setText(f"Deleted object {obj_index+1} from all SVGs. ({deleted_count} elements removed)")






    def export_colorwise_stl_with_scale(self):
        import os
        import numpy as np
        from datetime import datetime
        from xml.etree import ElementTree as ET
        from PyQt6.QtGui import QImage, QPainter
        from PyQt6.QtCore import Qt
        from io import BytesIO
        from trimesh.voxel.ops import matrix_to_marching_cubes
        from trimesh.voxel import VoxelGrid
        from trimesh.smoothing import filter_laplacian

        if self.mm_per_px is None or self.z_spacing_mm is None:
            print(f"[DEBUG] Spacing values before CSV load: mm_per_px={self.mm_per_px}, z_spacing_mm={self.z_spacing_mm}")
                        
            import csv
            from PyQt6.QtWidgets import QFileDialog
            
            # 🔽 常にユーザーにCSVファイルを選ばせる
            file_path, _ = QFileDialog.getOpenFileName(self, "Select CSV File", "", "CSV Files (*.csv)")
            if not file_path:
                print("[ERROR] CSV file not selected. Aborting STL export.")
                return
            
            try:
                with open(file_path, newline='', encoding='utf-8') as f:
                    reader = csv.reader(f)
                    rows = list(reader)
            
                    x_spacing = float(rows[3][0])  # 4行目・1列目
                    z_spacing = float(rows[3][2])  # 4行目・3列目
            
                    self.mm_per_px = x_spacing
                    self.z_spacing_mm = z_spacing
                    print(f"[INFO] Loaded spacing: mm/px = {self.mm_per_px}, z = {self.z_spacing_mm}")
                    print(f"[DEBUG] Spacing values after CSV load: mm_per_px={self.mm_per_px}, z_spacing_mm={self.z_spacing_mm}")
            except Exception as e:
                print(f"[ERROR] Failed to read CSV file: {e}")
                return

        rgb_keys = [f"#{r:02x}{g:02x}{b:02x}" for r, g, b in self.color_labels]
        num_colors = len(rgb_keys)

        svg_dir = self.output_mask_dir
        svg_files = sorted([f for f in os.listdir(svg_dir) if f.endswith(".svg")])
        if not svg_files:
            print("[ERROR] No SVG files found")
            return
        
        svg_files.sort()  # デフォルトは昇順（mask0001.svg → maskNNNN.svg）
        
        # ✅ Stacking direction を UI から取得して反映
        # 0: Backside (ascending), 1: Frontside (descending)
        if self.combo_stack_order.currentIndex() == 0:
            svg_files.reverse()
            print("[INFO] Using descending stacking order (Frontside)")
        else:
            print("[INFO] Using ascending stacking order (Backside)")        

        first_svg = os.path.join(svg_dir, svg_files[0])
        renderer = QSvgRenderer(first_svg)
        width, height = renderer.defaultSize().width(), renderer.defaultSize().height()

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = os.path.join(os.getcwd(), f"stl_output_{timestamp}")
        os.makedirs(output_dir, exist_ok=True)

        # masks_per_color = [np.zeros((len(svg_files), height, width), dtype=np.uint8) for _ in range(num_colors)]
        # ✅ チェックされているインデックスだけ抽出
        target_indices = [i for i, cb in enumerate(self.checkboxes) if cb.isChecked()]
        masks_per_color = [np.zeros((len(svg_files), height, width), dtype=np.uint8) for _ in target_indices]

        
        # 🔧 進捗表示関数を定義
        def update_progress_bar(label, task, current, total):
            percent = int(current / total * 100)
            bar_length = 20
            filled_length = int(bar_length * percent // 100)
            bar = '█' * filled_length + '-' * (bar_length - filled_length)
            label.setText(f"{task}... |{bar}| {percent}%")
            QApplication.processEvents()

        
        #進捗表示用
        self.label_status.setText("Generating masks from SVG...")
        QApplication.processEvents()



        svg_files = sorted([f for f in os.listdir(svg_dir) if f.endswith(".svg")])
        for z, fname in enumerate(svg_files):
            svg_path = os.path.join(svg_dir, fname)

            for out_idx, color_idx in enumerate(target_indices):  # ✅ 選択色だけ処理
                rgb = rgb_keys[color_idx]
                tree = ET.parse(svg_path)
                root = tree.getroot()
                parent_map = {c: p for p in root.iter() for c in p}
            
                for elem in list(root.iter()):
                    fill = elem.attrib.get("fill", "")
                    style = elem.attrib.get("style", "")
                    color = self._normalize_color(fill, style)
            
                    if color == rgb:
                        elem.set("fill", "white")
                        elem.attrib.pop("style", None)
                    else:
                        parent = parent_map.get(elem)
                        if parent is not None:
                            parent.remove(elem)
            
                svg_bytes = BytesIO()
                tree.write(svg_bytes, encoding='utf-8')
                svg_bytes.seek(0)
                renderer = QSvgRenderer(svg_bytes.read())
            
                image = QImage(width, height, QImage.Format.Format_Grayscale8)
                image.fill(Qt.GlobalColor.black)
                painter = QPainter(image)
                renderer.render(painter)
                painter.end()
            
                ptr = image.bits()
                ptr.setsize(image.width() * image.height())
                array = np.frombuffer(ptr, dtype=np.uint8).reshape((height, width))
                                
                # ✅ Frontside（降順）の場合は上下反転
                if self.combo_stack_order.currentIndex() == 0:
                    array = np.flipud(array)
                
                
                masks_per_color[out_idx][z] = (array > 127).astype(np.uint8) * 255
                            
            
                
                # ✅ 進捗表示更新（スライス単位）
                update_progress_bar(self.label_status, "Generating masks", z + 1, len(svg_files))                



        #進捗表示用
        self.label_status.setText("Exporting STL files...")
        QApplication.processEvents()
        
        num_valid_volumes = sum(np.count_nonzero(vol) > 0 for vol in masks_per_color)
        exported_count = 0
        
        
        # for i, volume in enumerate(masks_per_color):
        for i, volume in enumerate(masks_per_color):
            color_idx = target_indices[i]
            if np.count_nonzero(volume) == 0:
                continue
            print(f"[DEBUG] Final spacing values before STL export: mm_per_px={self.mm_per_px}, z_spacing_mm={self.z_spacing_mm}")
        
            if self.mm_per_px is None or self.z_spacing_mm is None:
                print("[ERROR] Calibration not completed.")
                return
        
                    
            # # 🔽 空でないスライスの範囲を抽出してトリミング
            # nonzero_slices = np.any(volume > 127, axis=(1, 2))
            # if not np.any(nonzero_slices):
            #     print(f"[SKIP] Object {color_idx+1} is completely empty. Skipped.")
            #     continue
            
            # z_start, z_end = np.where(nonzero_slices)[0][[0, -1]]
            # trimmed_volume = volume[z_start:z_end + 1]
            
            if np.count_nonzero(volume) == 0:
                print(f"[SKIP] Object {color_idx+1} is completely empty. Skipped.")
                continue
            
            binary_volume = (volume > 127)  # ✅ 修正点
        
        
        
            # ✅ VoxelGrid を使わずに直接メッシュ化
            mesh = matrix_to_marching_cubes(
                binary_volume,
                pitch=[self.z_spacing_mm, self.mm_per_px, self.mm_per_px]
            )
            
            
            
            # 🔽 スムージングモードとレベルを取得
            mode_text = self.combo_smooth_mode.currentText()
            level_str = self.combo_smooth_level.currentText().split("（")[0]
            smooth_level = int(level_str)
            
            from scipy.ndimage import zoom
            
            adjusted_z_spacing = self.z_spacing_mm  # 初期値
            
            # 🔽 Z方向補間（volume smoothing）
            if smooth_level > 0 and mode_text in ["Z-interpolation only", "Both"]:
                z_factor = 1.0 + smooth_level * 0.4
                
                
                binary_volume = zoom(
                    binary_volume.astype(np.uint8), 
                    zoom=[z_factor, 1.0, 1.0], 
                    order=3
                ) > 0.5
                adjusted_z_spacing = self.z_spacing_mm / z_factor  # 🔧 ここを追加
                
                
                print(f"[INFO] Applied Z-direction interpolation with factor {z_factor:.2f}")
            else:
                print("[INFO] Volume smoothing skipped")
            
      
            
            # ✅ 補正済みのピッチでメッシュ化
            mesh = matrix_to_marching_cubes(
                binary_volume,
                pitch=[adjusted_z_spacing, self.mm_per_px, self.mm_per_px]
            )            
            
            
            # 🔽 メッシュスムージング（surface smoothing）
            if smooth_level > 0 and mode_text in ["Mesh smoothing only", "Both"]:
                iterations = 10 + smooth_level * 5
                
                filter_laplacian(mesh, lamb=0.5, iterations=iterations)
                print(f"[INFO] Applied mesh smoothing: {iterations} iterations")
            else:
                print("[INFO] Mesh smoothing skipped")



        
            # stl_path = os.path.join(output_dir, f"object_{i+1:02}.stl")
            stl_path = os.path.join(output_dir, f"object_{color_idx + 1:02}.stl")
            mesh.export(stl_path)
            print(f"[SAVED] {stl_path}")          
                    
            # ✅ 進捗表示更新（色ごとのSTL出力単位）
            exported_count += 1
            update_progress_bar(self.label_status, "Exporting STLs", exported_count, num_valid_volumes)            
            

        self.label_status.setText(f"[Done] Exported STL per color to: {output_dir}")


        
    
    def export_colorwise_volumes_to_csv(self):
        import os
        import numpy as np
        import csv
        from datetime import datetime
        from xml.etree import ElementTree as ET
        from PyQt6.QtGui import QImage, QPainter
        from PyQt6.QtCore import Qt
        from io import BytesIO
    
        if self.mm_per_px is None or self.z_spacing_mm is None:
            from PyQt6.QtWidgets import QFileDialog
            file_path, _ = QFileDialog.getOpenFileName(self, "Select CSV File", "", "CSV Files (*.csv)")
            if not file_path:
                print("[ERROR] CSV file not selected. Aborting volume export.")
                return
            try:
                with open(file_path, newline='', encoding='utf-8') as f:
                    reader = csv.reader(f)
                    rows = list(reader)
                    self.mm_per_px = float(rows[3][0])
                    self.z_spacing_mm = float(rows[3][2])
                    print(f"[INFO] Loaded spacing: mm/px = {self.mm_per_px}, z = {self.z_spacing_mm}")
            except Exception as e:
                print(f"[ERROR] Failed to read CSV file: {e}")
                return
    
        rgb_keys = [f"#{r:02x}{g:02x}{b:02x}" for r, g, b in self.color_labels]
        num_colors = len(rgb_keys)
    
        svg_dir = self.output_mask_dir
        svg_files = sorted([f for f in os.listdir(svg_dir) if f.endswith(".svg")])
        if not svg_files:
            print("[ERROR] No SVG files found")
            return
    
        first_svg = os.path.join(svg_dir, svg_files[0])
        renderer = QSvgRenderer(first_svg)
        width, height = renderer.defaultSize().width(), renderer.defaultSize().height()
    
        masks_per_color = [np.zeros((len(svg_files), height, width), dtype=np.uint8) for _ in range(num_colors)]
    
        self.label_status.setText("Generating masks for volume calculation...")
        QApplication.processEvents()
    
        for z, fname in enumerate(svg_files):
            svg_path = os.path.join(svg_dir, fname)
            for i, rgb in enumerate(rgb_keys):
                tree = ET.parse(svg_path)
                root = tree.getroot()
                parent_map = {c: p for p in root.iter() for c in p}
    
                for elem in list(root.iter()):
                    fill = elem.attrib.get("fill", "")
                    style = elem.attrib.get("style", "")
                    color = self._normalize_color(fill, style)
                    if color == rgb:
                        elem.set("fill", "white")
                        elem.attrib.pop("style", None)
                    else:
                        parent = parent_map.get(elem)
                        if parent is not None:
                            parent.remove(elem)
    
                svg_bytes = BytesIO()
                tree.write(svg_bytes, encoding='utf-8')
                svg_bytes.seek(0)
                renderer = QSvgRenderer(svg_bytes.read())
    
                image = QImage(width, height, QImage.Format.Format_Grayscale8)
                image.fill(Qt.GlobalColor.black)
                painter = QPainter(image)
                renderer.render(painter)
                painter.end()
    
                ptr = image.bits()
                ptr.setsize(image.width() * image.height())
                array = np.frombuffer(ptr, dtype=np.uint8).reshape((height, width))
                masks_per_color[i][z] = (array > 127).astype(np.uint8)
    
        voxel_volume_mm3 = (self.mm_per_px ** 2) * self.z_spacing_mm
    
        results = []
        overlap_results = []
    
        # 通常体積
        for i, volume in enumerate(masks_per_color):
            voxel_count = np.count_nonzero(volume)
            total_volume_mm3 = voxel_count * voxel_volume_mm3
            total_volume_cm3 = total_volume_mm3 / 1000
            print(f"[RESULT] Object {i+1:02}: {total_volume_cm3:.3f} cm³")
            results.append((f"Object {i+1}", total_volume_mm3, total_volume_cm3))
    
        # オーバーラップ体積
        for i in range(num_colors):
            for j in range(i + 1, num_colors):
                overlap = np.logical_and(masks_per_color[i], masks_per_color[j])
                voxel_count = np.count_nonzero(overlap)
                total_volume_mm3 = voxel_count * voxel_volume_mm3
                total_volume_cm3 = total_volume_mm3 / 1000
                if voxel_count > 0:
                    print(f"[OVERLAP] Object {i+1} & Object {j+1}: {total_volume_cm3:.3f} cm³")
                    overlap_results.append((f"Object {i+1} & {j+1}", total_volume_mm3, total_volume_cm3))
    
        # 出力
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_csv = os.path.join(os.getcwd(), f"volume_output_{timestamp}.csv")
        with open(output_csv, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["Label", "Volume (mm^3)", "Volume (cm^3)"])
            writer.writerows(results)
            if overlap_results:
                writer.writerow([])
                writer.writerow(["Overlapping Volumes"])
                writer.writerow(["Overlap Pair", "Volume (mm^3)", "Volume (cm^3)"])
                writer.writerows(overlap_results)
    
        self.label_status.setText(f"[Done] Volume results saved to: {output_csv}")
        
        



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SegRefMain()
    app.installEventFilter(window)  # ← ここでアプリケーション全体にフィルターを適用
    window.show()
    sys.exit(app.exec())

