import os
import sys
import time
import pickle
import pygame
from playsound import playsound

from socket import *
from requests import get

from Models import * 

def input_config(title, default_value):
    config = input(f'{title} (기본값 {default_value}): ')
    if not config.replace('.', '', 1).isdigit():
        print('올바른 값을 입력 해주세요. 기본값으로 설정 되었습니다.')
        config = default_value
    else:
        config = float(config)

    return config

if __name__ == '__main__':
    FPS = 240
    time_delta = 1.0 / FPS

    # Setup
    SCREEN_SIZE_W = input_config('화면 너비', 960)
    SCREEN_SIZE_H = input_config('화면 높이', 540)
    BALL_INITIAL_SPEED = input_config('공 시작 속력', 2.5)
    BALL_ACCELERATE_AMOUNT = input_config('가속량', 0.2)

    SCREEN_SIZE = (SCREEN_SIZE_W, SCREEN_SIZE_H)

    SCREEN_THRESHOLD = SCREEN_SIZE[0] / 2 - 10
    PADDLE_POSITION_BASE = SCREEN_THRESHOLD - 40

    # Socket Server
    server = socket(AF_INET, SOCK_STREAM)
    server.bind(('', 8080))
    server.listen(1)

    external_ip = get('https://api.ipify.org').text
    print(f'연결을 기다리는 중... (IP: {external_ip})')

    connect, addr = server.accept()

    print(f'연결되었습니다 - {addr[0]}')

    payload = pickle.dumps({ 'screen_size': SCREEN_SIZE })
    connect.send(payload)

    # Screen
    wn = turtle.Screen()
    wn.title('BOOK_DDAK (Server mode)')
    wn.bgcolor('black')
    wn.setup(width=SCREEN_SIZE[0], height=SCREEN_SIZE[1])
    wn.tracer(0)

    # Ball
    ball = Ball(SCREEN_SIZE, BALL_INITIAL_SPEED)

    # Score Board
    score = Score(SCREEN_SIZE)

    # Player
    player1 = Player(SCREEN_SIZE, -PADDLE_POSITION_BASE)
    player2 = Player(SCREEN_SIZE, PADDLE_POSITION_BASE)

    # Listner
    def motion(event):
        y = event.y
        player1.sety(-(y - SCREEN_SIZE[1] / 2))

    canvas = wn.getcanvas()
    canvas.bind('<Motion>', motion)

    # Round Controller
    def round_ended(winner):
        winner.score += 1
        score.update(player1.score, player2.score)
        ball.dx *= -1
        playsound('clear.mp3', False)

    def round_continue():
        ball.dx *= -1
        ball.accelerate(BALL_ACCELERATE_AMOUNT)
        playsound('startsound.mp3', False)

    # Wait for ready
    time.sleep(2)

    pygame.mixer.music.load('bgmusic.mp3')
    pygame.mixer.Sound.set_volume(0.2)
    pygame.mixer.music.play(-1)

    while True:
        wn.update()
        ball.update()

        try:
            data = connect.recv(128)
            client_data = pickle.loads(data)

            player2.sety(client_data['position_player2'])

            winner = None
                
            if ball.xcor() > SCREEN_THRESHOLD:
                winner = 1
                round_ended(player1)

            if ball.xcor() < -SCREEN_THRESHOLD:
                winner = 2
                round_ended(player2)

            if ((ball.xcor() > PADDLE_POSITION_BASE - 10) and (ball.xcor() < PADDLE_POSITION_BASE) and
               (ball.ycor() < player2.ycor() + 50 and ball.ycor() > player2.ycor() - 50)):
                round_continue()
                winner = False

            if ((ball.xcor() < -(PADDLE_POSITION_BASE - 10)) and (ball.xcor() > -PADDLE_POSITION_BASE) and
               (ball.ycor() < player1.ycor() + 50 and ball.ycor() > player1.ycor() - 50)):
                round_continue()
                winner = False

            payload = ServerData(pos_server=player1.ycor(), pos_ball=(ball.xcor(), ball.ycor()), winner=winner)
            connect.send(payload.dump())

            if winner is not None and winner is not False:
                time.sleep(1.5)
                ball.reset()
        except Exception as ex:
            print(f'오류가 발생했습니다: {ex}')
            wn.bye()
            os.system('Pause')
            sys.exit(1)
        
        time.sleep(time_delta)