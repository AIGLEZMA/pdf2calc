import os
import sys
import shutil
import subprocess
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import random
from selenium.common.exceptions import NoSuchElementException

def compress_pdf(input_pdf, output_pdf):
    if shutil.which("gswin64c") is None:
        print("❌ Error: Ghostscript (gswin64c) is not installed or not in PATH.")
        sys.exit(1)

    gs_command = [
        "gswin64c",
        "-sDEVICE=pdfwrite",
        "-dCompatibilityLevel=1.4",
        "-dPDFSETTINGS=/ebook",
        "-r72",
        "-dDownsampleColorImages=true",
        "-dColorImageResolution=72",
        "-dNOPAUSE", "-dBATCH", "-dQUIET",
        f"-sOutputFile={output_pdf}",
        input_pdf
    ]

    try:
        subprocess.run(gs_command, check=True)
        original_size = os.path.getsize(input_pdf)
        compressed_size = os.path.getsize(output_pdf)

        print(f"📄 Original size: {original_size / 1024:.2f} KB")
        print(f"📦 Compressed size: {compressed_size / 1024:.2f} KB")

        if compressed_size < original_size:
            print(f"✅ Compression was successful: {output_pdf}")
        else:
            print("⚠️ Compression didn't reduce size, keeping original file.")
            os.remove(output_pdf)
            os.rename(input_pdf, output_pdf)
            
    except Exception as e:
        print(f"❌ Error: {e}")

def get_accounts():
    current_directory = os.path.dirname(os.path.abspath(__file__))
    
    file_path = os.path.join(current_directory, "accounts.txt")
    
    accounts = []
    try:
        with open(file_path, 'r') as file:
            for line in file:
                account_info = line.strip().split(':')
                if len(account_info) == 2:
                    username, password = account_info
                    accounts.append({"username": username, "password": password})
    except FileNotFoundError:
        print(f"❌ Error: The file {file_path} was not found.")
    print("📄 Found", len(accounts), "account(s)")
    return accounts

def setup_driver(download_path):
    download_path = os.path.abspath(download_path)
    """ if not os.path.exists(download_path):
        os.makedirs(download_path) """

    options = webdriver.EdgeOptions()
    options.add_argument("--silent")
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-logging')
    options.add_argument("--log-level=3")
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    options.add_argument("--start-maximized")
    options.add_argument("--headless")
    prefs = {
        "download.default_directory": download_path,
        "download.prompt_for_download": False,
        "directory_upgrade": True
    }
    options.add_experimental_option("prefs", prefs)
    driver = webdriver.Edge(options=options)
    return driver

def login(driver, username, password):
    print("📄 Logging in with account:", username, "...")
    driver.get("https://tiplanet.org/forum/editgx.php")
    time.sleep(2)
    
    driver.find_element(By.ID, "username").send_keys(username)
    driver.find_element(By.ID, "password").send_keys(password)
    driver.find_element(By.NAME, "login").click()
    
    time.sleep(3)
    try:
        driver.find_element(By.XPATH, "//span[contains(text(), 'You have reached the number of maximum generations per day')]")
        print("❌ Generation limit reached.")
        return False
    except NoSuchElementException:
        print(f"✅ Logged in successfully with account: {username}")
        return True

def select_hp_prime(driver):
    time.sleep(2)
    driver.find_element(By.XPATH, "//a[contains(text(), 'Prime')]").click()
    time.sleep(3)
    print("✅ HP Prime option selected!")

def select_nspire(driver):
    time.sleep(2)
    print("✅ TI Nspire option is selected by default!")

def enter_name(driver, name):
    name_input = driver.find_element(By.ID, "name_input")
    name_input.clear()
    name_input.send_keys(name)
    print(f"✅ Name '{name}' entered!")

def upload_pdf(driver, pdf_path):
    if not os.path.isabs(pdf_path):
        pdf_path = os.path.abspath(pdf_path)
    
    file_input = driver.find_element(By.NAME, "img0")
    file_input.send_keys(pdf_path)
    print(f"✅ PDF file '{pdf_path}' uploaded!")

def click_download_button(driver):
    try:
        try:
            checkbox = driver.find_element(By.NAME, "rulesOK")
            if not checkbox.is_selected():
                checkbox.click()
                print("✅ Checkbox 'rulesOK' has been checked.")
        except NoSuchElementException:
            print("⚠️ Checkbox 'rulesOK' not found. Skipping...")

        download_button = driver.find_element(By.ID, "downloadButton")
        download_button.click()
        print("✅ Conversion started...")
    except Exception as e:
        print(f"❌ Error clicking the download button: {e}")


def wait_for_new_download(download_folder, timeout=60):
    existing_files = set(os.listdir(download_folder))
    start_time = time.time()

    while time.time() - start_time < timeout:
        current_files = set(os.listdir(download_folder))
        new_files = current_files - existing_files

        if new_files:
            if not any(f.endswith(".crdownload") for f in new_files):
                finished_file = list(new_files)[0]
                return os.path.join(download_folder, finished_file)

        time.sleep(1)

    raise TimeoutError("❌ Download did not complete within the timeout period.")

if __name__ == "__main__":
    if len(sys.argv) < 5:
        print("❌ Error: Missing mandatory arguments. Usage: py convert.py <name> <input pdf> <output folder> <mode=[ti|prime]> [<compress>]")
        sys.exit(1)

    name = sys.argv[1]
    if len(name) < 8:
        print("❌ Error: Name must be at least 8 characters long.")
        sys.exit(1)
    input_pdf = sys.argv[2]
    output_folder = sys.argv[3]
    mode = sys.argv[4].lower()

    if mode not in ("ti", "prime"):
        print(f"❌ Error: Invalid mode '{mode}'. Must be either 'ti' or 'prime'.\n")

    compress = sys.argv[5].lower() if len(sys.argv) >= 6 else None

    if not os.path.isfile(input_pdf):
        print(f"❌ Error: Input PDF file '{input_pdf}' does not exist.")
        sys.exit(1)

    if not os.path.isdir(output_folder):
        print(f"❌ Error: Output folder '{output_folder}' does not exist.")
        sys.exit(1)

    pdf_name = os.path.splitext(os.path.basename(input_pdf))[0]
    if not output_folder.endswith(os.path.sep):
        output_folder += os.path.sep

    output_pdf = os.path.join(output_folder, pdf_name + "_c.pdf")
    if compress:
        compress_pdf(input_pdf, output_pdf)
    else:
        print(f"✅ Skipping compression, using the original file: {input_pdf}")
    
    to_convert = input_pdf if not compress else output_pdf
    
    accounts = get_accounts()
    tried_accounts = set()

    while True:
        account = random.choice(accounts)
        print("⚠️ Account:", account["username"], ", already tried accounts:", tried_accounts)
        available_accounts = [account for account in accounts if account["username"] not in tried_accounts]
        if not available_accounts:
            print("❌ All accounts have reached the generation limit. Exiting.")
            sys.exit(1)

        driver = setup_driver(output_folder)
        
        try:
            if not login(driver, account["username"], account["password"]):
                tried_accounts.add(account["username"])
                print("❌ Generation limit reached or login failed, retrying with another account. (current: ", account["username"], ")")
                driver.quit()
                continue

            if mode == "prime":
                select_hp_prime(driver)
            else:
                select_nspire(driver)
            enter_name(driver, name)
            upload_pdf(driver, to_convert)
            click_download_button(driver)
            print("✅ Please wait for the download to complete...")
            wait_for_new_download(output_folder)
            print("✅ Download completed!")
            
            driver.quit()
            sys.exit()
            break
        
        except Exception as e:
            print(f"❌ Error: {e}")
            driver.quit()
            time.sleep(3)