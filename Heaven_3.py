from Base import *
def run_3():
    """Заезд №3"""
    print_battery()
    set_heading(0)

    righta(80, -65, wait=False)
    go(665, 30, 60, 30, 200, 1)
    turn(60, -45)
    go(130, 30, 40, 30, 0, 1)
    righta(80, -300)
    go(-150, 30, 60, 30, 0, 1)
    turn(70, 45)
    go(-510, 30, 60, 30, 300, 1)
    turn(60, 45)
    go(345, 30, 60, 30, 300, 1)
    lefta(100, 210)
    go(-485, 30, 60, 30, 300, 1)
    lefta(100, -180)
    wait(1500)
    turn(60, 45)
    go(685, 30, 60, 30, 100, 1)
    go(-30, 30, 60, 30, 0, 1)

    turn(80, -90, pivot=LEFT)
    turn(80, 30, pivot=LEFT)
    go(-20, 30, 50, 30, 0, 1)
    turn(80, -30)
    turn(80, 90)
    go(-750, 30, 80, 80, 100, 1)

if __name__ == "__main__":
    set_heading(0)  
    run_3()