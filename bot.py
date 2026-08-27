cat > modules/youtube_fixed.py << 'EOF'
# -*- coding: utf-8 -*-

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import ElementNotInteractableException
from selenium.common.exceptions import ElementClickInterceptedException
from selenium.common.exceptions import JavascriptException
from modules import utils


class YouTube:
    """ YouTube """

    def __init__(self, url='https://youtube.com', proxy=None, verbose=False):
        """ init variables """

        self.url = url
        self.proxy = proxy
        self.verbose = verbose
        # Firefox options
        self.options = webdriver.FirefoxOptions()
        # Run in headless mode
        self.options.add_argument('--headless')
        # Disables GPU hardware acceleration
        self.options.add_argument('--disable-gpu')
        # Disable audio
        self.options.add_argument('--mute-audio')
        # Firefox specific settings
        self.options.set_preference('browser.cache.disk.enable', False)
        self.options.set_preference('browser.cache.memory.enable', False)
        self.options.set_preference('browser.cache.offline.enable', False)
        self.options.set_preference('network.http.use-cache', False)
        
        if self.proxy:
            # Set proxy for Firefox
            proxy_parts = self.proxy.split(':')
            self.options.set_preference('network.proxy.http', proxy_parts[0])
            self.options.set_preference('network.proxy.http_port', int(proxy_parts[1]))
            self.options.set_preference('network.proxy.ssl', proxy_parts[0])
            self.options.set_preference('network.proxy.ssl_port', int(proxy_parts[1]))
            self.options.set_preference('network.proxy.type', 1)
        
        # User agent
        self.user_agent = utils.user_agent()
        self.options.set_preference('general.useragent.override', self.user_agent)
        
        self.browser = webdriver.Firefox(options=self.options)
        self.default_timeout = 20
        self.browser.implicitly_wait(self.default_timeout)
        self.browser.set_window_size(1920, 1080)
        self.open_url()

    def find_by_class(self, class_name):
        """ finds an element by class name """
        return self.browser.find_element(By.CLASS_NAME, class_name)

    def find_all_by_class(self, class_name):
        """ finds all elements by class name """
        return self.browser.find_elements(By.CLASS_NAME, class_name)

    def find_by_id(self, id_name):
        """ finds a element by id """
        return self.browser.find_element(By.ID, id_name)

    def find_all_by_id(self, id_name):
        """ finds all elements by id """
        return self.browser.find_elements(By.ID, id_name)

    def find_by_name(self, name):
        """ finds a element by name """
        return self.browser.find_element(By.NAME, name)

    def find_all_by_name(self, name):
        """ finds all elements by name """
        return self.browser.find_elements(By.NAME, name)

    def find_by_xpath(self, xpath):
        """ finds a element by xpath """
        return self.browser.find_element(By.XPATH, xpath)

    def find_all_by_xpath(self, xpath):
        """ finds all elements by xpath """
        return self.browser.find_elements(By.XPATH, xpath)

    def click(self, how, what):
        """ clicks on the element """
        try:
            wait = WebDriverWait(self.browser, self.default_timeout)
            wait.until(EC.element_to_be_clickable((how, what))).click()
        except (ElementClickInterceptedException, TimeoutException):
            return False
        return True

    def open_url(self):
        """ opens the URL """
        self.browser.get(self.url)

    def get_current_url(self):
        """ gets the current url """
        return self.browser.current_url

    def get_title(self, id_name='video-title'):
        """ gets the video title """
        try:
            wait = WebDriverWait(self.browser, self.default_timeout)
            wait.until(EC.presence_of_element_located((By.ID, id_name)))
            return self.browser.title
        except TimeoutException:
            return None

    def search(self, query):
        """ searches for the given term(s) and print the result """
        result = {}
        try:
            search = self.find_by_name('search_query')
            time.sleep(2)
            search.click()
            time.sleep(2)
            search.clear()
            search.send_keys(query)
            time.sleep(10)
            search.send_keys(Keys.DOWN)
            search.send_keys(Keys.ENTER)
            self.click(
                By.XPATH,
                "//div[@id='more']/yt-formatted-string/span[3]")
            wait = WebDriverWait(self.browser, self.default_timeout)
            wait.until(
                EC.visibility_of_all_elements_located(
                    ((By.CSS_SELECTOR,
                      'a.yt-simple-endpoint.style-scope.ytd-video-renderer#video-title'))))
            items = self.find_all_by_xpath(
                '//*[@id="contents"]/ytd-video-renderer')
            for item in items:
                if item.is_displayed():
                    v_info = item.find_element(By.ID, 'video-title')
                    c_info = item.find_element(By.CLASS_NAME, 'ytd-channel-name')
                    v_link = v_info.get_attribute('href')
                    v_id = v_link.strip('https://www.youtube.com/watch?v=')
                    v_title = v_info.get_attribute('title')
                    c_url = c_info.find_element(By.CLASS_NAME, 'yt-formatted-string').get_attribute('href')
                    result[v_id] = {
                        'id': v_id,
                        'video title': v_title,
                        'video url': v_link,
                        'channel name': c_info.text,
                        'channel url': c_url,
                        'element': v_info,
                    }
            return result
        except NoSuchElementException:
            return None

    def play_video(self, class_name='ytp-play-button'):
        """ clicks on the play button """
        self.click(By.CLASS_NAME, class_name)

    def mute_video(self, class_name='ytp-mute-button'):
        """ clicks on the mute button """
        self.click(By.CLASS_NAME, class_name)

    def skip_ad(self, class_name='ytp-ad-skip-button-text', max_attempts=20, time_wait=0.5):
        """ skips ads """
        attempts = 0
        while attempts <= max_attempts:
            try:
                button = self.find_by_class(class_name)
                if button.is_enabled() or button.is_displayed():
                    if self.verbose:
                        print(button.get_attribute('textContent').lower())
                    button.click()
            except (ElementNotInteractableException, ElementClickInterceptedException):
                time.sleep(time_wait)
            except (NoSuchElementException, TimeoutException, AttributeError):
                break
            attempts += 1

    def get_views(self, class_name='view-count'):
        """ gets the total views """
        try:
            views = self.find_by_class(class_name).get_attribute('textContent')
            return views.strip(' views')
        except NoSuchElementException:
            return None

    def get_channel_name(self, class_name='ytd-channel-name'):
        """ gets the channel name """
        try:
            return self.find_by_class(class_name).text
        except NoSuchElementException:
            return None

    def get_subscribers(self, id_name='owner-sub-count'):
        """ gets the total of subscribers """
        try:
            return self.find_by_id(id_name).text.strip(' subscribers')
        except NoSuchElementException:
            return None

    def get_player_state(self):
        """ returns the state of the player """
        try:
            js_element = "return document.getElementById('movie_player').getPlayerState()"
            return self.browser.execute_script(js_element)
        except JavascriptException:
            return -2

    def refresh_page(self):
        """ refreshes the page """
        self.browser.refresh()

    def time_duration(self, class_name='ytp-time-duration'):
        """ gets the video duration time """
        try:
            duration = self.find_by_class(class_name)
            if duration:
                return duration.get_attribute('textContent')
        except NoSuchElementException:
            return None
        return None

    def disconnect(self):
        """ closes the connection """
        self.browser.close()
        self.browser.quit()

# vim: set et ts=4 sw=4 sts=4 tw=80
EOF
