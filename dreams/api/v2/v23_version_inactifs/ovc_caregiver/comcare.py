from datetime import datetime
date_du_jour = datetime.today().strftime("%Y-%m-%d")
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import os
#from sys import path
#path.insert(0, '../core')
from decouple import config
from dotenv import load_dotenv


load_dotenv('id_cc.env')
email = os.getenv('COMCARE_EMAIL')
password_cc = os.getenv('COMCARE_PASSWORD')

#Defining the driver
driver = webdriver.Chrome(ChromeDriverManager().install())
driver.implicitly_wait(1000)

#Creating login function
def caregiver_KAP():
    driver.get(
        'https://www.commcarehq.org/a/caris-test/data/export/custom/new/form/download/40c7b4a7a15d3dc7d1b60ba9e5a26304/'
    )
    #driver.find_element_by_xpath('//*[@id="id_auth-username"]').send_keys(email)
    driver.find_element(By.XPATH,'//*[@id="id_auth-username"]').send_keys(email)
    #driver.find_element_by_xpath('//*[@id="id_auth-password"]').send_keys(password_cc)
    driver.find_element(By.XPATH,'//*[@id="id_auth-password"]').send_keys(password_cc)
    driver.find_element(By.CSS_SELECTOR,'button[type=submit]').click()

#Muso beneficiaries
caregiver_KAP()

#Download the database "All gardens"
#driver.find_element_by_xpath('//*[@id="download-export-form"]/form/div[2]/div/div[2]/div[1]/button/span[1]').click()
driver.find_element(By.XPATH,"//*[@id='download-export-form']/form/div[2]/div/div[2]/div[1]/button/span[1]").click()
#driver.find_element_by_xpath('//*[@id="download-progress"]/div/div/div[2]/div[1]/form/a/span[1]').click()    
driver.find_element(By.XPATH,"//*[@id='download-progress']/div/div/div[2]/div[1]/form/a/span[1]").click()

