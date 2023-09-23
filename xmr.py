from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import re

def initialisation():
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--window-size=1920,1080')
    service = Service(executable_path=ChromeDriverManager().install())
    return options, service

def grab_html(options, service, url) :
    driver = webdriver.Chrome(service=service, options=options)
    driver.get(url)
    html_soup = BeautifulSoup(driver.page_source, features="lxml")
    driver.quit()
    return html_soup

def grab_nodes(html_soup):
    onglets = html_soup.find_all("tbody")
    pays = onglets[0].find_all("tr")

    country_list_node = []

    for country in pays :
        infos = country.find_all("td")
        country_list = {}
        country_list["pays"] = infos[0].text
        country_list["node"] = int(infos[1].text)
        country_list_node.append(country_list)
    return country_list_node

def grab_price(html_soup):
    # prices
    first = html_soup.find_all(id = "graphic")
    second = first[0].find_all("div")
    prices = second[0].find_all("div", style=re.compile("absolute; top"))

    # names
    countrys = html_soup.find_all('a', attrs={"class": "graph_outside_link"})


    country_list_price = []
    count = -1
    while count != len(prices)-1 :
        count = count + 1
        identity = {}
        identity["pays"] = rename_pays(countrys[count].text)
        identity["price"] = float(prices[count].text)
        country_list_price.append(identity)
    return country_list_price

def rename_pays(string) :
    if string == "USA" :
        string = "United States"
    elif string == "UK" :
        string = "United Kingdom"
    elif string == "" :
        string = ""
    elif string == "" :
        string = ""
    return string

def list_diff(country_list_node, country_list_price):
    yes_count = 0
    yes_list = []
    no_list = []

    for country_node in country_list_node :
        for country_price in country_list_price :
            if country_node["pays"] == country_price["pays"] :
                country_node["price"] = country_price["price"]
                yes_count = yes_count + 1
                yes_list.append(country_node["pays"])

    skipped = 0
    no_list =[]
    for country_node in country_list_node :
        found = False
        for yes in yes_list :
            if yes == country_node["pays"] :
                found = True
        if found ==  False :
            skipped = skipped + country_node["node"]
            no_list.append(country_node["pays"])
    return no_list, skipped

def average_cost(country_list_node):
    total_sum = 0
    total_node = 0

    for country in country_list_node :
        if len(country) == 3 :
            total_sum = total_sum + country["price"] * country["node"]
            total_node = total_node + country["node"]
    return total_sum, total_node


options, service = initialisation()

html_soup_node = grab_html(options, service, "https://monerohash.com/nodes-distribution.html")
html_soup_price = grab_html(options, service, "https://www.globalpetrolprices.com/electricity_prices/")

country_list_node = grab_nodes(html_soup_node)
country_list_price = grab_price(html_soup_price)

no_list, skipped = list_diff(country_list_node, country_list_price)
total_sum, total_node = average_cost(country_list_node)

print("Total countries : ",len(country_list_price))
print("Total nodes : ",total_node, "\n")
print("Country's node skipped : ", no_list)
print("Node skipped : ", skipped,"\n")
print("Average kWh cost", round(total_sum / total_node,3),"$")


# 23/09/23
# Total countries :  147
# Total nodes :  4049 
# Country's node skipped :  ['Czechia', 'United Arab Emirates', 'Seychelles', 'Dominican Republic', 'Croatia', 'Puerto Rico', 'Mongolia', 'Bosnia and Herzegovina']
# Node skipped :  37 
# Average kWh cost 0.236 $

# 06/09/23
# Total countries :  147
# Total nodes :  3984 
# Country's node skipped :  ['Czechia', 'Seychelles', 'Croatia', 'United Arab Emirates', 'Puerto Rico', 'Bosnia and Herzegovina']
# Node skipped :  36 
# Average kWh cost 0.242 $
