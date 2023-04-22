import requests
from bs4 import BeautifulSoup
import pandas as pd
import logging
import tkinter as tk

logging.basicConfig(level=logging.DEBUG, filename="logfile", filemode="a+",
                    format="%(asctime)-15s %(levelname)-8s %(message)s")

def scrape_hotel_contacts(url):
    response = requests.get(url)
    logging.info(f"Base URL - {url}: Status code: {response.status_code}")
    soup = BeautifulSoup(response.content, 'html.parser')
    hotels = soup.find_all('div', class_='city_tab')

    pages_ul = soup.find('ul', class_='pagination')
    pages = pages_ul.find_all('li')
    number_of_pages = int(pages[-3].text) if len(pages)>=3 and pages[-3]!=None and pages[-3].text!=None else 0
    logging.info(f"Number of pages: {number_of_pages}")
    result = []
    for page in range(1, number_of_pages+1):
        logging.info(f"Scrape started for page number: {page}")
        url = url
        if(page!=1):
            url+="/pag="+str(page)+"/"
            response = requests.get(url)
            soup = BeautifulSoup(response.content, 'html.parser')
            hotels = soup.find_all('div', class_='city_tab')
        for hotel in hotels:
            hotel_details_url = hotel.find('div', class_='city_title').find('a')['href']
            hotel_name = hotel.find('div', class_='city_title').find('h3').text
            hotel_city = hotel.find('h4').text
            if(hotel_details_url!=None):
                hotel_details_page_content = requests.get(hotel_details_url).content
                details_soup = BeautifulSoup(hotel_details_page_content, 'html.parser')
                contact_details = details_soup.find('div', class_='table_address').find_all('table')[1].find_all('tr')
                for contact_detail in contact_details:
                    try:
                        if(contact_detail.find('td', class_='table_space_td_left1').find('img')['title'] == 'Mobile'):
                            mobile_nos = contact_detail.find('td', class_='table_space_td_right1').text.split(", ")
                            for mobile_number in mobile_nos:
                                result.append({"Name": hotel_name+" "+hotel_city, "Mobile": mobile_number})
                                logging.info({"Name": hotel_name+" "+hotel_city, "Mobile": mobile_number})
                    except Exception as exp:
                        pass
        logging.info(f"Scrape successfull for page: {page}")
    return result

def save_results_to_csv(result, csv_name):
    df = pd.DataFrame(result)
    df.drop_duplicates(inplace=True)
    df.to_csv(f"downloads/{csv_name}.csv", index=False)
    logging.info(f"Results saved to downloads/{csv_name}.csv")

def submit():
    url = entry1.get()
    csv_name = entry2.get()
    result = scrape_hotel_contacts(url)
    save_results_to_csv(result, csv_name)

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Hotel Scraper")
    root.geometry("400x300")

    label1 = tk.Label(root, text="Provide url")
    label1.pack(pady=10)

    entry1 = tk.Entry(root, width=30)
    entry1.pack()

    label2 = tk.Label(root, text="Enter output file name")
    label2.pack(pady=10)

    entry2 = tk.Entry(root, width=30)
    entry2.pack()

    button = tk.Button(root, text="Submit", command=submit)
    button.pack(pady=10)

    root.mainloop()