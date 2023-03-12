import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import random
import json
import time

urls_group=[]
website_dic = []
website_group ={}
dic_to_json ={}
sku_ids = []
cnt= 0 

while True:
    print('warning: the j2_web_data.json will be re-write ')
    print('press y  if you want to continue ')
    answer = input('inupt: ')
    if answer.lower() == 'y':
        print(' you have to wait this , or skuid-data  will be incomplete')
        break
    else:
        print('exit')
        exit(0)


with open('j1_website_unit.json') as f:
    data = json.load(f)
#extract the product_type and urls form the json
for website in data["website_unit"]:
    product_type = website["product_type"]
    urls = website["urls"]
    for url in urls:
        urls_item= url.split('item/')[1].strip()   
        urls_item = urls_item.split('.html')[0].strip()
        urls_group.append(urls_item)
    website_dic.append([product_type, urls_group]) 
    urls_group=[]  
f.close()
#print(len(website_dic),len(website_dic[0]),len(website_dic[0][1]))    
print(website_dic)
      
err_status= 0    
err_times = 0
header = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'}
with open("j2_web_data.json", "w") as outfile:
    outfile.write("[")#json foramt complete 
    for i in range(0,len(website_dic)):   # each product type
        for x in range(0,len(website_dic[i][1])): # each store
            url = "https://aliexpress.ru/item/"+str(website_dic[i][1][x])+".html" 
            print(url)
            try:
                response = requests.get(url,headers=header)
                print(response.status_code)
                if(response.status_code!=200):
                    err_status+=1
                    print ("err_status"+str(err_status))
                    print('error requrest=',response.status_code)
                    time.sleep(10)
                    continue
            except Exception as e:
                err_times+=1
                print(e)
                print("current err_times="+str(err_times))   
                time.sleep(10)
                continue
            html = response.text
            soup = BeautifulSoup(html, 'html.parser')
            #locate the skuid 
            skuid_json = soup.find("script", {"id": "__AER_DATA__"})
            content = skuid_json.string.strip()
            data = json.loads(content)
            #extract the skuid in one website
            for widget in data['widgets']:  
                widget=widget.get("children")
                if(widget!=None):
                    for item in widget:
                        if(item!=None):
                            for child in item['children']:
                                if(child!=None):
                                    for grandchild in child['children']:
                                        if(grandchild!=None):
                                            try:
                                                sku_info = grandchild['props']['skuInfo']
                                                if(sku_info!=None):
                                                    for price_info in sku_info['priceList']:
                                                        sku_id = price_info['skuId']
                                                        sku_ids.append(sku_id)
                                                        #print(sku_id)
                                            except Exception as e:
                                                print("end the fetch")
            time.sleep(10)
    ####prduct type
        #store
            #skuid
            website_group[website_dic[i][1][x]] = sku_ids
            sku_ids=[]
        #print(website_group)
        dic_to_json[website_dic[i][0]]=website_group
        json.dump(dic_to_json, outfile)
        #print(group_to_json)
        website_group={}   
        dic_to_json={}  #clen the stack when one mode_dic was write in json

    #json foramt complete 
        cnt+=1
        if(cnt!=len(website_dic)):
            outfile.write(",")
    outfile.write("]")

       
#outfile.write("err_times="+str(err_times)+"    err_status="+str(err_status))
outfile.close()

print('-----------------------------------------------------------------------')
print ("err_times"+str(err_times))
print ("err_status"+str(err_status))       
print('-----------------------------------------------------------------------')
print("this process is finish , check the j2_web_data.josn  formath is right ")
print("check it in this website:  https://www.json.cn/")
print("and copy the convert-data to the j2_web_data.josn")
print('-----------------------------------------------------------------------')

