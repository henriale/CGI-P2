import math
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import sys

ESCAPE = b'\x1b'

TEAPOTS = []
MIN_SCORE = 3
SCENARIO_SIZE = 60
CURRENT_SCORE = 0
CURRENT_LEVEL = 0
GAME_OVER = False

X_AXIS = 0.0
Z_AXIS = 0.0
Y_AXIS = 0.0

AVATAR_X = 0
AVATAR_Y = 1
AVATAR_Z = 0


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


def main():
    init_window(width=640, height=480)

    next_level()

    glutDisplayFunc(draw_scene)
    glutIdleFunc(draw_scene)

    glutKeyboardFunc(key_pressed)
    glutSpecialFunc(special_key_pressed)

    glutMainLoop()


def next_level():
    global TEAPOTS, CURRENT_SCORE, CURRENT_LEVEL

    CURRENT_SCORE = 0
    CURRENT_LEVEL = (CURRENT_LEVEL % 29) + 1

    file = open("./dataset/%02d.txt" % CURRENT_LEVEL)
    TEAPOTS = normalize_data_set(*read_data_set(file))


def init_window(width, height):
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_DEPTH)
    glutInitWindowSize(width, height)
    glutInitWindowPosition(200, 200)
    glutCreateWindow('CGI-P2')

    glClearColor(0.0, 0.0, 0.0, 0.0)
    glClearDepth(1.0)
    glDepthFunc(GL_LESS)
    glEnable(GL_DEPTH_TEST)
    glShadeModel(GL_SMOOTH)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45.0, float(width) / float(height), 0.1, 100.0)
    glMatrixMode(GL_MODELVIEW)


def key_pressed(*args):
    if args[0] == b'r':
        reset_game()
        next_level()

    if args[0] == ESCAPE:
        sys.exit()


def reset_game():
    global TEAPOTS, CURRENT_SCORE, CURRENT_LEVEL, GAME_OVER
    global AVATAR_X, AVATAR_Y, AVATAR_Z

    AVATAR_X = 0
    AVATAR_Y = 1
    AVATAR_Z = 0
    TEAPOTS = []
    GAME_OVER = False
    CURRENT_SCORE = 0
    CURRENT_LEVEL = 0


def special_key_pressed(*args):
    global AVATAR_X, AVATAR_Y, AVATAR_Z

    if args[0] == GLUT_KEY_LEFT:
        AVATAR_X += 1

    if args[0] == GLUT_KEY_RIGHT:
        AVATAR_X -= 1

    if args[0] == GLUT_KEY_UP:
        AVATAR_Z += 1

    if args[0] == GLUT_KEY_DOWN:
        AVATAR_Z -= 1

    glutPostRedisplay()


def draw_scene():
    global SCENARIO_SIZE
    global AVATAR_X, AVATAR_Z, AVATAR_Y

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    glLoadIdentity()
    gluLookAt(
        AVATAR_X - 20, 10, AVATAR_Z - 20,  # camera position
        AVATAR_X, 1, AVATAR_Z,  # target position
        0.0, 1.0, 0.0  # up vector
    )

    printText(AVATAR_X, AVATAR_Y + 1, AVATAR_Z, 'Teapots left: %d' % len(TEAPOTS))
    printText(AVATAR_X, AVATAR_Y + 2, AVATAR_Z, 'Score: %02d' % CURRENT_SCORE)
    printText(AVATAR_X, AVATAR_Y + 3, AVATAR_Z, 'Level: %02d' % CURRENT_LEVEL)

    draw_avatar(size=2)
    draw_teapots()
    draw_ground(sqm=1)

    glutSwapBuffers()


def draw_ground(sqm=10, size=None, color=None):
    global SCENARIO_SIZE

    if color is None:
        color = RGB(0.2, 0.1, 0.2)

    if size is None:
        size = SCENARIO_SIZE

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


def draw_teapots():
    global MIN_SCORE, CURRENT_SCORE, GAME_OVER
    global AVATAR_X, AVATAR_Z, TEAPOTS

    if not TEAPOTS:
        if CURRENT_SCORE < MIN_SCORE:
            GAME_OVER = True

        if GAME_OVER:
            printText(AVATAR_X, 5, AVATAR_Z, 'GAME OVER!')
            return
        else:
            next_level()

    if not TEAPOTS[0]:
        del TEAPOTS[0]
        return draw_teapots()

    (x, z) = TEAPOTS[0].pop()

    diff_x = AVATAR_X - x
    diff_z = AVATAR_Z - z

    if abs(diff_x) < 1 or abs(diff_z) < 1:
        CURRENT_SCORE += 1
        del TEAPOTS[0]

    draw_teapot(position=Vertex(x, 1, z), size=1)


def draw_avatar(size=2, position=None, color=None):
    global AVATAR_X, AVATAR_Y, AVATAR_Z
    half = size / 2

    if color is None:
        color = RGB(0.8, 0.3, 0.3)

    if position is None:
        position = Vertex(AVATAR_X, AVATAR_Y, AVATAR_Z)

    glPushMatrix()

    glTranslatef(position.x, position.y, position.z)
    glColor3f(color.r, color.g, color.b)
    glutSolidSphere(half, 5, 50, 50)

    glPopMatrix()


def draw_teapot(size=2, position=None, color=None):
    half = size / 2

    if color is None:
        color = RGB(0.2, 0.4, 0.6)

    if position is None:
        position = Vertex(0, half, 0)

    glPushMatrix()
    glTranslatef(position.x, position.y, position.z)
    glColor3f(color.r, color.g, color.b)
    glutSolidTeapot(half, 50, 50)
    glPopMatrix()


def normalize_data_set(data, max_x, max_z, min_x, min_z):
    global SCENARIO_SIZE
    ratio_x = (SCENARIO_SIZE - 0) / (max_x - min_x)
    ratio_z = (SCENARIO_SIZE - 0) / (max_z - min_z)

    normalized_items = list(map(
        lambda positions: list(map(
            lambda position: (
                position[0] * ratio_x - (ratio_x * min_x),
                position[1] * ratio_z - (ratio_z * min_z)
            ),
            positions
        )),
        data
    ))

    return normalized_items


def read_data_set(file):
    items = []
    max_x = 0
    max_z = 0
    min_x = math.inf
    min_z = math.inf

    for line in file.readlines()[1:]:
        [line_max, line] = line.split('\t', 1)

        positions = []
        for pos in line[1:-2].split(')('):
            [x, z, time] = map(float, pos.split(','))

            if x > max_x:
                max_x = x

            if z > max_z:
                max_z = z

            if x < min_x:
                min_x = x

            if z < min_z:
                min_z = z

            if (x, z) not in positions:
                positions.append((x, z))

        items.append(positions)

    return items, max_x, max_z, min_x, min_z


def printText(x, y, z, message):
    glColor3d(1, 1, 1)

    glRasterPos3d(x, y, z)
    for c in message:
        glutBitmapCharacter(globals()['GLUT_BITMAP_HELVETICA_18'], ord(c))


if __name__ == "__main__":
    main()
