from Base import *
def run_4():
    """Заезд №4"""
    print_battery()
    set_heading(0)

    go(470, 30, 50, 30, 70, 1)
    go(-350, 50, 100, 90, 0, 1)

if __name__ == "__main__":
    set_heading(0)
    run_4()
