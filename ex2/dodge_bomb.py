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


    


def main():
    pg.display.set_caption("逃げろ！こうかとん")
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    bg_img = pg.image.load("fig/pg_bg.jpg")    
    kk_img = pg.transform.rotozoom(pg.image.load("fig/3.png"), 0, 0.9)
    kk_rct = kk_img.get_rect()
    kk_rct.center = 300, 200

    # 爆弾Surfaceと加速度リストの初期化
    bb_imgs, bb_accs = init_bb_imgs()

    # 爆弾の初期設定
    bb_img = bb_imgs[0]  # 初期の爆弾Surface
    bb_rct = bb_img.get_rect()  # 爆弾Rectの抽出
    bb_rct.centerx = random.randint(0, WIDTH)
    bb_rct.centery = random.randint(0, HEIGHT)
    vx, vy = +5, +5  # 爆弾速度ベクトル

    clock = pg.time.Clock()
    tmr = 0  # タイマー変数の初期化

    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return

        # tmrに応じて爆弾サイズと加速度を変更
        idx = min(tmr // 500, 9)  # インデックスを計算（最大値9）
        avx = vx * bb_accs[idx]  # 加速度に応じた速度
        avy = vy * bb_accs[idx]
        bb_img = bb_imgs[idx]  # サイズに応じた爆弾Surfaceを選択
        bb_rct = bb_img.get_rect(center=bb_rct.center)  # サイズ変更に伴いRectを更新

        # 背景を描画
        screen.blit(bg_img, [0, 0])

        # こうかとんの移動処理
        key_lst = pg.key.get_pressed()
        sum_mv = [0, 0]
        for key, tpl in DELTA.items():
            if key_lst[key]:
                sum_mv[0] += tpl[0]
                sum_mv[1] += tpl[1]
        kk_rct.move_ip(sum_mv)
        if check_bound(kk_rct) != (True, True):  # 画面外なら元に戻す
            kk_rct.move_ip(-sum_mv[0], -sum_mv[1])
        screen.blit(kk_img, kk_rct)

        # 爆弾の移動処理
        bb_rct.move_ip(avx, avy)  # 加速度を反映した移動
        yoko, tate = check_bound(bb_rct)
        if not yoko:
            vx *= -1
        if not tate:
            vy *= -1

        # 衝突判定
        if kk_rct.colliderect(bb_rct):
            gameover(screen)
            return

        # 爆弾を描画
        screen.blit(bb_img, bb_rct)

        # 画面を更新
        pg.display.update()
        tmr += 1  # タイマーをインクリメント
        clock.tick(50)



if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()