from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QPushButton, QLabel, QGraphicsView,
    QCheckBox, QScrollArea, QFrame, QComboBox,  # ← ここに QComboBox を追加
    QDoubleSpinBox, QSpinBox  # ✅ ← これを追加
)
from PyQt6.QtGui import QColor, QPixmap
from PyQt6.QtCore import Qt


class Ui_MainWindow:
       
        
    def setupUi(self, MainWindow):
        MainWindow.setWindowTitle("AlignRef")
        MainWindow.resize(1000, 800)
    
        self.central_widget = QWidget(MainWindow)
        MainWindow.setCentralWidget(self.central_widget)
    
        outer_layout = QVBoxLayout(self.central_widget)
            
        # 🔹 上段：ボタン（新構成）
        button_layout1 = QHBoxLayout()
        
        # キャンバス背景色選択
        self.label_canvas_bg = QLabel("Canvas BG Color:")
        self.label_canvas_bg.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        
        self.btn_load_images = QPushButton("Load Image Folder")
        
 
        self.combo_canvas_bg = QComboBox()
        self.combo_canvas_bg.addItems(["White", "Black"])
        self.combo_canvas_bg.setCurrentText("White")  # デフォルト白
        
        self.btn_expand_canvas = QPushButton("Expand Canvas")
        self.btn_fit_to_window = QPushButton("Fit to Window")
        

        
        
        
        button_layout1.addWidget(self.label_canvas_bg)
        button_layout1.addWidget(self.combo_canvas_bg)
        button_layout1.addWidget(self.btn_load_images)
        button_layout1.addWidget(self.btn_expand_canvas)
        button_layout1.addWidget(self.btn_fit_to_window)
        

        


        # 🔹 ボタン行：2段目
        button_layout2 = QHBoxLayout()
        
        self.btn_prev_image = QPushButton("Overlay Previous Image")
        self.btn_next_image = QPushButton("Overlay Next Image")
        self.btn_clear_overlay = QPushButton("Clear Overlay")
        self.btn_start_record_position = QPushButton("Start Recording Position")
        self.btn_end_record_position = QPushButton("Finish Recording Position")
        self.btn_cancel_record_position = QPushButton("Cancel Recording Position")
        
        self.btn_set_pos_start = QPushButton("Set Position Start")
        self.btn_set_pos_end = QPushButton("Set Position End")
        self.btn_apply_pos_rotation = QPushButton("Apply Position & Rotation")
        
        self.btn_cancel_apply_pos = QPushButton("Cancel Applied Position")
        
        button_layout2.addWidget(self.btn_prev_image)
        button_layout2.addWidget(self.btn_next_image)
        button_layout2.addWidget(self.btn_clear_overlay)
        button_layout2.addWidget(self.btn_start_record_position)
        button_layout2.addWidget(self.btn_end_record_position)
        button_layout2.addWidget(self.btn_cancel_record_position)
        button_layout2.addWidget(self.btn_set_pos_start)
        button_layout2.addWidget(self.btn_set_pos_end)
        button_layout2.addWidget(self.btn_apply_pos_rotation)
        button_layout2.addWidget(self.btn_cancel_apply_pos)
        
       

        # 🔽 2段レイアウトとして追加
        outer_layout.addLayout(button_layout1)
        outer_layout.addLayout(button_layout2)
        






    
        # 🔹 画像ビュー
        self.graphicsView = QGraphicsView()
        self.graphicsView.setMinimumSize(800, 600)
        outer_layout.addWidget(self.graphicsView)


        # 🔹 ステータスラベル（画像ファイル名など）
        self.label_status = QLabel("Ready")
        self.label_status.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        outer_layout.addWidget(self.label_status)




        position_layout = QHBoxLayout()

        # キャンバス背景色選択

        # クロップ関係ボタン
        self.btn_start_crop = QPushButton("Start Crop")
        self.btn_clear_crop_box = QPushButton("Clear Crop Box")
        self.btn_apply_crop = QPushButton("Apply Crop")
        self.btn_undo_crop = QPushButton("Undo Crop")
        
        self.combo_export_format = QComboBox()
        self.combo_export_format.addItems(["JPG", "PNG", "BMP", "TIFF", "DCM"])
        self.combo_export_format.setCurrentText("JPG")
        self.btn_export_aligned = QPushButton("Export Aligned Images")
        
        # すべて同じレイアウトに追加
        position_layout.addWidget(self.btn_start_crop)
        position_layout.addWidget(self.btn_clear_crop_box)
        position_layout.addWidget(self.btn_apply_crop)
        position_layout.addWidget(self.btn_undo_crop)

        position_layout.addWidget(self.combo_export_format)
        position_layout.addWidget(self.btn_export_aligned)
        

        # 全体レイアウトに追加
        outer_layout.addLayout(position_layout)



    

                
        
        # # ✅ ボタンの色をスタイルで設定
        load_style = "background-color: #cce5ff; color: black;"  # 明るい青
        for btn in [
            self.btn_load_images
        ]:
            btn.setStyleSheet(load_style)
            
        export_style = "background-color: #ccffcc; color: black;"  # 明るい緑
        for btn in [
            self.btn_export_aligned
        ]:
            btn.setStyleSheet(export_style)
        
        # 🟠 濃オレンジ：Apply Position & Rotation
        apply_style = "background-color: #ffcc99; color: black;"  # 明るいオレンジ
        self.btn_apply_pos_rotation.setStyleSheet(apply_style)
        
        # 🟧 薄オレンジ：録画開始・終了
        record_style = "background-color: #ffe0b3; color: black;"  # 薄いオレンジ
        for btn in [
            self.btn_start_record_position,
            self.btn_end_record_position
        ]:
            btn.setStyleSheet(record_style)
        
        # ⚪ グレー系：キャンセル・Undo 系
        cancel_style = "background-color: #dcdcdc; color: black;"  # ライトグレー
        for btn in [
            self.btn_clear_overlay,
            self.btn_cancel_record_position,
            self.btn_cancel_apply_pos,
            self.btn_clear_crop_box,
            self.btn_undo_crop
        ]:
            btn.setStyleSheet(cancel_style)






