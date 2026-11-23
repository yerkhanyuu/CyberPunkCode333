from Base import *
def run_8():
    """Заезд №8"""
    print_battery()
    set_heading(0)

    go(730, 40, 70, 40, 150, 1)
    turn(80, 45, pivot=RIGHT)
    go(90, 30, 40, 30, 0, 1)

    righta_dc(100, 90)
    lefta_dc(100, 150)
    righta(100, -90, wait=False)

    go(-200, 30, 60, 30, 0, 1)
    turn(80, -45)
    righta(100, 90)

    go(-730, 30, 60, 60, 0, 1)

if __name__ == "__main__":
    set_heading(0) 
    run_8()