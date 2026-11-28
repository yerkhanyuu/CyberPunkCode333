from Base import *
def run_5():
    """Заезд №5"""
    print_battery()
    set_heading(0)

    righta(100, 400)
    go(100, 30, 40, 30, 60, 1)
    turn(60, 45)
    go(230, 30, 50, 30, 100, 1)
    turn(60, 45)
    go(760, 40, 80, 60, 160, 1)
    turn(60, -90)
    go(320, 40, 70, 60, 100, 1)
    turn(50, 45, pivot=RIGHT)
    go(200, 40, 60, 30, 100, 1)
    go(107, 30, 30, 30, 0, 1)
    go(-60, 40, 60, 40, 0, 1)
    turn(60, 90)
    go(500, 40, 80, 60, 100, 1)
    turn(60, 45)
    go(380, 40, 80, 60, 150, 1)
    righta(100, -400, wait=False)
    turn(80, 180)

if __name__ == "__main__":
    set_heading(0)
    run_5()