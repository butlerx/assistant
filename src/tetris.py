from .aiy.toneplayer import TonePlayer


def play_tetris():
    tetris_theme = [
        "E5q",
        "Be",
        "C5e",
        "D5e",
        "E5s",
        "D5s",
        "C5s",
        "Be",
        "Bs",
        "Aq",
        "Ae",
        "C5e",
        "E5q",
        "D5e",
        "C5e",
        "Bq",
        "Be",
        "C5e",
        "D5q",
        "E5q",
        "C5q",
        "Aq",
        "Aq",
    ]

    player = TonePlayer(22)
    player.play(*tetris_theme)
