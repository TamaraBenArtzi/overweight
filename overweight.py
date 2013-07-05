"""

Overweight

Display videos intermixed with white screens, changing when a toy starts moving and stops moving
"""

"""
mouse hiding
stichless switching (foreground setting with win32api)
"""

import random
import glob
import itertools
import sys
import os
import subprocess
import time

import pygame
import serial

VIDEO_DIRECTORY = r'c:\Users\TAMARA\Desktop'
VLC = r"C:\Program Files (x86)\VideoLAN\VLC\vlc.exe"

VIDEOS = glob.glob(os.path.join(VIDEO_DIRECTORY, '*.mp4'))
if not os.path.exists(VIDEO_DIRECTORY):
        print "please set VIDEO_DIRECTORY to an existing path in %s" % sys.modules[__name__].__file__
        raise SystemExit
if len(VIDEOS) == 0:
        print "no videos in %s?" % VIDEO_DIRECTORY
        raise SystemExit
if not os.path.exists(VLC):
        print "VLC points to non existent %s, please edit %s" % (VLC, sys.modules[__name__].__file__)
        raise SystemExit

class Video(object):
        def __init__(self):
                self.videos = VIDEOS
                self.video_iter = itertools.cycle(self.videos)
                self.player = None
                
        def next(self):
                video = self.video_iter.next()
                self.stop()
                self.player = subprocess.Popen(executable=VLC, args=[VLC, '-f', '--no-overlay', '--no-video-title-show', '--no-osd', '--video-on-top', video])
                
        def stop(self):
                if self.player:
                        self.player.kill()
                        self.player = None

class WhiteScreen(object):
        def __init__(self):
                self.surface = None
                self.white = pygame.Color(255, 255, 255)
        def display(self):
                if self.surface:
                        return
                self.surface = pygame.display.set_mode((1366, 768), pygame.FULLSCREEN)
                self.surface.fill(self.white)
                pygame.display.update()
        def hide(self):
                pygame.display.quit()
                self.surface = None                        

class Sensor(object):
        def __init__(self):
                # TODO - find correct com port
                self.s = serial.Serial('COM3', baudrate=9600)
                self.is_running = False
                self.is_certain = False
                self.is_moving = False
                self.last_readings = []
                # Constants
                self.N = 20            # Number of samples to determine stopped or running state 
                self.MIN_DT = 2.0      # minimum time from last change
                self.MOVING_MIN_VAR = 30 # Minimal variance of signal that indicates movement
                self.t_start = time.time()
                self.t = self.t_start
                self.t_running = self.t
                self.t_stopped = self.t

        def _get_line(self, count=1):
                ret = []
                for i in xrange(count):
                        l = self.s.readline()
                        try:
                                f = float(l.strip())
                        except:
                                print "bad value %r" % l
                                f = 0.0
                        ret.append(f)
                return ret

        def get_reading(self):
                change = False
                r = self._get_line(count=1)[0]
                self.last_readings.append(r)
                if len(self.last_readings) > self.N:
                        del self.last_readings[:(len(self.last_readings) - self.N)]
                avg = float(sum(self.last_readings)) / len(self.last_readings)
                var = (sum((x - avg) * (x - avg) for x in self.last_readings) / len(self.last_readings))**0.5
                self.is_certain = len(self.last_readings) >= self.N
                self.var = var
                was_running = self.is_running
                was_moving = self.is_moving
                self.is_moving = is_moving = var > self.MOVING_MIN_VAR
                self.t = time.time() - self.t_start
                dt_running = self.t - self.t_running
                dt_stopped = self.t - self.t_stopped
                self.is_running = is_moving or (was_running and (dt_running < self.MIN_DT))
                if self.is_running and not was_running or self.is_moving and not was_moving:
                        self.t_running = self.t
                        change = True
                if not self.is_running and was_running:
                        self.t_stopped = self.t
                        change = True
                return change

class DebugDisplay(object):
        def __init__(self):
                self.s = pygame.display.set_mode((640, 480))
                self.black = pygame.Color(0, 0, 0)
                self.white = pygame.Color(255, 255, 255)
                self.font = pygame.font.Font('freesansbold.ttf', 32)
                
        def print_string(self, msg):
                y = 0
                for m in msg.split('\n'):
                        s = self.font.render(m, False, self.white)
                        rect = s.get_rect()
                        rect.topleft = (10, 20 + y)
                        self.s.blit(s, rect)
                        y += 32
                
        def show(self, sensor):
                self.s.fill(self.black)
                self.print_string(
"""%5.1f (var %5.1f)
%15s, %15s
t: %5.2f
last run t: %5.2f
last stopped t: %5.2f
dt_running: %5.2f""" % (
                                sensor.last_readings[-1], sensor.var,
                                'running' if sensor.is_running else 'stopped',
                                'moving' if sensor.is_moving else 'unmoving',
                                sensor.t, sensor.t_running, sensor.t_stopped,
                                sensor.t - sensor.t_running))

class Loop(object):
        def __init__(self, debug=False):
                self.video = Video()
                self.white_screen = WhiteScreen()
                self.sensor = Sensor()
                if debug:
                        self.debug = DebugDisplay()
                else:
                        self.debug = False

        def iterate(self):
                if pygame.display.get_init():
                        for event in pygame.event.get():
                                if event.type == pygame.QUIT:
                                        pygame.quit()
                                        sys.exit()
                                elif event.type == pygame.KEYDOWN:
                                        if event.key == pygame.K_ESCAPE:
                                                pygame.event.post(pygame.event.Event(pygame.QUIT))
                change = self.sensor.get_reading()
                if self.debug:
                        self.debug.show(self.sensor)
                        pygame.display.update()
                else:
                        if change:
                                if self.sensor.is_running:
                                        self.white_screen.display()
                                        self.video.stop()
                                else:
                                        self.video.next()
                                        self.white_screen.hide()
                # Check if someone closed the movie
                #if self.sensor.is_running and 

def test_pygame():
        s = pygame.display.set_mode((500,500))
        pygame.draw.circle(s, pygame.Color(255, 255, 255), (100, 100), 50, 0)
        pygame.display.update()
        time.sleep(5)

def test_white_screen():
        screen = WhiteScreen()
        screen.display()
        time.sleep(1)
        screen.hide()

def test_video():
        video = Video()
        video.next()
        time.sleep(5)
        video
        video.next()

def test_both():
        video = Video()
        screen = WhiteScreen()
        screen.display()
        time.sleep(10)
        video.next()
        screen.hide()
        time.sleep(10)
        video.stop()
        screen.display()
        time.sleep(10)
        video.next()
        screen.hide()
        time.sleep(10)
        video.stop()

def test_plot():
        import pylab
        dat=[0,1]
        fig = plt.figure()
        ax = fig.add_subplot(111)
        Ln, = ax.plot(dat, '.')
        ax.set_xlim([0,20])
        ax.set_ylim([0,1100])
        plt.ion()
        plt.show()
        s = Sensor()
        while True:
                dat = [s.get_reading() for i in xrange(10)]
                a = array(dat)
                dat = array([sum(a) / len(a), 0, 0] + dat)
                #print ", ".join(map(str, dat))
                Ln.set_ydata(dat)
                Ln.set_xdata(range(len(dat)))
                plt.pause(0.01)

def main():
        l = Loop(debug=sys.argv[-1].lower() == 'debug')
        while True:
                l.iterate()

if __name__ == '__main__':
        pygame.init()
        #test_pygame()
        main()