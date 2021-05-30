import turtle
import pickle
from playsound import playsound

class Player(turtle.Turtle):
    def __init__(self, screen_size, base_position):
        super().__init__()
        self.speed(0)
        self.shape('square')
        self.color('white')
        self.shapesize(stretch_wid=5, stretch_len=1)
        self.penup()
        self.goto(base_position, 0)

        self.score = 0
        self.SCREEN_THRESHOLD = screen_size[1] / 2 - 50

    def move(self, amount):
        y = self.ycor()
        y += amount

        if y > self.SCREEN_THRESHOLD:
            y = self.SCREEN_THRESHOLD

        if y < -self.SCREEN_THRESHOLD:
            y = -self.SCREEN_THRESHOLD
            
        self.sety(y)

    def move_up(self):
        self.move(20)

    def move_down(self):
        self.move(-20)

class Ball(turtle.Turtle):
    def __init__(self, screen_size, initial_speed=3):
        super().__init__()
        self.speed(0)
        self.shape('circle')
        self.color('red')
        self.penup()
        self.goto(0, 0)
        self.dx = initial_speed
        self.dy = -initial_speed

        self.INITIAL_SPEED = initial_speed
        self.SCREEN_THRESHOLD = screen_size[1] / 2 - 10

    def reset(self):
        self.goto(0, 0)
        self.dx = -self.INITIAL_SPEED if self.dx < 0 else self.INITIAL_SPEED
        self.dy = -self.INITIAL_SPEED if self.dy < 0 else self.INITIAL_SPEED

    def accelerate(self, amount):
        self.dx = self.dx - amount if self.dx < 0 else self.dx + amount
        self.dy = self.dy - amount if self.dy < 0 else self.dy + amount

    def update(self, server_mode=True):
        y = self.ycor() + self.dy

        if y > self.SCREEN_THRESHOLD:
            y = self.SCREEN_THRESHOLD
            self.dy *= -1
            playsound('wallsound_2.mp3', False)

        if y < -self.SCREEN_THRESHOLD:
            y = -self.SCREEN_THRESHOLD
            self.dy *= -1
            playsound('wallsound.mp3', False)

        if server_mode:
            self.setx(self.xcor() + self.dx)
            self.sety(y)

class Score(turtle.Turtle):
    def __init__(self, screen_size):
        super().__init__()
        self.speed(0)
        self.color('white')
        self.penup()
        self.hideturtle()
        self.goto(0, screen_size[1] / 2 - 50)

        self.update()

    def update(self, score1=0, score2=0):
        self.clear()
        self.write(f'{score1} 붂 │ 딲 {score2}', align='center', font=('맑은 고딕', 22, 'bold'))

class ServerData:
    def __init__(self, pos_server=None, pos_ball=None, winner=None):
        self.pos_server = pos_server
        self.pos_ball = pos_ball
        self.winner = winner

    def load(self, data):
        data = pickle.loads(data)
        self.pos_server = data['pos_server']
        self.pos_ball = data['pos_ball']
        self.winner = data['winner']

    def dump(self):
        data = {
            'pos_server': self.pos_server,
            'pos_ball': self.pos_ball,
            'winner': self.winner
        }
        return pickle.dumps(data)
