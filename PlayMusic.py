import math
import wave
import os
from os.path import expanduser
import argparse
import tkinter as tk
import tkinter.filedialog
import unicodedata
import pyaudio
import numpy as np

def reshapeText(text):
    count = 0
    for c in text:
        if unicodedata.east_asian_width(c) in 'FWA':
            count += 2
        else:
            count += 1
    text += " " * (39-count)
    return text


def printEqualizer(amp_by_freq, filename):
    print("\033[18F")
    for i in range(15, 0, -1):
        #color = "\033[45m" if i<=3 else "\033[46m" if i<=6 else "\033[42m" if i<=9 else "\033[43m" if i<=12 else "\033[41m" 
        #level = ["\033[0m  "+color+" " if a>=i else "\033[0m   " for a in amp_by_freq]
        color = "\033[35m" if i<=3 else "\033[36m" if i<=6 else "\033[32m" if i<=9 else "\033[33m" if i<=12 else "\033[31m" 
        level = ["\033[0m  "+color+"|" if a>=i else "\033[0m   " for a in amp_by_freq]
        #level = ["  |" if a>=i else "   " for a in amp_by_freq]
        print("\033[0m "+"".join(level))
    print("\033[0m  LOW---------------MID--------------HIGH")
    print("  "+"".join(filename[:40]))


def getAmpByFreq(buf, framerate):
    data = np.frombuffer(buf, dtype='int16')
    #sampwidth == 4:
        #data = np.frombuffer(buf, dtype='int32')
    f = np.fft.rfft(data)
    freq = np.fft.rfftfreq(data.shape[0], d=1.0/framerate)
    amp = np.abs(f)
    amp_by_freq = []
    for i in range(len(sample_freqs)-1):
        p = np.sum(amp[(freq>sample_freqs[i]) & (freq<sample_freqs[i+1])])
        try:
            amp_by_freq.append(p//1000000)
        except ValueError:
            amp_by_freq.append(0)
    return amp_by_freq


def playWF(path):
    filename = os.path.splitext(os.path.basename(path))[0]
    filename = list(reshapeText(filename))
    wf = wave.open(path, mode='rb')
    p = pyaudio.PyAudio()
    sampwidth = wf.getsampwidth()
    framerate = wf.getframerate()
    channels = wf.getnchannels()
    stream = p.open(
        format=p.get_format_from_width(sampwidth),
        channels=channels,
        rate=framerate,
        output=True) 
    chunk = 1024 
    wf.rewind() 
    if sampwidth!=2 or channels!=2:
        print(sampwidth, channels)
    buf = wf.readframes(chunk)
    cnt = 0
    while buf:
        stream.write(buf)
        if cnt%1 == 0:
            amp_by_freq = getAmpByFreq(buf, framerate)
            printEqualizer(amp_by_freq, filename)
        buf = wf.readframes(chunk)
        if cnt%5 == 0:
            filename = filename[1:] + filename[:1]
        cnt += 1
    stream.close()
    p.terminate()


def main():
    print("\033[2J")
    global sample_freqs
    sample_freqs = [20, 40, 70, 100, 200, 400, 700, 1000, 2000, 4000, 7000, 10000, 20000, 40000]
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('-D', '--dir', action='store_true', help='ディレクトリ選択')
    args = parser.parse_args()
    home = expanduser("~")
    iDir = os.path.abspath(os.path.dirname(home))
    if args.dir:
        root = tk.Tk()
        dir_path = tkinter.filedialog.askdirectory(initialdir = iDir)
        root.destroy()
        files = os.listdir(dir_path)
        file_paths = [f for f in files if os.path.isfile(os.path.join(dir_path, f))]
        wav_paths = [f for f in file_paths if f.endswith('.wav')]
        while(True):
            wav_path = np.random.choice(wav_paths, 1)[0]
            path = "{}/{}".format(dir_path, wav_path)
            playWF(path)
    else:
        fTyp = [("", "*.wav")]
        root = tk.Tk()
        path = tkinter.filedialog.askopenfilename(filetypes=fTyp, initialdir=iDir)
        root.destroy()
        playWF(path)


if __name__ == '__main__':
    main()
