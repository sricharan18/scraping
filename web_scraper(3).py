import requests
from bs4 import BeautifulSoup
import csv
from datetime import date

class scraper:
    
    def __init__(self,search_text):
        
        '''
        A class to represent a Scraper

        Parameters:
            n(str) : storing the respose of google by giving headers and text we wan't to search as input
            method :
                a. getting the links from the google and storing in a list name links_list
                b. we created a csv file as 'test_project.csv' and wrote headings in csv file
                c. calling the functions related to website by passsing link as arguments
            
        '''
        
        self.search_text = search_text
        s = requests.session()
        links_list = []
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36'}
        try:
            n = s.get(' https://www.google.com/search?q='+self.search_text,headers = headers)   #get the response of URL
            soup = BeautifulSoup(n.text,'lxml')
            l = soup.findAll('div',class_='r')
            for i in l:
                k = i.findAll('a')
                for j in k:
                    link = str(j['href'])
                    if 'https://webcache.googleusercontent.com' in link or '#' in link:
                        pass
                    else:
                        links_list.append(link)   #adding Usefull and relevant links to the list
        except:
            pass
        with open('test_project.csv','w') as csvfile:
            fields = ['website','Review_id','Review_title','Review_text','Review_stars','Review_Date','Reviewer_Name','Reviewer_Address',]
            csvwriter = csv.writer(csvfile)
            csvwriter.writerow(fields)
        with open('retailer_details.csv','w') as csvfile:
            fields = ['product_name','website','retailer','retailer_price','Date']
            csvwriter2 = csv.writer(csvfile)
            csvwriter2.writerow(fields)
        total = 0    #to remove duplicate links
        total1 = 0
        for link in links_list:    
            if 'www.amazon' in link and total == 0:
                total += 1
                self.amazon(link,self.search_text)
                
            elif 'www.flipkart.com' in link and total1 == 0:
                total1 += 1
                self.flipkart(link,self.search_text)
                

    
    def amazon(self,link,product_name):
        
        '''
        Called a function 'amazon'
        
        Parameters:
            n(str) : storing the response given by the website after giving headers and link of website as input
            method:
                a. After getting the response we crawled the details such as review, review_tile, and reviewer_details
                b. After that we scraped retailer details and stored them in a variable named 'zipped'
                c. We scraped the reviwer Address and stored in a list named profile address
            output:
                After crawling the website we wrote to csv file by calling csv_write function
                
        '''
        list1 = []
        list2 = []
        s = requests.session()
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36'}
        try:
            n = s.get(link,headers = headers)
            soup = BeautifulSoup(n.text,'lxml')
            review = soup.findAll('div',class_="a-expander-content reviewText review-text-content a-expander-partial-collapse-content")
            review_title = soup.findAll('a',class_="a-size-base a-link-normal review-title a-color-base review-title-content a-text-bold")
            review_stars = soup.findAll('i',{'data-hook':"review-star-rating"})
            reviewer_name = soup.findAll('span',class_="a-profile-name")
            review_date = soup.findAll('span',{'data-hook':"review-date"})
            profile_address = []
            profile_links = soup.findAll('a',class_="a-profile")
            for i in profile_links:
                n = s.get('https://www.amazon.in'+ i['href'],headers = headers)
                soup1 = BeautifulSoup(n.text,'lxml')
                q = str(soup1.findAll('script',{'window.CustomerProfileRecognizedCustomerId' : ''})[37])
                profile_address.append(q.split(':')[71])
            for i in range(0,5):
                try:
                    if profile_address[i] == 'null,"personalDescription"':
                        self.csv_write('Amazon',i+1,str(review_title[i].text[1:])[:-1],str(review[i].text[1:])[:-1],str(review_stars[i].text)[:3],str(review_date[i].text)[21:],reviewer_name[i].text,'',)
                    else:
                        self.csv_write('Amazon',i+1,str(review_title[i].text[1:])[:-1],str(review[i].text[1:])[:-1],str(review_stars[i].text)[:3],str(review_date[i].text)[21:],reviewer_name[i].text,(profile_address[i])[:-22],)
                except:
                    pass
            try:
                retailer_link1 = soup.find('div',id="olp-upd-new-freeshipping",class_="a-section a-spacing-small a-spacing-top-small")
                if retailer_link1 == None:
                    p = soup.find('div',id="merchant-info")
                    retailer = str((p.find('a')).text)
                    retailer_price = str((soup.find('span',id="priceblock_ourprice")).text)[2:]
                    self.csv_retailer(product_name,'Amazon',retailer,retailer_price,date.today())

                else:
                    retailer_link = retailer_link1.find('a',class_='a-link-normal')['href']
                    aa = s.get('https://www.amazon.in'+retailer_link,headers = headers)
                    aaa = BeautifulSoup(aa.text,'lxml')
                    retailer_name = aaa.findAll('h3',class_="a-spacing-none olpSellerName")
                    retailer_price = aaa.findAll('span',class_="a-size-large a-color-price olpOfferPrice a-text-bold")
                    for a in retailer_name:
                        list1.append((str(a.text)[2:])[:-2])
                    for a in retailer_price:
                        list2.append(str(a.text)[2:])
                    cv = len(list1)
                    for t in range(0,cv):
                        self.csv_retailer(str(product_name),'Amazon',list1[t],list2[t],date.today())
                    try:
                        k = aaa.find('li',class_='a-last')
                        aa = s.get('https://www.amazon.in'+k.find('a')['href'],headers = headers)
                        aaa = BeautifulSoup(aa.text,'lxml')
                        retailer_name = aaa.findAll('h3',class_="a-spacing-none olpSellerName")
                        retailer_price = aaa.findAll('span',class_="a-size-large a-color-price olpOfferPrice a-text-bold")
                        for a in retailer_name:
                            list1.append((str(a.text)[2:])[:-2])
                        for a in retailer_price:
                            list2.append(str(a.text)[2:])
                        cv = len(list1)
                        for t in range(0,cv):
                            self.csv_retailer(str(product_name),'Amazon',list1[t],list2[t],date.today())
                    except:
                        pass
                    
            except:
                retailer = "Details not available"
                retailer_price = 'Details not available'
                self.csv_retailer(product_name,'Amazon',retailer,retailer_price,date.today())
        except:
            pass
 
    
    def flipkart(self,link,product_name):
        
        '''
        Called a function 'flipkart'
        
        Parameters:
            n(str) : storing the response given by the website after giving headers and link of website as input
            method:
                a. After getting the response, we crawled the details such as review, review_tile, and reviewer_details
                b. After that we crawled retailer details and stored them in a variable named 'zipped'
                c. We scraped the reviwer Address and stored in a list named profile address
            output:
                After crawling the website we wrote to csv file by calling csv_write function
        '''
        
        s = requests.session()
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36'}
        try:
            n = s.get(link,headers = headers)
            soup = BeautifulSoup(n.text,'lxml')
            review= soup.findAll('div',class_='qwjRop')
            review_title = soup.findAll('p',class_="_2xg6Ul")
            review_stars = soup.findAll('div',class_="hGSR34 E_uFuv")
            reviewer_name = soup.findAll('p',class_="_3LYOAd _3sxSiS")
            review_date = soup.findAll('p',class_='_3LYOAd')
            review_date = review_date[1::2] 
            reviewer_address = soup.findAll('p',class_="_19inI8")
            retailer1 = soup.find('div',id='sellerName')
            
            for i in range(0,3):
                try:
                    
                    self.csv_write('flipkart',i+1,review_title[i].text,str(review[i].text),str(review_stars[i].text),str(review_date[i].text),reviewer_name[i].text,str(reviewer_address[i].text)[17:])
                except:
                    try:
                        self.csv_write('flipkart',i+1,str(review[i].text),'','','','','')
                    except:
                        pass
            if retailer1 == None:
                retailer = 'Details not available'
                retailer_price = 'Details not available'
            else:
                retailer = str(retailer1.text)[:-3]
                k = str((soup.find('script',id="is_script")).text).split(':')
                retailer_price =  str(k[1040])[1:-12]
                if '.00' in retailer_price:
                    pass
                else:
                    retailer_price = (soup.find('div',class_="_1vC4OE _3qQ9m1")).text
            self.csv_retailer(product_name,'Flipkart',retailer,retailer_price[1:],date.today())
        except:
            pass
        

 
    def csv_write(self,website,Review_id,Review_title,Review_text,Review_stars,Review_Date,Reviewer_Name,Reviewer_Address,):
    
        '''
        called a function csv_write
        opening the csvfile and appending the data to file by using csvwriter
        '''      
        with open('test_project.csv','a+') as csvfile:
            csvwriter = csv.writer(csvfile)  
            csvwriter.writerow([website,Review_id,Review_title,Review_text,Review_stars,Review_Date,Reviewer_Name,Reviewer_Address,])
            
    def csv_retailer(self,website,product_name,retailer,retailer_price,date):
    
        '''
        called a function csv_write
        opening the csvfile and appending the data to file by using csvwriter
        '''      
        with open('retailer_details.csv','a+') as csvfile:
            csvwriter2 = csv.writer(csvfile)  
            csvwriter2.writerow([website,product_name,retailer,retailer_price,date])

            
if __name__ == '__main__':
    '''
    Parameters:
        num(str) : storing the integer, that number of be products to searched 
    We calling scraper class by passing product name as arguments
    '''
    num = int(input('Enter the Number of Products : '))
    for i in range(num):
        search_text = input('Enter the Search text : ')
        scraper(search_text)



        


