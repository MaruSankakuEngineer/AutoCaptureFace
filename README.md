# AutoCaptureFace

## 概要
特定日時になるまで待ち、特定日時になると顔を探して撮影する。  
撮影動作後、規定した間隔で次回撮影時刻を設定し待ち状態に入る。  
動作中は標準入力を受け付けており、キー入力で停止する。

## 構成
- raspberry pi 4B
- raspberry pi カメラモジュール V3
- サーボモータ組み立てキット
<img src="https://github.com/MaruSankakuEngineer/AutoCaptureFace/assets/159000149/bf3d8745-4d67-4fee-bd88-84aa0eea1d65" width="50%">
<img src="https://github.com/MaruSankakuEngineer/AutoCaptureFace/assets/159000149/016e5977-2713-4455-9ead-53ab21d79a5f" width="50%">


## 動作
動作は大きく分けて5つのモードから構成される。
1. WAITモード
   指定された時刻まで待つモード
2. SEARCHモード
   サーボを動かしながら顔を探すモード
3. ADJUSTモード
   カメラ位置を微調整して撮影タイミングを調整するモード
4. CAPTUREモード
   画像を撮影するモード
5. ENDモード
   各モード時にキー入力があると遷移するモード
   直ちにプログラムを終了する
<img src="https://github.com/MaruSankakuEngineer/AutoCaptureFace/assets/159000149/91751bac-8e6e-4389-8e3f-146d6f76ec56" width="75%">
