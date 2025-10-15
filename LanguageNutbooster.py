import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import random
import math
import os

# --- Configuration (Consider moving to a config file for security/flexibility) ---
# It's better not to hardcode credentials directly in the script for security.
# You could use environment variables, a config file, or prompt the user.
# For simplicity in this example, I'll keep them as placeholders.
USERNAME = os.environ.get('LANGUAGENUT_USERNAME') or "your_username_here" # Replace with your Languagenut username
PASSWORD = os.environ.get('LANGUAGENUT_PASSWORD') or "your_password_here" # Replace with your Languagenut password
CHROME_DRIVER_PATH = os.environ.get('CHROME_DRIVER_PATH') # e.g., "/usr/local/bin/chromedriver" or "C:\\path\\to\\chromedriver.exe"

if not USERNAME or USERNAME == "your_username_here":
    print("WARNING: Username is not set. Please set LANGUAGENUT_USERNAME environment variable or update the script.")
if not PASSWORD or PASSWORD == "your_password_here":
    print("WARNING: Password is not set. Please set LANGUAGENUT_PASSWORD environment variable or update the script.")
if not CHROME_DRIVER_PATH:
    print("WARNING: CHROME_DRIVER_PATH is not set. Please set the environment variable or ensure chromedriver is in your PATH.")
    print("Download ChromeDriver from: https://chromedriver.chromium.org/downloads (match your Chrome browser version)")


def login_to_languagenut(username, password, driver_path=None):
    """
    Initializes the WebDriver and logs into Languagenut.
    """
    options = webdriver.ChromeOptions()
    # options.add_argument("--headless")  # Run in headless mode (without opening a browser window)
    options.add_argument("--start-maximized") # Maximize window
    options.add_argument("--disable-gpu") # Disable GPU hardware acceleration
    options.add_argument("--no-sandbox") # Bypass OS security model
    options.add_argument("--disable-dev-shm-usage") # Overcome limited resource problems

    if driver_path:
        driver = webdriver.Chrome(executable_path=driver_path, options=options)
    else:
        # Assumes chromedriver is in PATH if driver_path is not provided
        driver = webdriver.Chrome(options=options)

    driver.get("https://www.languagenut.com/en-gb/member/login/")
    print("Navigated to Languagenut login page.")

    try:
        # Wait for the username field to be present
        username_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "username"))
        )
        username_field.send_keys(username)
        print("Entered username.")

        password_field = driver.find_element(By.ID, "password")
        password_field.send_keys(password)
        print("Entered password.")

        login_button = driver.find_element(By.ID, "loginBtn")
        login_button.click()
        print("Clicked login button.")

        # Wait for the dashboard to load (or for an element specific to logged-in state)
        WebDriverWait(driver, 10).until(
            EC.url_contains("member/dashboard") or EC.url_contains("member/lessons")
        )
        print("Successfully logged in.")
        return driver

    except Exception as e:
        print(f"Login failed: {e}")
        driver.quit()
        return None

def get_target_percentage_from_user():
    """
    Prompts the user for a target percentage and validates the input.
    """
    while True:
        try:
            target_percentage = int(input("Enter the target percentage you want to reach for each task (0-100): "))
            if 0 <= target_percentage <= 100:
                return target_percentage
            else:
                print("Percentage must be between 0 and 100. Please try again.")
        except ValueError:
            print("Invalid input. Please enter a whole number.")

def complete_task(driver, target_percentage):
    """
    Navigates to lessons and completes tasks until the desired percentage is reached.
    """
    driver.get("https://www.languagenut.com/en-gb/member/lessons/")
    print("Navigated to lessons page.")
    time.sleep(3) # Give time for the page to fully load, including percentages

    # Find all lesson links that have a percentage indicator
    lessons = driver.find_elements(By.CSS_SELECTOR, 'a.link.has-percentage')

    if not lessons:
        print("No lessons with percentage found. Exiting.")
        return

    print(f"Found {len(lessons)} lessons.")

    # Iterate through each lesson
    for i, lesson_link in enumerate(lessons):
        try:
            # Re-find the element to avoid StaleElementReferenceException if we navigated away
            # This is crucial because we go back to the lessons page inside the loop
            lessons = driver.find_elements(By.CSS_SELECTOR, 'a.link.has-percentage')
            lesson_link = lessons[i] # Get the current lesson link again

            lesson_title_element = lesson_link.find_element(By.CSS_SELECTOR, 'div.title')
            lesson_title = lesson_title_element.text
            
            percentage_text_element = lesson_link.find_element(By.CSS_SELECTOR, 'div.percentage')
            percentage_text = percentage_text_element.text
            current_percentage = int(percentage_text.replace('%', ''))

            print(f"\n--- Processing Lesson: '{lesson_title}' ---")
            print(f"Current completion: {current_percentage}%")

            if current_percentage < target_percentage:
                print(f"Lesson needs completion. Current: {current_percentage}%, Target: {target_percentage}%")
                lesson_link.click()
                time.sleep(2) # Wait for lesson to load

                # Calculate how many times to click 'next'
                clicks_needed = target_percentage - current_percentage

                print(f"Will perform {clicks_needed} clicks to reach {target_percentage}%.")

                for _ in range(clicks_needed):
                    try:
                        # Wait for the 'next' button to be clickable
                        complete_btn = WebDriverWait(driver, 5).until(
                            EC.element_to_be_clickable((By.CSS_SELECTOR, 'button.button.next-button'))
                        )
                        complete_btn.click()
                        time.sleep(0.5 + random.uniform(0, 0.5)) # Small random delay for human-like interaction
                    except Exception as e:
                        print(f"Could not find or click next button. Error: {e}")
                        print("Assuming section finished or an unexpected element blocked.")
                        break # Exit the inner loop if next button isn't found/clickable

                print(f"Attempted to complete '{lesson_title}' to {target_percentage}%.")
                # After completing a section, navigate back to the main lessons page
                driver.get("https://www.languagenut.com/en-gb/member/lessons/")
                time.sleep(3) # Wait for page to reload and elements to be ready for the next iteration
            else:
                print(f"Lesson already at or above target percentage ({target_percentage}%). No action needed.")

        except selenium.common.exceptions.StaleElementReferenceException:
            print("Stale element reference, re-finding elements for next iteration.")
            # This is handled by re-finding `lessons` at the beginning of the loop
            continue
        except Exception as e:
            print(f"An unexpected error occurred while processing a lesson: {e}")
            # Try to navigate back to lessons page to reset for next iteration
            driver.get("https://www.languagenut.com/en-gb/member/lessons/")
            time.sleep(3)
            continue


def main():
    print("Starting Languagenut Automation Script...")

    # Get target percentage from user
    target_percentage = get_target_percentage_from_user()
    print(f"Target percentage for all tasks set to: {target_percentage}%")

    driver = None
    try:
        driver = login_to_languagenut(USERNAME, PASSWORD, CHROME_DRIVER_PATH)
        if driver:
            complete_task(driver, target_percentage)
            print("\nAutomation complete!")
        else:
            print("Failed to initialize driver or log in. Exiting.")
    except Exception as e:
        print(f"An error occurred in main execution: {e}")
    finally:
        if driver:
            driver.quit()
            print("Browser closed.")

if __name__ == "__main__":
    main()
