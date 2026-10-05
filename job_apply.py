import sys
import os

# Prevent Windows console charmap encoding crashes (cp1252)
if sys.stdout:
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace', line_buffering=True)
    except Exception:
        pass
if sys.stderr:
    try:
        sys.stderr.reconfigure(encoding='utf-8', errors='replace', line_buffering=True)
    except Exception:
        pass

import base64
import json
import requests
import time
import random

# Selenium Imports
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager

# Global Driver Reference
driver = None

#----------------- Configuration & Resume Intelligence -----------------

def load_config():
    """Reads configuration safely from user_config.txt by key-value pairs."""
    config_file = "user_config.txt"
    if not os.path.exists(config_file) and os.path.exists("user_config.example.txt"):
        try:
            import shutil
            shutil.copy("user_config.example.txt", config_file)
        except Exception:
            pass
    config = {
        "API_KEY": "",
        "USER_ID": "",
        "PASSWORD": "",
        "ROLES": "java developer fresher",
        "INPUT_RESUME_PATH": "",
        "YEARS": "0",
        "MONTHS": "0",
        "LINKS": "",
        "JOB_MODE": "Fresher"
    }
    if os.path.exists(config_file):
        with open(config_file, "r", encoding="utf-8") as f:
            for line in f:
                if ":" in line:
                    key, val = line.split(":", 1)
                    config[key.strip()] = val.strip()
    return config

def build_candidate_profile(config):
    """Builds a comprehensive candidate profile using config and resume PDF analysis."""
    resume_path = config.get("INPUT_RESUME_PATH", "").strip()

    # Auto-detect resume if path is empty or invalid
    if not resume_path or not os.path.exists(resume_path):
        candidates = [
            os.path.join(os.environ.get("USERPROFILE", ""), "Downloads", "Barath_R_Resume.pdf"),
            os.path.join(os.environ.get("USERPROFILE", ""), "Downloads", "Barath_R_Resume (1) (1).pdf"),
            os.path.join(os.path.abspath(os.path.dirname(__file__)), "Barath_R_Resume.pdf"),
        ]
        for c in candidates:
            if os.path.exists(c):
                resume_path = c
                break

    profile = {
        "name": "Barath R",
        "first_name": "Barath",
        "last_name": "R",
        "email": config.get("USER_ID", "barath020305@gmail.com"),
        "phone": "9791945156",
        "phone_country_code": "India (+91)",
        "city": "Chennai",
        "full_location": "Chennai, Tamil Nadu, India",
        "alt_city": "Coimbatore, Tamil Nadu, India",
        "degree": "Bachelor of Information Technology",
        "college": "Kamalam College of Arts and Science (Bharathiar University)",
        "university": "Bharathiar University",
        "graduation_year": "2025",
        "github": "https://github.com/Barath025",
        "linkedin": "https://linkedin.com/in/barath-2413b3293",
        "skills": ["Java", "OOP", "Python", "SQL", "Selenium", "Playwright", "Collections", "Multithreading"],
        "experience_years": config.get("YEARS", "0"),
        "experience_months": config.get("MONTHS", "0"),
        "current_ctc": "3 LPA",
        "current_ctc_num": "300000",
        "expected_ctc": "4 LPA",
        "expected_ctc_num": "400000",
        "notice_period": "Immediate",
        "notice_period_days": "0",
        "last_working_day": "05/30/2025",
        "gpa": "75",
        "resume_path": resume_path,
        "summary": "Detail-oriented Computer Science and IT graduate seeking an entry-level Java Developer role with hands-on skills in Java, OOP, database management, and software testing."
    }

    # Extract dynamic info from resume if pypdf is available
    if resume_path and os.path.exists(resume_path):
        try:
            import pypdf
            reader = pypdf.PdfReader(resume_path)
            raw_text = "".join(p.extract_text() for p in reader.pages)
            if "9791945156" in raw_text:
                profile["phone"] = "9791945156"
            if "barath020305@gmail.com" in raw_text:
                profile["email"] = "barath020305@gmail.com"
            print(f"[*] Successfully analyzed resume PDF: {os.path.basename(resume_path)}")
        except Exception as e:
            print(f"[!] Note on resume analysis: {e}")

    return profile

# Load settings & candidate profile
CONFIG = load_config()
PROFILE = build_candidate_profile(CONFIG)

API_KEY           = CONFIG.get("API_KEY", "")
USER_ID           = CONFIG.get("USER_ID", "")
PASSWORD          = CONFIG.get("PASSWORD", "")
ROLES             = CONFIG.get("ROLES", "java developer fresher")
INPUT_RESUME_PATH = PROFILE.get("resume_path", "")
YEARS             = CONFIG.get("YEARS", "0")
MONTHS            = CONFIG.get("MONTHS", "0")
LINKS             = CONFIG.get("LINKS", "")
JOB_MODE          = CONFIG.get("JOB_MODE", "Fresher")

#----------------- Browser Initialization -----------------

def init_driver():
    """Initializes Chrome with Anti-Detection and Persistent Session Profile."""
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    options.add_argument("--lang=en-US")
    options.add_experimental_option('prefs', {
        'intl.accept_languages': 'en-US,en'
    })

    base_dir = os.path.dirname(os.path.abspath(__file__))
    profile_dir = os.path.join(base_dir, "chrome_profile")
    os.makedirs(profile_dir, exist_ok=True)
    options.add_argument(f"--user-data-dir={profile_dir}")

    service = Service(ChromeDriverManager().install())
    try:
        drv = webdriver.Chrome(service=service, options=options)
    except Exception as e:
        print(f"[!] Note on Chrome profile: {e}. Starting standard browser session...")
        fallback_options = webdriver.ChromeOptions()
        fallback_options.add_argument("--start-maximized")
        fallback_options.add_argument("--disable-blink-features=AutomationControlled")
        fallback_options.add_argument("--lang=en-US")
        drv = webdriver.Chrome(service=service, options=fallback_options)

    try:
        drv.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": """
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
            """
        })
    except Exception:
        pass

    return drv

#----------------- Helper Functions -----------------

def click_element_safe(element):
    """Safely clicks an element using multiple methods."""
    try:
        element.click()
        return True
    except Exception:
        try:
            driver.execute_script("arguments[0].click();", element)
            return True
        except Exception:
            try:
                ActionChains(driver).move_to_element(element).click().perform()
                return True
            except Exception:
                return False

def is_logged_in():
    """Checks whether the browser is currently authenticated to LinkedIn."""
    try:
        cur = driver.current_url.lower()
        if any(p in cur for p in ["/feed", "/jobs", "/mynetwork", "/messaging"]):
            return True
        nav = driver.find_elements(
            By.XPATH,
            "//nav[contains(@class, 'global-nav')] | //button[contains(@class, 'global-nav__me')] | //div[contains(@class, 'feed-identity-module')]"
        )
        return len(nav) > 0
    except Exception:
        return False

#----------------- Login Functionality -----------------

def login_to_linkedin(user_id, password):
    """Directly and reliably logs into LinkedIn, with 2FA / CAPTCHA support."""
    print("\n" + "=" * 55)
    print(">> [1/3] CHECKING LINKEDIN LOGIN STATUS...")
    print("=" * 55)

    try:
        driver.get("https://www.linkedin.com/feed/?locale=en_US")
        time.sleep(3)
        if is_logged_in():
            print("[OK] [LOGIN] Already logged in to LinkedIn (persistent session active)!")
            return True
    except Exception as e:
        print(f"   (Session check note: {e})")

    print(">> [LOGIN] Not currently logged in. Navigating to Sign-in page...")
    driver.get("https://www.linkedin.com/login?locale=en_US")
    time.sleep(3)

    username_input = None
    username_xpaths = [
        "//input[@autocomplete='username']",
        "//input[@type='email']",
        "//input[@id='username']",
        "//input[@name='session_key']",
        "//input[@id='session_key']",
        "//input[@type='text']"
    ]
    for xp in username_xpaths:
        elems = driver.find_elements(By.XPATH, xp)
        for el in elems:
            if el.is_displayed():
                username_input = el
                break
        if username_input:
            break

    password_input = None
    password_xpaths = [
        "//input[@autocomplete='current-password']",
        "//input[@type='password']",
        "//input[@id='password']",
        "//input[@name='session_password']",
        "//input[@id='session_password']"
    ]
    for xp in password_xpaths:
        elems = driver.find_elements(By.XPATH, xp)
        for el in elems:
            if el.is_displayed():
                password_input = el
                break
        if password_input:
            break

    if username_input and password_input:
        print(f">> [LOGIN] Entering credentials for '{user_id}'...")
        try:
            username_input.clear()
            time.sleep(0.3)
            username_input.send_keys(user_id)
            time.sleep(0.5)
            password_input.clear()
            time.sleep(0.3)
            password_input.send_keys(password)
            time.sleep(0.5)
        except Exception as e:
            print(f"[!] Error typing credentials: {e}")

        # Click ONLY genuine LinkedIn Sign In button (strictly exclude Microsoft/Apple SSO)
        button_clicked = False
        buttons = driver.find_elements(By.TAG_NAME, "button")
        target_btn = None
        for b in buttons:
            if not b.is_displayed():
                continue
            txt = (b.text or "").strip()
            if any(sso in txt for sso in ["Microsoft", "Apple", "Google", "マイクロソフト", "アップル", "グーグル"]):
                continue
            if txt in ["Sign in", "Sign In", "サインイン", "ログイン"]:
                target_btn = b
                break
            if b.get_attribute("type") == "submit" and not any(sso in txt for sso in ["Microsoft", "Apple", "Google"]):
                target_btn = b
                break

        if target_btn:
            print(f">> [LOGIN] Clicking '{target_btn.text.strip()}' button...")
            try:
                target_btn.click()
                button_clicked = True
            except Exception:
                try:
                    driver.execute_script("arguments[0].click();", target_btn)
                    button_clicked = True
                except Exception:
                    pass

        if not button_clicked:
            print(">> [LOGIN] Submitting via Enter key...")
            try:
                password_input.send_keys(Keys.ENTER)
            except Exception:
                pass
    else:
        print("[!] Could not automatically detect standard login fields.")
        print("[*] If prompted on screen, please log in manually.")

    print(">> [LOGIN] Verifying authentication...")
    max_wait = 90
    start_time = time.time()
    security_prompted = False

    while time.time() - start_time < max_wait:
        time.sleep(2)
        cur_url = driver.current_url.lower()

        if is_logged_in():
            print("[OK] [LOGIN] Login successful! Session is now saved.")
            time.sleep(2)
            return True

        if any(sso in cur_url for sso in ["login.live.com", "microsoft", "apple.com"]):
            print(">> [LOGIN] Detected 3rd-party OAuth redirect. Returning to LinkedIn login...")
            driver.get("https://www.linkedin.com/login?locale=en_US")
            time.sleep(3)
            continue

        is_checkpoint = any(k in cur_url for k in ["checkpoint", "challenge", "verification"])
        page_source = driver.page_source.lower()
        if is_checkpoint or any(k in page_source for k in ["security check", "verification code", "puzzle", "認証"]):
            if not security_prompted:
                print("\n" + "!" * 60)
                print("[!] LINKEDIN SECURITY CHECK / 2FA DETECTED!")
                print("[*] Please solve the CAPTCHA or enter the verification code in the Chrome window.")
                print(">> The bot will automatically detect completion and continue!")
                print("!" * 60 + "\n")
                security_prompted = True
            continue

        error_elems = driver.find_elements(
            By.XPATH,
            "//div[contains(@class, 'alert--error') or contains(@id, 'error-for-password') or contains(@id, 'error-for-username')]"
        )
        if error_elems and any(e.is_displayed() for e in error_elems):
            print("[ERROR] [LOGIN ERROR] Invalid username or password in user_config.txt!")
            print("[*] Please verify your login credentials.")
            return False

    if is_logged_in():
        print("[OK] [LOGIN] Authenticated successfully!")
        return True
    else:
        print("[!] Proceeding with session check...")
        return True

#----------------- Easy Apply & Button Recognition -----------------

def get_easy_apply_button():
    """Finds the Easy Apply button on the current job details panel across languages."""
    try:
        buttons = driver.find_elements(By.XPATH, "//button[contains(@class, 'jobs-apply-button')]")
        for btn in buttons:
            txt = (btn.text or "").strip().lower()
            aria = (btn.get_attribute("aria-label") or "").strip().lower()

            if "applied" in txt or "applied" in aria or "応募済み" in txt or "応募済み" in aria:
                return None

            if any(term in txt or term in aria for term in ["easy apply", "apply", "application", "応募", "カンタン応募", "簡易応募"]):
                return btn

            if btn.is_displayed() and btn.is_enabled():
                return btn

        fallbacks = [
            "//button[contains(., 'Easy Apply')]",
            "//button[contains(., 'Easy Application')]",
            "//button[contains(., 'Application') and not(contains(., 'Applied'))]",
            "//button[contains(., '応募') and not(contains(., '応募済み'))]",
            "//button[contains(@aria-label, 'Easy Apply')]",
            "//button[contains(@aria-label, '応募')]"
        ]
        for xpath in fallbacks:
            found = driver.find_elements(By.XPATH, xpath)
            for f_btn in found:
                if f_btn.is_displayed() and f_btn.is_enabled():
                    f_txt = (f_btn.text or "").lower()
                    if "applied" not in f_txt and "応募済み" not in f_txt:
                        return f_btn
    except Exception:
        pass
    return None

def find_primary_button(labels):
    """Finds a modal wizard button by a list of possible labels (multilingual)."""
    for label in labels:
        try:
            btn = driver.find_element(By.XPATH, f"//button[contains(@aria-label, '{label}')]")
            if btn.is_displayed(): return btn
        except Exception: pass

        try:
            btn = driver.find_element(By.XPATH, f"//button[contains(normalize-space(), '{label}')]")
            if btn.is_displayed(): return btn
        except Exception: pass

        try:
            btn = driver.find_element(By.XPATH, f"//button/span[contains(normalize-space(), '{label}')]")
            if btn.is_displayed(): return btn
        except Exception: pass

    return None

def close_active_modal():
    """Aggressively closes any active modal or confirmation dialog."""
    start_time = time.time()
    while time.time() - start_time < 8:
        if not driver.find_elements(By.CLASS_NAME, "artdeco-modal"):
            return

        done_btns = driver.find_elements(
            By.XPATH,
            "//button[span[contains(normalize-space(), 'Done') or contains(normalize-space(), '完了') or contains(normalize-space(), '閉じる')]]"
        )
        if done_btns and done_btns[0].is_displayed():
            click_element_safe(done_btns[0])
            time.sleep(1)
            continue

        close_selectors = [
            "//button[@aria-label='Dismiss']",
            "//button[@aria-label='閉じる']",
            "//button[contains(@class, 'artdeco-modal__dismiss')]",
            "//button[@data-test-modal-close-btn]",
            "//li-icon[@type='cancel-icon']/.."
        ]
        for sel in close_selectors:
            try:
                btns = driver.find_elements(By.XPATH, sel)
                for btn in btns:
                    if btn.is_displayed():
                        click_element_safe(btn)
                        time.sleep(0.5)
            except Exception: pass

        discard_selectors = [
            "//button[@data-control-name='discard_application_confirm_btn']",
            "//button[contains(., 'Discard') or contains(., '破棄')]",
            "//button[span[contains(text(), 'Discard') or contains(text(), '破棄')]]",
            "//button[contains(@class, 'artdeco-button--primary') and span[contains(text(), 'Discard')]]"
        ]
        for sel in discard_selectors:
            try:
                btns = driver.find_elements(By.XPATH, sel)
                for btn in btns:
                    if btn.is_displayed():
                        click_element_safe(btn)
                        time.sleep(0.8)
            except Exception: pass

        try:
            driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ESCAPE)
            time.sleep(0.5)
        except Exception: pass

#----------------- Form Automation & Smart Fillers -----------------

def handle_resume_upload(modal, profile):
    """Handles resume upload or existing resume selection in the wizard."""
    resume_path = profile.get("resume_path", "")
    
    # 1. Check if a resume is already selected
    try:
        resumes = modal.find_elements(
            By.XPATH, 
            ".//div[contains(@class, 'jobs-document-upload__title') or contains(@class, 'ui-attachment')]"
        )
        if resumes:
            # Existing resume is already present on LinkedIn profile
            return True
    except Exception:
        pass

    # 2. Upload file if file input is present and resume exists
    if resume_path and os.path.exists(resume_path):
        try:
            file_inputs = driver.find_elements(By.XPATH, "//input[@type='file']")
            if file_inputs:
                file_inputs[0].send_keys(resume_path)
                print(f"   [*] Uploaded resume: {os.path.basename(resume_path)}")
                time.sleep(2.5)
                return True
        except Exception as e:
            print(f"   [!] File upload attempt: {e}")

    return False

def handle_location_input(modal, city="Chennai"):
    """Accurately selects the city in LinkedIn's location autocomplete dropdown."""
    try:
        # Match inputs associated with Location or City
        loc_inputs = modal.find_elements(
            By.XPATH,
            ".//input[contains(@id, 'city') or contains(@name, 'city') or contains(@class, 'city') or contains(@aria-label, 'city') or contains(@aria-label, 'location') or @role='combobox']"
        )
        
        # Also check by label
        if not loc_inputs:
            labels = modal.find_elements(By.XPATH, ".//label[contains(translate(., 'LOCATIONCITY', 'locationcity'), 'location') or contains(translate(., 'CITY', 'city'), 'city')]")
            for lbl in labels:
                for_id = lbl.get_attribute("for")
                if for_id:
                    inp = modal.find_elements(By.ID, for_id)
                    if inp: loc_inputs.extend(inp)

        for inp in loc_inputs:
            if not inp.is_displayed(): continue
            curr_val = inp.get_attribute("value") or ""
            
            # Check if this input has a validation error or is empty
            parent = inp.find_element(By.XPATH, "./ancestor::div[contains(@class, 'jobs-easy-apply-form-element') or contains(@class, 'fb-form-element') or parent::div]")
            has_error = len(parent.find_elements(By.CLASS_NAME, "artdeco-inline-feedback__message")) > 0

            if not curr_val or has_error or "chennai" not in curr_val.lower():
                print(f"   [*] Filling location autocomplete: '{city}'...")
                driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", inp)
                time.sleep(0.3)
                click_element_safe(inp)
                time.sleep(0.2)
                
                # Clear completely
                inp.send_keys(Keys.CONTROL + "a")
                inp.send_keys(Keys.BACKSPACE)
                time.sleep(0.3)
                
                # Type city name
                for char in city:
                    inp.send_keys(char)
                    time.sleep(0.04)
                time.sleep(1.2)
                
                # Look for suggestions dropdown
                suggestions = driver.find_elements(
                    By.XPATH,
                    "//div[contains(@class, 'search-typeahead-v2__hit') or contains(@class, 'basic-typeahead__selectable') or @role='option' or contains(@class, 'typeahead')]"
                )
                clicked_suggestion = False
                for sug in suggestions:
                    if sug.is_displayed() and city.lower() in sug.text.lower():
                        click_element_safe(sug)
                        clicked_suggestion = True
                        print(f"   [OK] Selected location suggestion: '{sug.text.strip()}'")
                        break
                        
                if not clicked_suggestion and suggestions and suggestions[0].is_displayed():
                    click_element_safe(suggestions[0])
                    clicked_suggestion = True
                    print(f"   [OK] Selected first location suggestion: '{suggestions[0].text.strip()}'")

                if not clicked_suggestion:
                    # Select via keyboard navigation
                    inp.send_keys(Keys.ARROW_DOWN)
                    time.sleep(0.3)
                    inp.send_keys(Keys.ENTER)
                    time.sleep(0.3)
                    inp.send_keys(Keys.TAB)
                time.sleep(0.5)
    except Exception as e:
        print(f"   [!] Location autocomplete handler notice: {e}")

def handle_all_dropdowns(modal):
    """Selects valid answers for both native <select> and custom dropdowns."""
    # 1. Native <select> elements
    try:
        select_elems = modal.find_elements(By.TAG_NAME, "select")
        for sel_elem in select_elems:
            if not sel_elem.is_displayed(): continue
            try:
                sel = Select(sel_elem)
                curr_text = sel.first_selected_option.text.strip().lower() if sel.all_selected_options else ""
                
                # Trigger selection if unselected, empty, or placeholder
                if not curr_text or "select an option" in curr_text or "choose" in curr_text or curr_text == "":
                    parent_txt = ""
                    try:
                        parent_txt = sel_elem.find_element(
                            By.XPATH, 
                            "./ancestor::div[contains(@class, 'jobs-easy-apply-form-element') or contains(@class, 'fb-form-element') or parent::div]"
                        ).text.lower()
                    except Exception: pass

                    selected = False
                    # Consent, agreement, authorization questions -> Prefer "Yes" / "Agree"
                    if any(k in parent_txt for k in ["consent", "agree", "authorized", "eligible", "profile", "permission", "terms"]):
                        for opt in sel.options:
                            t = opt.text.strip().lower()
                            if t in ["yes", "i agree", "agree", "accept", "true"]:
                                sel.select_by_visible_text(opt.text)
                                selected = True
                                print(f"   [OK] Selected consent dropdown: '{opt.text.strip()}'")
                                break
                    # Sponsorship questions -> Prefer "No"
                    elif any(k in parent_txt for k in ["sponsor", "sponsorship", "visa"]):
                        for opt in sel.options:
                            t = opt.text.strip().lower()
                            if t in ["no", "i do not", "false"]:
                                sel.select_by_visible_text(opt.text)
                                selected = True
                                print(f"   [OK] Selected sponsorship dropdown: '{opt.text.strip()}'")
                                break

                    # Default fallback: pick index 1 (the first genuine option)
                    if not selected and len(sel.options) > 1:
                        sel.select_by_index(1)
                        print(f"   [OK] Selected dropdown option: '{sel.options[1].text.strip()}'")
            except Exception: pass
    except Exception: pass

    # 2. Custom Artdeco / Listbox dropdown buttons
    try:
        custom_btns = modal.find_elements(
            By.XPATH,
            ".//button[contains(@class, 'artdeco-dropdown__trigger') or @aria-haspopup='listbox' or contains(., 'Select an option')]"
        )
        for btn in custom_btns:
            if not btn.is_displayed(): continue
            txt = (btn.text or "").strip().lower()
            if "select an option" in txt or "choose" in txt or not txt:
                try:
                    click_element_safe(btn)
                    time.sleep(0.6)
                    options = driver.find_elements(
                        By.XPATH,
                        "//div[contains(@class, 'artdeco-dropdown__content')]//li | //ul[@role='listbox']//li | //div[@role='option']"
                    )
                    for opt in options:
                        if opt.is_displayed():
                            click_element_safe(opt)
                            print(f"   [OK] Selected custom dropdown item: '{opt.text.strip()}'")
                            break
                except Exception: pass
    except Exception: pass

def handle_radios_and_checkboxes(modal):
    """Answers radio buttons and ticks required checkboxes."""
    # 1. Radio Buttons
    try:
        fieldsets = modal.find_elements(By.TAG_NAME, "fieldset")
        for fs in fieldsets:
            text = fs.text.lower()
            yes_opts = fs.find_elements(By.XPATH, ".//label[contains(translate(., 'YES', 'yes'), 'yes') or contains(., 'はい')]")
            no_opts = fs.find_elements(By.XPATH, ".//label[contains(translate(., 'NO', 'no'), 'no') or contains(., 'いいえ')]")

            checked = fs.find_elements(By.XPATH, ".//input[@type='radio' and @checked]")
            if checked: continue

            if any(k in text for k in ["sponsor", "sponsorship", "visa"]):
                if no_opts: no_opts[0].click()
                elif yes_opts: yes_opts[0].click()
            elif any(k in text for k in ["authorized", "authorization", "legally", "citizen", "relocate", "commute", "travel", "background", "drug", "agree", "consent"]):
                if yes_opts: yes_opts[0].click()
                elif no_opts: no_opts[0].click()
            else:
                if yes_opts: yes_opts[0].click()
                else:
                    all_labels = fs.find_elements(By.TAG_NAME, "label")
                    if all_labels: all_labels[0].click()
    except Exception: pass

    # 2. Checkboxes
    try:
        checkboxes = modal.find_elements(By.XPATH, ".//input[@type='checkbox']")
        for cb in checkboxes:
            if cb.is_displayed() and not cb.is_selected():
                cb.click()
    except Exception: pass

def handle_text_inputs_and_blanks(modal, profile):
    """Fills all text, numeric, date, and textarea inputs from candidate profile."""
    try:
        inputs = modal.find_elements(By.XPATH, ".//input | .//textarea")
        for inp in inputs:
            if not inp.is_displayed(): continue
            inp_type = (inp.get_attribute("type") or "text").lower()
            if inp_type in ["hidden", "checkbox", "radio", "file", "submit", "button"]:
                continue

            curr_val = (inp.get_attribute("value") or "").strip()
            
            # Find associated label text
            label_txt = ""
            inp_id = inp.get_attribute("id")
            if inp_id:
                lbls = modal.find_elements(By.XPATH, f".//label[@for='{inp_id}']")
                if lbls: label_txt = lbls[0].text.lower()
            if not label_txt:
                label_txt = (inp.get_attribute("aria-label") or inp.get_attribute("placeholder") or "").lower()

            # Skip Location (handled specifically by handle_location_input)
            if any(l in label_txt for l in ["location", "city"]) or inp_id and "city" in inp_id.lower():
                continue

            # Check if this input has a validation error
            parent = inp.find_element(By.XPATH, "./ancestor::div[contains(@class, 'jobs-easy-apply-form-element') or contains(@class, 'fb-form-element') or parent::div]")
            has_error = len(parent.find_elements(By.CLASS_NAME, "artdeco-inline-feedback__message")) > 0

            # Only fill if empty or has error
            if curr_val and not has_error:
                continue

            # Clear if error
            if has_error and curr_val:
                try:
                    inp.clear()
                    time.sleep(0.2)
                except: pass

            # Value Resolution
            answer = ""
            if any(p in label_txt for p in ["phone", "mobile"]):
                answer = profile["phone"]
            elif "first name" in label_txt:
                answer = profile["first_name"]
            elif "last name" in label_txt:
                answer = profile["last_name"]
            elif "email" in label_txt:
                answer = profile["email"]
            elif any(s in label_txt for s in ["current ctc", "current annual ctc", "current salary"]):
                answer = profile["current_ctc_num"] if inp_type == "number" else profile["current_ctc"]
            elif any(s in label_txt for s in ["expected ctc", "expected annual ctc", "expected salary"]):
                answer = profile["expected_ctc_num"] if inp_type == "number" else profile["expected_ctc"]
            elif any(n in label_txt for n in ["notice", "notice period", "days to join"]):
                answer = profile["notice_period_days"] if inp_type == "number" else profile["notice_period"]
            elif any(y in label_txt for y in ["year", "experience", "how many years"]):
                answer = "1"
            elif any(d in label_txt for d in ["last working day", "date"]):
                answer = profile["last_working_day"]
            elif "linkedin" in label_txt:
                answer = profile["linkedin"]
            elif "github" in label_txt:
                answer = profile["github"]
            elif any(w in label_txt for w in ["website", "portfolio", "link"]):
                answer = profile["github"]
            elif any(g in label_txt for g in ["gpa", "percentage", "marks"]):
                answer = profile["gpa"]
            elif any(c in label_txt for c in ["college", "university"]):
                answer = profile["university"]
            elif "degree" in label_txt:
                answer = profile["degree"]
            elif inp.tag_name == "textarea":
                answer = profile["summary"]
            else:
                # Generic fallback for required blanks
                if inp_type == "number":
                    answer = "1"
                else:
                    answer = "1"

            if answer:
                try:
                    inp.clear()
                    inp.send_keys(str(answer))
                    print(f"   [*] Filled '{label_txt[:30]}...' -> '{answer}'")
                except Exception: pass
    except Exception: pass

def smart_fill_form(modal, profile):
    """Coordinates all specialized form fillers to guarantee a completely valid form."""
    handle_resume_upload(modal, profile)
    handle_location_input(modal, profile.get("city", "Chennai"))
    handle_all_dropdowns(modal)
    handle_radios_and_checkboxes(modal)
    handle_text_inputs_and_blanks(modal, profile)

    # Optional AI assistant if API key is valid
    if API_KEY and API_KEY.startswith("AIza"):
        try:
            ai_solver()
        except Exception:
            pass

def ai_solver():
    """Uses Gemini API to solve complex application questions if a valid API key is present."""
    if not API_KEY or not API_KEY.startswith("AIza"):
        return False

    modals = driver.find_elements(By.CLASS_NAME, "artdeco-modal")
    if not modals: return False
    modal = modals[0]

    try:
        screenshot = modal.screenshot_as_png
        b64_image = base64.b64encode(screenshot).decode('utf-8')

        prompt = f"""
        You are an expert candidate filling out a job application form on LinkedIn.
        Candidate Profile:
        - Email: {PROFILE['email']}
        - Target Role: {ROLES}
        - Total Experience: {PROFILE['experience_years']} years (Fresher)
        - Location: {PROFILE['full_location']}
        - Phone: {PROFILE['phone']}
        - Current CTC: {PROFILE['current_ctc']}
        - Expected CTC: {PROFILE['expected_ctc']}
        - Notice Period: {PROFILE['notice_period']}
        - Authorized to work: Yes
        - Sponsorship required: No
        - Skills: Java, OOP, Python, SQL, Selenium, Playwright
        
        Return a JSON array of objects for EVERY input field visible in the image.
        Format: [{{"label": "exact_text_from_screen", "type": "text|radio|dropdown|checkbox", "answer": "precise_value_to_fill"}}]
        """

        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}"
        headers = {'Content-Type': 'application/json'}
        data = { "contents": [{ "parts": [{"text": prompt}, {"inline_data": {"mime_type": "image/png", "data": b64_image}}] }] }

        response = requests.post(url, headers=headers, json=data, timeout=10)
        result = response.json()

        if 'candidates' not in result or not result['candidates']:
            return False

        text_response = result['candidates'][0]['content']['parts'][0]['text']
        if "```json" in text_response: text_response = text_response.split("```json")[1].split("```")[0].strip()
        elif "```" in text_response: text_response = text_response.split("```")[1].split("```")[0].strip()

        ai_data = json.loads(text_response)
        if isinstance(ai_data, dict): ai_data = [ai_data]

        for item in ai_data:
            answer = item.get("answer")
            q_type = item.get("type", "text")
            label_text = item.get("label", "")
            
            inputs = modal.find_elements(By.XPATH, f".//input[contains(@aria-label, '{label_text}')] | .//textarea[contains(@aria-label, '{label_text}')]")
            if inputs:
                inp = inputs[0]
                if q_type in ["text", "numeric", "textarea"]:
                    inp.clear()
                    inp.send_keys(str(answer))
                elif q_type == "radio":
                    xpath = f".//label[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{str(answer).lower()}')]"
                    modal.find_element(By.XPATH, xpath).click()

        return True
    except Exception:
        return False

#----------------- Application Flow -----------------

def handle_application_flow():
    """Handles the wizard steps (Next -> Review -> Submit) with comprehensive auto-filling."""
    max_steps = 25
    step = 0
    stuck_count = 0

    while step < max_steps:
        step += 1
        time.sleep(1.5)

        modals = driver.find_elements(By.CLASS_NAME, "artdeco-modal")
        if not modals:
            return True

        modal = modals[0]

        # 1. Fill all fields on the current screen
        smart_fill_form(modal, PROFILE)
        time.sleep(0.8)

        # 2. Check for Validation Errors
        errors = modal.find_elements(
            By.XPATH,
            ".//div[contains(@class, 'artdeco-inline-feedback--error')] | .//span[contains(@class, 'artdeco-inline-feedback__message')]"
        )
        if errors and any(e.is_displayed() for e in errors):
            print("   [!] Validation errors detected. Applying targeted corrections...")
            smart_fill_form(modal, PROFILE)
            stuck_count += 1
            if stuck_count > 4:
                print("   [ERROR] Cannot satisfy custom validation requirements. Skipping job.")
                return False
            time.sleep(1)

        # 3. Look for Primary Action Buttons
        submit_btn = find_primary_button([
            "Submit application", "Submit", "応募を送信", "送信", "応募する", "確定して応募"
        ])
        review_btn = find_primary_button([
            "Review your application", "Review", "確認", "次へ進む"
        ])
        next_btn = find_primary_button([
            "Continue to next step", "Next", "Continue", "次へ", "進む"
        ])

        # 4. Action: Submit
        if submit_btn:
            print("   >> Clicking 'Submit Application'...")
            click_element_safe(submit_btn)
            time.sleep(3)
            close_active_modal()
            return True

        # 5. Action: Review
        if review_btn:
            print("   >> Clicking 'Review'...")
            click_element_safe(review_btn)
            time.sleep(1.5)
            continue

        # 6. Action: Next
        if next_btn:
            print("   >> Clicking 'Next'...")
            prev_html = modal.get_attribute("innerHTML") if modal else ""

            click_element_safe(next_btn)
            time.sleep(1.5)

            curr_html = modal.get_attribute("innerHTML") if driver.find_elements(By.CLASS_NAME, "artdeco-modal") else ""

            if prev_html == curr_html:
                print("   [!] Wizard did not advance. Running smart correction...")
                smart_fill_form(modal, PROFILE)
                stuck_count += 1
                if stuck_count > 4:
                    print("   [ERROR] Wizard stuck. Skipping job.")
                    return False
            else:
                stuck_count = 0
            continue

        # 7. Fallback if no button recognized
        smart_fill_form(modal, PROFILE)
        time.sleep(1)
        stuck_count += 1
        if stuck_count > 5:
            return False

    return False

def process_page_jobs():
    """Processes all jobs on the current search page."""
    applied_count = 0
    card_selectors = [
        "job-card-container",
        "jobs-search-results__list-item",
        "scaffold-layout__list-item"
    ]
    base_selector = None
    for sel in card_selectors:
        if driver.find_elements(By.CLASS_NAME, sel):
            base_selector = sel
            break

    if not base_selector:
        base_selector = "job-card-container"

    initial_cards = driver.find_elements(By.CLASS_NAME, base_selector)
    count_jobs = len(initial_cards)
    print(f">> Found {count_jobs} jobs on this page.")

    for i in range(count_jobs):
        try:
            close_active_modal()

            current_cards = driver.find_elements(By.CLASS_NAME, base_selector)
            if i >= len(current_cards):
                break
            card = current_cards[i]

            driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", card)
            time.sleep(1)
            click_element_safe(card)
            time.sleep(2)

            title = f"Job #{i+1}"
            try:
                title_elem = driver.find_element(
                    By.XPATH,
                    "//h1[contains(@class, 'job-details-jobs-unified-top-card__job-title')] | //h2[contains(@class, 'job-details-jobs-unified-top-card__job-title')] | //h1 | //a[contains(@class, 'job-card-list__title')]"
                )
                if title_elem.text.strip():
                    title = title_elem.text.strip()
            except Exception:
                pass

            print(f"\n[{i+1}/{count_jobs}] Evaluating: {title}")

            apply_btn = get_easy_apply_button()
            if not apply_btn:
                print("   -- Skipped (Not Easy Apply or already applied).")
                continue

            print("   >> Easy Apply found! Starting application...")
            click_element_safe(apply_btn)
            time.sleep(2)

            if handle_application_flow():
                print(f"   [SUCCESS] Successfully applied to '{title}'!")
                applied_count += 1
            else:
                print(f"   [FAILED] Could not complete application for '{title}'.")

            close_active_modal()
            time.sleep(1)

        except Exception as e:
            print(f"   [!] Job processing notice: {e}")
            close_active_modal()

    return applied_count

#----------------- Main Execution Routine -----------------

def main():
    global driver, API_KEY, USER_ID, PASSWORD, ROLES, INPUT_RESUME_PATH, YEARS, MONTHS, LINKS, JOB_MODE, PROFILE

    config = load_config()
    PROFILE = build_candidate_profile(config)

    API_KEY           = config.get("API_KEY", "")
    USER_ID           = config.get("USER_ID", "")
    PASSWORD          = config.get("PASSWORD", "")
    ROLES             = config.get("ROLES", "java developer fresher")
    INPUT_RESUME_PATH = PROFILE.get("resume_path", "")
    YEARS             = config.get("YEARS", "0")
    MONTHS            = config.get("MONTHS", "0")
    LINKS             = config.get("LINKS", "")
    JOB_MODE          = config.get("JOB_MODE", "Fresher")

    print("\n" + "=" * 60)
    print("           [*] STARK LINKEDIN AUTO APPLICANT BOT           ")
    print("=" * 60)
    print(f"Candidate Name   : {PROFILE['name']}")
    print(f"Candidate Email  : {USER_ID}")
    print(f"Target Roles     : {ROLES}")
    print(f"Location         : {PROFILE['city']} ({PROFILE['full_location']})")
    print(f"Resume Path      : {INPUT_RESUME_PATH or 'Using LinkedIn Profile Resume'}")
    print(f"Job Mode         : {JOB_MODE}")
    print("=" * 60)

    if not USER_ID or not PASSWORD:
        print("[ERROR] LinkedIn credentials missing in user_config.txt!")
        print("[*] Please configure user_config.txt or run 'py app.py'.")
        return

    print("\n>> Initializing Chrome Browser with Anti-Detection and Session Persistence...")
    driver = init_driver()

    try:
        # Step 1: Direct LinkedIn Login Verification
        logged_in = login_to_linkedin(USER_ID, PASSWORD)
        if not logged_in:
            print("[ERROR] Cannot proceed with job applications without logging in.")
            return

        # Step 2: Search & Apply for Roles
        roles_list = [r.strip() for r in ROLES.split(',') if r.strip()]
        total_applied = 0

        print("\n" + "=" * 60)
        print(">> [2/3] STARTING AUTOMATED JOB SEARCH & APPLICATIONS...")
        print("=" * 60)

        for role in roles_list:
            print(f"\n==================================================")
            print(f"   SEARCHING ROLE: {role.upper()}")
            print(f"==================================================")

            encoded_role = requests.utils.quote(role)
            search_url = f"https://www.linkedin.com/jobs/search/?keywords={encoded_role}&f_AL=true&locale=en_US"
            driver.get(search_url)
            time.sleep(4)

            for page in range(5):
                print(f"\n--- [PAGE {page + 1}] ---")
                count = process_page_jobs()
                total_applied += count

                try:
                    next_page_btn = driver.find_element(
                        By.XPATH,
                        f"//button[@aria-label='Page {page+2}'] | //button[contains(@aria-label, 'page {page+2}')]"
                    )
                    if next_page_btn.is_displayed():
                        print(f">> Advancing to Page {page + 2}...")
                        click_element_safe(next_page_btn)
                        time.sleep(4)
                    else:
                        break
                except Exception:
                    print(">> Reached end of search results for this role.")
                    break

        print("\n" + "=" * 60)
        print(f"[OK] [3/3] PROTOCOL COMPLETE! Total Jobs Applied: {total_applied}")
        print("=" * 60)
        time.sleep(5)

    except KeyboardInterrupt:
        print("\n>> Process interrupted by user.")
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {e}")
    finally:
        print(">> Closing browser session...")
        try:
            driver.quit()
        except Exception:
            pass

if __name__ == "__main__":
    main()
