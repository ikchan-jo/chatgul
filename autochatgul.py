from selenium import webdriver
from time import sleep
import sys
import os
import threading
import dotenv

from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

from tkinter import *
from tkinter.messagebox import *

root = Tk()
root.title('DISCORD CHATGUL')
lbl = Label(root, text="서버 이름")
lbl.grid(row=0, column=0)
txt = Entry(root)
txt.grid(row=0, column=1)
lbl2 = Label(root, text="챗방 이름")
lbl2.grid(row=1, column=0)
txt2 = Entry(root)
txt2.grid(row=1, column=1)
lbl3 = Label(root, text="딜레이 초")
lbl3.grid(row=2, column=0)
txt3 = Entry(root)
txt3.grid(row=2, column=1)
btn = Button(root, text="START")
btn.grid(row=3, column=0, sticky='ew')
btn2 = Button(root, text="STOP")
btn2.grid(row=3, column=1, sticky='ew')

config_path = os.path.join(os.path.abspath('resources'), 'config.env')
try:
    config = dotenv.dotenv_values(config_path)
    txt.insert(0, f'{config["server_name"]}')
    txt2.insert(0, f'{config["chat_room_name"]}')
    txt3.insert(0, f'{config["delay_time"]}')
except:
    txt3.insert(0, '60')
script_path = os.path.join(os.path.abspath('resources'), 'scripts.txt')
chrome_path = os.path.join(os.path.abspath('resources'), 'chromedriver.exe')
# TODO : chrome 버전 파악하여 자동으로 내려받게 하면 좋을 듯?

stop_flag = False
driver = None


def chatgul_start(server_name, chat_room_name, delay_time): # 여러 채널을 동시에 챗굴 할 수 있도록 하면 좋을 듯
    with open(config_path, 'w') as file:
        file.write(f'server_name={server_name}\n')
        file.write(f'chat_room_name={chat_room_name}\n')
        file.write(f'delay_time={delay_time}\n')
    global driver
    driver = webdriver.Chrome(chrome_path) #driver path
    driver.implicitly_wait(3)

    driver.get('https://discord.com/login')

    counter = 100
    while True: # TODO: 자동으로 찾아 들어가게 하면 더 좋을 듯
        try:
            
            elm4 = driver.find_element_by_xpath('/html/body/div[1]/div[2]/div/div[2]/div/div/div/div[2]/div[1]/nav/div[1]/header/h1') #/[@draggable="true"][@data-dnd-name="{server_name}"]')
            print(elm4.get_attribute('innerText'))
            elm5 = driver.find_element_by_xpath('/html/body/div[1]/div[2]/div/div[2]/div/div/div/div[2]/div[2]/section/div[1]/h3')
            print(elm5.get_attribute('innerText'))
        except:
            print('selenium.common.exceptions.NoSuchElementException')
            continue
        try:
            if server_name in elm4.get_attribute('innerText') and chat_room_name in elm5.get_attribute('innerText'): 
                break
        except:
            print("not yet")
            counter -= 1
            if counter == 0:
                sys.exit()
            sleep(5)
            pass

    # 맨위에 채널 접속            
    # dm을 다 읽은 상태에서 동작 시켜야 함. 원하는 서버를 서버 맨위에 두어야 함.
    # elm4 = driver.find_element_by_xpath('//*[@id="app-mount"]/div[2]/div/div[2]/div/div/nav/ul/div[2]/div[3]/div[1]/div[2]/div')
    # elm4.click()
    # driver.implicitly_wait(10)


    # elm5 = driver.find_element_by_xpath(f'//*[@id="channels"]/div/div[@data-dnd-name="{chat_room_name}"]')
    # elm5.click()
    from random import seed
    from random import randint
    seed(1) # TODO: 날짜 값으로 받을 것. 현재는 항상 똑같은 randint 가 나옴
    with open(script_path, 'r', encoding='utf-8') as file:
        scripts = file.readlines()
    action = ActionChains(driver)
    action.key_down(Keys.TAB).perform()
    
    '''
    TODO
    1. 특정 시간 동안만 반복하게 한다. UI 쪽 입력에 따름
    2. 한번만 수행 되도록 한다. script에 스토리가 있을 경우
    3. UI에서 잠시 멈춤 기능 버튼 추가. 의심 받지 않기 위해 가끔 타이핑을 칠 때가 있는데 봇이랑 같이 대화가 나와서 당황 스러울 때가 있음
    '''
    while True: 
    
        for script in scripts:
            action.send_keys(script.rstrip()).key_down(Keys.ENTER).perform() # TODO: 입력 전에 입력되어 있는 항목 지울 것
            sleep(int(delay_time) + randint(0, 3600)) # TODO: 랜덤 시간을 추가하여 채팅 입력 속도를 동적으로 조절, UI에서 허용 범위를 정하면 좋을 듯?


class BackgroundTasks(threading.Thread):

    def __init__(self, server_name, chat_room_name, delay_time):
        self.server_name = server_name
        self.chat_room_name = chat_room_name
        self.delay_time = delay_time
        threading.Thread.__init__(self)
        self.daemon = True

    def run(self,*args,**kwargs):
        chatgul_start(self.server_name, self.chat_room_name, self.delay_time)

def btn_start(event):
    server_name = txt.get().strip()
    chat_room_name = txt2.get().strip()
    delay_time = txt3.get().strip()
    if not server_name or not chat_room_name or not delay_time:
        showerror("오류", "모든 내용을 입력해 주세요")
        return
    if askyesno("확인", f"server: {server_name}\n chat room: {chat_room_name}\n delay: {delay_time}\n 에 대한 챗굴 start?"):
        BackgroundTasks(server_name,chat_room_name,delay_time).start()


btn.bind('<Button-1>', btn_start)


def btn_stop(event):
    global stop_flag
    server_name = txt.get().strip()
    chat_room_name = txt2.get().strip()
    delay_time = txt3.get().strip()
    if askyesno("확인", f"server: {server_name}\n chat room: {chat_room_name}\n delay: {delay_time}\n 에 대한 챗굴 stop?"):
        driver.close()
        stop_flag = True

btn2.bind('<Button-1>', btn_stop)


root.mainloop()