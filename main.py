import urllib.request
import pandas as pd
from datetime import datetime

NEW_INDEX = {1: 22, 2: 24, 3: 23, 4: 25, 5: 3, 6: 4, 7: 8, 8: 19, 9: 20, 10: 21, 11: 9, 12: 0, 13: 10, 14: 11, 15: 12, 16: 13, 17: 14, 18: 15, 19: 16, 20: -1, 21: 17, 22: 18, 23: 6, 24: 1, 25: 2, 26: 7, 27: 5}
HEADERS = ['Year', 'Week', 'SMN', 'SMT', 'VCI', 'TCI', 'VHI', 'empty']

import urllib.request
import pandas as pd
from datetime import datetime

# Глобальні змінні
NEW_INDEX = {1: 22, 2: 24, 3: 23, 4: 25, 5: 3, 6: 4, 7: 8, 8: 19, 9: 20, 10: 21, 11: 9, 12: 0, 13: 10, 14: 11, 15: 12, 16: 13, 17: 14, 18: 15, 19: 16, 20: -1, 21: 17, 22: 18, 23: 6, 24: 1, 25: 2, 26: 7, 27: 5}
HEADERS = ['Year', 'Week', 'SMN', 'SMT', 'VCI', 'TCI', 'VHI', 'empty']

# Функції
def download_data(province_id):
    url = f"https://www.star.nesdis.noaa.gov/smcd/emb/vci/VH/get_TS_admin.php?country=UKR&provinceID={province_id}&year1=1981&year2=2023&type=Mean"
    with urllib.request.urlopen(url) as wp:
        text = wp.read()
    now = datetime.now()
    filename = f'NOAA_ID{province_id}_{now.strftime("%d%m%Y%H%M%S")}.csv'
    with open(filename, 'wb') as out:
        out.write(text)
    return filename

def process_data(filename, province_id):
    df = pd.read_csv(filename, header=1, names=HEADERS)
    df.at[0, 'Year'] = df.at[1, 'Year']
    df = df.drop([len(df)-1]).drop(df.loc[df['VHI'] == -1].index)
    df['area'] = newIndex(province_id)
    return df

def start(a=1, b=28, c=1, c1=3, d=2023):
    all_data = []
    for i in range(a, b):
        filename = download_data(i)
        df = process_data(filename, i)
        all_data.append(df)

    total_data = pd.concat(all_data)
    for i in range(c, c1):
        print("VHI")
        VHI(newIndex(i), d, total_data)
        print("VHIAll")
        VHIAll(newIndex(i), total_data)
    drought(total_data)

def newIndex(a):
    return NEW_INDEX[a]

def VHI(index, year, df):
    vhi_data = df[(df["area"] == index) & (df["Year"] == str(year))]['VHI']
    print(vhi_data)
    min_v = vhi_data.min()
    max_v = vhi_data.max()
    print(min_v, max_v)

def VHIAll(index, df):
    print(df.loc[df["area"] == index, ["VHI", "Year"]])

def drought(df):
    print("Посуха, інтенсивність якої від середньої до надзвичайної:")
    print(df[df.VHI <= 15])
    print("Посуха, інтенсивність якої від помірної до надзвичайної:")
    print(df[df.VHI <= 35])
    print("Стресові умови:")
    print(df[df.VHI <= 40])
    print("Сприятливі умови:")
    print(df[df.VHI > 60])


