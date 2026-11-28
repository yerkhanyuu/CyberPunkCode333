from Base import *
def run_3():
    """Заезд №3"""
    print_battery()
    set_heading(0)

    righta(80, -67, wait=False)
    go(675, 40, 70, 40, 175, 1)
    turn(60, -45)
    go(140, 30, 40, 30, 0, 1)
    righta(80, -280)
    go(-140, 30, 60, 30, 0, 1)
    turn(60, 45)
    go(-550, 40, 70, 40, 100, 1)

    turn(60, 45)
    go(370, 40, 70, 30, 100, 1)
    lefta(100, 190)
    go(-530, 30, 70, 40, 100, 1)
    lefta(100, -180)

    wait(1500)
    set_heading(0)
    go(570, 40, 70, 30, 0, 1)
    turn(80, -70, pivot=LEFT)
    turn(80, 70, pivot=LEFT)
    go(-650, 40, 80, 60, 100, 1)
    turn(70, -90)

if __name__ == "__main__":
    set_heading(0)  
    run_3()