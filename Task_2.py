import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

#Get response from flipkart
def get_response(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        return soup 
    except requests.exceptions.HTTPError as errh:
        print ("HTTP Error:", errh)
        return "error"
    except requests.exceptions.ConnectionError as errc:
        print ("Error Connecting:", errc)
        return "error"
    except requests.exceptions.Timeout as errt:
        print ("Timeout Error:", errt)
        return "error"
    except requests.exceptions.RequestException as err:
        print ("Something went wrong:", err)
        return "error"

def get_flipkart_data(search_query):
    base_url = "https://www.flipkart.com/search?q="
    search_url = base_url + search_query

    soup = get_response(search_url)

    #Get total number of pages
    page = soup.find('div', {'class': '_2MImiq'})
    page_num_text = page.find('span').text.strip()
    total_page_num = int(page_num_text.split(" ")[-1])
    print("Total Pages: ",total_page_num)
    # print(total_page_num)
    # print(type(total_page_num))

    #To store details of the product
    product_name_list = []
    product_price_list = []
    product_rating_list = []
    product_num_of_ratings_list = []
    product_num_of_reviews_list = []

    #get data of products with pages numbers
    for p in range(1,total_page_num+1):
        search_page_url = search_url+"&page="+str(p)
        soup = get_response(search_page_url)
        # print(soup)

        #if error occurs, it will stop requesting further pages and store data in csv
        if soup == "error":
            break
        for product in soup.find_all('div', {'class': '_3pLy-c row'}):
           # print(product)
            product_name_elem = product.find('div', {'class': '_4rR01T'})
            # print(product_name_elem)
            price_elem = product.find('div', {'class': '_30jeq3 _1_WHN1'})
            rating_elem = product.find('div',{'class':'_3LWZlK'})
            ratings_reviews_elem = product.find('span', {'class': '_2_R_DZ'})
            
            if product_name_elem and price_elem and ratings_reviews_elem and rating_elem:
                product_name = product_name_elem.text.strip()
                price = price_elem.text.strip()
                rating = rating_elem.text.strip()
                total_ratings, reviews = ratings_reviews_elem.text.strip().split(" & ")

                product_name_list.append(product_name)
                product_price_list.append(price.split("₹")[1])
                product_rating_list.append(rating)
                product_num_of_ratings_list.append(total_ratings.split(" ")[0])
                product_num_of_reviews_list.append(reviews.split(" ")[0])

        #to eliminate error of "to many requests for the url"
        #we can delay requests
        time.sleep(3)

    #create dataframe of products
    df = pd.DataFrame({
        'Name':product_name_list,
        'Price':product_price_list,
        'Rating':product_rating_list,
        'Number of Ratings':product_num_of_ratings_list,
        'Number of Reviews':product_num_of_reviews_list
        })
    return df

#save data in csv
def save_to_csv(data, file_path='flipkart_mobiles.csv'):
    try:
        data.to_csv(file_path, index=False, encoding='utf-8')
        print("Data saved in csv file")
    except Exception as e:
        print(f'Error saving data to CSV: {e}')

search_query = "iphone"
flipkart_data = get_flipkart_data(search_query)
# print(flipkart_data)
save_to_csv(flipkart_data)