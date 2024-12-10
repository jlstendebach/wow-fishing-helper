import mss.tools

class FishDetectorBase:
    bobberX = 0
    bobberY = 0
    bobberWidth = 50
    bobberHeight = 75

    # --------------------------------------------------------------------------
    def reset(self):
        raise NotImplementedError("'reset' not implemented")

    def update(self):
        raise NotImplementedError("'update' not implemented")

    def isFishDetected(self):
        raise NotImplementedError("'isFishDetected' not implemented")

    def setBobberPosition(self, x, y):
        self.bobberX = x
        self.bobberY = y

    def getImages(self):
        # Expects a 2D array of images
        raise NotImplementedError("'getImages' not implemented")

    # --[ Tools ]---------------------------------------------------------------
    def captureBobberImage(self): 
        with mss.mss() as sct:
            monitorNumber = 1
            monitor = sct.monitors[monitorNumber]
            area = {
                "top": int(monitor["top"] + int(self.bobberY - self.bobberHeight/2)),  
                "left": int(monitor["left"] + int(self.bobberX - self.bobberWidth/2)), 
                "width": self.bobberWidth,
                "height": self.bobberHeight,
                "mon": monitorNumber,
            }
            return sct.grab(area)


    
