import ctypes
import PIL.Image
import PIL.ImageDraw
import time
from os import getcwd
from random import randint

SPI_SETDESKWALLPAPER = 0x14
SPIF_UPDATEINIFILE   = 0x2



#finding the path for the pictures
# myPath = __file__.split("/")
# print("".join([part + "\\" if part != "background.py" else "" for part in myPath]) + "pictures")
# picDir = "".join([part + "\\" if part != "background.py" else "" for part in myPath]) + "pictures"
# print(picDir)
picDir = getcwd() + "\\pictures"
print(picDir)
print(len(picDir))
img = PIL.Image.new("RGB", (1920, 1080), (0, 0, 0))

class POINT(ctypes.Structure):
    _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]


def queryMousePosition():
    pt = POINT()
    ctypes.windll.user32.GetCursorPos(ctypes.byref(pt))
    return { "x": pt.x, "y": pt.y}


def getForegroundWindowTitle():
    hWnd = ctypes.windll.user32.GetForegroundWindow()
    length = ctypes.windll.user32.GetWindowTextLengthW(hWnd)
    buf = ctypes.create_unicode_buffer(length + 1)
    ctypes.windll.user32.GetWindowTextW(hWnd, buf, length + 1)
    # 1-liner alternative: return buf.value if buf.value else None
    if buf.value:
        return buf.value
    else:
        return None


class SnekGame:
    def __init__(self, dimensions, cellsize):
        #stores the x,y of the head as well as directions
        #    2
        # 3<   >1
        #    0
        self.dead = False
        self.board = [[-1 for _ in range(dimensions[1])] for _ in range(dimensions[0])]
        self.cellsize = cellsize
        self.head = [int(dimensions[0]/2), int(dimensions[1]/2), 1]
        self.board[self.head[0]][self.head[1]] = 0
        self.length = 3
        self.score = 0

    def update(self, direction, draw):
        if not self.dead:
            self.ageSnek()
            self.moveSnek(direction)
            self.makeFood()
            self.drawSnek(draw)
        else:
            self.length = 3
            self.board = [[-1 for _ in self.board[0]] for _ in self.board]
            self.head[0] = int(len(self.board)/2)
            self.head[1] = int(len(self.board[0])/2)
            self.dead = False


    def getDirectionFromPt(self, pt):
        headPos = [self.head[0] * self.cellsize + (1/2 * self.cellsize), self.head[1] * self.cellsize + (1/2 * self.cellsize)]
        try:
            slope = (headPos[1] - pt[1])/(headPos[0] - pt[0])
        except ZeroDivisionError:
            slope = 100 if headPos[1] > pt [1] else -100 
        
        if self.head[2] == 0:
            if abs(slope) > 1:
                return 0 
            else:
                if pt[0] > headPos[0]:
                    return 1
                else:
                    return 2
        elif self.head[2] == 2:
            if abs(slope) > 1:
                return 0 
            else:
                if pt[0] > headPos[0]:
                    return 2
                else:
                    return 1
        elif self.head[2] == 1:
            if abs(slope) < 1:
                return 0 
            else:
                if headPos[1] > pt[1]:
                    return 1
                else:
                    return 2
        elif self.head[2] == 3:
            if abs(slope) < 1:
                return 0 
            else:
                if headPos[1] > pt[1]:
                    return 2
                else:
                    return 1


    def makeFood(self):
        foodExists = False
        for row in self.board:
            for cell in row:
                if cell == -2:
                    foodExists = True
        if not foodExists:
            self.board[randint(0,len(self.board) - 1)][randint(0,len(self.board[0]) - 1)] = -2


    def moveSnek(self, direction):
        #directions are 0,1,2
        #     0
        # 1 ↰   ↱ 2
        #relative to the snake's forward direction 
        if direction == 1:
            self.head[2] = (self.head[2] + 1) % 4
        elif direction == 2:
            self.head[2] = (self.head[2] - 1) % 4
        if self.head[2] == 0:
            self.head[1] += 1
        elif self.head[2] == 1:
            self.head[0] += 1
        elif self.head[2] == 2:
            self.head[1] -= 1
        elif self.head[2] == 3:
            self.head[0] -= 1
        if self.head[0] <  0 or self.head[1] < 0 or self.head[0] >= len(self.board) or self.head[1] >= len(self.board[0]):
            self.dead = True
        elif self.board[self.head[0]][self.head[1]] >= 0:
            self.dead = True
        else:
            if self.board[self.head[0]][self.head[1]] == -2:
                self.length += 1
            self.board[self.head[0]][self.head[1]] = 0
    
    
    def ageSnek(self):
        #increments a cell's score by one if it is part of the snake then kills off any cells that are two old
        for ii in range(len(self.board)):
            for jj in range(len(self.board[ii])):
                cell = self.board[ii][jj]
                if cell > -1:
                    self.board[ii][jj] += 1
                    if cell > self.length:
                        self.board[ii][jj] = -1


    
    def drawSnek(self, draw):
        draw.rectangle([0, 0, 1919, 1079], (0,0,0))
        for ii in range(len(self.board)):
            for jj in range(len(self.board[ii])):
                if self.board[ii][jj] == 0:
                    color = (0, 255, 0)
                elif self.board[ii][jj] > 0:
                    color = (150, 255, 0)
                elif self.board[ii][jj] == -2:
                    color = (255, 0, 0)
                else:
                    color = (0, 0, 0)
                draw.rectangle([ii * self.cellsize, jj * self.cellsize, (ii + 1)* self.cellsize, (jj + 1) * self.cellsize], color)

draw = PIL.ImageDraw.Draw(img)
draw.rectangle([0, 0, 1919, 1079], (0,0,0))
img.save("pictures\\1.png")
game = SnekGame([48, 27], 40)
prev = None
i = 0
buf = ctypes.create_unicode_buffer(100)
while True:
    win = getForegroundWindowTitle()
    #Only go through extra code if there is a change in windows.
    if win != prev or win == "Program Manager" or win == None:
        time.sleep(0.1)
        prev = win
        while win == "Program Manager" or win == None:
            time.sleep(0.5)
            win = getForegroundWindowTitle()
            print(win)
            
            i += 1
            i = i % 2
            mousePos = queryMousePosition()
            inputDirection = game.getDirectionFromPt([mousePos["x"],mousePos["y"]])
            game.update(inputDirection, draw)
            #draw.ellipse([mousePos["x"] - 10, mousePos["y"] - 10, mousePos["x"] + 10, mousePos["y"] + 10])
            img.save("pictures\\%i.png" %(i))
            print(ctypes.windll.user32.SystemParametersInfoW(SPI_SETDESKWALLPAPER, 0, picDir + "\\%i.png" %(i), SPIF_UPDATEINIFILE))
        else:
            #checks if the current background img is the default img, if it is not it makes the 
            ctypes.windll.user32.SystemParametersInfoW(0x0073, 100, buf, SPIF_UPDATEINIFILE)
            if buf.value != picDir + "\\default.jpg":
                ctypes.windll.user32.SystemParametersInfoW(SPI_SETDESKWALLPAPER, 0, picDir + "\\default.jpg", SPIF_UPDATEINIFILE)
            time.sleep(1)