import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# --- NEW/CHANGED: Helper function to set up WebDriver for Codespaces ---
def get_webdriver():
    """
    Initializes and returns a Chrome WebDriver suitable for GitHub Codespaces.
    Runs in headless mode and uses webdriver-manager for automatic driver installation.
    """
    chrome_options = Options()
    chrome_options.add_argument("--headless")           # Run Chrome without a UI (essential for Codespaces)
    chrome_options.add_argument("--no-sandbox")         # Required for some Linux environments like Codespaces
    chrome_options.add_argument("--disable-dev-shm-usage") # Overcomes limited resource problems in some envs
    # You can add other options here, e.g., to set window size
    # chrome_options.add_argument("--window-size=1920,1080")

    # Use webdriver_manager to automatically download and manage the ChromeDriver
    service = ChromeService(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

# --- NEW/CHANGED: Main automation logic function ---
def automate_languagenut():
    driver = None
    try:
        driver = get_webdriver()
        print("WebDriver initialized. Navigating to LanguageNut...")
        driver.get("https://languagenut.com")

        print("Page title:", driver.title)

        # --- REPLACED/UPDATED: Use WebDriverWait for more robust waiting ---
        # Wait for the username field to be present before trying to interact with it
        WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.ID, "username")))
        
        # --- REPLACED/UPDATED: Use modern By locators (find_element_by_* is deprecated) ---
        username_field = driver.find_element(By.ID, "username")
        password_field = driver.find_element(By.ID, "password")

        # --- NEW/CHANGED: Get credentials from environment variables for security ---
        # Set these environment variables in your Codespace secrets or directly in the terminal
        # Example: export LANGUAGENUT_USERNAME="your_username"
        #          export LANGUAGENUT_PASSWORD="your_password"
        # If not set, it will use placeholder values (which will likely fail login)
        languagenut_username = os.getenv("LANGUAGENUT_USERNAME", "YOUR_LANGUAGENUT_USERNAME_HERE")
        languagenut_password = os.getenv("LANGUAGENUT_PASSWORD", "YOUR_LANGUAGENUT_PASSWORD_HERE")

        username_field.send_keys(languagenut_username)
        password_field.send_keys(languagenut_password)

        login_button = driver.find_element(By.NAME, "login")
        login_button.click()
        print("Attempted login with provided credentials.")

        # --- NEW/CHANGED: Wait for login redirect or dashboard element ---
        # Adjust this wait condition based on what happens after a successful login
        # For example, wait until the URL changes or a specific element on the dashboard appears.
        try:
            WebDriverWait(driver, 20).until(EC.url_changes("https://languagenut.com"))
            print("Login successful (page URL changed). Current URL:", driver.current_url)
            # You might want to add another wait for a specific element on the dashboard
            # For instance: WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "dashboard-header")))
        except:
            print("Login redirect or dashboard element not found within timeout. Check credentials or page.")
            print(f"Current URL: {driver.current_url}")
            # Optionally, take a screenshot for debugging
            # driver.save_screenshot("login_failed_screenshot.png")
            return # Exit if login likely failed

        # --- YOUR ORIGINAL SCRIPT'S LOGIC (UNCOMMENTED AND ADAPTED) ---
        # Now, implement your specific LanguageNut booster automation logic here.
        # This section will contain the steps to navigate through games, answer questions, etc.
        print("\n--- Starting LanguageNut Automation ---")
        print("Current page after login:", driver.current_url)

        # Example from your gist (make sure this XPath is still valid on languagenut.com)
        # Use WebDriverWait for element visibility/presence if navigating to new pages or waiting for content
        try:
            # You might need to navigate to a specific page or wait for an element to appear
            # e.g., driver.get("https://languagenut.com/dashboard/games")
            
            # --- REPLACED/UPDATED: Wait for the element instead of static time.sleep ---
            score_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="app"]/div[2]/div[1]/h1'))
            )
            print(f"Current Score: {score_element.text}")
            
            # Example: Click on a game or a specific button if it exists after login
            # game_button = WebDriverWait(driver, 10).until(
            #     EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Start New Game')]"))
            # )
            # game_button.click()
            # print("Clicked 'Start New Game'.")

            # Add more specific steps here for the LanguageNut booster process...
            time.sleep(5) # A short static sleep for demonstration, prefer WebDriverWait in real scenarios

        except Exception as e:
            print(f"Error during post-login automation: {e}")

    except Exception as e:
        print(f"An error occurred during overall automation setup or execution: {e}")
    finally:
        if driver:
            driver.quit()
            print("WebDriver closed.")

# --- NEW/CHANGED: Standard Python entry point ---
if __name__ == "__main__":
    automate_languagenut()
