from Base import *
def run_5():
    """Заезд №5"""
    print_battery()
    set_heading(0)

    righta(100, 400)
    go(600, 40, 80, 60, 100, 1)
    turn(80, -60, pivot=LEFT)
    turn(80, 60, pivot=RIGHT)
    go(400, 40, 80, 60, 100, 1)
    turn(70, -90)
    go(330, 40, 80, 60, 100, 1)
    turn(70, 45)
    go(200, 40, 80, 30, 100, 1)
    go(100, 30, 30, 30, 0, 1)
    go(-100, 40, 60, 40, 0, 1)
    turn(80, 90)
    go(500, 40, 80, 80, 100, 1)
    turn(60, 45)
    go(380, 40, 80, 80, 100, 1)
    turn(80, 180)

if __name__ == "__main__":
    set_heading(0)
    run_5()