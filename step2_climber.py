 #!/usr/bin/python
 # -*- coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup
import json
import time
import csv
import re 
import os
import schedule

money_rate =0
err_status  =0
err_times =0


def RuToCN_rate():
    global money_rate
    global err_status
    global err_times
    header = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'}
    #url1 ="https://wise.com/zh-cn/currency-converter/rub-to-cny-rate?amount=1"   
    url1 ="https://themoneyconverter.com/RUB/CNY"
    try:
        print(url1)
        response = requests.get(url1,headers=header)
        if(response.status_code!=200):
            err_status+=1
            print ("1.err_status"+str(err_status))
            print('1.error requrest=',response.status_code)
            money_rate = 1
            return 0 
    except Exception as e:
        err_times+=1
        print("2.current err_times="+str(err_times))   
        money_rate = 1
        return 0 
    html_content = response.text    
    pattern = re.compile(r'data-value="([\d\.]+)"')
    match = pattern.search(html_content)
    if match:
        data_value = match.group(1)
        print(data_value)
        rate= data_value
    else:
        print('data-value not found')
        rate = 1 
    rate = float(rate)
    #soup = BeautifulSoup(html_content, 'html.parser')   
    #rate = soup.find(attrs={'class':'text-xs-center text-lg-left'}) 
    #rate = rate.find(attrs={'class':'text-success'}) 
    #rate = float(rate.get_text())
    if (rate==0 or rate==''):
        rate=1
    money_rate = rate
    print("tody_money_rate is:"+str(rate))
    return 0 




def climber(webjson):
    global money_rate
    global err_status
    global err_times
    #get the time
    exc_cnt =0
    t =time.localtime()
    time_now=str(t.tm_year)+"_"+str(t.tm_mon)+"_"+str(t.tm_mday)+"_"+str(t.tm_hour)+"_"+str(t.tm_min)
    with open('csv_f\\'+time_now+'.csv', 'w', newline='') as file: #open csv.
        writer = csv.writer(file)
        if file.tell() == 0:
            writer.writerow(["links","Store_Name","Product_ID ","goods", "Sales_Volume", 'price(*('+str(money_rate)+')',"region"])   
    #open data.json and analysis
        with open(webjson) as f:
            data = json.load(f)            
        for items in data:
            for prodict_id in items:
                #print(prodict_id)
                for product_num in items[prodict_id]:
                    #print(product_num)
                    for skuid in items[prodict_id][product_num]:
                        url ="https://aliexpress.ru/item/"+str(product_num)+".html?sku_id="+str(skuid)
                    #anaylsis     
                        value = analysisweb(url,prodict_id)
                        if(value == 0 ):
                            continue                 
                        writer.writerow(value)
                        exc_cnt+=1
                        print('-----------------'+str(exc_cnt)+'----------------------')
                        time.sleep(10)

        print ("err_times"+str(err_times))
        print ("err_status"+str(err_status))         
        inforow=["err_times"+str(err_times),"err_status"+str(err_status),str(exc_cnt)]         
        writer.writerow(inforow)    
    file.close()
    f.close()



def analysisweb(url,prodict_id):
    global money_rate
    global err_status
    global err_times
    header = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'}
    print(url)
    try:
        response = requests.get(url,headers=header,timeout=10)
        print(response.status_code)
        if(response.status_code!=200):
            err_status+=1
            print ("1.err_status"+str(err_status))
            print('1.error requrest=',response.status_code)
            time.sleep(10)
            return 0
    except Exception as e:
        err_times+=1
        print("2.current err_times="+str(err_times))   
        time.sleep(10)
        return 0
    #bs4
    html_content = response.text
    soup = BeautifulSoup(html_content, 'html.parser')
#find the data   
    price = soup.find(attrs={'class':'snow-price_SnowPrice__mainS__18x8np'})
    seller_name =soup.find(attrs={'class':'snow-ali-kit_Typography__base__1shggo snow-ali-kit_Typography__base__1shggo snow-ali-kit_Typography__sizeTextM__1shggo SnowProductDescription_SnowProductDescription__typographyM__18hha'})
    good_country = soup.find_all(attrs={'class':'snow-ali-kit_Typography__base__1shggo snow-ali-kit_Typography-Primary__base__1xop0e SnowSku_SkuPropertyItem__propName__sj6tl'})
    sales_volume =soup.find(attrs={'class':'snow-ali-kit_Typography__base__1shggo snow-ali-kit_Typography__base__1shggo snow-ali-kit_Typography__sizeTextM__1shggo SnowProductDescription_SnowProductDescription__textItem__18hha SnowProductDescription_SnowProductDescription__typographyM__18hha'})
    prodict_ids = prodict_id
    try:
        seller_name = seller_name.getText().split('(')[0].strip()
    except Exception as e:
        seller_name=' '
        print("3.current err_times=seller_name"+str(e))
    try:
        sales_volume = sales_volume.getText().split(' ')[0].strip()
    except Exception as e:
        sales_volume =' '
        err_times+=1
        print("3.current err_times=sales_volume"+str(e))
    try:
        goodname=good_country[1].get_text()
    except Exception as e:
        goodname =' '
        err_times+=1
        print("3.current err_times=goodname"+str(e))
    try:
        region=good_country[3].get_text() 
        if(region!="CHINA"):
            region = "RU" 
    except Exception as e:
        region= ' '
        err_times+=1
        print("3.current err_times=region"+str(e))
    try:
        price = price.get_text()
        price = price.split('руб')[0].strip()  
        price = price.replace(",", ".")
        price = price.replace('\xa0', '')
        price = float(price)*money_rate
    except Exception as e:
        price=' '
        err_times+=1
        print("3.current err_times=price"+str(e))   
    #print(float(price))                  
    #print(region)
    #print(price)
    #print(goodname)
    #print(seller_name)
    #print(sales_volume)
    
    rowdata=[str(url),str(seller_name),str(prodict_ids),str(goodname),str(sales_volume),str(price),str(region)]
    return rowdata

def task():
    file_name = 'j2_web_data.json'
    if not os.path.exists('csv_f'):
        os.makedirs('csv_f')  
    RuToCN_rate()
    climber(file_name)
     


def main():
    task()
    #schedule.every(5).hours.do(task)
    #while True:
    #    schedule.run_pending()
    #    time.sleep(90)


if __name__=="__main__":
    main()
