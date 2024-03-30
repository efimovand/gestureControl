from __future__ import print_function
import time
import pyautogui
import platform
import screen_brightness_control as sbc
from pynput.keyboard import Key, Controller


keyboard = Controller()


# -------------------- Скриншот --------------------

# Создание скриншота (сохранение файлом)
def screenshot_save_file():
    timestamp = int(time.time())  # Текущее время в timestamp
    pyautogui.screenshot().save(f'screenshot_{timestamp}.png')
    print(f'*** 📸 The screenshot #{timestamp} has been SAVED ***')

# Создание скриншота (системно)
def screenshot_save_system():
    match platform.system():
        case 'Darwin':
            with keyboard.pressed(Key.shift_l):
                with keyboard.pressed(Key.cmd):
                    keyboard.tap('3')
        case 'Windows':
            with keyboard.pressed(Key.cmd_l):
                keyboard.tap(Key.print_screen)
    print(f'*** 📸 The screenshot has been SAVED ***')


# -------------------- Звук --------------------

# Увеличение громкости
def volume_up():
    keyboard.tap(Key.media_volume_up)
    print(f'*** 🔊 The volume has been INCREASED ***')

# Уменьшение громкости
def volume_down():
    keyboard.tap(Key.media_volume_down)
    print(f'*** 🔉 The volume has been REDUCED ***')

# Отключение/включение звука
def volume_mute():
    keyboard.tap(Key.media_volume_mute)
    print(f'*** 🔇 The volume has been MUTED/UNMUTED ***')


# -------------------- Воспроизведение --------------------

# Пауза/воспроизведение
def play_pause():
    keyboard.tap(Key.media_play_pause)
    print(f'*** ⏯️️ The media has been PAUSED/UNPAUSED ***')

# Следующий трек
def next_track():
    keyboard.tap(Key.media_next)
    print(f'*** ⏭️️ The NEXT track has been activated ***')

# Предыдущий трек
def previous_track():
    keyboard.tap(Key.media_previous)
    print(f'*** ⏮️️️ The PREVIOUS track has been activated ***')


# -------------------- Яркость --------------------

# Увеличение яркости (только для Windows)
def brightness_up():
    match platform.system():
        case 'Darwin':
            print("The brightness' controlling is unavailable on MacOS")
        case 'Linux':
            print("The brightness' controlling is unavailable on Linux")
        case 'Windows':
            sbc.set_brightness(sbc.get_brightness()[0] + 10)
            print(f'*** 🔆 The brightness has been INCREASED : {sbc.get_brightness()[0]}% ***')

# Уменьшение яркости (только для Windows)
def brightness_down():
    match platform.system():
        case 'Darwin':
            print("The brightness' controlling is unavailable on MacOS")
        case 'Linux':
            print("The brightness' controlling is unavailable on Linux")
        case 'Windows':
            sbc.set_brightness(sbc.get_brightness()[0] - 10)
            print(f'*** 🔅 The brightness has been REDUCED : {sbc.get_brightness()[0]}% ***')


if __name__ == '__main__':

    while True:

        x = int(input('\n0 (screenshot 📸)\n1 (volume_up 🔊)\n2 (volume_down 🔉)\n3 (mute 🔇)\n4 (play_pause ⏯️)\n5 (next_track ⏭️)\n6 (previous_track ⏮️️️️)\n7 (brightness_up 🔆️️️)\n8 (brightness_down 🔅️️️)\n'))

        match x:
            case 0:
                screenshot_save_system()
            case 1:
                for _ in range(10):
                    volume_up()
                    time.sleep(0.1)
            case 2:
                for _ in range(10):
                    volume_down()
                    time.sleep(0.1)
            case 3:
                volume_mute()
            case 4:
                play_pause()
            case 5:
                next_track()
            case 6:
                previous_track()
            case 7:
                brightness_up()
            case 8:
                brightness_down()
            case default:
                pass
