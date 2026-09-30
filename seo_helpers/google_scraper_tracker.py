#automated Google SERP (Search Engine Results Page) scraper and tracker.
#query Google for a list of keywords, analyze the search result layout, and automatically log the findings directly into a Google Sheet.
import time
import gspread
import pandas as pd
from datetime import datetime
from google.oauth2.service_account import Credentials
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

# 🔹 Google Sheets Authentication
creds = Credentials.from_service_account_file(
    "lakshmi-gsc-auth.json",
    scopes=["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/spreadsheets"]
)
client = gspread.authorize(creds)

# 🔹 Open Google Sheet
spreadsheet = client.open("SEO SERP Tracking")  # Replace with your sheet name
tracking_sheet = spreadsheet.worksheet("Daily SERP Data")  # Data storage sheet
keywords_sheet = spreadsheet.worksheet("Keywords")  # Keywords input sheet

# 🔹 Get Keywords from Google Sheet
keywords = keywords_sheet.col_values(1)[1:]  # Skip header row

# 🔹 Selenium Setup
options = Options()
options.add_argument("--headless")  # Run in headless mode
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

def get_google_serp(keyword):
    """Fetch Google SERP features for a keyword."""
    search_url = f"https://www.google.com/search?q={keyword.replace(' ', '+')}&hl=en"
    driver.get(search_url)
    time.sleep(3)  # Allow time for page to load

    soup = BeautifulSoup(driver.page_source, "html.parser")

    # Track SERP features
    ai_overview = "Yes" if soup.find("div", string="AI Overview") else "No"

    paa_pos = "-"
    paa_box = soup.find_all("div", class_="related-question-pair")
    if paa_box:
        paa_pos = 1  # PAA typically appears at the top

    sponsored_ads_count = len(soup.select("div[data-text-ad]"))

    # Extract Organic Results
    organic_results = []
    for i, result in enumerate(soup.select("div.tF2Cxc"), start=1):
        link = result.select_one("a")["href"] if result.select_one("a") else "-"
        organic_results.append((i, link))
        if i == 3:  # Capture top 3 results
            break

    org1_link = organic_results[0][1] if len(organic_results) > 0 else "-"
    org2_link = organic_results[1][1] if len(organic_results) > 1 else "-"
    org3_link = organic_results[2][1] if len(organic_results) > 2 else "-"

    pas_present = "Yes" if soup.find("div", string="People also search for") else "No"

    return [datetime.now().strftime("%Y-%m-%d"), keyword, ai_overview, paa_pos, sponsored_ads_count, 
            organic_results[0][0] if organic_results else "-", org1_link, org2_link, org3_link, pas_present]

def save_to_gsheet(data):
    """Saves SERP data to Google Sheet."""
    tracking_sheet.append_row(data)

# 🔹 Track All Keywords and Save Results
for keyword in keywords:
    serp_data = get_google_serp(keyword)
    save_to_gsheet(serp_data)

print("✅ Google SERP tracking updated in Google Sheets!")
driver.quit()