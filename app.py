import cv2
import numpy
import mss.tools
import pynput
import random
import sys
import time
import win32gui

class App:
    timePerFrame = .1 # seconds
    imageWidth = 50
    imageHeight = 75
    sampleStride = 2
    brightnessThreshold = 240
    brightSpotThreshold = 10
    imagePath = "images/"

    isRunning = False
    isFishing = False
    isSavingImage = False

    bobberX = 0
    bobberY = 0
    catchCooldown = 1.0 # seconds
    catchTime = 0

    mouseController = pynput.mouse.Controller()
    mouseUpTime = 0

    sct = mss.mss()

    # --[ init ]----------------------------------------------------------------
    def __init__(self):
        keyListener = pynput.keyboard.GlobalHotKeys({
            "<ctrl>+<shift>+q": self.onQuitHotkey,
            "<ctrl>+<shift>+f": self.onFishingHotkey,
        })
        keyListener.start()

        mouseListener = pynput.mouse.Listener(on_click = self.onClick)
        mouseListener.start()

        print("+-------------------------------------------+")
        print("| Fishing Helper                            |")
        print("| - Press 'ctrl-shift-q' to quit            |")
        print("| - Press 'ctrl-shift-f' to toggle fishing  |")
        print("| - Double-click to set the bobber location |")
        print("+-------------------------------------------+")

    # --[ Lifecycle ]-----------------------------------------------------------
    def start(self):
        self.isRunning = True

        lastImage = None
        while self.isRunning:
            frameTime = time.time()

            # Grab the brightness of the image
            if self.isFishing:
                #image = self.captureImageAtMouse(self.imageWidth, self.imageHeight)
                image = self.captureImageAtBobber(self.imageWidth, self.imageHeight)
                brightSpotCount = self.getBrightSpotCount(image, self.sampleStride)
                timeSinceCatch = time.time() - self.catchTime

                if (brightSpotCount >= self.brightSpotThreshold 
                    and lastImage != None
                    and timeSinceCatch >= self.catchCooldown):
                    print("Fish detected! ({0} bright spots)".format(brightSpotCount))                    
                    self.sleepRandomTime(0.50, 1.00)
                    self.rightClickAtBobber()
                    self.catchTime = time.time()
                    if self.isSavingImage:
                        self.saveBeforeAndAfterImage(lastImage, image)
                elif brightSpotCount >= self.brightSpotThreshold/2:
                    print("Close call! ({0} bright spots)".format(brightSpotCount))

                # Update the previous data for comparison in the next frame.
                lastImage = image

            # Sleep if needed
            frameTime = time.time() - frameTime
            sleepTime = self.timePerFrame - frameTime
            if sleepTime > 0:
                time.sleep(sleepTime)

    def stop(self):
        self.isRunning = False
        cv2.destroyAllWindows()

    # --[ Helpers ]-------------------------------------------------------------
    def captureImage(self, x, y, width, height): 
        monitorNumber = 1
        monitor = self.sct.monitors[monitorNumber]
        area = {
            "top": int(monitor["top"] + y),  
            "left": int(monitor["left"] + x), 
            "width": width,
            "height": height,
            "mon": monitorNumber,
        }
        return self.sct.grab(area)

    def captureImageAtMouse(self, width, height):
        mouseX, mouseY = self.mouseController.position
        return self.captureImage(mouseX - width/2, mouseY - height/2, width, height)
    
    def captureImageAtBobber(self, width, height):
        return self.captureImage(self.bobberX - width/2, self.bobberY - height/2, width, height)

    def previewImage(self, windowName, image):
        cv2.imshow(windowName, numpy.array(image))
    
    def getBrightSpotCount(self, image, stride):
        threshold = self.brightnessThreshold*3
        count = 0
        for x in range(0, image.size.width, stride):
            for y in range(0, image.size.height, stride):
                r, g, b = image.pixel(x, y)
                if r+g+b >= threshold:
                    count += 1
        return count        
        
    def rightClickAtBobber(self): 
        # Save the mouse position and active window to restore them later
        lastX, lastY = self.getMousePosition()
        lastWindowTitle = self.getActiveWindowTitle()

        # Right click at the bobber
        self.rightClick(self.bobberX, self.bobberY)

        # Restore the old mouse position and active window
        #pyautogui.moveTo(lastX, lastY)
        #if lastWindowTitle != "World of Warcraft":
        #    self.setActiveWindow(lastWindowTitle)

    def sleepRandomTime(self, min, max):
        waitTime = random.uniform(min, max)
        time.sleep(waitTime)

    def saveBeforeAndAfterImage(self, beforeImage, afterImage):
        beforeAndAfterImage = cv2.hconcat([numpy.array(beforeImage), numpy.array(afterImage)])
        cv2.imwrite(self.imagePath+str(int(time.time()))+".png", beforeAndAfterImage)

    def toggleFishing(self, isFishing=None):        
        self.isFishing = isFishing if isFishing != None else not self.isFishing
        print("Fishing started" if self.isFishing else "Fishing stopped")

    def getActiveWindowTitle(self):
        return win32gui.GetWindowText(win32gui.GetForegroundWindow())
    
    def setActiveWindow(self, windowTitle):
        window = win32gui.FindWindow(None, windowTitle)
        if window:
            win32gui.SetForegroundWindow(window)

    # --[ UI Wrappers ]---------------------------------------------------------
    def getMousePosition(self):
        return self.mouseController.position
    
    def setMousePosition(self, x, y):
        self.mouseController.position = (x, y)

    def rightClick(self, x = None, y = None):
        currentX, currentY = self.getMousePosition()
        self.setMousePosition(x or currentX, y or currentY)
        self.mouseController.click(pynput.mouse.Button.right)
        
    # --[ UI Events ]-----------------------------------------------------------
    def onClick(self, x, y, button, pressed):
        if button == pynput.mouse.Button.left and pressed == False:
            timeSinceLast = time.time() - self.mouseUpTime
            if timeSinceLast < 0.2:
                self.onDoubleClick(x, y)
            self.mouseUpTime = time.time()

    def onDoubleClick(self, x, y):
        if self.getActiveWindowTitle() == "World of Warcraft":
            self.bobberX = x
            self.bobberY = y
            print("Bobber location: ({0}, {1})".format(self.bobberX, self.bobberY))

    def onFishingHotkey(self):
        if self.getActiveWindowTitle() == "World of Warcraft":
            self.toggleFishing()
        else:
            self.toggleFishing(False)

    def onQuitHotkey(self):
        self.stop()

app = App()
for arg in sys.argv:
    if arg == "-s":
        app.isSavingImage = True
app.start()