import os
import random
import sys
import time
import pygame as pg


WIDTH, HEIGHT = 1100, 650
DELTA = {
    pg.K_UP: (0, -5),
    pg.K_DOWN: (0, +5),
    pg.K_LEFT: (-5, 0),
    pg.K_RIGHT: (+5, 0),
}
os.chdir(os.path.dirname(os.path.abspath(__file__)))


def check_bound(rct: pg.Rect) -> tuple[bool, bool]:
    """
    引数で与えられたRectが画面の中か外かを判定する
    引数：こうかとんRect or 爆弾Rect
    戻り値：真理値タプル（横，縦）／画面内：True，画面外：False
    """
    yoko, tate = True, True
    if rct.left < 0 or WIDTH < rct.right:
        yoko = False
    if rct.top < 0 or HEIGHT < rct.bottom:
        tate = False
    return yoko, tate

def  gameover(screen: pg.Surface) -> None:
    black_rect = pg.Surface((WIDTH, HEIGHT))  # 画面全体サイズ
    black_rect.set_alpha(200)  # 半透明
    black_rect.fill((0, 0, 0))  # 黒色で塗りつぶし
    screen.blit(black_rect, (0, 0))  # 背景を画面に描画

    # テキストを作成して表示
    font = pg.font.Font(None, 80)  # フォントを指定
    text = font.render("GAME OVER", True, (255, 255, 255))  # テキスト作成
    text_rct = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))  # 中央に配置
    screen.blit(text, text_rct)

    # 泣いているこうかとん画像を読み込む
    cry_img = pg.image.load("fig/8.png")
    cry_rct_left = cry_img.get_rect()
    cry_rct_left.center = ((WIDTH/2)-200, HEIGHT // 2)  # 左に配置
    screen.blit(cry_img, cry_rct_left)
    cry_rct_right = cry_img.get_rect()
    cry_rct_right.center = ((WIDTH/2)+200, HEIGHT // 2)  # 右に配置
    screen.blit(cry_img, cry_rct_right)

    pg.display.update()
    time.sleep(5) 

def init_bb_imgs() -> tuple[list[pg.Surface], list[int]]:
    bb_imgs = []  # 爆弾Surfaceリスト
    bb_accs = [a for a in range(1, 11)]  # 加速度リスト
    for r in range(1, 11):
        bb_img = pg.Surface((20 * r, 20 * r), pg.SRCALPHA)  # 透明なSurface
        pg.draw.circle(bb_img, (255, 0, 0), (10 * r, 10 * r), 10 * r)  # 爆弾を描画
        bb_imgs.append(bb_img)
    return bb_imgs, bb_accs

def prepare_koukaton_images() -> dict[tuple[int, int], pg.Surface]:
    kk_img = pg.image.load("fig/3.png")  # 基本のこうかとん画像を読み込む
    kk_img = pg.transform.flip(kk_img, True, False)
    kk_imgs = {}

    # 初期の右向き画像を基準に回転
    directions = [
        (-5, -5), (0, -5), (+5, -5),  # 上方向
        (-5,  0), (0,  0), (+5,  0),  # 水平方向
        (-5, +5), (0, +5), (+5, +5)   # 下方向
    ]
    for dx, dy in directions:
        # 右方向を基準に回転
        angle = 0
        if dx == 0 and dy == -5:  # 上方向
            angle = 90
        elif dx == 0 and dy == +5:  # 下方向
            angle = +180
        elif dx == +5 and dy == 0:  # 右方向
            angle = 0
        elif dx == -5 and dy == 0:  # 左方向
            angle = 180
        else:  # 斜め方向（右上、右下、左上、左下）
            angle = -45 if dx > 0 and dy < 0 else (45 if dx > 0 and dy > 0 else (135 if dx < 0 and dy > 0 else -135))

            rotated_img = pg.transform.rotozoom(kk_img, angle, 0.9)  # 回転
            kk_imgs[(dx, dy)] = rotated_img

        # 回転画像を作成
            rotated_img = pg.transform.rotozoom(kk_img, angle, 0.9)

        # 左方向の場合、逆向きの画像を用意（左右反転）
        if dx < 0:
            rotated_img = pg.transform.flip(kk_img, True, False)  # 左右反転

        # 画像を辞書に登録
        kk_imgs[(dx, dy)] = rotated_img

    return kk_imgs

    


def main():
    pg.display.set_caption("逃げろ！こうかとん")
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    bg_img = pg.image.load("fig/pg_bg.jpg")    

    # 方向に応じたこうかとん画像を準備
    kk_imgs = prepare_koukaton_images()
    current_image = kk_imgs[(0, 0)]  # 初期状態のこうかとん画像

    kk_rct = current_image.get_rect()
    kk_rct.center = 300, 200

    bb_imgs, bb_accs = init_bb_imgs()  # 爆弾Surfaceと加速度リストの初期化
    bb_img = bb_imgs[0]
    bb_rct = bb_img.get_rect()
    bb_rct.centerx = random.randint(0, WIDTH)
    bb_rct.centery = random.randint(0, HEIGHT)
    vx, vy = +5, +5  # 爆弾の速度ベクトル

    clock = pg.time.Clock()
    tmr = 0  # タイマーの初期化

    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return

        # 背景を描画
        screen.blit(bg_img, [0, 0])

        # キー入力処理と移動量計算
        key_lst = pg.key.get_pressed()
        sum_mv = [0, 0]
        for key, tpl in DELTA.items():
            if key_lst[key]:
                sum_mv[0] += tpl[0]
                sum_mv[1] += tpl[1]

        # 方向に応じたこうかとん画像を設定
        sum_mv_tuple = tuple(sum_mv)
        if sum_mv_tuple in kk_imgs:
            current_image = kk_imgs[sum_mv_tuple]

        # こうかとんを移動
        kk_rct.move_ip(sum_mv)
        if check_bound(kk_rct) != (True, True):
            kk_rct.move_ip(-sum_mv[0], -sum_mv[1])

        # 爆弾のサイズと速度を変更
        idx = min(tmr // 500, 9)
        avx = vx * bb_accs[idx]
        avy = vy * bb_accs[idx]
        bb_img = bb_imgs[idx]
        bb_rct = bb_img.get_rect(center=bb_rct.center)

        # 爆弾を移動
        bb_rct.move_ip(avx, avy)
        yoko, tate = check_bound(bb_rct)
        if not yoko:
            vx *= -1
        if not tate:
            vy *= -1

        # 衝突判定
        if kk_rct.colliderect(bb_rct):
            gameover(screen)
            return

        # 画面にこうかとんと爆弾を描画
        screen.blit(current_image, kk_rct)
        screen.blit(bb_img, bb_rct)

        pg.display.update()
        tmr += 1  # タイマーを1フレームごとに加算
        clock.tick(50)





if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()