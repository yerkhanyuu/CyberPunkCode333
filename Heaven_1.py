from Base import *
def run_1():
    """Заезд №1"""
    print_battery()
    set_heading(0)

    go(120, 30, 60, 30, 0, 1)
    turn(60, 45, pivot=RIGHT)
    go(520, 30, 70, 30, 126, 1)
    turn(60, -45, pivot=LEFT)
    go(110, 30, 50, 50, 50, 1)
    righta_dc(100, 90)
    righta_dc(100, -50)

    wait(100)
    go(160, 40, 70, 60, 0, 1)

    go(30, 50, 50, 50, 0, 1)
    go(-30, 50, 50, 50, 0, 1)
    go(30, 50, 50, 50, 0, 1)
    go(-30, 50, 50, 50, 0, 1)
    go(30, 50, 50, 50, 0, 1)
    go(-30, 50, 50, 50, 0, 1)
    go(30, 50, 50, 50, 0, 1)
    wait(200)
    go(-90, 50, 50, 50, 0, 1)

    turn(60, 26)
    go(-850, 50, 80, 70, 100, 1)

if __name__ == "__main__":
    set_heading(0)
    run_1()