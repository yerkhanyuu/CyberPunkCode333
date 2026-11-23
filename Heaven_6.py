from Base import *
def run_6():
    """Заезд №6"""
    print_battery()
    set_heading(0)

    lefta(80, 90, wait=False)
    righta(100, 180, wait=False)

    go(150, 30, 60, 30, 50, 1)
    turn(80, -70)
    go(490, 40, 60, 40, 190, 1)
    turn(80, 70)
    go(190, 30, 60, 30, 90, 1)
    turn(60, -90)
    go(90, 30, 30, 30, 0, 1)

    lefta(80, -90)
    righta(100, -120)
    go(-90, 30, 40, 40, 0, 1)
    righta(100, 180)

    turn(60, 90)
    go(-150, 40, 70, 50, 75, 1)
    turn(80, -70, pivot=RIGHT)
    go(-700, 40, 80, 50, 100, 1)

if __name__ == "__main__":
    set_heading(0)
    run_6()