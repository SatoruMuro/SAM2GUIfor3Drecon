# -*- coding: utf-8 -*-
"""
Created on Mon Mar 18 16:44:50 2024

@author: Satoru Muro
"""

import pyautogui
import time
import tkinter as tk
from tkinter import simpledialog
from tkinter import messagebox
import keyboard  # keyboardモジュールをインポート

def ungroup_selected_objects():
    try:
        pyautogui.hotkey('ctrl', 'a')
        pyautogui.hotkey('ctrl', 'shift', 'g')
        time.sleep(1)
        pyautogui.press('y')
        time.sleep(0.5)  # 'Yes'を選択後、少し待ってから次の操作へ移る / Wait a bit after selecting 'Yes'
        pyautogui.press('pagedown')  # 追加: 操作完了後に次のスライドへ移動 / Added: Move to the next slide after completing the operation
        time.sleep(0.5)  # 次のスライドへ移動する際に少し待つ / Wait a bit when moving to the next slide
    except Exception as e:
        messagebox.showerror("エラー / Error", f"エラーが発生しました: {str(e)}\nプログラムを終了します。 / An error occurred: {str(e)}\nThe program will terminate.")
        raise

def main():
    root = tk.Tk()
    root.withdraw()  # メインウィンドウを表示しない / Hide the main window

    try:
        # ユーザーに全スライド数を尋ねる / Ask the user for the total number of slides
        total_slides = simpledialog.askinteger("全スライド数 / Total Slides", 
                                               "プレゼンテーションの全スライド数を入力してください: / Enter the total number of slides in the presentation:", 
                                               parent=root, minvalue=1)
        if total_slides is None:
            messagebox.showwarning("キャンセル / Cancelled", "操作がキャンセルされました。プログラムを終了します。 / Operation was cancelled. The program will terminate.")
            return
        
        # 追加の指示をユーザーに表示 / Show additional instructions to the user
        messagebox.showinfo("準備の指示 / Preparation Instructions", 
                            "OKを押した後、パワーポイントに移動し、1枚目のスライド上のオブジェクトをクリックで選択して待機してください（5秒）。途中で中止したい場合はESCボタンを押してください。 / After clicking OK, switch to PowerPoint, select an object on the first slide, and wait (5 seconds). If you want to cancel the process, press the ESC key.", 
                            parent=root)

        # ここで5秒間待機し、ユーザーがPowerPointに戻って準備する時間を与える / Wait 5 seconds here to allow the user to switch back to PowerPoint and prepare
        time.sleep(5)

        # 全スライドに対して操作を実行 / Execute operations on all slides
        for i in range(1, total_slides + 1):
            if keyboard.is_pressed('esc'):  # ESCキーが押された場合、操作を中断 / If the ESC key is pressed, interrupt the operation
                messagebox.showinfo("中断 / Interrupted", f"操作が中断されました（スライド {i} で停止）。 / Operation was interrupted (stopped at slide {i}).")
                break
            ungroup_selected_objects()

        messagebox.showinfo("完了 / Completed", "すべてのスライドの操作が完了しました。 / All slides have been processed.")

    except Exception as e:
        messagebox.showerror("エラー / Error", f"エラーが発生しました: {str(e)}\nプログラムを終了します。 / An error occurred: {str(e)}\nThe program will terminate.")

if __name__ == "__main__":
    main()
