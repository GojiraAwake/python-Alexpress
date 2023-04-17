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
        print ("err_status  "+str(err_status))         
        inforow=["err_times"+str(err_times),"err_status"+str(err_status),str(exc_cnt)]         
        writer.writerow(inforow)    
    file.close()
    f.close()



def analysisweb(url,prodict_id):
    global money_rate
    global err_status
    global err_times
    header = {'cookie':'xman_t=8uZ0p04SjNiNlWaVlhMZgRdHr3/4HdNOJbSzfdS8AMH8v4CQzRhznS8kA+SOUAr5; xman_f=Iw6qJN+rCCu7EP5PWbDF/MFbhBiE2fQy5cJEysLJTcW009B8qLZ35+mHf6NDTkDWA+GAREDVmkwtrw4RA//BrAycq05ru7g0hYf7/+HNYXzqU2nnhiRquQ==; aer_abid=5d6276e80de39ab7; cna=nk+oF5/q+3ICAaxoUaCGGPDm; _ym_uid=167629996958093974; _ym_d=1676299969; tmr_lvid=13f589b89f1aec7090d4c552861d8dd3; tmr_lvidTS=1676299969440; ae_ru_pp_v=1.0.2; _gcl_au=1.1.865669814.1676300060; aer_lang=ru_RU; _ga=GA1.2.1630750625.1676299968; _ga_VED1YSGNC7=GS1.1.1676303240.2.1.1676304693.0.0.0; _gid=GA1.2.1648671296.1677241612; _bl_uid=zkl1FemOi0Ilpz48ziC8pahcFtCO; _m_h5_tk=a6c123016606ed48c3f0f588f1bc58c9_1677407105255; _m_h5_tk_enc=cdfbfe229671fdb09f309b1c35986c1f; _fbp=fb.1.1677406263513.1926034384; xlly_s=1; _ym_isad=2; xman_us_f=x_locale=ru_RU&x_l=0&x_c_chg=1&x_c_synced=1; acs_usuc_t=x_csrf=_3ovf56lh5hf&acs_rt=fae0731ebaf94ba089aced5bd29b2a92; intl_locale=ru_RU; aep_usuc_f=b_locale=ru_RU&c_tp=RUB&region=RU&site=rus; _ym_visorc=b; x5sec=7b22733b32223a226137363936613166363237336563626438383463303130306562326439666564222c2261656272696467653b32223a226338653163336232373536623665316235386433333861393530666436313466434d506167714147454f6e2f6f4f795476766e386d774577792f6e647067524141773d3d227d; tmr_detect=0%7C1677765975228; intl_common_forever=Z8p35OZWLimj33g1lmU6IrOqouhzvBUCoBRVENNAC1aF3q75acGiog==; JSESSIONID=6C16FFF2C74FD738FB3549A9023D96C7; tfstk=cSudByYktdvnSD9u7yKG4op0vvWdabJgENycyqWwfzMympQfksqnoqBxZdPb3JdO.; l=fBE78Dz7T7GKAGH8BO5Zlurza77tNQAf5sPzaNbMiIEGa6whQFw4VOCsMMMWYdtjgT5cBeKrl5ZFzdF2yxaLRxtJTTCZ8V21spJM8es3m3b5.; isg=BDQ0e6_Y7GfnuX9BMEHGzn5nBfKmDVj31kmhns6X5b9COd2D9xmVhx2_uXHhwZBP',
        'origin':'https://aliexpress.ru',
        'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'
    }
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
    price = soup.find(attrs={'class':'snow-price_SnowPrice__blockMain__azqpin HazeProductPrice_HazeProductPrice__priceMain__1wtyf'})
    price = price.find_all(attrs={'class':'snow-price_SnowPrice__mainM__azqpin'})    
    seller_name =soup.find(attrs={'class':'snow-ali-kit_Typography__base__1shggo snow-ali-kit_Typography-Primary__base__1xop0e snow-ali-kit_Typography__strong__1shggo snow-ali-kit_Typography__sizeHeadingL__1shggo SnowStoreInfo_SnowStoreInfo__storeName__1a34j'})
    good_country = soup.find_all(attrs={'class':'snow-ali-kit_Typography__base__1shggo snow-ali-kit_Typography-Primary__base__1xop0e SnowSku_SkuPropertyItem__propName__sj6tl'})
    sales_volumes =soup.find_all(attrs={'class':'snow-ali-kit_Typography__base__1shggo snow-ali-kit_Typography__base__1shggo snow-ali-kit_Typography__sizeTextM__1shggo HazeProductDescription_HazeProductDescription__typographyM__1uxkw'})  
    prodict_ids = prodict_id
    try:
        seller_name = seller_name.getText()#.split('(')[0].strip()
        print("Seller_name="+str(seller_name))
    except Exception as e:
        seller_name=' '
        print("3.current err_times=seller_name"+str(e))
        
    try:
        sales_volume= sales_volumes[2].getText().split(' ')[0].strip()
        print("sales_volume="+str(sales_volume))
    except Exception as e:
        sales_volume =' '
        err_times+=1
        print("3.current err_times=sales_volume"+str(e))
        
    try:
        goodname=good_country[1].get_text()
        print("goodname="+str(goodname))
    except Exception as e:
        goodname =' '
        err_times+=1
        print("3.current err_times=goodname"+str(e))
        
    try:
        region=good_country[3].get_text() 
        if(region!="CHINA"):
            region = "RU" 
        print("region"+str(region))
    except Exception as e:
        region= ' '
        err_times+=1
        print("3.current err_times=region"+str(e))
        
    try:
        price = price[0].get_text() 
        price = price.replace(",", ".").replace('\xa0', '').replace(' ', '')
        total_prices = ''
        for i in range(len(price)-1):
            total_prices = total_prices + price[i]
        total_prices = float(total_prices)*money_rate
    except Exception as e:
        total_prices=0
        err_times+=1
        print("3.current err_times=price"+str(e))   
    
    rowdata=[str(url),str(seller_name),str(prodict_ids),str(goodname),str(sales_volume),str(total_prices),str(region)]
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
