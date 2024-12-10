import numpy
from FishDetectorBase import *

class BrightSpotFishDetector(FishDetectorBase):
    brightnessThreshold = 220 # pixel brightness to be considered a bright spot
    brightSpotThreshold = 5 # number of bright spots to detect a fish

    initialBobberImage = None
    initialBobberBrightSpots = 0
    currentBobberImage = None
    currentBobberBrightSpots = 0

    # --------------------------------------------------------------------------
    def reset(self):
        self.initialBobberImage = None
        self.initialBobberBrightSpots = 0

    def update(self):
        self.currentBobberImage = self.captureBobberImage()
        self.currentBobberBrightSpots = self.getBrightSpotCount(self.currentBobberImage)
        if self.currentBobberBrightSpots > 0:
            print("Current bright spots: {0}".format(self.currentBobberBrightSpots))

    def isFishDetected(self):
        if self.initialBobberImage == None:
            return False        
        brightSpotDiff = self.currentBobberBrightSpots - self.initialBobberBrightSpots
        if brightSpotDiff > 0:
            print("Bright spot difference: {0}".format(brightSpotDiff))
        return brightSpotDiff >= self.brightSpotThreshold

    def setBobberPosition(self, x, y):
        super().setBobberPosition(x, y)
        self.initialBobberImage = self.captureBobberImage() 
        self.initialBobberBrightSpots = self.getBrightSpotCount(self.initialBobberImage)
        print("Initial bright spots: {0}".format(self.initialBobberBrightSpots))

    def getImages(self):
        return [
            [
                numpy.array(self.initialBobberImage), 
                numpy.array(self.currentBobberImage),
            ],
            [
                self.getImageMask(self.initialBobberImage),
                self.getImageMask(self.currentBobberImage),
            ],
        ]

    # --------------------------------------------------------------------------
    def isBrightSpot(self, r, g, b):
        return r+g+b >= self.brightnessThreshold*3
    
    def getBrightSpotCount(self, image):
        count = 0
        for x in range(0, image.size.width):
            for y in range(0, image.size.height):
                r, g, b = image.pixel(x, y)
                if self.isBrightSpot(r, g, b): 
                    count += 1
        return count        

    # --[ Helpers ]-------------------------------------------------------------
    def getImageMask(self, image):
        imageArray = numpy.array(image)
        for x in range(imageArray.shape[0]):
            for y in range(imageArray.shape[1]):
                r, g, b = imageArray[x, y][:3]
                if self.isBrightSpot(int(r), int(g), int(b)): 
                    imageArray[x, y] = [255, 255, 255, 255]
                else:
                    imageArray[x, y] = [0, 0, 0, 255]
        return imageArray

