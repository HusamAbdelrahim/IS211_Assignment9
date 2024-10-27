# scraped this page https://en.wikipedia.org/wiki/List_of_World_Series_champions
import requests
from bs4 import BeautifulSoup
import pandas as pd

def scrape_world_series_data():
    # URL of the Wikipedia page
    url = "https://en.wikipedia.org/wiki/List_of_World_Series_champions"
    
    try:
        # send a GET request to the URL
        response = requests.get(url)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # find the main table
        table = soup.find('table', {'class': 'wikitable'})
        
        if table:
            world_series = []
            
            # process each row in the table
            for row in table.find_all('tr')[1:]:  # skip header row
                cols = row.find_all(['td', 'th']) # <td> <th> dom elements
                
                if len(cols) >= 4: 
                    try:
                        # extract the data we want
                        year = cols[0].text.strip()
                        winner = cols[1].text.strip()
                        loser = cols[2].text.strip()
                        result = cols[3].text.strip()
                        
                        # clean up the data
                        winner = ''.join([i for i in winner if not i.isdigit() and i not in '[]'])
                        loser = ''.join([i for i in loser if not i.isdigit() and i not in '[]'])
                        
                        # add to our list
                        world_series.append({
                            'Year': year,
                            'Winner': winner,
                            'Loser': loser,
                            'Result': result
                        })
                    except:
                        continue
            
            # convert to DataFrame
            df = pd.DataFrame(world_series)
            
            # save to CSV
            df.to_csv('world_series_champions.csv', index=False)
            print("\nData has been saved to 'world_series_champions.csv'")
            
        else:
            print("Could not find the World Series table on the page")
            
    except requests.RequestException as e:
        print(f"Error fetching the webpage: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    print("\nScraping World Series Champions data...")
    scrape_world_series_data()