from Base import *
def run_4():
    """Заезд №4"""
    print_battery()
    set_heading(0)

    go(470, 40, 60, 30, 70, 1)
    go(-370, 50, 80, 70, 70, 1)

if __name__ == "__main__":
    set_heading(0)
    run_4()
