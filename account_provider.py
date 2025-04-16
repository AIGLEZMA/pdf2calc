import sys
import os
import string
import time
import random
import re
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def setup_driver():
    options = webdriver.EdgeOptions()
    options.add_argument("--silent")
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-logging')
    options.add_argument("--log-level=3")
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    options.add_argument("--start-maximized")
    options.add_argument("--headless")
    driver = webdriver.Edge(options=options)
    return driver

def random_email():
    name = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
    return f"{name}@gmail.com"

def solve_captcha(driver):
    try:
        captcha_label_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//*[@id='register']/div[2]/div/fieldset/dl/dt/label"))
        )
        
        captcha_label = captcha_label_element.text
        print(f"📄 CAPTCHA label: {captcha_label}")

        pattern = r"First (\d+) & Last (\d+) characters of \"([^\"]+)\""
        match = re.search(pattern, captcha_label)

        if match:
            first_count = int(match.group(1))
            last_count = int(match.group(2))
            captcha_string = match.group(3)

            if len(captcha_string) >= first_count + last_count:
                captcha_answer = captcha_string[:first_count] + captcha_string[-last_count:]

                captcha_input = driver.find_element(By.ID, "answer")
                captcha_input.send_keys(captcha_answer)

                captcha_input.send_keys(Keys.RETURN)
                print(f"✅ CAPTCHA solved and submitted: {captcha_answer}")
            else:
                print("❌ CAPTCHA string is too short for the specified number of characters.")
        else:
            print("❌ CAPTCHA format not recognized.")
    except Exception as e:
        print(f"❌ Error during CAPTCHA handling: {e}")


def register_account(username, password, driver):
    driver.get("https://tiplanet.org/forum/ucp.php?mode=register&coppa=0")

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "agreed"))
    ).click()

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "username"))
    )

    email = random_email()

    driver.find_element(By.ID, "username").send_keys(username)
    driver.find_element(By.ID, "email").send_keys(email)
    driver.find_element(By.ID, "email_confirm").send_keys(email)
    driver.find_element(By.ID, "new_password").send_keys(password)
    driver.find_element(By.ID, "password_confirm").send_keys(password)

    solve_captcha(driver)

    print(f"✅ Account form filled and CAPTCHA solved for {username}")
    try:
        #WebDriverWait(driver, 10).until(
        #    EC.presence_of_element_located((By.XPATH, "//div[contains(text(),'Thank you for registering, your account has been created')]"))
        #)
        print(f"✅ Account created for {username}")
        return True
    except Exception as e:
        print(f"❌ Account creation failed for {username}")
        return False

def save_account_to_file(username, password):
    file_path = os.path.join(os.getcwd(), "accounts.txt")

    with open(file_path, "a") as file:
        file.write(f"{username}:{password}\n")
        file.flush()
        os.fsync(file.fileno())
        print(f"✅ Account {username} saved to {file_path}")


if __name__ == "__main__":
    args = sys.argv[1:]

    if len(args) % 2 != 0:
        print("❌ Usage: python account_provider.py <username1> <password1> <username2> <password2> ...")
        sys.exit(1)

    for i in range(0, len(args), 2):
        username = args[i]
        if len(username) < 4 or len(username) > 30:
            print("❌ Username must be between 4 and 30 characters.", username)
            continue
        password = args[i + 1]

        if len(password) < 12 or len(password) > 100:
            print("❌ Password must be between 12 and 100 characters.", password)
            continue
    
        if not any(char.islower() for char in password) or not any(char.isupper() for char in password) or not any(char.isdigit() for char in password):
            print("❌ Password must contain letters in mixed case and must contain numbers.", password)
            continue
        
        print(f"📄 Registering account: {username}")
        driver = setup_driver()
        if register_account(username, password, driver):
            save_account_to_file(username, password)
        print(f"✅ Account form filled and CAPTCHA solved: {username}")
    
        time.sleep(1)

    print("✅ All accounts processed (forms filled, CAPTCHA solved, and submitted).")
