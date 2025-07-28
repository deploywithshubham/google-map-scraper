import datetime
from playwright.sync_api import sync_playwright
from dataclasses import dataclass, asdict, field
import pandas as pd
import argparse
import os
import sys

# ---------------------------
# Business Data Class
# ---------------------------
@dataclass
class Business:
    name: str = None
    address: str = None
    domain: str = None
    website: str = None
    phone_number: str = None
    category: str = None
    location: str = None
    reviews_count: int = None
    reviews_average: float = None
    latitude: float = None
    longitude: float = None

    def __hash__(self):
        name = str(self.name).lower().strip() if self.name else ""
        phone = str(self.phone_number).strip() if self.phone_number else ""
        address = str(self.address).lower().strip() if self.address else ""
        return hash((name, phone, address))

# ---------------------------
# Business List Class
# ---------------------------
@dataclass
class BusinessList:
    keyword: str
    business_list: list[Business] = field(default_factory=list)
    _seen_businesses: set = field(default_factory=set, init=False)

    def __post_init__(self):
        self.today = datetime.datetime.now().strftime("%Y-%m-%d")
        self.save_at = os.path.join('GMaps Data', self.today)
        os.makedirs(self.save_at, exist_ok=True)
        sanitized_keyword = self.keyword.replace(' ', '_').replace('/', '_')
        self.custom_csv = os.path.join(self.save_at, f"{sanitized_keyword}.csv")
        self.master_csv = os.path.join('GMaps Data', "all_scraped_master.csv")
        self.load_existing_data()

    def load_existing_data(self):
        if os.path.exists(self.master_csv):
            try:
                df = pd.read_csv(self.master_csv)
                for _, row in df.iterrows():
                    existing_business = Business(
                        name=str(row.get('name', '') or ''),
                        address=str(row.get('address', '') or ''),
                        phone_number=str(row.get('phone_number', '') or '')
                    )
                    self._seen_businesses.add(hash(existing_business))
                print(f"Loaded {len(self._seen_businesses)} previously scraped businesses.")
            except Exception as e:
                print(f"Warning: Failed to read master CSV: {e}")

    def add_business(self, business: Business) -> bool:
        business_hash = hash(business)
        if business_hash not in self._seen_businesses:
            self.business_list.append(business)
            self._seen_businesses.add(business_hash)
            return True
        return False

    def dataframe(self):
        return pd.json_normalize((asdict(b) for b in self.business_list), sep="_")

    def save_to_csv(self):
        new_data = self.dataframe()

        if new_data.empty:
            print("No new businesses found to save.")
            return

        # Save to master
        if os.path.exists(self.master_csv):
            old_df = pd.read_csv(self.master_csv)
            combined_df = pd.concat([old_df, new_data], ignore_index=True)
            combined_df.drop_duplicates(subset=['name', 'phone_number', 'address'], inplace=True)
            combined_df.to_csv(self.master_csv, index=False)
        else:
            new_data.to_csv(self.master_csv, index=False)

        # Save to keyword-specific file
        if os.path.exists(self.custom_csv):
            old_df = pd.read_csv(self.custom_csv)
            combined_df = pd.concat([old_df, new_data], ignore_index=True)
            combined_df.drop_duplicates(subset=['name', 'phone_number', 'address'], inplace=True)
            combined_df.to_csv(self.custom_csv, index=False)
        else:
            new_data.to_csv(self.custom_csv, index=False)

        print(f"Saved {len(new_data)} new businesses to '{self.custom_csv}'.")


# ---------------------------
# Helper Functions
# ---------------------------
def extract_coordinates_from_url(url: str) -> tuple[float, float]:
    try:
        coordinates = url.split('/@')[-1].split('/')[0]
        return float(coordinates.split(',')[0]), float(coordinates.split(',')[1])
    except Exception:
        return None, None

def scrape_business_data(page, search_for):
    name_attribute = 'h1.DUwDvf'
    address_xpath = '//button[@data-item-id="address"]//div[contains(@class, "fontBodyMedium")]'
    website_xpath = '//a[@data-item-id="authority"]//div[contains(@class, "fontBodyMedium")]'
    phone_number_xpath = '//button[contains(@data-item-id, "phone:tel:")]//div[contains(@class, "fontBodyMedium")]'
    review_count_xpath = '//div[@jsaction="pane.reviewChart.moreReviews"]//span'
    reviews_average_xpath = '//div[@jsaction="pane.reviewChart.moreReviews"]//div[@role="img"]'

    business = Business()
    business.name = page.locator(name_attribute).inner_text().strip() if page.locator(name_attribute).count() else ""
    business.address = page.locator(address_xpath).inner_text() if page.locator(address_xpath).count() else ""
    if page.locator(website_xpath).count() > 0:
        domain = page.locator(website_xpath).inner_text().strip()
        business.domain = domain
        business.website = f"https://www.{domain}"
    else:
        business.website = ""
    business.phone_number = page.locator(phone_number_xpath).inner_text() if page.locator(phone_number_xpath).count() else ""
    business.reviews_count = int(page.locator(review_count_xpath).inner_text().split()[0].replace(',', '').strip()) if page.locator(review_count_xpath).count() else ""
    business.reviews_average = float(page.locator(reviews_average_xpath).get_attribute('aria-label').split()[0].replace(',', '.').strip()) if page.locator(reviews_average_xpath).count() else ""
    business.category = search_for.split(' in ')[0].strip() if ' in ' in search_for else search_for
    business.location = search_for.split(' in ')[-1].strip() if ' in ' in search_for else ""
    business.latitude, business.longitude = extract_coordinates_from_url(page.url)
    return business

# ---------------------------
# Main Function
# ---------------------------
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--search", type=str, required=False)
    parser.add_argument("-t", "--total", type=int, default=20, help="Number of NEW unique businesses to scrape.")
    args = parser.parse_args()

    if args.search:
        search_list = [args.search]
    else:
        input_file_path = os.path.join(os.getcwd(), 'input.txt')
        if os.path.exists(input_file_path):
            with open(input_file_path, 'r') as file:
                search_list = [line.strip() for line in file.readlines() if line.strip()]
        else:
            print('Error: You must either pass -s or add searches to input.txt')
            sys.exit()

    total = args.total

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page(locale="en-GB")
        page.goto("https://www.google.com/maps", timeout=20000)

        for search_for_index, search_for in enumerate(search_list):
            print(f"-----\n{search_for_index} - {search_for}".strip())

            page.locator('//input[@id="searchboxinput"]').fill(search_for)
            page.wait_for_timeout(3000)
            page.keyboard.press("Enter")
            page.wait_for_timeout(5000)

            business_list = BusinessList(keyword=search_for)
            new_count = 0
            previous_loaded = -1

            while new_count < total:
                listings = page.locator('//div[contains(@class, "Nv2PK")]').all()

                for listing in listings:
                    if new_count >= total:
                        break
                    try:
                        listing.hover()
                        page.wait_for_timeout(500)
                        listing.click()
                        page.wait_for_timeout(2000)

                        business = scrape_business_data(page, search_for)
                        if business_list.add_business(business):
                            new_count += 1
                            print(f"New business added ({new_count}/{total}): {business.name}")
                    except Exception as e:
                        print(f"Error occurred: {e}", end='\r')

                current_loaded = page.locator('//div[contains(@class, "Nv2PK")]').count()
                if current_loaded == previous_loaded:
                    print(f"Reached the end of listings. Only {new_count} unique businesses found.")
                    break
                previous_loaded = current_loaded
                page.mouse.wheel(0, 3000)
                page.wait_for_timeout(2000)

            business_list.save_to_csv()

        browser.close()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f'Failed err: {e}')
