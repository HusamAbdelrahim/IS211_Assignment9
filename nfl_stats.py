# Scraped each card inside this link https://www.cbssports.com/nfl/stats/

import requests
from bs4 import BeautifulSoup
import pandas as pd

def get_stats_from_table(soup):
    """Extract top 20 players from a stat table"""
    stats = []
    table = soup.find('div', class_='TableBaseWrapper')
    
    if table:
        # get all rows except header, limit to top 20
        rows = table.select('tbody tr.TableBase-bodyTr')[:20]
        # find col# of touchdown data
        rowHeader = table.select('.TableBase-headTr')
        colCounter = 0
        
        for _tdcol in rowHeader:
            if _tdcol.text.strip() == 'Touchdown Passes':
                break
            colCounter+=1

        for row in rows:
            cols = row.find_all('td', class_='TableBase-bodyTd')
            
            # extract player data 
            player_cell = cols[0]

            # find col that has touchdown data
            player_td_cell = cols[colCounter];
  

            player_info = player_cell.select_one('.CellPlayerName--long')
            if player_info:
                player_name = player_info.select_one('a').text.strip()
                position = player_info.select_one('.CellPlayerName-position').text.strip()
                team = player_info.select_one('.CellPlayerName-team').text.strip()
                touch_down = player_td_cell.text.strip()
                stats.append({
                    'Player': player_name,
                    'Team': team,
                    'Position': position,
                    'Touchdown': touch_down
                })
    return stats

def get_all_stats():
    """Get stats from main page and follow links to detailed stats"""
    base_url = "https://www.cbssports.com"
    main_url = f"{base_url}/nfl/stats/"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    all_stats = []

    try:
        # get main page
        response = requests.get(main_url, headers=headers)
        response.raise_for_status()
        main_soup = BeautifulSoup(response.content, 'html.parser')
        
        # find all stat categories from footer links
        stat_sections = main_soup.find_all('div', class_='TableBase-footer')


        for section in stat_sections:
            link = section.find('a')
            if link:
                category_url = base_url + link['href']
                category_name = link.text.strip().replace('Complete ', '').replace(' Leaders', '')
                
                print(f"\nFetching {category_name}...")
                
                # Get detailed stats page
                detail_response = requests.get(category_url, headers=headers)
                detail_response.raise_for_status()
                detail_soup = BeautifulSoup(detail_response.content, 'html.parser')
                
                # Get stats from the detailed page
                stats = get_stats_from_table(detail_soup)
                
                if stats:
                    # Add category name to each stat record
                    for stat in stats:
                        stat['Category'] = category_name
                    all_stats.extend(stats)
                else:
                    print(f"No data found for {category_name}")

        # Convert all stats to a DataFrame and save to single CSV
        if all_stats:
            combined_df = pd.DataFrame(all_stats)
            combined_df.insert(0, 'Rank', combined_df.groupby('Category').cumcount() + 1)
            combined_df.to_csv("nfl_top_20_players_stats.csv", index=False)
            print("\nAll stats saved to 'nfl_top_20_players_stats.csv'")
                
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
    except Exception as e:
        print(f"Error processing data: {e}")
        print("Error details:", str(e))

if __name__ == "__main__":
    get_all_stats()