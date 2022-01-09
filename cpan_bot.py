import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from random import randint, shuffle
from traceback import print_exc
from pprint import pprint
import sys 

def find_planes(dv):
    result = []
    cnt = 0
    for index in range(20):
        div_index  = index+1
        try:
            rarity = dv.find_element_by_xpath(f'//*[@id="app"]/div[1]/div/div[2]/div[{div_index}]/div/span')
            _id = dv.find_element_by_xpath(f'//*[@id="app"]/div[1]/div/div[2]/div[{div_index}]/div/div[2]/span')
            name = dv.find_element_by_xpath(f'//*[@id="app"]/div[1]/div/div[2]/div[{div_index}]/div/div[4]/div[1]/p[2]')
            fuel =  dv.find_element_by_xpath(f'//*[@id="app"]/div[1]/div/div[2]/div[{div_index}]/div/div[5]/div[6]/span/span')
            btn = dv.find_element_by_xpath(f'//*[@id="app"]/div[1]/div/div[2]/div[{div_index}]/div/div[6]/div/div[1]/button')
            tmp = {
                "rarity" : rarity.text,
                "id" : _id.text,
                "name" : name.text,
                "fuel" : int(fuel.text.split("/")[0]),
                "btn" : btn
            }
            result.append(tmp)
            cnt += 1
        except Exception as e:
            print(e)
            break
    
    print("found ", cnt, "planes ")
    return result


def auto_play(planes):
    planes = [{'btn': '<selenium.webdriver.remote.webelement.WebElement (session="94454c62ae861b8be4a67ce893509dba", element="bfb5feb2-bb40-4b24-849b-7afb5248c431")>',
  'fuel': 60,
  'id': '#180307',
  'name': 'TWINPYRE',
  'rarity': 'COMMON'},
 {'btn': '<selenium.webdriver.remote.webelement.WebElement (session="94454c62ae861b8be4a67ce893509dba", element="fac777e2-f147-4235-8621-fd2c0fa4b857")>',
  'fuel': 60,
  'id': '#88779',
  'name': 'SKYRAID',
  'rarity': 'COMMON'},
 {'btn': '<selenium.webdriver.remote.webelement.WebElement (session="94454c62ae861b8be4a67ce893509dba", element="73c7202c-333e-4dd0-a65c-21bfb6557c2b")>',
  'fuel': 60,
  'id': '#76963',
  'name': 'SKYRAID',
  'rarity': 'COMMON'},
 {'btn': '<selenium.webdriver.remote.webelement.WebElement (session="94454c62ae861b8be4a67ce893509dba", element="46ef73ed-3e01-4fcf-936e-540451f96e5b")>',
  'fuel': 60,
  'id': '#62967',
  'name': 'WATER BOATMEN',
  'rarity': 'CLASSIC'},
 {'btn': '<selenium.webdriver.remote.webelement.WebElement (session="94454c62ae861b8be4a67ce893509dba", element="36c91c58-2d11-4ef4-97c0-16703d91a12c")>',
  'fuel': 60,
  'id': '#62963',
  'name': 'SKYRAID',
  'rarity': 'COMMON'}]

    ## random order to play 
    ## Create all turn list
    all_turn = []
    for p in planes:
        [ all_turn.append(p) for i in range(p["fuel"]//15) ] 
    
    ## Caculate number of 
    [ shuffle(all_turn) for i in range(randint(2, 6))] 

    for t in all_turn:
        btn = t["btn"]
        btn.click()
        time.sleep(30)

        



def start_process():
    ans = input("[AX CPAN BOT ] [INFO ] Are you log-in to crypto-planes (yes, no) : ")
    if ans.lower() in ["yes", "y"]:
        ans = input("[AX CPAN BOT ] [INFO ] Are you Re-fuel your planes (yes, no) : ")
        all_planes_obj = find_planes(driver) 
        pprint(all_planes_obj)
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
        time.sleep(2)
        driver.get('https://cryptoplanes.me/play/#/planes')
        time.sleep(8)
        start_process()
        
    except Exception as e:
        print(print_exc())

    finally:
        print("Done")

    driver = ""
    auto_play([])


