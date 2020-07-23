import scrapy
import re
import scrapy.spiders

from lxml.html import fromstring
import requests
from itertools import cycle
import traceback

import selenium
from scrapy.selector import Selector
from selenium import webdriver

from scrapy import Spider
from scrapy.selector import Selector
from scrapy.http import Request
 
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException

from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from time import sleep
from .. items import FlippaItem
import numpy as np
from selenium.webdriver.remote.command import Command





class FlippaSpider(scrapy.Spider):
    name = 'flippa'
    start_urls = [
        "https://flippa.com/search?filter%5Bprofit_per_month%5D%5Bmin%5D=1000&filter%5Bstatus%5D=open&filter%5Bproperty_type%5D=website,established_website,starter_site,fba,ios_app&filter%5Bsitetype%5D=all,content,blog,directory,review,forum-community,ecommerce,dropship,digital-products,shopify,inventory-holding,saas,services,digital,physical,transact-market'"
    ]
    headers = {
        'User-Agent': 
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'}
    
    
    items = FlippaItem()

    
    
    # ip proxies to not get banned
    def get_proxies():
        url = 'https://free-proxy-list.net/'
        response = requests.get(url)
        parser = fromstring(response.text)
        proxies = set()
        for i in parser.xpath('//tbody/tr')[:10]:
            if i.xpath('.//td[7][contains(text(),"yes")]'):
                proxy = ":".join([i.xpath('.//td[1]/text()')[0], i.xpath('.//td[2]/text()')[0]])
                proxies.add(proxy)
        return proxies


    #If you are copy pasting proxy ips, put in the list below
    #proxies = ['121.129.127.209:80', '124.41.215.238:45169', '185.93.3.123:8080', '194.182.64.67:3128', '106.0.38.174:8080', '163.172.175.210:3128', '13.92.196.150:8080']

    proxies = get_proxies()
    proxy_pool = cycle(proxies)

    url = 'https://httpbin.org/ip'
    for i in range(1,11):
        #Get a proxy from the pool
        proxy = next(proxy_pool)
        print("Request #%d"%i)
        try:
            response = requests.get(url,proxies={"http": proxy, "https": proxy})
            print(response.json())
        except:
            #Most free proxies will often get connection errors. You will have retry the entire request using another proxy to work. 
            #We will just skip retries as its beyond the scope of this tutorial and we are only downloading a single url 
            print("Skipping. Connnection error")

    
    def parse(self, response):
    
        self.driver = webdriver.Chrome("/Users/alxander44/Desktop/chromedriver")
        
        self.driver.get('https://flippa.com/search?filter%5Bprofit_per_month%5D%5Bmin%5D=1000&filter%5Bstatus%5D=open&filter%5Bproperty_type%5D=website,established_website,starter_site,fba,ios_app&filter%5Bsitetype%5D=all,content,blog,directory,review,forum-community,ecommerce,dropship,digital-products,shopify,inventory-holding,saas,services,digital,physical,transact-market')
        sleep(3)

        self.signin_button = self.driver.find_element_by_link_text('Sign In')
        self.signin_button.click()
        sleep(2.5)
        # for email
        self.driver.find_element_by_xpath(
            '//*[(@id = "session_email")]').send_keys('pierrealexanders@gmail.com \ue004')
        sleep(2.5)
        # for password 
        self.driver.find_element_by_xpath(
            '//*[(@id = "session_password")]').send_keys('pierrealexanders\ue007')
        sleep(2.5)
        privacy_ok_button = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div/a')))
        privacy_ok_button.click()
        sleep(1)
        url = self.driver.current_url
        yield response.follow(url=url, callback=self.parse_asset_data)



    def parse_asset_data(self, response):
        current_url = self.driver.current_url
        count = 0
        counter = [0, 2, 4, 6, 10, 11]
        
        loops = 0
        ignored_exceptions = (NoSuchElementException, StaleElementReferenceException)
        asset_page = WebDriverWait(self.driver, 10, ignored_exceptions=ignored_exceptions).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, 'listing-card ')))
        
        while count < len(asset_page):
            while loops < len(asset_page):
                asset_page1 = WebDriverWait(self.driver, .5).until(
                    EC.presence_of_all_elements_located((By.CLASS_NAME, 'listing-card ')))
                
                # remove all the /n and replace ever space with a ,
                items = FlippaItem()
                lst = asset_page1[loops].text
                # puts each asset in a list as a str separeated by ,
                lst = re.split('; |, |\*|\n', lst)
                lst = np.array(lst)
                
                # returnns only the 4 items in the list that we want
                lst = lst[counter]
                
                # get the net profit out of the list as a str and turns it into a int
                net = int(re.sub(r'[^0-9]', '', lst[3]))

                # append the net to the numpy array
                lst = np.append(lst, net)
    
                # convert lst back to a list to later yield to items
                lst = list(lst)
            
                # passing the scaped contain into a dic() called item
               
                #test = re.sub(r'[^0-9]', '', lst[4])
               
                #items['multiple'] = [float(re.sub(r"[a-zA-Z]+", "",lst[5]))]
                items['title'] = [lst[0]]
                items['type_'] = [lst[1]]
                items['monetization'] = [lst[2]]
                items['net'] = [int(lst[6])]


                asset_page1[loops].click()
             
                # for use in gross rev function
                jj = []
                # for use in grow rev function
                e = []
                # for use in traffic funct
                tt = []
                # for use in traffic
                elst = []
                # try:
                # asset_page2[count].click()
                sleep(2.5)

                traffic = self.driver.find_elements_by_xpath(
                    '/html/body/div[5]/div/div[1]/div[4]/div[3]/div/div[1]')
                # traffic_2 = self.driver.find_elements_by_xpath('/html/body/div[5]/div/div[1]/div[4]/div[4]/div/div[1]/div')
                gross = self.driver.find_elements_by_xpath(
                    '/html/body/div[5]/div/div[1]/div[4]/div[4]/div/div[1]/div')
                # gross_2 = self.driver.find_elements_by_xpath('/html/body/div[5]/div/div[1]/div[4]/div[3]/div/div[1]/div')
                glance = self.driver.find_elements_by_xpath('/html/body/div[5]/div/div[1]/div[4]/div[2]/div')
                for i in glance:
                    x = i.text
                    x = re.split('; |, |\*|\n', x)
                    x = np.array(x)
                    x = list(x)
                    
                    
                price = self.driver.find_elements_by_xpath('/html/body/div[5]/div/div[2]/div[1]/div[1]/div[2]/h2')
               
                
                for i in price:
                    p = i.text
                    print(p)
                    breakpoint()
                    p = re.split('; |, |\*|\n', p)
                    p = np.array(p)
                    p = list(p)  
                    p = [int(re.sub(r'[^0-9]', '', p[0]))]
                    print(p)
                    breakpoint()

                breakpoint()
                site_type = [x[1]]
                platform = [x[3]]
                age_of_site = [int(re.sub(r'[^0-9]', '', x[5]))]
                monthly_net = [int(re.sub(r'[^0-9]', '', x[7]))]
                price = p
                sleep(5)
                
                for j in gross:
                    # place str inside of a list
                    j = [j.text]
                    for i in j:
                        jj.extend(i.split())
                        for q in jj:
                            q = re.sub('\D', '', q)
                            if q != '':
                                e.append(q)
                
                sleep(5)
                print('TRAFFIC')
                # if traffic_2 is None:
                try:
                    for i in traffic:
                        i = [i.text]
                        for j in i:
                            tt.extend(j.split())
                            for j in tt:
                                j = re.sub('\D', '', j)
                                if j != '':
                                    elst.append(j)
                except IndexError:
                    elst = ['0','0']
                    

                page_views = [int(elst[0])]
                unique_visits = [int(elst[1])]
                gross_rev = [int(e[0])]
            

                items['monthly_net'] = monthly_net
                items['age_of_site'] = age_of_site
                items['site_type'] = site_type
                items['platform'] = platform
                items['gross_rev'] = gross_rev
                items['page_views'] = page_views
                items['unique_visits'] = unique_visits
                items['price'] = price
                print('this is :', items)
                breakpoint()
                yield items

                self.driver.back()
                sleep(2.5)
                loops += 1
            next_page = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located(
                (By.XPATH, '//*[@id="searchResults"]/div[27]/div[2]/span[13]')))
            next_page.click()
            next_page_url = self.driver.current_url
            
            if current_url == next_page_url:
                break
            
            count += 1
            yield response.follow(url=next_page_url, callback=self.parse_asset_data)





















#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    # def parse(self, response):
        
    #     self.driver = webdriver.Chrome("/Users/alxander44/Desktop/chromedriver")  
    #     self.driver.get('https://flippa.com/search?filter%5Bprofit_per_month%5D%5Bmin%5D=1000&filter%5Bstatus%5D=open&filter%5Bproperty_type%5D=website,established_website,starter_site,fba,ios_app&filter%5Bsitetype%5D=all,content,blog,directory,review,forum-community,ecommerce,dropship,digital-products,shopify,inventory-holding,saas,services,digital,physical,transact-market')	
    #     sleep(3)
       
    #     self.signin_button = self.driver.find_element_by_link_text('Sign In')
    #     self.signin_button.click()
    #     sleep(2.5)
    #     email = self.driver.find_element_by_xpath('//*[(@id = "session_email")]').send_keys('pierrealexanders@gmail.com \ue004')
    #     sleep(2.5)
    #     password = self.driver.find_element_by_xpath('//*[(@id = "session_password")]').send_keys('pierrealexanders\ue007')
    #     sleep(2.5)

    #     items = FlippaItem()
    #     sleep(2.5)
    #     sleep(2.5)
    #     privacy_ok_button = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div/a')))
    #     privacy_ok_button.click()
    #     sleep(1)

    #     counter = [0,2,4,6]
    #     empty = list()
    #     index = 3
    #     count =0
    #     num = 2
    #     loops = 0
    #     ignored_exceptions=(NoSuchElementException,StaleElementReferenceException)
    #     asset_page = WebDriverWait(self.driver, 10,ignored_exceptions=ignored_exceptions).until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'listing-card ')))
        

    #     while loops < 2:
    #         asset_page1 = WebDriverWait(self.driver, .5).until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'listing-card ')))
    #         #breakpoint()
    #         for i in range(len(asset_page1)):
    #             #remove all the /n and replace ever space with a , 
    #         # items = FlippaItem()
    #         # q = [asset_page1[loops].text]
    #         # breakpoint()
    #         # for lst in q:
    #             # puts each asset in a list as a str separeated by ,
    #             # print(' 999999999999999999999',lst)
    #             i = [asset_page[i].text]
    #             for lst in i:
    #                 lst = re.split('; |, |\*|\n',lst)
    #                 lst = np.array(lst)

    #                 #returnns only the 4 items in the list that we want
    #                 lst = lst[counter]

    #                 #get the net profit out of the list as a str and turns it into a int
    #                 net = int(re.sub(r'[^0-9]','',lst[3]))

    #                 #append the net to the numpy array 
    #                 lst = np.append(lst,net) 

    #                 # convert lst back to a list to later yield to items
    #                 lst = list(lst)

    #                 # delets the unneed item from the list
    #                 del lst[index]
    #                 # passing the scaped contain into a dic() called item 
            
    #                 items['title'] = [lst[0]]
    #                 items['type_'] = [lst[1]]
    #                 items['monetization'] = [lst[2]]
    #                 items['net'] = [lst[3]]
                    
    #                 print(lst)
    #                 print(items)
    #                 loops += 1
                
    #         # asset_page1[loops].click()
    #         print('YESSSSSSSSSSSSSSSSSSSSSSSSS')
    #         url = self.driver.current_url
    #         yield response.follow(url=url, callback=self.parse_asset_data)
        


    # def parse_asset_data(self, response):

    #     print('MADE IT TO THE LAAAAASSSSSTTTTTT DEF')
    #     count =0
    #     num = 2
    #     items = FlippaItem()

    #     newlist = []
    #     newl = []
    #     newl2 = []
    #     newl3 = []
    #     newl4 = []

    #     empty1 = []
    #     empty2 =[]
    #     empty3 = []
    #     empty4 = []

    #     def pp_to_int(i):
    #         i = int(re.sub(r'[^\w]','',i))
    #         newlist.append(i)
    #         return newlist  

    #     def monthly_net_to_int(n):
    #         for i in n:
    #             i = re.sub(r'[^\w]','',i)
    #             i = re.sub(r"[a-zA-Z]+", "",i)
    #             i = int(i)
    #             newl.append(i)
    #         return newl

    #     def age_to_int(a):
    #         for i in a:
    #             i = re.sub(r'[^\w]','',i)
    #             i = re.sub(r"[a-zA-Z]+", "",i)
    #             i = int(i)
    #             newl2.append(i)
    #         return newl2

    #     def site_type_lst(s):
    #         for i in s:
    #             i = i.strip(' \n ')
    #             newl3.append(i)
    #         return newl3

    #     def multiple_mo(m):
    #         m = m[0]
    #         empty1.append(m)
    #         for i in empty1:
    #             i = i.strip(' \n ')
    #             i = i.strip('Multiple x')
    #             i = float(i)
    #             empty2.append(i)
    #         return empty2


    #     def multiple_yr(m):
    #         m= m[0]
    #         empty3.append(m)
    #         for i in empty3:
    #             i = i.strip(' \n ')
    #             i = i.strip('Multiple x')
    #             i = float(i)
    #             i = round(i*12,2)
    #             empty4.append(i)
    #         return empty4


    #     def pf_lst(pf):
    #         for i in pf:
    #             i = i.strip(' \n ')
    #             newl4.append(i)
    #         return newl4

    #     count = 0
    #     index = 3
    #     ignored_exceptions=(NoSuchElementException,StaleElementReferenceException)
    #     asset_page = WebDriverWait(self.driver, 10,ignored_exceptions=ignored_exceptions).until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'listing-card ')))
    #     l = 0
        
        
# price = response.css('.ListingStatus-price::text').extract()[0][7:]
                # print(price)
                
                # monthly_net = response.css('.Snapshot-value--small::text').extract()
                # print(monthly_net)
                # breakpoint()
                # age_of_site = response.xpath('//*[(@id = "site_age")]/text()').extract()
                # site_type = response.css('#site_type::text').extract()
                # #multiple_by_month = response.css('.ListingStatus-multiple::text').extract()
                # #multiple_by_year = response.css('.ListingStatus-multiple::text').extract()
                # platform = response.css('.Snapshot-inspect #platform::text').extract()

                #items['price'] = pp_to_int(price)

                    
 

    #     while l <= (num-1):
    #         # try:
    #         asset_page2 = WebDriverWait(self.driver, 10).until(
    #             EC.presence_of_all_elements_located((By.CLASS_NAME, 'listing-card '))
    #         )
    #         # for use in gross rev function 
    #         jj = []
    #         # for use in grow rev function
    #         e = []
    #         # for use in traffic funct
    #         tt = []
    #         # for use in traffic
    #         elst = []
            
    #         if count <= num:
    #             # try:
    #             asset_page2[count].click()
    #             sleep(2.5)

    #             traffic = self.driver.find_elements_by_xpath('/html/body/div[5]/div/div[1]/div[4]/div[3]/div/div[1]')
    #             # traffic_2 = self.driver.find_elements_by_xpath('/html/body/div[5]/div/div[1]/div[4]/div[4]/div/div[1]/div')
    #             gross = self.driver.find_elements_by_xpath('/html/body/div[5]/div/div[1]/div[4]/div[4]/div/div[1]/div')
    #             # gross_2 = self.driver.find_elements_by_xpath('/html/body/div[5]/div/div[1]/div[4]/div[3]/div/div[1]/div')
    #             # glance = self.driver.find_elements_by_xpath('/html/body/div[5]/div/div[1]/div[4]/div[2]/div')
    #             sleep(5)

    #             #price = response.css('.ListingStatus-price::text').extract()[0][7:]
    #             monthly_net = response.css('.Snapshot-value--small::text').extract()
    #             age_of_site = response.xpath('//*[(@id = "site_age")]/text()').extract()
    #             site_type = response.css('#site_type::text').extract()
    #             #multiple_by_month = response.css('.ListingStatus-multiple::text').extract()
    #             #multiple_by_year = response.css('.ListingStatus-multiple::text').extract()
    #             platform = response.css('.Snapshot-inspect #platform::text').extract()

    #             #items['price'] = pp_to_int(price)
    #             items['monthly_net'] = monthly_net_to_int(monthly_net)
    #             items['age_of_site'] = age_to_int(age_of_site)
    #             items['site_type'] = site_type_lst(site_type)
    #             #items['multiple_by_month'] = multiple_mo(multiple_by_month)
    #             #items['multiple_by_year'] = multiple_yr(multiple_by_year)
    #             items['platform'] = pf_lst(platform) 

    #             print('brooooooooo items got through')

    #             for j in gross:
    #             # place str inside of a list
    #                 j= [j.text]
    #                 for i in j:
    #                     jj.extend(i.split())
    #                     for q in jj:
    #                         q = re.sub('\D', '', q)
    #                         if q != '':
    #                             e.append(q)

    #             print('this is e:', e)
    #             # items['gross_rev'] = [e[0]]
    #             items['net'] = [e[1]]
    #             print(items)
                

    #             sleep(5)
    #             print('TRAFFIC')
    #             # if traffic_2 is None:
    #             for i in traffic:
    #                 i = [i.text]
    #                 for j in i:
    #                     tt.extend(j.split())
    #                     for j in tt:
    #                         j = re.sub('\D', '', j)
    #                         if j != '':
    #                             elst.append(j)

    #             print(traffic)
    #             # items['page_views'] = [elst[0]]
    #             # items['unique_visits'] = [elst[1]]
    #             print('this is :', items)
    #             yield items

    #             self.driver.back()
    #             sleep(2.5)
    #             count +=1
    #             l +=1 
    #             print('MADE IT TO THE END OF SECOND LOOP')
    #             if count > num:
    #                 count = 0
    #                 sleep(2.5)
    #                 next_page = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="searchResults"]/div[27]/div[2]/span[13]')))
    #                 breakpoint()
    #                 next_page.click()
    #                 sleep(2.5)
    #         print('GOO TO BACK TO FIRST PARSER')
    #         url = self.driver.current_url
    #         yield response.follow(url=url, callback=self.parse)
        
                    
                    


#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@


    
                
                # else:
                #     url = self.driver.current_url
                #     scrapy.Request(url=url, callback=self.parse)
                            

                        # except IndexError:
                            
                        #     break
                    # except Exception as e:
                    #     continue
            # except Exception as x:
            #     print(x)
            #     yield items
        # url = self.driver.current_url
        # scrapy.Request(url=url, callback=self.parse)




       # else:
        #     print('MADDDDDEEE IT HEREEEEEEEEEEE')
            
        #     # yield scrapy.Request(
        #     #     url = url, 
        #     #     callback= self.parse_asset_data)
        #     print('MADDDDDEEE IT HEREEEEEEEEEEE2')
            
    # except StaleElementReferenceException:
        # self.driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
        # sleep(3)
        
       
        
        # GET ASSETS








# ___________________________________________________________________________________________________
    #asset_page = WebDriverWait(self.driver, 10).until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'listing-card ')))
    # next_page_saas = response.css('div:nth-child(8) .subnavbar__inner__link ::attr(href)').extract()
    # to get all the catorgory links response.css('div:nth-child(8) .subnavbar__inner__link , div:nth-child(4) .subnavbar__inner__link , div:nth-child(5) .subnavbar__inner__link , div:nth-child(6) .subnavbar__inner__link ,div:nth-child(7) .subnavbar__inner__link , div+ .subnavbar__inner__link a::attr(href)').extract()
    
    # scrapy the hope page to get to desinated business catagories

    # """ [CHECK] set a condition for if asset page is none that it yeilds items and closes driver"""
    
    # """[CHECK] set acondition if the index is less than n and is on the last page bc the last page loops"""
    
    # """[CHECK] so you might have to set a condition if assets page repeats or the same content is scraped that it 
    # throws and error or yields items and closes the driver"""

    # """ have to set up a condition where it checks if the page is looped once you hit the next button
    # at the bottom. NOTE: assets page loops when you click the next page button and you are on the last page.
    # which will result in you scraping the same page forever. have a check to see if assets page is =
    # to previous assets page and if so yield items and close driver if needed. NOTE: the 
    # only way this will happen with your current code is if the # of assets on a page is = to n 
    
    # maybe a way to do this is to instanciate drive.back() and set a condition to see 
    # if the object is == to get driver.current_url  """

    
    # """ set up where parser goes to each domain type. outline structure """



        # ios_app_button = self.driver.find_element_by_xpath('//*[@id="filter[property_type]-ios_app"]/span[1]')                       
        # ios_app_button.click()
        # sleep(2)
        # content_button = self.driver.find_element_by_xpath('//*[@id="filter[sitetype]-content"]/span[1]')
        # content_button.click()
        # sleep(2)
        # saas_button = self.driver.find_element_by_xpath('//*[@id="filter[sitetype]-saas"]/span[1]')
        # saas_button.click()
        # sleep(2)
        # service_button = self.driver.find_element_by_xpath('//*[@id="filter[sitetype]-services"]/span[1]')
        # service_button.click()
        # sleep(2)
        # marketplace_button = self.driver.find_element_by_xpath('//*[@id="filter[sitetype]-transact-market"]/span[1]')
        # marketplace_button.click()
        
        # sleep(3)
        # dd = Select(self.driver.find_element_by_xpath('//*[@id="searchResults"]/div[27]/div[3]/div/select'))
        # dd.select_by_visible_text('100 items')
        # self.driver.execute_script("window.scrollTo(0, Y)")


        # eCommerce_button = self.driver.find_element_by_link_text('eCommerce')
        # eCommerce_button.click()
        # sleep(5)
        # thousand = self.driver.find_element_by_xpath('//*[@id="searchFilters"]/div/div[1]/div[2]/div[7]/div[2]/input[1]').send_keys('1000')
        #sleep(3)

        # driver.get('https://flippa.com/10376975-advertising-education')


# newlist = []
#         newl = []
#         newl2 = []
#         newl3 = []
#         newl4 = []

#         empty1 = []
#         empty2 = []
#         empty3 = []
#         empty4 = []

#         def pp_to_int(i):
#             i = int(re.sub(r'[^\w]', '', i))
#             newlist.append(i)
#             return newlist

#         def monthly_net_to_int(n):
#             for i in n:
#                 i = re.sub(r'[^\w]', '', i)
#                 i = re.sub(r"[a-zA-Z]+", "", i)
#                 i = int(i)
#                 newl.append(i)
#             return newl

#         def age_to_int(a):
#             for i in a:
#                 i = re.sub(r'[^\w]', '', i)
#                 i = re.sub(r"[a-zA-Z]+", "", i)
#                 i = int(i)
#                 newl2.append(i)
#             return newl2

#         def site_type_lst(s):
#             for i in s:
#                 i = i.strip(' \n ')
#                 newl3.append(i)
#             return newl3

#         def multiple_mo(m):
#             m = m[0]
#             empty1.append(m)
#             for i in empty1:
#                 i = i.strip(' \n ')
#                 i = i.strip('Multiple x')
#                 i = float(i)
#                 empty2.append(i)
#             return empty2

#         def multiple_yr(m):
#             m = m[0]
#             empty3.append(m)
#             for i in empty3:
#                 i = i.strip(' \n ')
#                 i = i.strip('Multiple x')
#                 i = float(i)
#                 i = round(i*12, 2)
#                 empty4.append(i)
#             return empty4

#         def pf_lst(pf):
#             for i in pf:
#                 i = i.strip(' \n ')
#                 newl4.append(i)
#             return newl4
