from Base import *
def run_7():
    """Заезд 7"""
    print_battery()
    set_heading(0)

    righta(50, 56, wait=False)
    go(525, 40, 60, 40, 0, 1)
    lefta(30, 300)
    righta(30, 40)
    righta(30, 20, wait=False)
    go(-145, 30, 40, 30, 0, 1)
    righta(30, -60)
    go(-320, 40, 60, 40, 0, 1)

if __name__ == "__main__":
    set_heading(0)  
    run_7()