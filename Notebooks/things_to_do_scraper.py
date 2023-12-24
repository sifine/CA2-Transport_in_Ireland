from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from datetime import datetime
import re
import time

# default path to file to store data
path_to_file = "./reviews.csv"

# default number of scraped pages
num_page = 10

# default tripadvisor website of hotel or things to do (attraction/monument) 
#url = "https://www.tripadvisor.com/Hotel_Review-g60763-d1218720-Reviews-The_Standard_High_Line-New_York_City_New_York.html"
url = "https://www.tripadvisor.com/Attraction_Review-g187791-d192285-Reviews-Colosseum-Rome_Lazio.html"
# import the webdriver
driver = webdriver.Chrome()
driver.get(url)

"""
# if you pass the inputs in the command line
if (len(sys.argv) == 4):
    path_to_file = sys.argv[1]
    num_page = int(sys.argv[2])
    url = sys.argv[3]

"""

"""
# open the file to save the review
csvFile = open(path_to_file, 'a', encoding="utf-8")
csvWriter = csv.writer(csvFile)

# change the value inside the range to save more or less reviews
for i in range(0, num_page):

    # expand the review 
    time.sleep(5)
    # Click on the "Expand Review" button
    driver.find_element_by_xpath(".//div[contains(@data-test-target, 'expand-review')]").click()

    # Find all review containers
    containers = driver.find_elements_by_xpath("//div[@data-automation='reviewCard']")

    # Find dates of the reviews
    dates = driver.find_elements_by_xpath(".//div[@class='_T']/div[@class='TreSq']/div[@class='biGQs _P pZUbB ncFvv osNWb']")

    # Loop through each review container
    for j in range(len(containers)):
        # Extract data from the current container
        rating = containers[j].find_element_by_xpath(".//svg[contains(@aria-label, 'of 5 bubbles')]").get_attribute("aria-label").split(" ")[0]
        title = containers[j].find_element_by_xpath(".//div[@class='biGQs _P fiohW qWPrE ncFvv fOtGX']/a/span").text
        review = containers[j].find_element_by_xpath(".//div[@class='fIrGe _T bgMZj']/div[@class='biGQs _P pZUbB KxBGd']/span/span").text
        date = dates[j].text.split(" ")[1]

        # Write the data to a CSV file
        csvWriter.writerow([date, rating, title, review])
        
    # change the page            
    driver.find_element_by_xpath('.//a[@class="ui_button nav next primary "]').click()

driver.quit()
"""

# Wait for the page to load (you may need to adjust the wait time based on your website)
driver.implicitly_wait(10)

# Find all review elements
review_elements = driver.find_elements(By.CSS_SELECTOR, 'div[data-automation="reviewCard"]')

for review_element in review_elements:
    # Extract reviewer information
    reviewer_name = review_element.find_element(By.CSS_SELECTOR, 'span.biGQs._P.fiohW.fOtGX a').text
    reviewer_contributions = review_element.find_element(By.CSS_SELECTOR, 'div.zpDvc.Zb span').text

    # Extract review details
    review_score_element = review_element.find_element(By.CSS_SELECTOR, 'svg.UctUV.d.H0')
    review_score = float(review_score_element.get_attribute('aria-label').split()[0])

    review_text = review_element.find_element(By.CSS_SELECTOR, 'div.biGQs._P.fiohW.qWPrE.ncFvv.fOtGX a span.yCeTE').text

    review_date_string = review_element.find_element(By.CSS_SELECTOR, 'div.RpeCd').text

    # Use regular expression to extract month and year
    match = re.search(r'(\w+ \d{4})', review_date_string)
    if match:
        review_date = datetime.strptime(match.group(1), '%b %Y').date()
    else:
        # Handle other date formats if necessary
        review_date = None

    # Print or process the extracted information
    print(f"Reviewer: {reviewer_name} ({reviewer_contributions})")
    print(f"Score: {review_score}")
    print(f"Review Text: {review_text}")
    print(f"Date: {review_date}")
    print("\n")

# Close the webdriver
driver.quit()