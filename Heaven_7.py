from Base import *
def run_7():
    """Заезд 7"""
    print_battery()
    set_heading(0)

    righta(50, 180, wait=False)
    go(580, 30, 60, 30, 100, 1)

    go(-110, 30, 60, 30, 0, 1)
    righta(50, -110)

    go(25, 30, 30, 30, 0, 1)
    righta(40, 120)
    go(-160, 30, 30, 30, 50, 1)
    righta(50, -130)
    go(-100, 30, 30, 30, 0, 1)
    go(-200, 50, 80, 50, 50, 1)

if __name__ == "__main__":
    set_heading(0)  
    run_7()