import cv2
import sys
import time
import numpy as np
import pyautogui
import pyscreeze
from PyQt5.QtCore import Qt, QTimer, QSettings
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel, QSlider, QSpinBox, QPushButton
from PyQt5.QtGui import QIcon


class VPNController:
    def __init__(self, status_callback):
        self.on_time = 0
        self.off_time = 0
        self.before_time = 1
        self.loop_count = 0
        self.current_loop = 0
        self.timer = QTimer()
        self.timer.timeout.connect(self.toggle_vpn)
        self.running = False
        self.status_callback = status_callback

    def set_timing_parameters(self, on_time, off_time, before_time,loop_count):
        self.on_time = on_time
        self.off_time = off_time
        self.before_time = before_time
        self.loop_count = loop_count

    def start_vpn_toggle(self):
        self.current_loop = 0
        self.running = True
        self.timer.start(self.before_time*60000 + self.off_time * 1000)

    def stop_vpn_toggle(self):
        self.running = False
        self.timer.stop()

    def stop_vpn_controller(self):
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.timer.stop()

    def find_button_coordinates(self,screenshot_path, button_image_path):
        # Load the screenshot image
        screenshot = cv2.imread(screenshot_path)
        screenshot_gray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)

        # Load the button image
        button_image = cv2.imread(button_image_path, 0)

        # Perform template matching
        result = cv2.matchTemplate(screenshot_gray, button_image, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(result)

        # Set a threshold for the match
        threshold = 0.8
        if max_val >= threshold:
            # Get the coordinates of the matched region
            button_width, button_height = button_image.shape[::-1]
            top_left = max_loc
            center_x = top_left[0] + button_width // 2
            center_y = top_left[1] + button_height // 2
            return center_x, center_y

        return None
      
    def toggle_vpn(self):

        time.sleep(2) 
        screenshot = pyautogui.screenshot()
        screenshot.save("pia_screenshot.png")                 

              
        if self.current_loop % 2 == 0:
            icon_coordinates = self.find_button_coordinates("pia_screenshot.png", "icon_on.png")
            if icon_coordinates:
                pyautogui.click(icon_coordinates[0], icon_coordinates[1])
                time.sleep(2) 
                screenshot = pyautogui.screenshot()
                screenshot.save("pia_screenshot.png")  
                button_coordinates = self.find_button_coordinates("pia_screenshot.png", "on.png")
                if button_coordinates:
                    pyautogui.click(button_coordinates[0], button_coordinates[1])
                    self.status_callback("VPN ステータス: OFF")
                else:
                    self.status_callback("ON/OFF button not found.")
            else:
                self.status_callback("VPN icon not found.")
                
        else:
            icon_coordinates = self.find_button_coordinates("pia_screenshot.png", "icon_off.png")
            if icon_coordinates:   
                pyautogui.click(icon_coordinates[0], icon_coordinates[1])
                time.sleep(2) 
                screenshot = pyautogui.screenshot()
                screenshot.save("pia_screenshot.png")          
                button_coordinates = self.find_button_coordinates("pia_screenshot.png", "off.png")
                if button_coordinates:
                    pyautogui.click(button_coordinates[0], button_coordinates[1])
                    self.status_callback("VPN ステータス: ON")
                else:
                    self.status_callback("ON/OFF button not found.")
            else:
                self.status_callback("VPN icon not found.")

        self.current_loop += 1

        if self.current_loop == self.loop_count:
           self.status_callback("ループ回数が限界に達した。")
           self.stop_vpn_toggle()
        elif self.current_loop % 2 == 0:
            self.timer.start(self.off_time * 1000)
        else:
            self.timer.start(self.on_time * 1000)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('VPN オートメーション')
        self.setFixedSize(350, 400)
        icon = QIcon('icon.png')
        self.setWindowIcon(icon)

        layout = QVBoxLayout()

        # VPN Status Label
        self.status_label = QLabel("VPN ステータス: ")
        layout.addWidget(self.status_label)

        # ON Time Slider
        on_time_label = QLabel("ON 時間 (秒):")
        self.on_time_slider = QSlider(Qt.Horizontal)
        self.on_time_slider.setMinimum(10)
        self.on_time_slider.setMaximum(60)
        self.on_time_slider.setSingleStep(10)
        self.on_time_slider.setTickInterval(10)
        self.on_time_slider.setTickPosition(QSlider.TicksBelow)
        layout.addWidget(on_time_label)
        layout.addWidget(self.on_time_slider)

        self.on_time_label = QLabel()
        layout.addWidget(self.on_time_label)

        # OFF Time Slider
        off_time_label = QLabel("OFF 時間 (秒):")
        self.off_time_slider = QSlider(Qt.Horizontal)
        self.off_time_slider.setMinimum(10)
        self.off_time_slider.setMaximum(60)
        self.off_time_slider.setSingleStep(10)
        self.off_time_slider.setTickInterval(10)
        self.off_time_slider.setTickPosition(QSlider.TicksBelow)
        layout.addWidget(off_time_label)
        layout.addWidget(self.off_time_slider)

        self.off_time_label = QLabel()
        layout.addWidget(self.off_time_label)

        # before_time Slider
        before_time_label = QLabel("ループ動作実行まで時間 (分):")
        self.before_time_slider = QSlider(Qt.Horizontal)
        self.before_time_slider.setMinimum(1)
        self.before_time_slider.setMaximum(20)
        self.before_time_slider.setSingleStep(1)
        self.before_time_slider.setTickInterval(10)
        self.before_time_slider.setTickPosition(QSlider.TicksBelow)
        layout.addWidget(before_time_label)
        layout.addWidget(self.before_time_slider)

        self.before_time_label = QLabel()
        layout.addWidget(self.before_time_label)

        # Loop Count Slider
        loop_count_label = QLabel("ループ回数:")
        self.loop_count_slider = QSlider(Qt.Horizontal)
        self.loop_count_slider.setMinimum(1)
        self.loop_count_slider.setMaximum(100)
        self.loop_count_slider.setTickInterval(1)
        self.loop_count_slider.setTickPosition(QSlider.TicksBelow)
        layout.addWidget(loop_count_label)
        layout.addWidget(self.loop_count_slider)

        self.loop_count_label = QLabel()
        layout.addWidget(self.loop_count_label)

        # Start Button
        self.start_button = QPushButton("開始")
        self.start_button.clicked.connect(self.start_vpn_toggle)
        layout.addWidget(self.start_button)

       # Close Button
        self.close_button = QPushButton("完了")
        self.close_button.clicked.connect(self.close_application)
        layout.addWidget(self.close_button)

        # Central Widget
        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        # VPN Controller
        self.vpn_controller = VPNController(self.update_vpn_status)

        # Timing Parameters
        self.on_time_slider.valueChanged.connect(self.update_on_time_label)
        self.off_time_slider.valueChanged.connect(self.update_off_time_label)
        self.before_time_slider.valueChanged.connect(self.update_before_time_label)
        self.loop_count_slider.valueChanged.connect(self.update_loop_count_label)

        # Load settings
        self.load_settings()
   

    def update_vpn_status(self, status):
      self.status_label.setText(status)

    def update_on_time_label(self, value):
        self.on_time_label.setText(f"{value} 秒")

    def update_off_time_label(self, value):
        self.off_time_label.setText(f"{value} 秒")

    def update_before_time_label(self, value):
        self.before_time_label.setText(f"{value} 分")

    def update_loop_count_label(self, value):
        self.loop_count_label.setText(f"{value} 回")

    def start_vpn_toggle(self):
        on_time = self.on_time_slider.value()
        off_time = self.off_time_slider.value()
        before_time = self.before_time_slider.value()
        loop_count = self.loop_count_slider.value()

        self.vpn_controller.set_timing_parameters(on_time, off_time, before_time, loop_count)
        self.vpn_controller.start_vpn_toggle()

    def stop_vpn_toggle(self):
        self.vpn_controller.stop_vpn_toggle()

    def close_application(self):
        self.save_settings()
        QApplication.quit()

    def load_settings(self):
        settings = QSettings("config.ini", QSettings.IniFormat)

        on_time = settings.value("on_time", 10, type=int)
        off_time = settings.value("off_time", 10, type=int)
        before_time = settings.value("before_time", 1, type=int)
        loop_count = settings.value("loop_count", 1, type=int)

        self.on_time_slider.setValue(on_time)
        self.off_time_slider.setValue(off_time)
        self.before_time_slider.setValue(before_time)
        self.loop_count_slider.setValue(loop_count)

    def save_settings(self):
        settings = QSettings("config.ini", QSettings.IniFormat)

        on_time = self.on_time_slider.value()
        off_time = self.off_time_slider.value()
        before_time = self.before_time_slider.value()
        loop_count = self.loop_count_slider.value()

        settings.setValue("on_time", on_time)
        settings.setValue("off_time", off_time)
        settings.setValue("loop_count", loop_count)
        settings.setValue("before_time", before_time)

    def closeEvent(self, event):
        self.save_settings()
        event.accept()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())

   


   
