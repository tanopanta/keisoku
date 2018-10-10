import argparse
import csv
import os
import signal
import time
import grovepi2 as grovepi
from datetime import datetime

import signal_processing as sp
fs_pulse = 512

parser = argparse.ArgumentParser()
parser.add_argument("id" , help="IDを指定してください", type=str)
parser.add_argument("-t", "--time", help="計測時間(秒)の指定", type=int, default=60)
parser.add_argument("-s", "--save", help="聞かれずとも保存する True/False(default True)", type=bool, default=True)
args = parser.parse_args()
keisoku_seconds = args.time

#引数のIDをフォルダ分けに利用
fdir = "data/{id}/".format(id=args.id)
fname = fdir + "{id}_{time}".format(id=args.id, time=datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))


if not os.path.isdir(fdir):
    #ディレクトリが存在しないとき
    print(fdir + "を作成します")
    os.makedirs(fdir)


def save(pulse, seconds):
    print("計算中...")
    rri = sp.pulse_to_rri(pulse, fs_pulse, 2, seconds)
    print("save " + fname + " ...")
    timestamp = start
    with open(fname + "rri.csv", 'w') as file:
        for i in rri:
            line = "{0}, {1}\n".format(timestamp, i)
            file.write(line)
            timestamp += 0.5
    print("done")

def task(signum, frame):
    #タイマー処理
    #taskにかかる最大時間 << タイマ周期じゃないとだめ
    global data
    try:
        sensor_value = grovepi.analogRead(1)        
        data.append(sensor_value)
    except KeyboardInterrupt:
        print("キーボードインタラプト")
        raise KeyboardInterrupt()
    except Exception as e:
        #import logging
        #logging.exception(e)
        raise e

data = []

#タイマー処理を設定
signal.signal(signal.SIGALRM, task)
signal.setitimer(signal.ITIMER_REAL, 1 / fs_pulse, 1 / fs_pulse)
print("start")
print(keisoku_seconds, "秒計測")
start = time.time()
try:
    while time.time() - start < keisoku_seconds:
        time.sleep(1)
    signal.setitimer(signal.ITIMER_REAL, 0)
    save(data, keisoku_seconds)
except KeyboardInterrupt:
    print("キーボードインタラプト")
    signal.setitimer(signal.ITIMER_REAL, 0)
    if args.save:
        save(data, int(time.time() - start))
    else:
        answer = input("保存しますか? y or n:")
        if answer == "y":
            save(data, int(time.time() - start))
except Exception as e:
    import logging
    logging.exception(e)
    save(data, int(time.time() - start))