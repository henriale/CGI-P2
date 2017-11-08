import math
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import os
import sys
import time

ESCAPE = b'\x1b'

window = 0
scenario_size = 60
bullets = []
score = 0
elapsed_time = 0

# rotation
X_AXIS = 0.0
Z_AXIS = 0.0
Y_AXIS = 0.0

obs_x = 0
obs_y = 0
obs_z = 0

level = 0
game_over = False

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
    global window, elapsed_time

    next_level()

    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_DEPTH)
    glutInitWindowSize(640, 540)
    glutInitWindowPosition(200, 200)

    window = glutCreateWindow('CGI-P2')

    elapsed_time = glutGet(GLUT_ELAPSED_TIME)
    glutDisplayFunc(draw_scene)
    glutIdleFunc(draw_scene)
    glutKeyboardFunc(key_pressed)
    glutSpecialFunc(special_key_pressed)

    init(640, 480)
    glutMainLoop()


def next_level():
    global bullets, score, level

    score = 0
    level += 1

    file = open("./dataset/%02d.txt" % level)
    bullets = normalize_dataset(*read_dataset(file))


def init(width, height):
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
    global bullets,score,obs_x,obs_y,obs_z,level,game_over

    if args[0] == b'r':
        bullets = []
        score = 0
        obs_x = 0
        obs_y = 0
        obs_z = 0
        level = 0
        game_over = False
        next_level()

    if args[0] == ESCAPE:
        sys.exit()


def special_key_pressed(*args):
    global obs_x, obs_y, obs_z, X_AXIS, Z_AXIS, Y_AXIS

    if args[0] == GLUT_KEY_LEFT:
        #Y_AXIS = (Y_AXIS + 45) % 360
        obs_x += 1

    if args[0] == GLUT_KEY_RIGHT:
        #Y_AXIS = (Y_AXIS - 45) % 360
        obs_x -= 1

    if args[0] == GLUT_KEY_UP:
        obs_z += 1

    if args[0] == GLUT_KEY_DOWN:
        obs_z -= 1

    glutPostRedisplay()


def draw_scene():
    global scenario_size
    global elapsed_time
    global obs_x, obs_z
    global X_AXIS, Y_AXIS, Z_AXIS

    curr_time = glutGet(GLUT_ELAPSED_TIME)
    delta_time = curr_time - elapsed_time
    elapsed_time = curr_time

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    glLoadIdentity()
    glRotatef(-Y_AXIS, 0.0, 1.0, 0.0)
    gluLookAt(obs_x - 20, 10, obs_z - 20, obs_x, 1, obs_z, 0.0, 1.0, 0.0)

    printText(obs_x, 2, obs_z, 'Teapots left: %d' % len(bullets))
    printText(obs_x, 3, obs_z, 'Score: %s' % score)
    printText(obs_x, 4, obs_z, 'Level: %02d' % level)

    draw_main_character(position=Vertex(obs_x, 1, obs_z), size=2)

    draw_bullets()

    draw_ground(sqm=1, size=scenario_size)

    glutSwapBuffers()


def draw_ground(sqm=10, size=1000, color=None):
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


def draw_bullets():
    global bullets, score, obs_x, obs_z, game_over

    if not bullets:
        if score < 3:
            game_over = True

        if game_over:
            printText(obs_x, 5, obs_z, 'GAME OVER!')
            return
        else:
            next_level()

    if not bullets[0]:
        del bullets[0]
        return draw_bullets()

    (x, z) = bullets[0].pop()

    diffX = obs_x - x
    diffZ = obs_z - z

    if abs(diffX) < 1 or abs(diffZ) < 1:
        print(abs(diffX), abs(diffZ))
        score += 1
        del bullets[0]

    draw_bullet(position=Vertex(x, 1, z), size=1)


def draw_main_character(size=2, position=None, color=None):
    global X_AXIS, Z_AXIS, Y_AXIS
    half = size / 2

    if color is None:
        color = RGB(0.8, 0.3, 0.3)

    if position is None:
        position = Vertex(0, half, 0)

    glPushMatrix()

    glRotatef(Y_AXIS, 0.0, 1.0, 0.0)
    glTranslatef(position.x, position.y, position.z)
    glColor3f(color.r, color.g, color.b)
    glutSolidSphere(half, 5, 50, 50)

    glPopMatrix()


def draw_bullet(size=2, position=None, color=None):
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


def normalize_dataset(data, max_x, max_z, min_x, min_z):
    global scenario_size
    ratio_x = (scenario_size - 0) / (max_x - min_x)
    ratio_z = (scenario_size - 0) / (max_z - min_z)

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


def read_dataset(file):
    bxs = []
    max_x = 0
    max_z = 0
    min_x = math.inf
    min_z = math.inf
    for line in file.readlines()[1:]:
        [line_max, line] = line.split('\t', 1)

        moves = []
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

            if (x, z) not in moves:
                moves.append((x, z))

        bxs.append(moves)

    return bxs, max_x, max_z, min_x, min_z


def printText(x, y, z, message):
    glColor3d(1, 1, 1)

    glRasterPos3d(x, y, z)
    for c in message:
        glutBitmapCharacter(globals()['GLUT_BITMAP_HELVETICA_18'], ord(c))


if __name__ == "__main__":
    main()
