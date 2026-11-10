from pico2d import load_image

# ---------------------------------------------------------------------------
# bird_animation.png (918 x 506) 스프라이트 시트 정보
#  - 5열 x 3행, 마지막 행은 4프레임 → 총 14프레임
#  - 가로 간격: 부리 끝 x 좌표가 179, 361, 543, 725, 907 로 정확히 182px 간격
#  - 세로 구간: 행 사이의 완전 투명 구간(144~215, 340~369)을 기준으로
#    행의 윗변(top)을 0 / 169 / 340 으로 잡음 (이미지 위쪽 기준 좌표)
#  - pico2d 의 clip_draw 는 이미지 '아래쪽' 기준 좌표를 쓰므로 bottom 으로 변환
# ---------------------------------------------------------------------------
PIXEL_PER_METER = (10.0 / 0.3)  # 10 pixel 30 cm
FRAMES_PER_ACTION = 14  # 날갯짓 1회를 구성하는 프레임 수

SHEET_H = 506
FRAME_W = 182
ROW_RECTS = [(0, 169), (169, 171), (340, 166)]  # (top, height), 이미지 위쪽 기준

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

    def __init__(self, x=800, y=400):
        if Bird.image is None:
            Bird.image = load_image('bird_animation.png')
        self.x, self.y = x, y
        self.frame = 0

    def update(self):
        pass

    def draw(self):
        left, bottom, w, h = FRAMES[int(self.frame)]
        Bird.image.clip_draw(left, bottom, w, h,
                             self.x, self.y, w * DRAW_SCALE, h * DRAW_SCALE)
