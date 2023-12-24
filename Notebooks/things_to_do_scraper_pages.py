import argparse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from datetime import datetime
import re
import pandas as pd

def scrape_reviews(url, csv_path):
    # Set up the Selenium webdriver
    driver = webdriver.Chrome()

    # Navigate to the provided URL
    driver.get(url)

    # Wait for the page to load (you may need to adjust the wait time based on your website)
    driver.implicitly_wait(10)

    reviews_data = []

    while True:
        # Find all review elements
        review_elements = driver.find_elements(By.CSS_SELECTOR, 'div[data-automation="reviewCard"]')

        for review_element in review_elements:
            try:
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

                # Append the extracted information to the data list
                reviews_data.append({
                    "Reviewer": reviewer_name,
                    "Contributions": reviewer_contributions,
                    "Score": review_score,
                    "Review Text": review_text,
                    "Date": review_date
                })

            except Exception as e:
                print(f"Unable to parse a comment: {str(e)}")

        try:
            next_button = driver.find_element(By.CSS_SELECTOR, 'a[data-smoke-attr="pagination-next-arrow"]')
            next_page_url = next_button.get_attribute('href')
            driver.get(next_page_url)
            driver.implicitly_wait(10)
        except Exception as e:
            print(f"Unable to locate next page button: {str(e)}")
            break

    # Close the webdriver
    driver.quit()

    # Create a DataFrame from the reviews data
    df = pd.DataFrame(reviews_data)

    # Save the DataFrame to a CSV file
    df.to_csv(csv_path, index=False)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scrape TripAdvisor reviews.")
    parser.add_argument("url", type=str, help="URL of the TripAdvisor page")
    parser.add_argument("csv_path", type=str, help="Path to the CSV file for storing scraped data")
    args = parser.parse_args()

    scrape_reviews(args.url, args.csv_path)