import cv2
import numpy
import mss.tools
import pyautogui
import random
import sys
import time
from pynput import keyboard

class App:
    timePerFrame = .1 # seconds
    imageWidth = 50
    imageHeight = 75
    sampleStride = 1
    brightnessThreshold = 240
    brightSpotThreshold = 10
    imagePath = "images/"

    isRunning = False
    isFishing = False
    isSavingImage = False

    sct = mss.mss()

    # --[ init ]----------------------------------------------------------------
    def __init__(self):
        listener = keyboard.GlobalHotKeys({
            "<ctrl>+<shift>+q": (lambda: self.onQuitHotkey()),
            "<ctrl>+<shift>+f": (lambda: self.onFishingHotkey()),
        })
        listener.start()

        print("Press 'ctrl+shift+q' to quit.")
        print("Press 'ctrl+shift+f' to toggle fishing.")

    # --[ Lifecycle ]-----------------------------------------------------------
    def start(self):
        self.isRunning = True

        lastImage = None
        lastBrightSpotCount = 0
        while self.isRunning:
            frameTime = time.time()

            # Grab the brightness of the image
            if self.isFishing:
                image = self.captureImageAtMouse(self.imageWidth, self.imageHeight)

                countTime = time.time()
                brightSpotCount = self.getBrightSpotCount(image, self.sampleStride)
                print("countTime: ", int((time.time() - countTime)*1000))

                brightSpotCountDiff = brightSpotCount - lastBrightSpotCount

                if brightSpotCount >= self.brightSpotThreshold and lastImage != None:
                    print("Fish detected! ({0} - {1} more bright spots)".format(brightSpotCount, brightSpotCountDiff))
                    self.sleepRandomTime(0.50, 1.00)
                    self.rightClick()
                    if self.isSavingImage:
                        self.saveBeforeAndAfterImage(lastImage, image)
                elif brightSpotCountDiff >= self.brightSpotThreshold/2:
                    print("Close call! ({0} - {1} more bright spots)".format(brightSpotCount, brightSpotCountDiff))

                # Update the previous data for comparison in the next frame.
                lastImage = image
                lastBrightSpotCount = brightSpotCount

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
        mouseX, mouseY = pyautogui.position()
        return self.captureImage(mouseX - width/2, mouseY - height/2, width, height)

    def previewImage(self, windowName, image):
        cv2.imshow(windowName, numpy.array(image))

    def getBrightness(self, r, g, b):
        # return int(r*0.299 + g*0.587 + b*0.114) # Perceived brightness
        return int((r+g+b)/3) # RGB average
    
    def getImageBrightness(self, image, stride): 
        count = 0
        brightness = 0
        for x in range(0, image.size.width, stride):
            for y in range(0, image.size.height, stride):
                r, g, b = image.pixel(x, y)
                count += 1
                brightness += self.getBrightness(r, g, b)
        return int(brightness / count)
    
    def getBrightSpotCount(self, image, stride):
        threshold = self.brightnessThreshold*3
        count = 0
        for x in range(0, image.size.width, stride):
            for y in range(0, image.size.height, stride):
                r, g, b = image.pixel(x, y)
                average = r+g+b
                if r+g+b > threshold:
                    count += 1
        return count        
    
    def rightClick(self):
        x, y = pyautogui.position()
        pyautogui.rightClick(x = x, y = y)

    def sleepRandomTime(self, min, max):
        waitTime = random.uniform(min, max)
        time.sleep(waitTime)

    def saveBeforeAndAfterImage(self, beforeImage, afterImage):
        beforeAndAfterImage = cv2.hconcat([numpy.array(beforeImage), numpy.array(afterImage)])
        cv2.imwrite(self.imagePath+str(int(time.time()))+".png", beforeAndAfterImage)

    # --[ UI Events ]-----------------------------------------------------------
    def onFishingHotkey(self):
        self.isFishing = not self.isFishing
        print("Fishing", ("started." if self.isFishing else "stopped."))

    def onQuitHotkey(self):
        self.stop()

app = App()
for arg in sys.argv:
    if arg == "-s":
        app.isSavingImage = True
app.start()