import math
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import os
import sys

ESCAPE = b'\x1b'

window = 0

boxes = []

# rotation
X_AXIS = 0.0
Y_AXIS = 0.0
Z_AXIS = 0.0

# camera
OBS_X = 0.0
OBS_Y = 0.0
OBS_Z = 0.0

DIRECTION = 1


class Vertex:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z


class RGB:
    def __init__(self, r, g, b):
        self.r = r
        self.g = g
        self.b = b


def InitGL(Width, Height):
    glClearColor(0.0, 0.0, 0.0, 0.0)
    glClearDepth(1.0)
    glDepthFunc(GL_LESS)
    glEnable(GL_DEPTH_TEST)
    glShadeModel(GL_SMOOTH)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45.0, float(Width) / float(Height), 0.1, 100.0)
    glMatrixMode(GL_MODELVIEW)


def keyPressed(*args):
    if args[0] == ESCAPE:
        sys.exit()


def specialKeyPressed(*args):
    global OBS_X, OBS_Y, OBS_Z

    if args[0] == GLUT_KEY_LEFT:
        OBS_X += 5

    if args[0] == GLUT_KEY_RIGHT:
        OBS_X -= 5

    if args[0] == GLUT_KEY_UP:
        OBS_Z += 5

    if args[0] == GLUT_KEY_DOWN:
        OBS_Z -= 5

    glutPostRedisplay()


def drawBoxes():
    i = 0

    if not boxes or not boxes[i]:
        return

    (x, z) = boxes[0].pop()
    print(x, z)
    drawCube(position=Vertex(x, 1, z), size=10)
    pass


def DrawGLScene():
    global X_AXIS, Y_AXIS, Z_AXIS
    global OBS_X, OBS_Y, OBS_Z
    global DIRECTION

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    glLoadIdentity()
    glTranslatef(0.0, -10.0, -60.0)

    glRotatef(X_AXIS, 1.0, 0.0, 0.0)
    glRotatef(Y_AXIS, 0.0, 1.0, 0.0)
    glRotatef(Z_AXIS, 0.0, 0.0, 1.0)

    gluLookAt(OBS_X, 1, OBS_Z, OBS_X, 1, OBS_Z + 1, 0.0, 1.0, 0.0)

    glPushMatrix()
    drawCube(position=Vertex(2, 1, 2), size=2)
    glPopMatrix()

    drawBoxes()


    drawGround(sqm=1)

    glutSwapBuffers()


def drawGround(sqm=10, size=1000, color=None):
    if color is None:
        color = RGB(0.2, 0.1, 0.2)

    glColor3f(color.r, color.g, color.b)
    glLineWidth(2)
    glBegin(GL_LINES)

    for z in range(0, size, sqm):
        glVertex3f(0, -0.01, z)
        glVertex3f(size, -0.01, z)

    for x in range(0, size, sqm):
        glVertex3f(x, -0.01, 0)
        glVertex3f(x, -0.01, size)

    glEnd()
    glLineWidth(1)


def drawCube(size=2, position=None, color=None):
    half = size / 2

    if color is None:
        color = RGB(0.2, 0.4, 0.6)

    if position is None:
        position = Vertex(0, half, 0)

    glBegin(GL_QUADS)
    glColor3f(color.r, color.g, color.b)
    glVertex3f(position.x + half, position.y + half, position.z - half)
    glVertex3f(position.x - half, position.y + half, position.z - half)
    glVertex3f(position.x - half, position.y + half, position.z + half)
    glVertex3f(position.x + half, position.y + half, position.z + half)
    # side
    glVertex3f(position.x + half, position.y - half, position.z + half)
    glVertex3f(position.x - half, position.y - half, position.z + half)
    glVertex3f(position.x - half, position.y - half, position.z - half)
    glVertex3f(position.x + half, position.y - half, position.z - half)
    # side
    glVertex3f(position.x + half, position.y + half, position.z + half)
    glVertex3f(position.x - half, position.y + half, position.z + half)
    glVertex3f(position.x - half, position.y - half, position.z + half)
    glVertex3f(position.x + half, position.y - half, position.z + half)
    # side
    glVertex3f(position.x + half, position.y - half, position.z - half)
    glVertex3f(position.x - half, position.y - half, position.z - half)
    glVertex3f(position.x - half, position.y + half, position.z - half)
    glVertex3f(position.x + half, position.y + half, position.z - half)
    # side
    glVertex3f(position.x - half, position.y + half, position.z + half)
    glVertex3f(position.x - half, position.y + half, position.z - half)
    glVertex3f(position.x - half, position.y - half, position.z - half)
    glVertex3f(position.x - half, position.y - half, position.z + half)
    # side
    glVertex3f(position.x + half, position.y + half, position.z - half)
    glVertex3f(position.x + half, position.y + half, position.z + half)
    glVertex3f(position.x + half, position.y - half, position.z + half)
    glVertex3f(position.x + half, position.y - half, position.z - half)
    glEnd()


# TODO
def normalize_dataset(bxs, max_x, max_y, min_x, min_y):
    # print(bxs, max_x, max_y, min_x, min_y)

    # print(len(bxs))
    # sys.exit(1)

    return bxs


def main():
    global window

    file = open("./dataset/BR-01.txt")

    moves = normalize_dataset(*read_dataset(file))

    boxes.append(moves)

    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_DEPTH)
    glutInitWindowSize(640, 540)
    glutInitWindowPosition(200, 200)

    window = glutCreateWindow('CGI-P2')

    glutDisplayFunc(DrawGLScene)
    glutIdleFunc(DrawGLScene)
    glutKeyboardFunc(keyPressed)
    glutSpecialFunc(specialKeyPressed)
    InitGL(640, 480)
    glutMainLoop()


def read_dataset(file):
    bxs = []
    max_x = 0
    max_y = 0
    min_x = math.inf
    min_y = math.inf
    for line in file.readlines()[1:]:
        [line_max, line] = line.split('\t', 1)

        for pos in line[1:-2].split(')('):
            [x, y, time] = map(int, pos.split(','))

            if x > max_x:
                max_x = x

            if y > max_y:
                max_y = y

            if x < min_x:
                min_x = x

            if y < min_y:
                min_y = y

            moves = []
            if (x, y) not in moves:
                moves.append((x, y))

            bxs.append(*moves)

    return bxs, max_x, max_y, min_x, min_y


def printText(x, y, message):
    glDisable(GL_TEXTURE_2D)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0.0, 640, 0.0, 480)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    glRasterPos2i(10, 10)

    for c in message:
        glColor3d(1.0, 0.0, 0.0)
        var = fonts.name
        # glutBitmapCharacter(GLUT_BITMAP_9_BY_15, c)

    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
    glPopMatrix()
    glEnable(GL_TEXTURE_2D)


if __name__ == "__main__":
    main()
