import argparse
import csv
import os
import signal
import time
import grovepi2 as grovepi
from datetime import datetime

fs_pulse = 512
fs_acc = 64
acc_interval = fs_pulse // fs_acc

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


def save(pulse, acc):
    print("save " + fname + " ...")
    with open(fname + "heart.csv", 'w') as file:
        writer = csv.writer(file, lineterminator='\n')
        writer.writerows(pulse)
    
    with open(fname + "acc.csv", 'w') as file:
        writer = csv.writer(file, lineterminator='\n')
        writer.writerows(acc)
    
    print("done")

def task(signum, frame):
    #タイマー処理
    #taskにかかる最大時間 << タイマ周期じゃないとだめ
    
    global count
    global data
    global acc_data
    count += 1
    try:
        sensor_value = grovepi.analogRead(1)
        timestamp = ""
        if count % fs_pulse == 1:
            timestamp = time.time()
        
        if count % acc_interval == 1:
            acc = grovepi.acc_xyz(True) #acc_interval 回に一回だけ加速度を読み取り
            acc_data.append((timestamp,) + acc)
            
        data.append([timestamp, sensor_value])
    except KeyboardInterrupt:
        print("キーボードインタラプト")
        raise KeyboardInterrupt()
    except Exception as e:
        #import logging
        #logging.exception(e)
        raise e

data = []
acc_data = []
grovepi.acc_init(fs_acc)
count = 0

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
    save(data, acc_data)
except KeyboardInterrupt:
    print("キーボードインタラプト")
    signal.setitimer(signal.ITIMER_REAL, 0)
    if args.save:
        save(data, acc_data)
    else:
        answer = input("保存しますか? y or n:")
        if answer == "y":
            save(data, acc_data)
