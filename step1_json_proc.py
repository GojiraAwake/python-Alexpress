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
header = {
    'cookie':'xman_t=8uZ0p04SjNiNlWaVlhMZgRdHr3/4HdNOJbSzfdS8AMH8v4CQzRhznS8kA+SOUAr5; xman_f=Iw6qJN+rCCu7EP5PWbDF/MFbhBiE2fQy5cJEysLJTcW009B8qLZ35+mHf6NDTkDWA+GAREDVmkwtrw4RA//BrAycq05ru7g0hYf7/+HNYXzqU2nnhiRquQ==; aer_abid=5d6276e80de39ab7; cna=nk+oF5/q+3ICAaxoUaCGGPDm; _ym_uid=167629996958093974; _ym_d=1676299969; tmr_lvid=13f589b89f1aec7090d4c552861d8dd3; tmr_lvidTS=1676299969440; ae_ru_pp_v=1.0.2; _gcl_au=1.1.865669814.1676300060; aer_lang=ru_RU; _ga=GA1.2.1630750625.1676299968; _ga_VED1YSGNC7=GS1.1.1676303240.2.1.1676304693.0.0.0; _gid=GA1.2.1648671296.1677241612; _bl_uid=zkl1FemOi0Ilpz48ziC8pahcFtCO; _m_h5_tk=a6c123016606ed48c3f0f588f1bc58c9_1677407105255; _m_h5_tk_enc=cdfbfe229671fdb09f309b1c35986c1f; _fbp=fb.1.1677406263513.1926034384; xlly_s=1; _ym_isad=2; xman_us_f=x_locale=ru_RU&x_l=0&x_c_chg=1&x_c_synced=1; acs_usuc_t=x_csrf=_3ovf56lh5hf&acs_rt=fae0731ebaf94ba089aced5bd29b2a92; intl_locale=ru_RU; aep_usuc_f=b_locale=ru_RU&c_tp=RUB&region=RU&site=rus; _ym_visorc=b; x5sec=7b22733b32223a226137363936613166363237336563626438383463303130306562326439666564222c2261656272696467653b32223a226338653163336232373536623665316235386433333861393530666436313466434d506167714147454f6e2f6f4f795476766e386d774577792f6e647067524141773d3d227d; tmr_detect=0%7C1677765975228; intl_common_forever=Z8p35OZWLimj33g1lmU6IrOqouhzvBUCoBRVENNAC1aF3q75acGiog==; JSESSIONID=6C16FFF2C74FD738FB3549A9023D96C7; tfstk=cSudByYktdvnSD9u7yKG4op0vvWdabJgENycyqWwfzMympQfksqnoqBxZdPb3JdO.; l=fBE78Dz7T7GKAGH8BO5Zlurza77tNQAf5sPzaNbMiIEGa6whQFw4VOCsMMMWYdtjgT5cBeKrl5ZFzdF2yxaLRxtJTTCZ8V21spJM8es3m3b5.; isg=BDQ0e6_Y7GfnuX9BMEHGzn5nBfKmDVj31kmhns6X5b9COd2D9xmVhx2_uXHhwZBP',
    'origin':'https://aliexpress.ru',
    'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'
}
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
print()
print ("count the num  of the web site is not right: err_times"+str(err_times))
print (" count the num of no  webesite response: err_status"+str(err_status))       
print('-----------------------------------------------------------------------')
print("this process is finish , check the j2_web_data.josn  formath is right ")
print("check it in this website:  https://www.json.cn/")
print("and copy the convert-data to the j2_web_data.josn")
print('-----------------------------------------------------------------------')