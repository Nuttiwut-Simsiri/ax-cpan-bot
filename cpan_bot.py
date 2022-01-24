import time
from selenium import webdriver
import sys 
from random import randint, shuffle
from traceback import print_exc
from pprint import pprint
import sys 
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPM
import re
import cv2 
import pytesseract
import json 
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities




def process_browser_log_entry(entry):
    response = json.loads(entry['message'])['message']
    return response


def get_all_planes(dv):
    try:
        return len(dv.find_elements_by_xpath('//*[@id="app"]/div[1]/div/div[2]/div'))
    except Exception as e:
        print(e)
        return 0


def find_planes(dv):
    result = []
    cnt = 0
    NUM_OF_PLANES = get_all_planes(dv)
    print("FOUND ", NUM_OF_PLANES )
    for index in range(NUM_OF_PLANES):
        div_index  = index+1
        try:
            rarity = dv.find_element_by_xpath(f'//*[@id="app"]/div[1]/div/div[2]/div[{div_index}]/div/span')
            _id = dv.find_element_by_xpath(f'//*[@id="app"]/div[1]/div/div[2]/div[{div_index}]/div/div[2]/span')
            name = dv.find_element_by_xpath(f'//*[@id="app"]/div[1]/div/div[2]/div[{div_index}]/div/div[4]/div[1]/p[2]')
            fuel =  dv.find_element_by_xpath(f'//*[@id="app"]/div[1]/div/div[2]/div[{div_index}]/div/div[5]/div[6]/span/span')
            btn = dv.find_element_by_xpath(f'//*[@id="app"]/div[1]/div/div[2]/div[{div_index}]/div/div[6]/div/div[1]/button')
            fuel_int = int(fuel.text.split("/")[0])
            tmp = {
                "rarity" : rarity.text,
                "id" : _id.text,
                "name" : name.text,
                "fuel" : fuel_int,
                "btn" : btn
            }
            print(f"Found ! :  Name: {name.text}{_id.text} Type: {rarity.text} fuel: {fuel.text}")
            if not fuel_int:
                print("Skip : no fuel")
                continue
            result.append(tmp)
            cnt += 1
        except Exception as e:
            print(e)
            break
    return result



def get_captcha_svg(dv):
    try:
        svg =  dv.find_element_by_xpath('//*[@id="confirm-training"]/div/div/div/div/form/div[1]/div[1]/div').get_attribute('innerHTML')
    except Exception as e:
        print(e)
        svg = ""
    return svg

def get_captcha_input(dv):
    input = dv.find_element_by_xpath('//*[@id="captcha"]')
    confirm_btn = dv.find_element_by_xpath('//*[@id="confirm-training"]/div/div/div/div/form/div[2]/button[1]')
    return input, confirm_btn


def remove_stroke(svg_code):
    result = re.findall(r"<[^>]*>", svg_code)
    new_svg = []
    for tag in result:
        
        if "/svg" in tag and "/path" in tag:
            continue 

        if tag.startswith("<svg"):
            new_svg.append(tag)

        elif tag.startswith("<path") and "stroke" not in tag:
            new_svg.append(tag)
            new_svg.append("</path>")

    new_svg.append("</svg>")

    return "".join(new_svg)



def convert_svg2png(svg_code):
    new_code = remove_stroke(svg_code)
    with open("temp/temp_svg.svg", "w") as f:
        f.write(new_code)

    drawing = svg2rlg('temp/temp_svg.svg')
    renderPM.drawToFile(drawing, 'temp/captcha.png', fmt='PNG')

def png2text(png_path="temp/captcha.png"):
    def get_grayscale(image):
        return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    def remove_noise(image):
        return cv2.medianBlur(image, 5)

    img = cv2.imread(png_path)

    gray = get_grayscale(img)
    noise = remove_noise(gray)

    # Adding custom options
    custom_config = r'-l eng --oem 3 --psm 6 -c tessedit_char_whitelist=0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
    res = pytesseract.image_to_string(noise, config=custom_config)
    return res


def input_catpcha(btn, driver):
    svg_code = get_captcha_svg(driver)
    convert_svg2png(svg_code)
    captcha_text = png2text()
    if not captcha_text:
        input_catpcha(btn, driver)

    return captcha_text.replace(" ", "")


def close_modal_btn(dv):
    try:
        main_div = driver.find_element_by_xpath('//*[@id="app"]')
        main_div.click()
    except Exception as e:
        return False
    
    return True

def click_n_wait(btn, xpath, timeout=5):
    btn.click()
    wait.until(EC.visibility_of_element_located((By.XPATH, xpath)))

def filter_XHR(event):
    type = event['params'].get("type", "")
    if "XHR" in type:
        return True
    return False

def isCorrect(driver):
    browser_log = driver.get_log('performance')
    events = [process_browser_log_entry(entry) for entry in browser_log]
    events = [event for event in events if 'Network.responseReceived' in event['method'] and filter_XHR(event)]
    for ev in events:
        url = ev['params']["response"]["url"]
        status = ev['params']["response"]["status"]

        print(url, status)
        if url == "https://cryptoplanes.me/plane/training/virtual" and status == 200:
            return 1
        elif url == "https://cryptoplanes.me/plane/training/virtual" and status != 200:
            return 0

def auto_play(driver):
    
    t_index = 0
    while 1:
        planes = find_planes(driver) 
        ## random order to play 
        ## Create all turn list
        # all_turn = []
        # for p in planes:
        #     [ all_turn.append(p) for i in range(p["fuel"]//15) ] 
        
        # ## Caculate number of 
        # [ shuffle(all_turn) for i in range(randint(2, 4))] 

        all_turn = planes

        if not len(all_turn):
            return 1

        t = all_turn[-1]
        time.sleep(1)
        print(f"Play turn {t_index+1} : { t['name']} {t['id']} ")
        ## input captcha    
        try:            
            t["btn"].send_keys(Keys.ENTER)
            print("clicked button")
        except Exception as e:
            print(e)

        time.sleep(1.5)
        captcha_input, confirm_btn = get_captcha_input(driver)
        wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="confirm-training"]/div/div/div/div/form/div[1]/div[1]/div')))
        captcha_text = input_catpcha(t["btn"], driver)
        time.sleep(2)
        print("Captcha is ", captcha_text)
        cancel_btn = driver.find_element_by_xpath('//*[@id="confirm-training"]/div/div/div/div/form/div[2]/button[2]')
        #
        captcha_input.send_keys(captcha_text[:4])
        confirm_btn.send_keys(Keys.ENTER)

        time.sleep(2)
        res = isCorrect(driver)
        
        if res:
            while 1:
                try:
                    result_btn = driver.find_element_by_xpath('//*[@id="virtual-training"]/div/div/div/div[2]/div[1]/div')
                except Exception as e:
                    print("keep waiting ...")
                else:
                    if "CPAN" in result_btn.text or "EXP" in result_btn.text:
                        time.sleep(1)
                        result_btn = driver.find_element_by_xpath('//*[@id="virtual-training"]/div/div/div/div[2]/div[1]/div')
                        driver.refresh()
                        
                        break
                    else:
                        print("keep waiting ...")
                time.sleep(5)

            
            print("Done ...")
        time.sleep(1)

def start_process():
    auto_play(driver)

if __name__ == "__main__":
    
    options = webdriver.ChromeOptions()
    options.add_argument("start-maximized")
    options.add_argument("--user-data-dir=C://Users//nutti//AppData//Local//Google//Chrome//User Data")

    # USE THIS IF YOU NEED TO HAVE MULTIPLE PROFILES
    options.add_argument('--profile-directory=Profile 1')

    options.add_argument('--log-level=3')
    try:
        caps = DesiredCapabilities.CHROME
        caps['goog:loggingPrefs'] = {'performance': 'ALL'}
        driver = webdriver.Chrome("./chromedriver_win32/chromedriver.exe", options=options, desired_capabilities=caps)
        wait = WebDriverWait(driver, 60)
        
        
        driver.get('https://cryptoplanes.me/play/#/planes')
        time.sleep(6)
        
        main_div = driver.find_element_by_xpath('//*[@id="app"]')
        
        refuel_btn = driver.find_element_by_xpath('//*[@id="app"]/div[1]/div/div[1]/div/button[1]')
        mapper = {
            "COMMON" : 5,    
            "CLASSIC" : 5,
            "SUPER" : 6,
            "RARE" : 7,
        }
 
        res = start_process()

        NUM_OF_PLANES = get_all_planes(driver)
        for i in range(NUM_OF_PLANES):
            wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="app"]/div[1]/div/div[2]/div[1]')))
            time.sleep(1)
            btn = driver.find_element_by_xpath(f'//*[@id="app"]/div[1]/div/div[2]/div[{i+1}]/div/div[6]/div/div[2]/button')
            btn.send_keys(Keys.ENTER)
            print("Sent Enter")  
        
            wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="reward-history"]/div')))

            print("loading result ")
            wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="reward-history"]/div/div/div/div[3]/div[1]')))

            # refresh_btn = driver.find_element_by_xpath(f'//*[@id="reward-history"]/div/div/div/div[2]/button')
            # refresh_btn.send_keys(Keys.ENTER)
            wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="reward-history"]/div/div/div/div[3]/div[1]')))
            rarity = driver.find_element_by_xpath(f'//*[@id="app"]/div[1]/div/div[2]/div[{i+1}]/div/span').text
           
            num_rewards_div = len(driver.find_elements_by_xpath('//*[@id="reward-history"]/div/div/div/div[3]/div'))
            claim_btn = driver.find_element_by_xpath(f'//*[@id="reward-history"]/div/div/div/div[3]/div[1]/div[1]/div/button')
            total_earn = driver.find_element_by_xpath(f'//*[@id="reward-history"]/div/div/div/div[3]/div[1]/div[2]/table/tbody/tr[{mapper.get(rarity, 5)}]')
            recently_total_earn = driver.find_element_by_xpath(f'//*[@id="reward-history"]/div/div/div/div[3]/div[{num_rewards_div}]/div[2]/table/tbody/tr[{mapper.get(rarity, 5)}]')
            print("Recently earn", recently_total_earn.text)
            if claim_btn.text.lower() == "claim":
                print("Claim ", total_earn.text)
            else:
                print("Please wait for  ", claim_btn.text)

            time.sleep(2)
            main_div.click()
            time.sleep(1)

    except Exception as e:
        print(print_exc())

    finally:
        print("Done")
        driver.close()
        sys.exit(0)
