import sys
import pygame
from pygame.locals import DOUBLEBUF, OPENGL
from OpenGL.GL  import (glClear, glLoadIdentity, glColor3f, glBegin, glEnd,
                         glVertex2f, glLineWidth, GL_COLOR_BUFFER_BIT,
                         GL_LINES, GL_LINE_STRIP, GL_QUADS)
from OpenGL.GLU import gluOrtho2D


POPULATION       = 1000.0
INITIAL_INFECTED = 1.0
CONTACT_RATE     = 4.0    
TRANSMISSION     = 0.5    
DURATION         = 28.0   
RECOVERY_RATE    = 0.701 / DURATION   
DEATH_RATE       = 0.02  / DURATION   
SIM_DAYS         = 100


WIN_W, WIN_H  = 900, 600
FPS           = 60
STEP_DELAY_MS = 50


X_MIN, X_MAX = 0, SIM_DAYS
Y_MIN, Y_MAX = 0, POPULATION


C_BG   = (0.12, 0.12, 0.12)   
C_GRID = (0.25, 0.25, 0.25)   
C_AXES = (0.85, 0.85, 0.85)   
C_LINE = (0.75, 0.10, 0.10)   



class SISModel:

    def __init__(self) -> None:
        self.N = POPULATION
        self.W = INITIAL_INFECTED
        self.history: list[tuple[float, float]] = [(0.0, self.W)]

    def step(self, day: int) -> float:
        new_cases  = (self.N * TRANSMISSION) * CONTACT_RATE * (self.W / self.N) * ((self.N - self.W) / self.N)
        self.W     = max(0.0, self.W + new_cases - RECOVERY_RATE * self.W - DEATH_RATE * self.W)
        self.N     = max(0.0, self.N - DEATH_RATE * self.W)
        self.history.append((float(day), self.W))
        return self.W

    @property
    def peak(self) -> float:
        return max(w for _, w in self.history)



def draw_background() -> None:
    glColor3f(*C_BG)
    glBegin(GL_QUADS)
    for x, y in [(X_MIN, Y_MIN), (X_MAX, Y_MIN), (X_MAX, Y_MAX), (X_MIN, Y_MAX)]:
        glVertex2f(x, y)
    glEnd()


def draw_grid(x_steps: int = 10, y_steps: int = 5) -> None:
    glColor3f(*C_GRID)
    glLineWidth(1.0)
    glBegin(GL_LINES)
    for i in range(1, x_steps):
        x = X_MIN + i * (X_MAX - X_MIN) / x_steps
        glVertex2f(x, Y_MIN); glVertex2f(x, Y_MAX)
    for i in range(1, y_steps):
        y = Y_MIN + i * (Y_MAX - Y_MIN) / y_steps
        glVertex2f(X_MIN, y); glVertex2f(X_MAX, y)
    glEnd()


def draw_axes() -> None:
    glColor3f(*C_AXES)
    glLineWidth(2.0)
    glBegin(GL_LINES)
    glVertex2f(X_MIN, Y_MIN); glVertex2f(X_MAX, Y_MIN)  # X axis
    glVertex2f(X_MIN, Y_MIN); glVertex2f(X_MIN, Y_MAX)  # Y axis
    glEnd()


def draw_curve(history: list[tuple[float, float]]) -> None:
    if len(history) < 2:
        return
    glColor3f(*C_LINE)
    glLineWidth(2.5)
    glBegin(GL_LINE_STRIP)
    for day, infected in history:
        glVertex2f(day, infected)
    glEnd()


def render(model: SISModel) -> None:
    glClear(GL_COLOR_BUFFER_BIT)
    glLoadIdentity()
    gluOrtho2D(X_MIN, X_MAX, Y_MIN, Y_MAX)
    draw_background()
    draw_grid()
    draw_axes()
    draw_curve(model.history)
    pygame.display.flip()



def main() -> None:
    pygame.init()
    pygame.display.set_mode((WIN_W, WIN_H), DOUBLEBUF | OPENGL)
    pygame.display.set_caption("SIS Epidemic Simulation")
    clock = pygame.time.Clock()
    model = SISModel()

    print(f"[INFO] SIS simulation started — N={int(POPULATION)}, days={SIM_DAYS}")

    day, running = 0, True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        if day < SIM_DAYS:
            day += 1
            model.step(day)
            pygame.time.wait(STEP_DELAY_MS)
            if day == SIM_DAYS:
                print(f"[INFO] Done. Peak infected: {model.peak:.1f}")

        render(model)
        clock.tick(FPS)

    pygame.quit()
    sys.exit(0)


if __name__ == "__main__":
    main()
