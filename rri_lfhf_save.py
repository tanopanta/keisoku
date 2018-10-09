import argparse
import csv
import os
import queue
import signal
import time
import threading
import grovepi2 as grovepi
from datetime import datetime

import numpy as np

import signal_processing as sp

fs_pulse = 500
buff_size = fs_pulse * 10

class CalcThread(threading.Thread):
    """
    キューにデータが来たら処理して保存を繰り返すスレッド
    """
    def run(self):
        while True:
            try:
                #キューからデータを取得する
                pulse = que.get()
            except queue.Empty:
                print("empty")
                break
            #print(time.time())
            rri = sp.pulse_to_rri(pulse, fs_pulse, 2)
            #print(rri)


def save(pulse):
    print("save " + fname + " ...")
    with open(fname + "heart.csv", 'w') as file:
        writer = csv.writer(file, lineterminator='\n')
        writer.writerows(pulse)
    print("done")

def task(signum, frame):
    #タイマー処理
    #taskにかかる最大時間 << タイマ周期じゃないとだめ
    
    global count
    global data
    count += 1
    try:
        sensor_value = grovepi.analogRead(1)
        times.append(time.time())
        timestamp = ""
        if count % fs_pulse == 1:
            timestamp = time.time()        
        #data.append([timestamp, sensor_value])
        data.append(sensor_value)
        """
        if len(data) >= buff_size:
            que.put(data)
            #data = data[fs_pulse*10:]
            data = []
         """

    except KeyboardInterrupt:
        print("キーボードインタラプト")
        raise KeyboardInterrupt()
    except Exception as e:
        #import logging
        #logging.exception(e)
        raise e


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

data = []
times = []
count = 0

que = queue.Queue()

thd = CalcThread(daemon=True)#デーモンスレッド（メインスレッドと同時に落ちる）
#thd.start()


#タイマー処理を設定
signal.signal(signal.SIGALRM, task)
signal.setitimer(signal.ITIMER_REAL, 1 / fs_pulse, 1 / fs_pulse)
print("start")
try:
    print(keisoku_seconds, "秒計測")
    start = time.time()
    while time.time() - start < keisoku_seconds:
        time.sleep(1)
    signal.setitimer(signal.ITIMER_REAL, 0)
    diffs = np.diff(times)
    np.savetxt("times.csv", diffs)
    #save(data)
except KeyboardInterrupt:
    print("キーボードインタラプト")
    signal.setitimer(signal.ITIMER_REAL, 0)
    #print(np.diff(times))
    diffs = np.diff(times)
    np.savetxt("times.csv", diffs)
    if args.save:
        #save(data)
        pass
    else:
        answer = input("保存しますか? y or n:")
        if answer == "y":
            save(data)
