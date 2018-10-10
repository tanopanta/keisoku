import signal
import time

fs_pulse = 500
endcount = fs_pulse * 600
endtime = 0
count = 0
def task(a, b):
    global count
    global endtime
    count += 1
    if count == endcount:
        endtime = time.time()
        signal.setitimer(signal.ITIMER_REAL, 0)
        raise KeyboardInterrupt

signal.signal(signal.SIGALRM, task)
signal.setitimer(signal.ITIMER_REAL, 1 / fs_pulse, 1 / fs_pulse)
starttime = time.time()
try:
    while True:
        time.sleep(1)
    signal.setitimer(signal.ITIMER_REAL, 0)
    
except KeyboardInterrupt:
    #signal.setitimer(signal.ITIMER_REAL, 0)
    print("誤差")
    print(endtime - starttime - 600)
    print("秒")
