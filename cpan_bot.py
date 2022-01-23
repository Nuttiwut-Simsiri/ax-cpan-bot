from lib2to3.pgen2.token import NUMBER
import time
from selenium import webdriver
import sys 
from random import randint, shuffle
from traceback import print_exc
from pprint import pp, pprint
import sys 
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPM
import re
import cv2 
import pytesseract
from pprint import pprint
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

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
        svg =  dv.find_element_by_xpath('//*[@id="confirm-training"]/div/div/div/div/form/div[1]/div[1]/div/svg').get_attribute('innerHTML')
    except Exception as e:
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
        return cv2.medianBlur(image, 7)

    img = cv2.imread(png_path)

    gray = get_grayscale(img)
    noise = remove_noise(gray)

    # Adding custom options
    custom_config = r'--psm 10 --oem 3'
    res = pytesseract.image_to_string(noise, config=custom_config)
    return res


def input_catpcha(btn, driver):

    while 1:
        try:
            confirm_captcha_modal = driver.find_element_by_xpath('//*[@id="confirm-training"]')
            class_name = confirm_captcha_modal.get_attribute("class") 

            if class_name == "modal fade show":
                print("Modal open ")
                break

        except Exception as e:
            print(e)
            
        time.sleep(1)
        print("waiting modal")
        btn.sendKeys()

    svg_code = get_captcha_svg(driver)
    convert_svg2png(svg_code)
    captcha_text = png2text()
    if not captcha_text:
        input_catpcha()

    return captcha_text


def close_modal_btn(dv):
    try:
        main_div = driver.find_element_by_xpath('//*[@id="app"]')
        main_div.click()
    except Exception as e:
        return False
    
    return True
def isCorrect(driver):
    for request in driver.requests:
        if request.response:
            print(
                request.url,
                request.response.status_code,
                request.response.headers['Content-Type']
            )

def click_n_wait(btn, xpath, timeout=5):
    btn.click()
    wait.until(EC.presence_of_element_located((By.XPATH, xpath)))

def auto_play(planes, driver):
#     planes = [{'btn': '<selenium.webdriver.remote.webelement.WebElement (session="94454c62ae861b8be4a67ce893509dba", element="bfb5feb2-bb40-4b24-849b-7afb5248c431")>',
#   'fuel': 60,
#   'id': '#180307',
#   'name': 'TWINPYRE',
#   'rarity': 'COMMON'},
#  {'btn': '<selenium.webdriver.remote.webelement.WebElement (session="94454c62ae861b8be4a67ce893509dba", element="fac777e2-f147-4235-8621-fd2c0fa4b857")>',
#   'fuel': 60,
#   'id': '#88779',
#   'name': 'SKYRAID',
#   'rarity': 'COMMON'},
#  {'btn': '<selenium.webdriver.remote.webelement.WebElement (session="94454c62ae861b8be4a67ce893509dba", element="73c7202c-333e-4dd0-a65c-21bfb6557c2b")>',
#   'fuel': 60,
#   'id': '#76963',
#   'name': 'SKYRAID',
#   'rarity': 'COMMON'},
#  {'btn': '<selenium.webdriver.remote.webelement.WebElement (session="94454c62ae861b8be4a67ce893509dba", element="46ef73ed-3e01-4fcf-936e-540451f96e5b")>',
#   'fuel': 60,
#   'id': '#62967',
#   'name': 'WATER BOATMEN',
#   'rarity': 'CLASSIC'},
#  {'btn': '<selenium.webdriver.remote.webelement.WebElement (session="94454c62ae861b8be4a67ce893509dba", element="36c91c58-2d11-4ef4-97c0-16703d91a12c")>',
#   'fuel': 60,
#   'id': '#62963',
#   'name': 'SKYRAID',
#   'rarity': 'COMMON'}]

    pprint(planes)
    ## random order to play 
    ## Create all turn list
    all_turn = []
    for p in planes:
        [ all_turn.append(p) for i in range(p["fuel"]//15) ] 
    
    ## Caculate number of 
    [ shuffle(all_turn) for i in range(randint(2, 4))] 

    for t in all_turn:
        
        ## input captcha 
        click_n_wait(t["btn"], '//*[@id="confirm-training"]/div/div/div/div/form/div[1]/div[1]/div/svg')
        print("clicked button")
        captcha_text = input_catpcha(t["btn"], driver)
        captcha_input, confirm_btn = get_captcha_input(driver)

        captcha_input.send_keys(captcha_text)
        confirm_btn.send_keys(Keys.ENTER)

        isCorrect()
        break
        if isCorrect():
            
            while close_modal_btn(driver):
                time.sleep(1)

def start_process():
    ans = input("[AX CPAN BOT ] [INFO ] Are you log-in to crypto-planes (yes, no) : ")
    if ans.lower() in ["yes", "y"]:
        ans = input("[AX CPAN BOT ] [INFO ] Are you Re-fuel your planes (yes, no) : ")
        all_planes_obj = find_planes(driver) 
        auto_play(all_planes_obj, driver)
    else:
        ans = input("[AX CPAN BOT ] [INFO ] Do you want to exit (yes, no) : ") 
        if ans.lower() in ["yes", "y"]:
            return 
        else:
            start_process()

if __name__ == "__main__":
    
    options = webdriver.ChromeOptions()
    options.add_argument("--user-data-dir=C://Users//nutti//AppData//Local//Google//Chrome//User Data")

    # USE THIS IF YOU NEED TO HAVE MULTIPLE PROFILES
    options.add_argument('--profile-directory=Profile 1')

    options.add_argument('--log-level=3')
    try:
        driver = webdriver.Chrome("./chromedriver_win32/chromedriver.exe", options=options)
        wait = WebDriverWait(driver, 20)
        
        
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
        for i in range(5):
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

        # start_process()

        if ":" not in refuel_btn.text:
            print("Refuel all planes", refuel_btn.text)
            refuel_btn.send_keys(Keys.ENTER)

            all_planes_obj = find_planes(driver)
            pprint(all_planes_obj)
        else:
            print("Please wait for ", refuel_btn.text.split(" ")[1])

    except Exception as e:
        print(print_exc())

    finally:
        print("Done")
        driver.close()
        sys.exit(0)
