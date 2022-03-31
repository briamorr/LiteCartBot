from datetime import datetime
import requests
from bs4 import BeautifulSoup
from time import time, sleep

#Search for matching product name and return direct link if found
def findProducts(product):
    URL = "https://demo.litecart.net/search?query=" + product 
    page = requests.get(URL)

    soup = BeautifulSoup(page.content, "html.parser")

    result = soup.find("a", class_="link", title=product)

    if(result):
        return result.get('href')

#Check if the product is in stock by looking for add to cart button and then checkout if it is
def checkInstock(productUrl):
    page = requests.get(productUrl)
    sessioncookies = page.cookies
  
    soup = BeautifulSoup(page.content, "html.parser")

    result = soup.find("button", class_="btn btn-success", text="Add To Cart")
    if(not result):
        print(datetime.now(), "- Product Out Of Stock")
        return

    productdata = 'product_id='+ soup.find('input', {'name': 'product_id'}).get('value') + '&quantity=1&add_cart_product=true'
    headers = {'Content-type': 'application/x-www-form-urlencoded; charset=UTF-8'}

    result = requests.post('https://demo.litecart.net/ajax/cart.json',data=productdata, cookies=sessioncookies, headers=headers)
    productidkey = result.json()["items"][0]["key"]

    checkOut(sessioncookies, productidkey)

#Complete order checkout
def checkOut(sessioncookies, productidkey):
    firstname, lastname = "Bob", "Smith"
    address1, postcode, city, country_code, zone_code = "1+Main+St", "27509", "Cary", "US", "NC"
    email, phone = "bob%40gmail.com", "%2B19199009999"

    #Customer Info
    checkoutData="customer_details=true&company=&tax_id=NA\
        &firstname="+firstname+"&lastname="+lastname+"\
        &address1="+address1+"&address2=&postcode="+postcode+"&city="+city+"&country_code="+country_code+"&zone_code="+zone_code+"\
        &email="+email+"&phone="+phone
    result = requests.post('https://demo.litecart.net/ajax/checkout_customer',data=checkoutData, cookies=sessioncookies, headers={'Content-type': 'application/x-www-form-urlencoded'})

    #Delivery Method
    checkoutData="shipping%5Boption_id%5D=sm_zone_weight%3Azone_x"
    result = requests.post('https://demo.litecart.net/ajax/checkout_shipping',data=checkoutData, cookies=sessioncookies, headers={'Content-type': 'application/x-www-form-urlencoded'})

    #Payment Method (CoD)
    checkoutData="payment%5Boption_id%5D=pm_cod%3Acod"
    result = requests.post('https://demo.litecart.net/ajax/checkout_payment',data=checkoutData, cookies=sessioncookies, headers={'Content-type': 'application/x-www-form-urlencoded'})

    #Checkout Review
    checkoutData="comments="
    result = requests.post('https://demo.litecart.net/ajax/checkout_summary',data=checkoutData, cookies=sessioncookies, headers={'Content-type': 'application/x-www-form-urlencoded'})
   
    #Checkout
    checkoutData = "item%5B" + productidkey + "%5D%5Bquantity%5D=1\
        &customer_details=true&company=&tax_id=NA\
        &firstname="+firstname+"&lastname="+lastname+"&address1="+address1+"&address2=&postcode="+postcode+"&city="+city+"&country_code="+country_code+"&zone_code="+zone_code+"\
        &email="+email+"&phone="+phone+"\
        &shipping%5Boption_id%5D=sm_zone_weight%3Azone_x\
        &payment%5Boption_id%5D=pm_cod%3Acod\
        &comments=&terms_agreed=1&confirm_order=true"
    result = requests.post('https://demo.litecart.net/order_process',data=checkoutData, cookies=sessioncookies, headers={'Content-type': 'application/x-www-form-urlencoded', 'Referer': 'https://demo.litecart.net/checkout'})

    soup = BeautifulSoup(result.content, "html.parser")

    result = soup.find("a",text="Click here for a printable copy")
    print(datetime.now(), "Order Confirmation: " + result.get('href'))
    quit()

#Enter product to search for and loop through until it is in stock and buy it
product = "Green Duck"

while True:
    productUrl = findProducts(product)

    if productUrl:
        checkInstock(productUrl)
    else:
        print(datetime.now(), "- Product Not Found")

    sleep(5)
        
