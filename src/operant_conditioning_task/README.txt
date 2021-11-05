operant_conditioning_task-211101 プログラムについて

2021年11月1日
株式会社知能情報システム
高田直樹


1. operant_conditioning_task プログラムの概要

operant_conditioning_task プログラムは、Raspberry Pi (Raspberry 
Pi 4 Model B) を用いて、マウスの nose poke 行動によるオペラント
条件付け行動課題実験を行う Python プログラムです。


2. セットアップ

Raspberry Pi と Python 環境を以下の手順を参考にセットアップして
ください。
  
(1) https://www.raspberrypi.com/software/ から、Raspberry Pi OS 
    のインストーラーを適当な PC にダウンロードします。
    
(2) 8 GB 以上の microSD カードを PC に接続し、Raspberry Pi OS を 
    microSD カード にインストールします。
    
(3) microSD カード を Raspberry Pi に装着して、Raspberry Pi を
    起動します。
    
(4) 下記のコマンドで、Raspberry Pi OS にデフォルトで設定されている 
    Python 2 を Python 3 に変更します。
    
    $ cd /usr/bin
    $ sudo unlink python
    $ sudo ln -s python3 python

    上記の代わりに Berry Conda を使用する場合は、下記のコマンドで
    インストールします。
    
    $ wget https://github.com/jjhelmus/berryconda/releases/download/v2.0.0/Berryconda3-2.0.0-Linux-armv7l.sh
    $ wget https://github.com/jjhelmus/berryconda/releases/download/v2.0.0/Berryconda3-2.0.0-Linux-armv7l.sh
    $ chmod +x Berryconda3-2.0.0-Linux-armv7l.sh
    $ ./Berryconda3-2.0.0-Linux-armv7l.sh
    
(5) 下記の Python パッケージを pip コマンドでインストールします。

    transitions==0.8.10
    gpiozero==1.6.2
    RPi.GPIO==0.7.0
    numpy==1.15.1
    dataclasses==0.8
    toml==0.10.2

(6) "operant_conditioning_task-211101" フォルダーを Raspberry Pi 
    の任意の場所にコピーします。
    
(7) GPIO ピンに適切なデバイスを接続します。

[参考1: PyCharm のインストール]
(1) 公式ページから Linux 版の PyCharm をダウンロードします。
(2) 下記のコマンドで、Java SDK をインストールします。
    $ sudo apt install openjdk-11-jdk
(3) 下記のコマンドで、ダウンロード ファイルを解凍します。
    $ tar zxvf <ダウンロード フォルダー>/pycharm-community-<バージョン名>.tar.gz
(4) 下記のコマンドで、PyCharm を起動します。
    <PyCharm フォルダー>/bin/pycharm.sh

[参考2: Raspberry Pi OS の日本語入力設定]
$ sudo apt update
$ sudo apt install ibus-mozc

[参考3: Raspberry Pi OS のスリープ設定解除の参考ページ]
https://rikoubou.hatenablog.com/entry/2020/06/11/133716


2. プログラムの操作方法

operant_conditioning_task プログラムの操作は、以下にように行います。

(1) "settings" フォルダーにある settings.toml ファイルを
    テキスト エディターで開いて、必要な設定の変更を行います。
    各設定項目については、settings.toml ファイルに記載の
    コメントを参照してください。

(2) LXTerminal を開き、"operant_conditioning_task-211101" フォルダー
    に移動して、下記のコマンドでプログラムを実行します。
    
    python operant_conditioning_task.py <-n, --name experiment_name> 
      <-s, --setting setting_file_path> <-r, --results results_file_path> 
      <-l, --log log_file_path>
    
    [コマンドライン引数の説明]
    -n, --name experiment_name (オプション): 
      実験の名前です。指定しない場合は、現在の日時 (yymmdd-HHMMSS) 
      をデフォルトの名前とします。
    -s, --setting setting_file_path (オプション): 
      toml 形式の設定ファイル (*.toml) のパスです。指定しない場合は、
      settings フォルダーにある setting.toml ファイルをデフォルトの
      設定ファイルとします。
    -r, --results results_file_path (オプション): 
      CSV 形式の結果データ ファイル (*.csv) のパスです。指定しない
      場合は、ルート フォルダーに現在の日時 (results-<yymmdd-HHMMSS>.csv) 
      でファイルを生成します。
    -l, --log log_file_path (オプション): 
      テキスト形式のログ ファイル (*.txt) のパスです。指定しない
      場合は、ルート フォルダーに現在の日時 (log-<yymmdd-HHMMSS>.txt) 
      でファイルを生成します。

(3) Ctrl+C キーを押すと、プログラムが終了します。
