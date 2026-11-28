from Base import *
def run_2():
    """Заезд №2"""
    print_battery()
    set_heading(0)
    lefta(80, -200, wait=False)
    go(830, 40, 70, 40, 220, 1)
    righta(100, 70)
    righta(50, -45)
    wait(250)
    righta_dc(100, 100)
    turn(60, -28)
    go(60, 30, 40, 30, 0, 1)
    lefta(20, 204)
    wait(1000)
    lefta(20, -205)
    go(-60, 30, 40, 30, 0, 1)
    turn(70, 29, pivot=LEFT)
    go(-780, 40, 70, 50, 0, 1)

if __name__ == "__main__":
    set_heading(0) 
    run_2()