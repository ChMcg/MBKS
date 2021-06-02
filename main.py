from lab_1.app import App as Lab1_App
from lab_2.app import App as Lab2_App
from lab_3.app import App as Lab3_App
from lab_4.app import main as Lab4_main


if __name__ == '__main__':
    chosen_lab = 4
    labs = {
        1: Lab1_App().exec,
        2: Lab2_App().exec,
        3: Lab3_App().exec,
        4: Lab4_main,
    }
    labs[chosen_lab].__call__()
