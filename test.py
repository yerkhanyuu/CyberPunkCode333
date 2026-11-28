from Base import *
def run_1():
    """Заезд №1"""
    print_battery()
    set_heading(0)

    go(300, 30, 60, 30, 100, 1)

if __name__ == "__main__":
    set_heading(0)
    run_1()