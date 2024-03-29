import numpy as np
import scipy.signal as sg
import math
from scipy import integrate
from scipy.interpolate import interp1d

def pulse_to_rri(pulse, fs, hokan_fs, interval):
    #脈波からRRIの時系列データに変換
    #fc = 2.338
    
    pulse = sg.medfilt(pulse, 3) #スパイクノイズの削除
    
    num = 44 #移動平均の個数
    filt = np.ones(num) / num

    pulse = np.convolve(pulse, filt, mode='same')#移動平均
    
    #lpf_fil = sg.firwin(33, fc / (fs/2.0), window="hamming")
    #pulse = sg.lfilter(lpf_fil, 1, pulse)
    #pulse -= 511 #DC成分
    
    peak_indexes, _ = sg.find_peaks(pulse, height=0, distance=fs//2.0)
    peak_diffs = np.gradient(peak_indexes) / fs #RR間隔の計算
    
    peak_seconds = peak_indexes / fs
    
    f = interp1d(peak_seconds, peak_diffs, kind="cubic", fill_value='extrapolate')
    new_sample_len = interval * hokan_fs
    xnew = np.linspace(0 , interval-1, num=new_sample_len)
    hokan = f(xnew)
    return hokan

def rri_to_lfhf(rri, fs, fft_size, interval=10):
    """RRIの時系列からlf/hfを計算 
    計算に60秒分使うため前後30秒は0.0
    """
    hokan = sg.detrend(rri, type="constant")
    #hokan = hokan[hokan_fs//2:-hokan_fs] #前後1秒分ぐらいをカット
    
    
    out_len = int(len(rri) / fs // interval)
    out_len -= 60//interval
    if out_len <= 0:
        print("lf/hfの計算には１分以上のデータが必要です")
    result = [0.0] * (60//interval//2)
    
    lf_min = hz_to_idx(0.04, fs, fft_size)
    lf_max = hz_to_idx(0.15, fs, fft_size)
    hf_min = lf_max # + 1(sumの場合)
    hf_max = hz_to_idx(0.4, fs, fft_size)
    
    for i in range(out_len):
        rri_tmp = hokan[i*interval:i*interval + fs*60]

        window = np.hanning(len(rri_tmp))
        rri_tmp = rri_tmp * window 
        
        
        f = np.fft.fft(rri_tmp, n=fft_size) #fft_size点でfft
        amp = np.abs(f) #a + ib => sqrt(a^2 + b^2)
        pow = amp ** 2 #パワースペクトルに
        
        #ストレス値計算------------
        lf = integrate.trapz(pow[lf_min:lf_max+1]) #台形公式による積分
        hf = integrate.trapz(pow[hf_min:hf_max+1]) 
        result.append(lf/hf)
    for i in range(60//interval//2):
        result.append(0.0)
    return result

def hz_to_idx(hz, fs, point):
    return math.ceil(hz / (fs / (point)))
