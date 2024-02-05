import argparse
import cv2
import datetime
import multiprocessing
import os
import time
from enum import Enum
from pynput import keyboard
from common import load_yaml, dump_yaml
from wait_time import wait_at_time
from ServoMotor import ServoMotor
from FaceDetector import FaceDetector


class Mode(Enum):
    """
    動作モード
    """
    WAIT = 0  # 待ち状態
    SEARCH = 1  # 顔探索状態
    ADJUST = 2  # カメラ調整状態
    CAPTURE = 3 # 撮影状態
    END = 4  # 終了


class AutoCaptureFace():
    """
    顔を検出して写真を撮影・保存するクラス
    撮影間隔は設定ファイルで調整する
    """
    def __init__(self, setting_path: str, output_dir: str) -> None:
        """
        Args:
            setting_path (str): 設定ファイルのパス
            output_dir (str): 撮影画像保存フォルダのパス
        """
        self.mode = multiprocessing.Value('i', Mode.WAIT.value)
        self.output_dir = output_dir
        self.setting = load_yaml(setting_path)
        self.setting_path = setting_path
        self.update_interval = self.setting['update_interval']
        self.research_interval = self.setting['research_interval']

        servo_setting = load_yaml(self.setting["servo_setting_path"])
        self.servo_motor_horizontal = ServoMotor()  # 横方向のサーボモータ
        self.servo_motor_vertical = ServoMotor()  # 縦方向のサーボモータ
        self.servo_motor_horizontal.load_setting(servo_setting["horizontal"])
        self.servo_motor_vertical.load_setting(servo_setting["vertical"])

        self.detector = FaceDetector(self.setting["camera_setting_path"])
        self.detector.start()

    def change_mode(self, mode: Enum) -> None:
        """
        実行モードを変更する

        Args:
            mode (str): 実行モード
        """
        if self.mode.value != Mode.END.value:  # 終了フラグON時はモードを変更しない
            self.mode.value = mode.value

    def waiting(self) -> None:
        """
        待ち状態
        設定された時刻まで待機する
        """
        target_date = self.setting['target_date']
        target_time = datetime.datetime(int(target_date["year"]),
                                        int(target_date["month"]),
                                        int(target_date["day"]),
                                        int(target_date["hour"]),
                                        int(target_date["minute"]),
                                        int(target_date["second"]))
        # target_time = datetime.datetime.now() + datetime.timedelta(seconds=1)
        print(f"wait at: {target_time}")
        wait_at_time(target_time, self.mode)
        self.change_mode(Mode.SEARCH)

    def serching(self) -> None:
        """
        顔探索状態
        カメラを動かしながら顔を探す
        """
        self.servo_motor_horizontal.start()
        self.servo_motor_vertical.start()
        self.detector.start()
        is_detected = False
        
        min_angle_h = self.servo_motor_horizontal.min_angle
        max_angle_h = self.servo_motor_horizontal.max_angle
        min_angle_v = self.servo_motor_vertical.min_angle
        max_angle_v = self.servo_motor_vertical.max_angle
        
        for angle_v in range(min_angle_v, max_angle_v, 10):
            self.servo_motor_vertical.set_angle(angle_v)
            for angle_h in range(min_angle_h, max_angle_h, 10):
                self.servo_motor_horizontal.set_angle(angle_h)
                _, face = self.detector.detect()
                time.sleep(0.5)
                print(face)
                if len(face) > 0:
                    print("detected")
                    is_detected = True
                    break
            if is_detected or self.mode.value == Mode.END.value:
                break

        if is_detected or self.mode.value == Mode.END.value:
            self.change_mode(Mode.ADJUST)
        else:
            self.servo_motor_horizontal.set_ini_angle()
            self.servo_motor_vertical.set_ini_angle()
            self.servo_motor_horizontal.stop()
            self.servo_motor_vertical.stop()
            self.detector.stop()
            time.sleep(self.research_interval["second"])

    def adjusting(self) -> None:
        """
        カメラ調整状態
        顔を追従して撮影タイミングを調整する
        """
        detected_time = time.perf_counter()
        center_x = self.detector.cam_setting["center"][0]
        center_y = self.detector.cam_setting["center"][1]

        while True:
            # 顔検出して座標取得
            _, face = self.detector.detect()

            if len(face) > 0:
                is_adjusted_h = False
                is_adjusted_v = False
                face_x = face[0][0] + face[0][2] / 2
                face_y = face[0][1] + face[0][3] / 2

                if face_x > center_x + 10:
                    self.servo_motor_horizontal.set_angle(self.servo_motor_horizontal.angle + 1)
                elif face_x < center_x - 10:
                    self.servo_motor_horizontal.set_angle(self.servo_motor_horizontal.angle - 1)
                else:
                    is_adjusted_h = True

                if face_y > center_y + 10:
                    print("y+")
                    self.servo_motor_vertical.set_angle(self.servo_motor_vertical.angle + 1)
                elif face_y < center_y - 10:
                    print("y-")
                    self.servo_motor_vertical.set_angle(self.servo_motor_vertical.angle - 1)
                else:
                    is_adjusted_v = True

                if is_adjusted_h and is_adjusted_v:
                    print("ready")
                    self.change_mode(Mode.CAPTURE)
                    break

                print(f"h:{self.servo_motor_horizontal.angle}, v:{self.servo_motor_vertical.angle}")
                detected_time = time.perf_counter()
            else:
                if time.perf_counter() - detected_time > 30:  # 30秒以上未検出
                    print("time_over")
                    self.change_mode(Mode.SEARCH)
                    break

            if self.mode.value == Mode.END.value:
                break

    def capturing(self) -> None:
        """
        撮影状態
        画像を撮影する
        """
        img, _ = self.detector.detect()
        date_now = datetime.datetime.now()
        output_dir = os.path.join(self.output_dir, str(date_now.year), str(date_now.month))
        output_file_name = f"{date_now.year}_{str(date_now.month).zfill(2)}_{str(date_now.day).zfill(2)}_{str(date_now.hour).zfill(2)}_{str(date_now.minute).zfill(2)}_face.jpg"
        output_file = os.path.join(output_dir, output_file_name)

        os.makedirs(output_dir, exist_ok=True)
        cv2.imwrite(output_file, img)
        print("capture")
        self.change_mode(Mode.WAIT)
        self.servo_motor_vertical.pi.stop()
        self.servo_motor_horizontal.pi.stop()
        self.detector.stop()
        self.update_target_date()

    def update_target_date(self) -> None:
        """
        次の撮影日時を設定する
        """
        target_date = self.setting['target_date']
        target_time = datetime.datetime(target_date["year"],
                                        target_date["month"],
                                        target_date["day"],
                                        target_date["hour"],
                                        target_date["minute"],
                                        target_date["second"])
        target_time += datetime.timedelta(days=self.update_interval["day"],
                                          hours=self.update_interval["hour"],
                                          minutes=self.update_interval["minute"],
                                          seconds=self.update_interval["second"])
        self.setting["target_date"]["year"] = target_time.year
        self.setting["target_date"]["month"] = target_time.month
        self.setting["target_date"]["day"] = target_time.day
        self.setting["target_date"]["hour"] = target_time.hour
        self.setting["target_date"]["minute"] = target_time.minute
        self.setting["target_date"]["second"] = target_time.second
        dump_yaml(self.setting_path, self.setting)

    def press(self, key) -> None:
        """
        キーボードのタイピングを検出し、終了フラグをONにする

        Args:
            key (keyboard.KeyCode): キー入力
        """
        try:
            print(f'アルファベット {0} が押されました'.format(key.char))
            self.change_mode(Mode.END)
        except AttributeError:
            print(f'スペシャルキー {0} が押されました'.format(key))
            self.change_mode(Mode.END)

    def __call__(self):
        listener = keyboard.Listener(on_press=self.press)
        listener.start()

        while True:
            if self.mode.value == Mode.WAIT.value:
                self.waiting()
            elif self.mode.value == Mode.SEARCH.value:
                self.serching()
            elif self.mode.value == Mode.ADJUST.value:
                self.adjusting()
            elif self.mode.value == Mode.CAPTURE.value:
                self.capturing()
            elif self.mode.value == Mode.END.value:
                break
            else:
                break
        self.servo_motor_horizontal.stop()
        self.servo_motor_vertical.stop()


def main(setting_path: str, output_dir: str) -> None:
    """
    メイン関数

    Args:
        setting_path (str): 設定ファイルのパス
        output_dir (str): 撮影画像保存フォルダのパス
    """
    AutoCaptureFace(setting_path, output_dir)()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--setting_path', default="../data/yaml/auto_capture_setting.yaml")
    parser.add_argument('--output_dir', default="../output/")
    args = parser.parse_args()

    main(args.setting_path, args.output_dir)
