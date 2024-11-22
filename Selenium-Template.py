from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import chromedriver_autoinstaller
from pyvirtualdisplay import Display
import logging
import time

display = Display(visible=0, size=(800, 800))  
display.start()

chromedriver_autoinstaller.install()  # Check if the current version of chromedriver exists
                                      # and if it doesn't exist, download it automatically,
                                      # then add chromedriver to path

chrome_options = webdriver.ChromeOptions()    
# Add your options as needed    
options = [
  # Define window size here
   "--window-size=1200,1200",
    "--ignore-certificate-errors"
 
    #"--headless",
    #"--disable-gpu",
    #"--window-size=1920,1200",
    #"--ignore-certificate-errors",
    #"--disable-extensions",
    #"--no-sandbox",
    #"--disable-dev-shm-usage",
    #'--remote-debugging-port=9222'
]

for option in options:
    chrome_options.add_argument(option)

    
driver = webdriver.Chrome(options = chrome_options)

driver.get('https://iranicard.ir/')


try:
    logging.info("Scraping started...")
    # باز کردن یک صفحه وب
    driver.get("https://www.iranicard.ir/card/giftcard/")  # آدرس وب‌سایت موردنظر خود را جایگزین کنید


    all_products = {}

    # باز کردن منوی برندها
    products_brand_dropdown = driver.find_element(By.XPATH, "//*[@id='block-card-block_9ea71d6d4ffff7e694494e8f3cf11fda']/div/div/div/div/div[1]/div/div/a")
                                                            
    products_brand_dropdown.click()

    # استخراج دسته‌بندی‌ها
    categories_ul = driver.find_element(By.XPATH, "//*[@id='block-card-block_9ea71d6d4ffff7e694494e8f3cf11fda']/div/div/div/div/div[1]/div/div/div/ul")
                                                        
    category_li = categories_ul.find_elements(By.TAG_NAME, "li")

    # لیست تمام محصولات
    for category in category_li:
        category_name = category.text.strip()
        if not category_name:
            continue  # رد کردن دسته‌بندی‌های خالی

        # کلیک بر روی هر دسته
        category_a_tag = category.find_element(By.TAG_NAME, "a")
        category_name = category_a_tag.text.strip()

        print(f"Processing category: {category_name}")

        try:
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable(category_a_tag)).click()

            # category_a_tag.click()  # کلیک بر روی دسته‌بندی
            print("Click was success")
            time.sleep(2)  # اجازه می‌دهیم تا محصولات بارگذاری شوند
        except Exception as e:
            print(f"there is an error: {e}")
            driver.save_screenshot("error_screenshot.png")
            continue
        # انتظار برای بارگذاری منوی مقادیر کارت
        card_values_a_tag = WebDriverWait(driver, 10).until(EC.element_to_be_clickable(
            (By.XPATH, "//*[@id='block-card-block_9ea71d6d4ffff7e694494e8f3cf11fda']/div/div/div/div/div[3]/div/div/a")
            
        ))
        card_values_a_tag.click()
        time.sleep(1)

        # استخراج مقادیر کارت‌ها
        card_values_ul = driver.find_element(By.XPATH, "//*[@id='block-card-block_9ea71d6d4ffff7e694494e8f3cf11fda']/div/div/div/div/div[3]/div/div/div/ul")
        li_elements = card_values_ul.find_elements(By.TAG_NAME, "li")

        category_products = []

        # استخراج اطلاعات محصولات در هر دسته
        for li in li_elements:
            a_tag = li.find_element(By.TAG_NAME, "a")

            data_currency = a_tag.get_attribute("data-currency")
            data_price_currency = a_tag.get_attribute("data-price_currency")
            data_price_rial = a_tag.get_attribute("data-price_rial")
            product_text = a_tag.text.strip()

            if not product_text and data_currency and data_price_currency:
                product_text = f"{data_price_currency} {data_currency}"

            # ایجاد دیکشنری از اطلاعات محصول
            item_dict = {
                "category": category_name,
                "data-currency": data_currency,
                "data-price_currency": data_price_currency,
                "data-price_rial": data_price_rial,
                "product_text": product_text
            }
            category_products.append(item_dict)

        all_products[category_name] = category_products
        card_values_a_tag.click()
        time.sleep(1)
        products_brand_dropdown.click()

except Exception as e:
    with open('./GitHub_Action_Results.txt', 'w') as f:
        f.write(f"Salam {e}")



    # pprint.pprint(all_products)

    # آماده‌سازی داده‌ها برای نوشتن در اکسل
    # excel_data = []

    # for category, products in all_products.items():
    #     for product in products:
    #         excel_data.append(product)

    # # تبدیل داده‌ها به یک DataFrame با استفاده از pandas
    # df = pd.DataFrame(excel_data)

    # # صادر کردن داده‌ها به فایل Excel
    # df.to_excel("products_data.xlsx", index=False)

    # print("Data has been written to 'products_data.xlsx'")
    # logging.info("Scraping completed...")

finally:
    logging.info("I dont know what should I do...")
    # بستن مرورگر
    driver.quit()

# print(driver.title)
# with open('./GitHub_Action_Results.txt', 'w') as f:
#     f.write(f"Salam {len(all_products)}")

