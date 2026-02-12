from selenium import webdriver
from selenium.webdriver.common.by import By
import pandas as pd
import random
import time
import re



# opens a Firefox window
driver = webdriver.Firefox()

# Navigate to the website
driver.get("https://www.strava.com/segments/12666537?filter=overall")

activity_urls = []

def get_links():
    specific_links = driver.find_elements(By.CSS_SELECTOR, ".track-click:nth-child(3) a")
    specific_urls = [link.get_attribute("href") for link in specific_links]
    return specific_urls

i = 0
while i < 3:
    activity_urls.append(get_links())
    time.sleep(random.randint(5, 10))
    next = driver.find_element(By.CSS_SELECTOR, ".next_page a")
    i += 1
    next.click()

temp = pd.DataFrame({'url': activity_url_list})
temp.to_csv("projects/boston_marathon_data/boston_m_urls_2025.csv")

temp

url = activity_url_list[0]
url = current_urls[0]
test_urls = activity_url_list[1:20]

for url in current_urls:
    time.sleep(random.uniform(20, 60))
    driver.get(url)
    time.sleep(random.uniform(2, 9))
    overview = driver.find_element(By.LINK_TEXT, "Overview")
    max_attempts = 4
    attempts = 0
    stats = ['']
    gear = ['']
    
    while attempts < max_attempts and (len(stats[0]) < 1 or len(gear[0]) < 1):
        overview.click()
        time.sleep(random.uniform(2, 10))
        stats = driver.find_elements(By.CSS_SELECTOR, ".inline-stats")
        stats = [element.text for element in stats]
        gear = driver.find_elements(By.CSS_SELECTOR, ".device-section")
        gear = [element.text for element in gear]
        attempts += 1
    date = driver.find_elements(By.CSS_SELECTOR, "time")
    date = [element.text for element in date]
    temp = pd.DataFrame({
    'date': date[0],
    'run_data': stats,
    'gear': gear
    })
    result = pd.concat([result, temp], ignore_index=True)


for url in current_urls:
    time.sleep(random.uniform(3, 10))
    driver.get(url)
    time.sleep(random.uniform(2, 9))
    current_url = driver.current_url
    new_url = re.sub(r'segments.*', 'overview', current_url)
    if new_url == current_url:
        new_url = re.sub(r'#.*', '/overview', current_url)
    driver.get(new_url)
    time.sleep(random.uniform(2, 5))
    stats = driver.find_elements(By.CSS_SELECTOR, ".inline-stats")
    stats = [element.text for element in stats]
    gear = driver.find_elements(By.CSS_SELECTOR, ".device-section")
    gear = [element.text for element in gear]
    date = driver.find_elements(By.CSS_SELECTOR, "time")
    date = [element.text for element in date]
    temp = pd.DataFrame({
    'date': date[0],
    'run_data': stats,
    'gear': gear,
    'url' : new_url
    })
    result = pd.concat([result, temp], ignore_index=True)


result.to_csv("projects/boston_marathon_data/strava_results_4.csv")
temp_result = pd.read_csv("projects/boston_marathon_data/strava_results_3.csv")

current_urls = activity_url_list[762:]
url = current_urls[0]


current_url = "kjanrf345#34"
new_url = re.sub(r'#.*', '/overview', current_url)
https://www.strava.com/activities/14244793286#3349455487572884570