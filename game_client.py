import os
import sys
import time
import pickle
import pygame
from socket import *
from playsound import playsound

from Models import *

if __name__ == '__main__':
    host = input('서버 IP를 입력 해주세요: ')
    # Socket Server
    try:
        connect = socket(AF_INET, SOCK_STREAM)
        connect.connect((host, 8080))
    except:
        print('서버에 접속할 수 없습니다!')
        os.system('Pause')
        sys.exit(1)

    data = connect.recv(128)
    server_data = pickle.loads(data)

    SCREEN_SIZE = server_data['screen_size']

    SCREEN_THRESHOLD = SCREEN_SIZE[0] / 2 - 10
    PADDLE_POSITION_BASE = SCREEN_THRESHOLD - 40

    # Screen
    wn = turtle.Screen()
    wn.title('BOOK_DDAK (Client mode)')
    wn.bgcolor('black')
    wn.setup(width=SCREEN_SIZE[0], height=SCREEN_SIZE[1])
    wn.tracer(0)

    # Ball
    ball = Ball(SCREEN_SIZE)

    # Score Board
    score = Score(SCREEN_SIZE)

    # Player
    player1 = Player(SCREEN_SIZE, -PADDLE_POSITION_BASE)
    player2 = Player(SCREEN_SIZE, PADDLE_POSITION_BASE)

    # Listner
    def motion(event):
        y = event.y
        player2.sety(-(y - SCREEN_SIZE[1] / 2))

    canvas = wn.getcanvas()
    canvas.bind('<Motion>', motion)

    # Round Controller
    def round_ended(winner):
        winner.score += 1
        score.update(player1.score, player2.score)
        playsound('clear.mp3', False)

    def round_continue():
        playsound('startsound.mp3', False)

    pygame.mixer.music.load('bgmusic.mp3')
    pygame.mixer.Sound.set_volume(0.2)
    pygame.mixer.music.play(-1)

    while True:
        wn.update()
        ball.update(server_mode=False)

        try:
            payload = pickle.dumps({ 'position_player2': player2.ycor() })
            connect.send(payload)

            data = connect.recv(512)
            server_data = ServerData()
            server_data.load(data)

            player1.sety(server_data.pos_server)
            ball.setx(server_data.pos_ball[0])
            ball.sety(server_data.pos_ball[1])

            if server_data.winner is not None:
                if server_data.winner is False:
                    round_continue()
                else:
                    if server_data.winner == 1:
                        round_ended(player1)

                    if server_data.winner == 2:
                        round_ended(player2)
        except Exception as ex:
            print(f'오류가 발생했습니다: {ex}')
            wn.bye()
            os.system('Pause')
            sys.exit(1)