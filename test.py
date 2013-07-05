#!/usr/bin/python

import pylab
import matplotlib.pyplot as plt
import serial
from pylab import array

s = serial.Serial('COM3', baudrate=9600)

def get_line(s, count=10):
    ret = []
    for i in xrange(count):
        l = s.readline()
        try:
            f = float(l.strip())
        except:
            print "bad value %r" % l
            f = 0.0
        ret.append(f)
    return ret

dat=[0,1]
fig = plt.figure()
ax = fig.add_subplot(111)
Ln, = ax.plot(dat, '.')
ax.set_xlim([0,20])
ax.set_ylim([0,1100])
plt.ion()
plt.show()

while True:
    dat = get_line(s)
    a = array(dat)
    dat = array([sum(a) / len(a), 0, 0] + dat)
    #print ", ".join(map(str, dat))
    Ln.set_ydata(dat)
    Ln.set_xdata(range(len(dat)))
    plt.pause(0.01)
