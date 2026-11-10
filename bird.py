import random

from pico2d import load_image, get_canvas_width

import game_framework

# ---------------------------------------------------------------------------
# Bird Fly Speed (boy.py 와 동일한 물리 단위 체계: 10 pixel = 30 cm)
# ---------------------------------------------------------------------------
PIXEL_PER_METER = (10.0 / 0.3)  # 10 pixel 30 cm
FLY_SPEED_KMPH = 20.0  # 기준 비행 속도 Km / Hour (개체별로 약간씩 변동)
FLY_SPEED_MPM = (FLY_SPEED_KMPH * 1000.0 / 60.0)
FLY_SPEED_MPS = (FLY_SPEED_MPM / 60.0)
FLY_SPEED_PPS = (FLY_SPEED_MPS * PIXEL_PER_METER)

# ---------------------------------------------------------------------------
# Bird Action Speed (날갯짓 1회 = 스프라이트 14프레임 1사이클)
# ---------------------------------------------------------------------------
TIME_PER_ACTION = 0.5  # 날갯짓 1회에 걸리는 시간(초)
ACTION_PER_TIME = 1.0 / TIME_PER_ACTION  # 초당 날갯짓 횟수
FRAMES_PER_ACTION = 14  # 날갯짓 1회를 구성하는 프레임 수
FRAMES_PER_SECOND = FRAMES_PER_ACTION * ACTION_PER_TIME

# ---------------------------------------------------------------------------
# bird_animation.png (918 x 506) 스프라이트 시트 정보
#  - 5열 x 3행, 마지막 행은 4프레임 → 총 14프레임
#  - 가로 간격: 부리 끝 x 좌표가 179, 361, 543, 725, 907 로 정확히 182px 간격
#  - 세로 구간: 행 사이의 완전 투명 구간(144~215, 340~369)을 기준으로
#    행의 윗변(top)을 0 / 169 / 340 으로 잡음 (이미지 위쪽 기준 좌표)
#    → 각 셀의 top 에서 부리까지의 거리가 프레임 순서대로
#      103→95 / 95→97 / 100→103 으로 이어져 행이 바뀔 때 몸통이 튀지 않음
#  - pico2d 의 clip_draw 는 이미지 '아래쪽' 기준 좌표를 쓰므로 bottom 으로 변환
# ---------------------------------------------------------------------------
SHEET_H = 506
FRAME_W = 182
ROW_RECTS = [(0, 169), (169, 171), (340, 166)]  # (top, height), 이미지 위쪽 기준
REF_H = ROW_RECTS[0][1]  # 화면 배치 기준 높이

# 프레임 번호 → (left, bottom, width, height)  (pico2d clip 좌표계)
FRAMES = []
for _row, (_top, _h) in enumerate(ROW_RECTS):
    for _col in range(5):
        if len(FRAMES) == FRAMES_PER_ACTION:
            break
        FRAMES.append((_col * FRAME_W, SHEET_H - _top - _h, FRAME_W, _h))

# 화면에 그릴 크기: 날개 끝까지 포함한 프레임 폭을 약 2m 로 표현
BIRD_SIZE_M = 2.0
DRAW_SCALE = BIRD_SIZE_M * PIXEL_PER_METER / FRAME_W


class Bird:
    image = None

    def __init__(self, x=None, y=None):
        if Bird.image is None:
            Bird.image = load_image('bird_animation.png')  # 10마리가 텍스처 1개를 공유

        self.half_w = FRAME_W * DRAW_SCALE / 2
        self.x = x if x is not None else random.uniform(
            self.half_w, get_canvas_width() - self.half_w)
        self.y = y if y is not None else random.uniform(300, 550)

        # 새마다 시작 프레임 / 속도 / 날갯짓 빠르기 / 방향을 다르게 해 자연스러운 새떼 표현
        self.frame = random.uniform(0, FRAMES_PER_ACTION)
        self.speed = FLY_SPEED_PPS * random.uniform(0.8, 1.2)
        self.fps = FRAMES_PER_SECOND * random.uniform(0.9, 1.1)
        self.dir = random.choice([-1, 1])

    def update(self):
        dt = game_framework.frame_time
        self.frame = (self.frame + self.fps * dt) % FRAMES_PER_ACTION
        self.x += self.dir * self.speed * dt

        # 화면 좌우 끝에 닿으면 방향 전환 → 좌우 반복 비행
        right_limit = get_canvas_width() - self.half_w
        if self.x > right_limit:
            self.x = right_limit
            self.dir = -1
        elif self.x < self.half_w:
            self.x = self.half_w
            self.dir = 1

    def draw(self):
        left, bottom, w, h = FRAMES[int(self.frame)]
        # 행마다 셀 높이가 다르므로 셀 윗변을 같은 화면 위치에 맞춰 몸통 떨림 방지
        draw_y = self.y + (REF_H - h) * DRAW_SCALE / 2
        # 원본 스프라이트는 오른쪽을 바라봄 → 왼쪽 비행 시 좌우 반전
        flip = '' if self.dir == 1 else 'h'
        Bird.image.clip_composite_draw(left, bottom, w, h, 0, flip,
                                       self.x, draw_y, w * DRAW_SCALE, h * DRAW_SCALE)
