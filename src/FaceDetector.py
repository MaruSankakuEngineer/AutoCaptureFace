import cv2
import numpy as np
import typing
from libcamera import controls
from picamera2 import Picamera2
from common import load_yaml


class FaceDetector():
    """
    カメラを起動し顔検出を実施するクラス
    """

    def __init__(self, setting_yaml: str) -> None:
        """
        Args:
            setting_yaml (str): 設定ファイルのパス
        """
        self.cam = Picamera2()
        config = load_yaml(setting_yaml)

        self.cam_setting = config.get("camera_setting")
        self.cam_setting["size"] = tuple((self.cam_setting["size"]["width"], self.cam_setting["size"]["height"]))
        self.cam.configure(self.cam.create_preview_configuration(main=self.cam_setting))
        self.cam_setting["center"] = tuple((self.cam_setting["size"][0]/2, self.cam_setting["size"][1]/2),)

        self.cascade_setting = config["cascade_setting"]
        self.cascade_setting["min_size"] = tuple((self.cascade_setting["min_size"]["width"], self.cascade_setting["min_size"]["height"]))
        self.cascade = cv2.CascadeClassifier(self.cascade_setting["xml_path"])

    def start(self):
        """
        カメラを動作開始する
        """
        self.cam.start()
        self.cam.set_controls({"AfMode": controls.AfModeEnum.Continuous})

    def detect(self) -> tuple[np.ndarray, np.ndarray]:
        """
        画像を取得し、顔検出結果を返却する

        Returns:
            tuple: (取得画像, 顔検出座標)
        """
        img = self.cam.capture_array()
        img = cv2.flip(img, 0)  # カメラの設置向きによっては不要
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        face = self.cascade.detectMultiScale(gray,
                                            scaleFactor=self.cascade_setting["scale_factor"],
                                            minNeighbors=self.cascade_setting["min_neighbors"],
                                            minSize=self.cascade_setting["min_size"])
        return img, face

    def stop(self):
        """
        カメラを動作停止する
        """
        self.cam.stop()


def main():
    """
    メイン関数
    顔検出を行い、検出結果を画像に上書きしながら表示し続ける
    """
    detector = FaceDetector("../data/yaml/camera_setting.yaml")
    detector.start()

    while True:
        img, face = detector.detect()
        for (x, y, w, h) in face:
            cv2.rectangle(img, (x, y), (x + w, y+h), (0, 0, 300), 2)

        cv2.imshow("Camera", img)

        key = cv2.waitKey(1)
        # Escキーで停止
        if key == 27:
            break
    detector.stop()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
