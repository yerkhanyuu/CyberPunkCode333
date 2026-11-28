from Base import *
def run_8():
    """Заезд №8"""
    print_battery()
    set_heading(0)

    go(720, 40, 70, 40, 150, 1)
    turn(70, 45, pivot=RIGHT)
    go(100, 30, 40, 30, 0, 1)

    righta_dc(100, 90)
    lefta_dc(80, 150)
    righta(100, 60, wait=False)

    go(-220, 40, 50, 40, 0, 1)
    lefta_dc(70, -160)

    turn(80, -90, pivot=RIGHT)
    go(-200, 40, 70, 60, 0, 1)
    turn(80, 45, pivot=LEFT)
    go(-230, 40, 80, 60, 0, 1)
    turn(80, -90)

if __name__ == "__main__":
    set_heading(0) 
    run_8()