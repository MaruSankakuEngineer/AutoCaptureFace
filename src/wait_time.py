import datetime
import multiprocessing
import time
from pynput import keyboard


def wait_at_time(target_date: datetime, stop_flag: multiprocessing.Value) -> None:
    """
    指定された日時まで待つ

    Args:
        target_date (datetime): 待つ日時 
        stop_flag (multiprocessing.Value): 終了フラグ
    """
    while target_date > datetime.datetime.now():
        time.sleep(1)
        if stop_flag.value != 0:
            print(f"stop_flag is {stop_flag}")
            break


def press(key: keyboard.KeyCode) -> None:
    """
    キーボードのタイピングを検出し、終了フラグをONにする

    Args:
        key (keyboard.KeyCode): キー入力
    """
    try:
        print(f'アルファベット {0} が押されました'.format(key.char))
        stop_flag.value = 1
    except AttributeError:
        print(f'スペシャルキー {0} が押されました'.format(key))
        stop_flag.value = 1


if __name__ == "__main__":
    target_time = datetime.datetime.now() + datetime.timedelta(seconds=5)  # target_timeを5秒後に設定
    print(f"wait at: {target_time}")
    stop_flag = multiprocessing.Value('i', 0)
    waiting_process = multiprocessing.Process(target=wait_at_time, args=(target_time, stop_flag,))
    waiting_process.start()

    listener = keyboard.Listener(on_press=press)
    listener.start()
    waiting_process.join()
    listener.stop()
