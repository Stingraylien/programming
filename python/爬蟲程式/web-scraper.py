import requests
from bs4 import BeautifulSoup
import time
import random
from urllib.parse import urljoin
import logging

class WebScraper:
    def __init__(self, target_website_url, wait_time_seconds=1):
        """
        初始化網路爬蟲
        
        Parameters:
        target_website_url (str): 要爬取的網站基礎URL
        wait_time_seconds (int): 每次請求之間的延遲秒數
        """
        self.target_website_url = target_website_url
        self.wait_time_seconds = wait_time_seconds
        self.http_client_session = requests.Session()
        self.http_client_session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # 設定logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.activity_logger = logging.getLogger(__name__)

    def fetch_and_parse_page(self, target_page_url):
        """
        獲取並解析網頁內容
        
        Parameters:
        target_page_url (str): 要爬取的網頁URL
        
        Returns:
        BeautifulSoup object: 解析後的網頁內容
        """
        try:
            # 加入隨機延遲避免過度頻繁請求
            time.sleep(self.wait_time_seconds + random.random())
            
            server_response = self.http_client_session.get(target_page_url)
            server_response.raise_for_status()
            
            # 檢查內容類型是否為HTML
            if 'text/html' not in server_response.headers.get('Content-Type', ''):
                raise ValueError('非HTML內容')
                
            return BeautifulSoup(server_response.text, 'html.parser')
            
        except requests.exceptions.RequestException as e:
            self.activity_logger.error(f"請求錯誤: {target_page_url} - {str(e)}")
            return None
        except Exception as e:
            self.activity_logger.error(f"解析錯誤: {target_page_url} - {str(e)}")
            return None

    def extract_all_hyperlinks(self, parsed_html_document):
        """
        從網頁中提取所有連結
        
        Parameters:
        parsed_html_document (BeautifulSoup): 解析後的網頁內容
        
        Returns:
        list: 網頁中的所有URL列表
        """
        extracted_hyperlinks = []
        try:
            for hyperlink_element in parsed_html_document.find_all('a', href=True):
                extracted_href = hyperlink_element['href']
                # 將相對URL轉換為絕對URL
                full_absolute_url = urljoin(self.target_website_url, extracted_href)
                if full_absolute_url.startswith(self.target_website_url):
                    extracted_hyperlinks.append(full_absolute_url)
        except Exception as e:
            self.activity_logger.error(f"提取連結錯誤: {str(e)}")
        return extracted_hyperlinks

    def extract_specific_content(self, target_page_url, css_target_selector):
        """
        使用CSS選擇器提取特定內容
        
        Parameters:
        target_page_url (str): 要爬取的網頁URL
        css_target_selector (str): CSS選擇器
        
        Returns:
        list: 符合選擇器的所有內容
        """
        parsed_html_document = self.fetch_and_parse_page(target_page_url)
        if not parsed_html_document:
            return []
            
        try:
            matched_html_elements = parsed_html_document.select(css_target_selector)
            return [html_element.get_text(strip=True) for html_element in matched_html_elements]
        except Exception as e:
            self.activity_logger.error(f"內容提取錯誤: {target_page_url} - {str(e)}")
            return []

# 使用範例
if __name__ == "__main__":
    website_content_scraper = WebScraper("https://example.com")
    
    # 爬取特定頁面的內容
    extracted_text_content = website_content_scraper.extract_specific_content(
        "https://example.com/page",
        "div.content"  # CSS選擇器
    )
    
    for text_item in extracted_text_content:
        print(text_item)
