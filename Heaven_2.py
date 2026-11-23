from Base import *
def run_2():
    """Заезд №2"""
    print_battery()
    set_heading(0)

    go(820, 40, 60, 40, 200, 1)
    righta(60, 60)
    righta(50, -30)
    righta(100, 120)
    go(180, 30, 30, 20, 0, 1)
    lefta(20, 180)
    wait(1000)
    lefta(50, -200)
    go(-1000, 40, 80, 80, 200, 1)

if __name__ == "__main__":
    set_heading(0) 
    run_2()