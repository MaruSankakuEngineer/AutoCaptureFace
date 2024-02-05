import pigpio
import time


class ServoMotor:
    """
    サーボモータを制御するクラス

    Attributes:
        pin: GPIOのピン番号
        max_angle: 最大移動角度
        min_angle: 最小移動角度
        angle: 現在の角度
        ini_angle: 初期設定角度
        pi: gpio制御
    """
    def __init__(self, pin=17, min_angle=0, max_angle=180, ini_angle=90) -> None:
        """
        サーボモータを制御するクラス
        """
        self.pin = pin
        self.max_angle = max_angle
        self.min_angle = min_angle
        self.angle = 0
        self.ini_angle = ini_angle
        self.pi = pigpio.pi()

    def start(self) -> None:
        """
        GPIOの開始処理
        """
        self.pi.set_mode(self.pin, pigpio.OUTPUT)

    def stop(self) -> None:
        """
        GPIOの終了処理
        """
        self.pi.set_mode(self.pin, pigpio.INPUT)
        self.pi.stop()

    def set_angle(self, target_angle: int) -> None:
        """
        サーボモータを指定角度に移動する

        Args:
            target_angle (int): 動作させる角度
        """
        if target_angle < self.min_angle or target_angle > self.max_angle:
            print(f"角度は{self.min_angle}から{self.max_angle}度の間で指定してください。")
            return

        # 角度を500から2500のパルス幅にマッピングする
        pulse_width = (target_angle / 180) * (2500 - 500) + 500
        self.angle = target_angle
        # パルス幅を設定してサーボを回転させる
        self.pi.set_servo_pulsewidth(self.pin, pulse_width)
        time.sleep(0.2)  # サーボモータが移動するのを待つために少し待つ

    def set_ini_angle(self) -> None:
        """
        サーボモータを初期設定の角度に移動する
        """
        self.set_angle(self.ini_angle)

    def load_setting(self, servo_setting: dict):
        """
        サーボモータの設定を適用する

        Args:
            servo_setting (dict): サーボモータの設定
        """
        self.pin = servo_setting.get("pin")
        self.max_angle = servo_setting.get("max_angle", 180)
        self.min_angle = servo_setting.get("min_angle", 0)
        self.ini_angle = servo_setting.get("ini_angle", 90)


if __name__ == "__main__":
    # 動作サンプル
    # ServoMotorクラスのインスタンス化
    servo_motor_horizontal = ServoMotor(pin=17, max_angle=160, min_angle=0, ini_angle=90)
    servo_motor_vertical = ServoMotor(pin=18, max_angle=130, min_angle=0, ini_angle=40)
    servo_motor_horizontal.start()
    servo_motor_vertical.start()

    # # サンプル動作
    servo_motor_vertical.set_angle(20)
    for angle in range(0, 181, 10):
        servo_motor_horizontal.set_angle(angle)

    servo_motor_vertical.set_angle(40)
    for angle in range(180, -1, -10):
        servo_motor_horizontal.set_angle(angle)

    servo_motor_vertical.set_angle(60)
    for angle in range(0, 181, 10):
        servo_motor_horizontal.set_angle(angle)

    # 初期位置に移動
    servo_motor_vertical.set_ini_angle()
    servo_motor_horizontal.set_ini_angle()
