import cv2
import numpy as np
import random
import math as m

"""
painter using openCV
press c, l, r, s(curve), p(closed curve) to choose diagram to draw
press +, - to increse/decrese diagram's thickness
press <, > to go prev/next state
press f, e to choose fill or not
press q to quit
"""


class State:
    def __init__(self, src):
        self.__prev_src = []
        self.__next_src = []
        self.__src = src
        self.__tmp_src = src.copy()
        self.__diagram_vertex = []
        self.is_drawing = False
        self.selected_color = (0, 0, 0)
        self.diagram = "l"
        self.mouseBtn = None
        self.prev_event = 0
        self.prev_location = None
        self.start_location = None
        self.random_color = True
        self.fill = False
        self.thickness = 1

    def setThickness(self, key):
        cal = self.thickness
        if key == "-":
            cal -= 1
        else:
            cal += 1
        if cal <= 0:
            print("thickness must be positive!")
        else:
            self.thickness = cal

    def setColor(self):
        if self.random_color:
            self.selected_color = makeRandC()
        else:
            self.selected_color = (
                cv2.getTrackbarPos("B", "trackbar"),
                cv2.getTrackbarPos("G", "trackbar"),
                cv2.getTrackbarPos("R", "trackbar"),
            )

    def getSrc(self, where=None):
        if self.diagram in "sp" or self.is_drawing == False:
            return self.__src
        else:
            return self.__tmp_src

    def copySrc(self):
        self.__tmp_src = self.__src.copy()

    def drawSelected(self, location):
        t = self.thickness
        if self.fill:
            t = -1
        if self.diagram == "l":
            cv2.line(
                self.getSrc(),
                self.start_location,
                location,
                self.selected_color,
                self.thickness,
            )
        elif self.diagram == "r":
            cv2.rectangle(
                self.getSrc(), self.start_location, location, self.selected_color, t
            )
        elif self.diagram == "c":
            sx, sy = self.start_location
            lx, ly = location
            rad = m.sqrt((lx - sx) ** 2 + (ly - sy) ** 2)
            cv2.circle(
                self.getSrc(),
                self.start_location,
                int(rad),
                self.selected_color,
                t,
                cv2.LINE_AA,
            )
        elif self.diagram in "sp":
            if len(self.__diagram_vertex) != 0:
                cv2.line(
                    self.getSrc(),
                    self.__diagram_vertex[-1],
                    location,
                    self.selected_color,
                    self.thickness
                )
            self.__diagram_vertex.append(location)
        # elif self.diagram == ord("t"):
        #     cv2.putText

    def startDraw(self, mouse_event, start_location):
        self.mouseBtn = mouse_event
        self.setColor()
        self.start_location = start_location
        self.is_drawing = True
        self.copySrc()

    def finishDraw(self):
        self.__prev_src.append(self.__src)
        self.__next_src = []
        self.__src = self.__tmp_src
        if self.diagram == "p":
            cv2.line(
                    self.getSrc(),
                    self.__diagram_vertex[-1],
                    self.__diagram_vertex[0],
                    self.selected_color,
                    self.thickness
                )
        self.__diagram_vertex = []
        self.mouseBtn = None
        # self.diagram = None
        self.start_location = None
        self.is_drawing = False

    def goPrev(self):
        if len(self.__prev_src) == 0:
            print("there is no prev state!")
        else:
            self.__next_src.append(self.__src)
            self.__src = self.__prev_src.pop()

    def goNext(self):
        if len(self.__next_src) == 0:
            print("there is no next state!")
        else:
            self.__prev_src.append(self.__src)
            self.__src = self.__next_src.pop()


def makeRandC():
    randColor = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
    return randColor


def onMouse(event, x, y, flags, s):
    if s.prev_location != (x, y):
        if s.mouseBtn == cv2.EVENT_LBUTTONDOWN:
            s.copySrc()
            s.drawSelected((x, y))
        s.prev_location = (x, y)
    if s.prev_event != event:
        # print(event)
        s.prev_event = event
        if event == cv2.EVENT_LBUTTONDOWN:
            s.startDraw(event, (x, y))
        elif event == cv2.EVENT_LBUTTONUP:
            s.drawSelected((x, y))
            s.finishDraw()


def main():
    src = np.zeros((512, 512, 3), np.uint8)
    s = State(src)

    cv2.namedWindow("trackbar", cv2.WINDOW_AUTOSIZE)
    cv2.createTrackbar("B", "trackbar", 0, 255, lambda x: x)
    cv2.createTrackbar("G", "trackbar", 0, 255, lambda x: x)
    cv2.createTrackbar("R", "trackbar", 0, 255, lambda x: x)

    cv2.namedWindow("canvas", cv2.WINDOW_AUTOSIZE)
    cv2.setMouseCallback("canvas", onMouse, param=s)

    while True:
        cv2.imshow("canvas", s.getSrc("imshow"))
        key = cv2.waitKey(1)
        if key != -1:
            key = chr(key)
            if key in "lcrsp":
                s.diagram = key
                print("diagram is", key)
            elif key in "fe":
                s.fill = key == "f"
                print("fill type is", key)
            elif key in "=-":
                s.setThickness(key)
                print("thickness is", s.thickness)
            elif key == "t":
                s.random_color = not s.random_color
                print("random_color is", s.random_color)
            elif key == ",":
                s.goPrev()
            elif key == ".":
                s.goNext()
            elif key == "q":
                break
            # else:
            #     cv2.rectangle(s.getSrc(), (0, 300), (120, 440), (0,0,0), -1)
            #     cv2.putText(s.getSrc(), chr(key), (0, 400), cv2.FONT_ITALIC, 4, makeRandC(), 3)
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
