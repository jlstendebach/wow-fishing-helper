import cv2
import numpy
import pynput
import random
import sys
import time
import win32gui

from BrightSpotFishDetector import *

class App:
    # Constants
    TIME_PER_FRAME = .1 # seconds
    BOBBER_WIDTH = 50 # bobber image width
    BOBBER_HEIGHT = 75 # bobber image height
    CATCH_COOLDOWN = 1.0 # min time between catches in seconds

    # States
    isRunning = False
    isFishing = False
    isSavingImage = False

    # Fish detector
    detector = None

    # Controls
    keyListener = None
    mouseListener = None
    mouseController = None
    mouseUpTime = 0
    isRightPressed = False

    # --[ init ]----------------------------------------------------------------
    def __init__(self):
        self.initCommandLineArgs()
        self.initControls()
        self.initFishDetector()

    def initCommandLineArgs(self):
        for arg in sys.argv:
            if arg == "-s":
                self.isSavingImage = True

    def initControls(self):
        self.keyListener = pynput.keyboard.GlobalHotKeys({
            "<ctrl>+<shift>+q": self.onQuitHotkey,
            "<ctrl>+<shift>+f": self.onFishingHotkey,
        })
        self.keyListener.start()

        self.mouseListener = pynput.mouse.Listener(on_click = self.onClick)
        self.mouseListener.start()

        self.mouseController = pynput.mouse.Controller()

    def initFishDetector(self):
        self.detector = BrightSpotFishDetector()
        self.detector.bobberWidth = self.BOBBER_WIDTH
        self.detector.bobberHeight = self.BOBBER_HEIGHT

    # --[ Lifecycle ]-----------------------------------------------------------
    def start(self):
        self.printIntro()
        self.isRunning = True
        self.isFishing = False
        self.loop()

    def stop(self):
        self.isRunning = False

    def loop(self):
        while self.isRunning:
            frameTime = time.time()

            # If we aren't fishing, move on.
            if not self.isFishing:
                time.sleep(self.TIME_PER_FRAME)
                continue

            # Grab the brightness of the image.
            self.detector.update()
            if self.detector.isFishDetected():
                self.catchFish()

            # Sleep if needed
            frameTime = time.time() - frameTime
            sleepTime = self.TIME_PER_FRAME - frameTime
            if sleepTime > 0:
                time.sleep(sleepTime)

    # --[ Helpers ]-------------------------------------------------------------
    def printIntro(self):
        print("+-------------------------------------------+")
        print("| Fishing Helper                            |")
        print("| - Press 'ctrl-shift-q' to quit            |")
        print("| - Press 'ctrl-shift-f' to toggle fishing  |")
        print("| - Double-click to set the bobber location |")
        print("+-------------------------------------------+")

    def toggleFishing(self, isFishing=None):        
        self.isFishing = isFishing or not self.isFishing
        print("Fishing started" if self.isFishing else "Fishing stopped")

    def catchFish(self): 
        print("Catching fish")

        if self.isSavingImage:
            self.saveBobberImages()         

        # Save the mouse position and active window to restore them later
        lastX, lastY = self.getMousePosition()
        lastWindowTitle = self.getActiveWindowTitle()

        # Right click at the bobber
        self.rightClick(self.detector.bobberX, self.detector.bobberY)

        # Restore the old mouse position and active window
        self.setMousePosition(lastX, lastY)
        self.setActiveWindow(lastWindowTitle)

        # Reset the detector
        self.detector.reset()

    def saveBobberImages(self):
        try:
            images = self.detector.getImages()
            rowImages = []
            for row in images:
                rowImages.append(cv2.hconcat(row))
            finalImage = cv2.vconcat(rowImages)
            imageName = "images/{0}.png".format(int(time.time()))
            cv2.imwrite(imageName, finalImage)
        except Exception as e:
            print("Error: Could not save bobber images - {0}".format(e))            

    # --[ UI Helpers ]----------------------------------------------------------
    #########
    # Mouse #
    #########
    def getMousePosition(self):
        return self.mouseController.position
    
    def setMousePosition(self, x, y):
        self.mouseController.position = (x, y)

    def rightClick(self, x = None, y = None):
        currentX, currentY = self.getMousePosition()
        self.setMousePosition(x or currentX, y or currentY)
        time.sleep(0.01)
        self.mouseController.click(pynput.mouse.Button.right)

    ##########
    # Window #
    ##########
    def getActiveWindowTitle(self):
        return win32gui.GetWindowText(win32gui.GetForegroundWindow())
    
    def setActiveWindow(self, windowTitle):
        window = win32gui.FindWindow(None, windowTitle)
        if window:
            win32gui.SetForegroundWindow(window)

    # --[ UI Events ]-----------------------------------------------------------
    def onClick(self, x, y, button, pressed):
        if button == pynput.mouse.Button.left and pressed == False:
            timeSinceLast = time.time() - self.mouseUpTime
            if timeSinceLast < 0.2:
                self.onDoubleClick(x, y)
            self.mouseUpTime = time.time()

    def onDoubleClick(self, x, y):
        if self.getActiveWindowTitle() == "World of Warcraft":
            self.detector.setBobberPosition(x, y)

    def onFishingHotkey(self):
        if self.getActiveWindowTitle() == "World of Warcraft":
            self.toggleFishing()
        else:
            self.toggleFishing(False)

    def onQuitHotkey(self):
        self.stop()

# ------------------------------------------------------------------------------
app = App()
app.start()
