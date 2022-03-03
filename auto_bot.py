from selenium import webdriver
from selenium.common.exceptions import TimeoutException
# from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import json
import os
from datetime import datetime
from selenium.webdriver.common.action_chains import ActionChains
import csv
from threading import Thread, Event
from time import sleep

# config_data = json.loads(open("bot//config.json", "r").read())
# firefox_profile = config_data['firefox_profile']
# currentProject_PATH = os.path.abspath('auto_bot.exe').split('auto_bot.exe')[0]
# ABSOLUTE_UPLOADED_FILE_PATH = currentProject_PATH + 'bot\\web\\uploads\\'
# INPUT_FILENAME_PATH = currentProject_PATH + 'bot\\web\\uploads'
# PROGRESS_PATH = currentProject_PATH + 'bot\\web\\progress'
# geckodriver_PATH = currentProject_PATH + 'bot\\geckodriver.exe'


config_data = json.loads(open("config.json", "r").read())
firefox_profile = config_data['firefox_profile']
currentProject_PATH = os.path.abspath('auto_bot.exe').split('auto_bot.exe')[0]
ABSOLUTE_UPLOADED_FILE_PATH = currentProject_PATH + 'web\\uploads\\'
INPUT_FILENAME_PATH = currentProject_PATH + 'web\\uploads'
PROGRESS_PATH = currentProject_PATH + 'web\\progress'
geckodriver_PATH = currentProject_PATH + 'geckodriver.exe'


options = webdriver.FirefoxOptions()
options.add_argument("--start-maximized")
# options.headless = True
profile = webdriver.FirefoxProfile(firefox_profile)
global_driver = webdriver.Firefox(executable_path=geckodriver_PATH, options=options, firefox_profile=profile)

class Bot(Thread):
    def __init__(self, profile, url):
        Thread.__init__(self)
        self._stop = Event()
        self.profile = profile
        self.url = url
        self.new_upload = False
        self.config = {}
        self.worked_file_list = []
    
    def read_progress(self):
        progress_file = open(os.path.join(PROGRESS_PATH, 'progress.json'), "r")
        progress_file_text = progress_file.read()
        progress = json.loads(progress_file_text)
        return progress

    def write_progress(self, data):
        output = os.path.join(PROGRESS_PATH, 'progress.json')
        with open(os.path.join(PROGRESS_PATH, 'progress.json'), "w") as output:
            json.dump(data, output)

    def stop(self): 
        self._stop.set() 
    def stopped(self): 
        return self._stop.isSet() 

    def setdriver(self):
        try:
            print('setting firefox driver')

            progress = self.read_progress()
            if self.profile == "RUMBLE":
                progress['rumble']['status'] = 'open'
            elif self.profile == "BITCHUTE":
                progress['bitchute']['status'] = 'open'
            else:
                progress['odysee']['status'] = 'open'
            self.write_progress(progress)

            
        except Exception as e:
            print(e)
            sleep(10)
    def upload_video(self, data_json, filename):
        print(data_json)
        if not filename in self.worked_file_list:
            self.config = data_json
            print("uploading")
            self.setdriver()
            self.worked_file_list.append(filename)
            # self.config
            if self.profile == "RUMBLE":
                print("RUMBLE site is opening")
                global_driver.get("https://rumble.com/upload.php")
                # global_driver.execute_script('window.open("https://rumble.com/upload.php")')
                try:
                    username_input = global_driver.find_element(By.XPATH, '//*[@id="login-username"]')
                    print('found login element')
                    password_input = global_driver.find_element(By.XPATH, '//*[@id="login-password"]')
                    login_submit_btn = global_driver.find_element(By.XPATH, '//button[text()="Sign in"]')
                    username_input.send_keys(config_data['rumble_username'])
                    password_input.send_keys(config_data['rumble_password'])
                    login_submit_btn.click()
                    try:
                        WebDriverWait(global_driver, 10).until(EC.presence_of_element_located((By.XPATH,'//*[@id="submitForm"]')))
                        print('Rumble is ready!')
                        sleep(3)
                        global_driver.find_element(By.XPATH, '//*[@id="Filedata"]').send_keys(os.path.join(ABSOLUTE_UPLOADED_FILE_PATH, (self.config['video'].split('/'))[1]))
                        global_driver.find_element(By.XPATH, '//*[@id="customThumb"]').send_keys(os.path.join(ABSOLUTE_UPLOADED_FILE_PATH, (self.config['thumb'].split('/'))[1]))

                        #json file
                        progress = self.read_progress()
                        progress['rumble']['status'] = 'start_uploading'
                        self.write_progress(progress)

                        #catch percentage
                        while True:
                            sleep(1)
                            progress_bar = global_driver.execute_script("return document.getElementsByClassName('green_percent')[0].style.width")
                            print(progress_bar)
                            #json file
                            progress = self.read_progress()
                            progress['rumble']['progress'] = progress_bar
                            self.write_progress(progress)
                            if( progress_bar == '100%'):
                                break
                        print('finished uploading')

                        #json file
                        progress = self.read_progress()
                        progress['rumble']['progress'] = '0%'
                        progress['rumble']['status'] = 'finish_uploading'
                        self.write_progress(progress)

                        global_driver.find_element(By.XPATH, '//*[@id="title"]').send_keys(self.config['title'])
                        global_driver.find_element(By.XPATH, '//*[@id="description"]').send_keys(self.config['description'])
                        global_driver.find_element(By.XPATH, '//*[@id="submitForm"]').click()
                        try: 
                            WebDriverWait(global_driver, 100).until(EC.element_to_be_clickable((By.XPATH,'/html/body/main/div/div/div/section/form[2]/div/div[2]/div[1]/div/a'))).click()
                            global_driver.find_element(By.XPATH, '/html/body/main/div/div/div/section/form[2]/div/div[7]/div[1]/label').click()
                            global_driver.find_element(By.XPATH, '/html/body/main/div/div/div/section/form[2]/div/div[7]/div[2]/label').click()
                            global_driver.find_element(By.XPATH, '//*[@id="submitForm2"]').click()

                            #json file
                            progress = self.read_progress()
                            progress['rumble']['status'] = 'submitted'
                            self.write_progress(progress)

                        except TimeoutException:
                            print("Loading took too much time!")    
                            #json file
                            progress = self.read_progress()
                            progress['rumble']['status'] = 'failed'
                            self.write_progress(progress)
                    except TimeoutException:
                        print("Loading took too much time!")
                        #json file
                        progress = self.read_progress()
                        progress['rumble']['status'] = 'failed'
                        self.write_progress(progress)
                except:
                    print('not found')
                    try: 
                        WebDriverWait(global_driver, 10).until(EC.presence_of_element_located((By.XPATH,'//*[@id="submitForm"]')))
                        print('Rumble is ready!')
                        sleep(3)
                        global_driver.find_element(By.XPATH, '//*[@id="Filedata"]').send_keys(os.path.join(ABSOLUTE_UPLOADED_FILE_PATH, (self.config['video'].split('/'))[1]))
                        global_driver.find_element(By.XPATH, '//*[@id="customThumb"]').send_keys(os.path.join(ABSOLUTE_UPLOADED_FILE_PATH, (self.config['thumb'].split('/'))[1]))

                        #json file
                        progress = self.read_progress()
                        progress['rumble']['status'] = 'start_uploading'
                        self.write_progress(progress)

                        #catch percentage
                        while True:
                            sleep(1)
                            progress_bar = global_driver.execute_script("return document.getElementsByClassName('green_percent')[0].style.width")
                            print(progress_bar)
                            #json file
                            progress = self.read_progress()
                            progress['rumble']['progress'] = progress_bar
                            self.write_progress(progress)
                            if( progress_bar == '100%'):
                                break
                        print('finished uploading')

                        #json file
                        progress = self.read_progress()
                        progress['rumble']['progress'] = '0%'
                        progress['rumble']['status'] = 'finish_uploading'
                        self.write_progress(progress)

                        global_driver.find_element(By.XPATH, '//*[@id="title"]').send_keys(self.config['title'])
                        global_driver.find_element(By.XPATH, '//*[@id="description"]').send_keys(self.config['description'])
                        global_driver.find_element(By.XPATH, '//*[@id="submitForm"]').click()
                        try: 
                            WebDriverWait(global_driver, 100).until(EC.element_to_be_clickable((By.XPATH,'/html/body/main/div/div/div/section/form[2]/div/div[2]/div[1]/div/a'))).click()
                            global_driver.find_element(By.XPATH, '/html/body/main/div/div/div/section/form[2]/div/div[7]/div[1]/label').click()
                            global_driver.find_element(By.XPATH, '/html/body/main/div/div/div/section/form[2]/div/div[7]/div[2]/label').click()
                            global_driver.find_element(By.XPATH, '//*[@id="submitForm2"]').click()

                            #json file
                            progress = self.read_progress()
                            progress['rumble']['status'] = 'submitted'
                            self.write_progress(progress)

                        except TimeoutException:
                            print("Loading took too much time!")    
                            #json file
                            progress = self.read_progress()
                            progress['rumble']['status'] = 'failed'
                            self.write_progress(progress)
                    except TimeoutException:
                        print("Loading took too much time!")
                        #json file
                        progress = self.read_progress()
                        progress['rumble']['status'] = 'failed'
                        self.write_progress(progress)

            elif self.profile == "BITCHUTE":
                print("BITCHUTE site is opening")
                global_driver.get("https://www.bitchute.com/")
                # global_driver.execute_script('window.open("https://www.bitchute.com/")')
                try:
                    # WebDriverWait(global_driver, 10).until(EC.presence_of_element_located((By.XPATH,'/html/body/nav/div[1]/div[2]/div[4]/span/a[1]')))
                    global_driver.find_element(By.XPATH, '//span/a[text()="Login"]').click()
                    sleep(1)
                    global_driver.find_element(By.XPATH, '//*[@id="id_username"]').send_keys(config_data['bitchute_username'])
                    global_driver.find_element(By.XPATH, '//*[@id="id_password"]').send_keys(config_data['bitchute_password'])
                    global_driver.find_element(By.XPATH, '//*[@id="auth_submit"]').click()
                    try:
                        WebDriverWait(global_driver, 20).until(EC.presence_of_element_located((By.XPATH,'*//a[@href="/myupload/"]')))
                        sleep(5)
                        global_driver.find_element(By.XPATH, '*//a[@href="/myupload/"]').click()
                        try: 
                            WebDriverWait(global_driver, 20).until(EC.presence_of_element_located((By.XPATH,'//*[@id="fileupload"]')))
                            sleep(5)
                            print("Bitchute is ready!")
                            global_driver.find_element(By.XPATH, '//*[@id="fileupload"]').send_keys(os.path.join(ABSOLUTE_UPLOADED_FILE_PATH, (self.config['video'].split('/'))[1]))
                            global_driver.find_element(By.XPATH, '//*[@id="fileupload"]').send_keys(os.path.join(ABSOLUTE_UPLOADED_FILE_PATH, (self.config['thumb'].split('/'))[1]))

                            #json file
                            progress = self.read_progress()
                            progress['bitchute']['status'] = 'start_uploading'
                            self.write_progress(progress)

                            #catch percentage
                            while True:
                                sleep(1)
                                progress_bar = global_driver.execute_script("return document.getElementsByClassName('progress-bar')[0].style.width")
                                print(progress_bar)
                                #json file
                                progress = self.read_progress()
                                progress['bitchute']['progress'] = progress_bar
                                self.write_progress(progress)
                                if( progress_bar == '100%'):
                                    break
                            print('finished uploading')

                            #json file
                            progress = self.read_progress()
                            progress['bitchute']['progress'] = '0%'
                            progress['bitchute']['status'] = 'finish_uploading'
                            self.write_progress(progress)
                            sleep(3)
                            global_driver.find_element_by_name('upload_title').send_keys(self.config['title'])
                            global_driver.find_element_by_name('upload_description').send_keys(self.config['description'])
                            global_driver.find_element(By.XPATH, '//*[@id="finish-button"]').click()
                            #json file
                            progress = self.read_progress()
                            progress['bitchute']['status'] = 'submitted'
                            self.write_progress(progress)
                        except TimeoutException:
                            print("Loading took too much time!")
                            #json file
                            progress = self.read_progress()
                            progress['bitchute']['status'] = 'failed'
                            self.write_progress(progress)

                    except TimeoutException:
                        print("Loading took too much time!")
                        #json file
                        progress = self.read_progress()
                        progress['bitchute']['status'] = 'failed'
                        self.write_progress(progress)
                except:
                    try:
                        WebDriverWait(global_driver, 20).until(EC.presence_of_element_located((By.XPATH,'*//a[@href="/myupload/"]')))
                        sleep(5)
                        global_driver.find_element(By.XPATH, '*//a[@href="/myupload/"]').click()
                        try: 
                            WebDriverWait(global_driver, 10).until(EC.presence_of_element_located((By.XPATH,'//*[@id="fileupload"]')))
                            sleep(5)
                            print("Bitchute is ready!")
                            global_driver.find_element(By.XPATH, '//*[@id="fileupload"]').send_keys(os.path.join(ABSOLUTE_UPLOADED_FILE_PATH, (self.config['video'].split('/'))[1]))
                            global_driver.find_element(By.XPATH, '//*[@id="fileupload"]').send_keys(os.path.join(ABSOLUTE_UPLOADED_FILE_PATH, (self.config['thumb'].split('/'))[1]))

                            #json file
                            progress = self.read_progress()
                            progress['bitchute']['status'] = 'start_uploading'
                            self.write_progress(progress)

                            #catch percentage
                            while True:
                                sleep(1)
                                progress_bar = global_driver.execute_script("return document.getElementsByClassName('progress-bar')[0].style.width")
                                print(progress_bar)
                                #json file
                                progress = self.read_progress()
                                progress['bitchute']['progress'] = progress_bar
                                self.write_progress(progress)
                                if( progress_bar == '100%'):
                                    break
                            print('finished uploading')

                            #json file
                            progress = self.read_progress()
                            progress['bitchute']['progress'] = '0%'
                            progress['bitchute']['status'] = 'finish_uploading'
                            self.write_progress(progress)
                            sleep(3)
                            global_driver.find_element_by_name('upload_title').send_keys(self.config['title'])
                            global_driver.find_element_by_name('upload_description').send_keys(self.config['description'])
                            global_driver.find_element(By.XPATH, '//*[@id="finish-button"]').click()
                            #json file
                            progress = self.read_progress()
                            progress['bitchute']['status'] = 'submitted'
                            self.write_progress(progress)
                        except TimeoutException:
                            print("Loading took too much time!")
                            #json file
                            progress = self.read_progress()
                            progress['bitchute']['status'] = 'failed'
                            self.write_progress(progress)

                    except TimeoutException:
                        print("Loading took too much time!")
                        #json file
                        progress = self.read_progress()
                        progress['bitchute']['status'] = 'failed'
                        self.write_progress(progress)
            else:
                print("ODYSEE site is opening")
                global_driver.find_element(By.XPATH, '//*[@id="fileupload"]').send_keys(os.path.join(ABSOLUTE_UPLOADED_FILE_PATH, (self.config.split('/'))[1]))

    def run(self):
        while True:
            print('running bot')
            sleep(1)
            
        
                 

def main():
    RUMBLE_Bot_url = 'https://rumble.com/upload.php'
    RUMBLE_Bot = Bot("RUMBLE", RUMBLE_Bot_url)

    BITCHUTE_Bot_url = 'https://www.bitchute.com/'
    BITCHUTE_Bot = Bot("BITCHUTE", BITCHUTE_Bot_url)
    
    ODYSEE_Bot_url = 'https://up12.bitchute.com/videos/upload/?upload_code=UU1mrApdBVDt&channel=5MVo7z8ZqGu9&cid=1383148&cdid=5MVo7z8ZqGu9'
    ODYSEE_Bot = Bot("ODYSEE", ODYSEE_Bot_url)

    # RUMBLE_Bot.run()
    # BITCHUTE_Bot.run()
    # ODYSEE_Bot.run()

    worked_filelist = []
    while True:
        for filename in os.listdir(INPUT_FILENAME_PATH):
            if ".json" in filename and not filename in worked_filelist:
                worked_filelist.append(filename)
                input_file = open(os.path.join(INPUT_FILENAME_PATH, filename), "r")
                query_text = input_file.read()
                query_json = json.loads(query_text)
                print(os.path.join(ABSOLUTE_UPLOADED_FILE_PATH, query_json['video'].split('/')[1]))

                if "rumble" in query_json["service"]:
                    RUMBLE_Bot.upload_video(query_json, filename)
                
                if "bitchute" in query_json["service"]:
                    BITCHUTE_Bot.upload_video(query_json, filename)
                
                if "odysee" in query_json["service"]:
                    ODYSEE_Bot.upload_video(query_json, filename)
                
                input_file.close()


if __name__ == '__main__':
    main()