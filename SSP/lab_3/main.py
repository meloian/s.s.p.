import pandas as pd
import requests
from datetime import datetime
import os
from spyre import server
import matplotlib.pyplot as plt
import seaborn as sns

area_names = [
    "Vinnytsia", "Volyn", "Dnipropetrovsk", "Donetsk", 
    "Zhytomyr", "Transcarpathia", "Zaporizhzhia", "Ivano-Frankivsk", "Kyiv", 
    "Kirovohrad", "Luhansk", "Lviv", "Mykolaiv", "Odesa", 
    "Poltava", "Rivne", "Sumy", "Ternopil", "Kharkiv", 
    "Kherson", "Khmelnytskyi", "Cherkasy", "Chernihiv", "Chernivtsi", 
    "Crimea", "Kyiv City", "Sevastopol"
] 

dict_of_areas = {i + 1: name for i, name in enumerate(area_names)}
dict_of_areas_with_0 = {0: "nothing", **dict_of_areas}


def download_data():
    time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    data_dir = 'data'
    os.makedirs(data_dir, exist_ok=True)
    for i in range(1, 28):
        url = f'https://www.star.nesdis.noaa.gov/smcd/emb/vci/VH/get_TS_admin.php?country=UKR&provinceID={i}&year1=1981&year2=2023&type=Mean'
        response = requests.get(url)
        text = response.text.replace("<tt><pre>", "").replace("</pre></tt>", "").replace("<br>", "")
        filename = os.path.join(data_dir, f'vhi_data_province_{i}_{time}.csv')
        with open(filename, 'w') as file:
            file.write(text) 
            
            
def read_vhi_files(directory):
    vhi_data = pd.DataFrame()
    files = [f for f in os.listdir(directory) if f.startswith('vhi_data_province')]
    for file in files:
        file_path = os.path.join(directory, file)
        df = pd.read_csv(file_path, index_col=None, header=1)
        df = df[df['VHI'] != -1]
        province_id = int(file.split('_')[3])
        df.insert(0, 'area', province_id)
        vhi_data = pd.concat([vhi_data, df], ignore_index=True)

    dict_for_transfer = {i: i % 27 + 1 for i in range(1, 28)}
    vhi_data["area"].replace(dict_for_transfer, inplace=True)
    vhi_data.sort_values(by=['area', 'year', 'week'], inplace=True)
    return vhi_data

def filter_data(df, params):
    selected_region = int(params['selected_region'])
    start_year, end_year = map(int, params['yrange'].split('-'))
    start_week, end_week = map(int, params['wrange'].split('-'))
    df = df[(df['area'] == selected_region) & 
            (df['year'].between(start_year, end_year)) & 
            (df['week'].between(start_week, end_week))]
    return df

vhi_data = read_vhi_files(r'data')
a = 1
vhi_data_1 = vhi_data[vhi_data['area'] == a]
print(vhi_data_1)

class StockExample(server.App):
    title = 'NOAA data vizualization'

    inputs = [
         {
            "type": 'dropdown',
            "label": 'Select data',
            "options": [{'label': "VCI", "value": 'VCI'},
                        {'label': "TCI", "value": 'TCI'},
                        {'label': "VHI", "value": 'VHI'}],
            "key": 'ticker',
            "action_id": "update_data"
        },
        {
            "type": 'dropdown',
            "label": 'Region',
            "options": [{'label': dict_of_areas[i], 'value': i} for i in dict_of_areas],
            "key": 'selected_region',
            "action_id": "update_data"
        },
        {
            "type": 'text',
            "label": "Week range",
            "value": "1-52",
            "key": "wrange",
            "action_id": "update_data"

        },
        {
            "type": 'text',
            "label": "Year range",
            "value": "1983-2023",
            "key": "yrange",
            "action_id": "update_data"

        },

    ]
    
    
    controls = [{"type": "hidden", "id": "update_data"}]
    tabs = ["Table", "Plot"]
    outputs = [
        {"type": "table", "id": "data_table", "control_id": "update_data", "tab": "Table", "on_page_load": True},
        {"type": "plot", "id": "plot", "control_id": "update_data", "tab": "Plot"}
    ]
    
    
    def data_table(self, params):
        ticker = params['ticker']
        selected_region = params['selected_region']
        wrange = params['wrange']
        yrange = params['yrange']

        start_year, end_year = map(int, yrange.split('-'))
        start_week, end_week = map(int, wrange.split('-'))

        df = vhi_data[(vhi_data['area'] == int(selected_region)) & 
                      (vhi_data['year'].between(start_year, end_year)) & 
                      (vhi_data['week'].between(start_week, end_week))]
        
        list_to_show = ['year', 'week', ticker]
        df = df[list_to_show]
        return df


    def plot(self, params):
        df = self.data_table(params)
        df['year:week'] = df['year'].astype(str) + ':' + df['week'].astype(str)

        plt.figure(figsize=(16, 6))
        img = sns.lineplot(data=df, x='year:week', y=params["ticker"],
                           label=f'{params["ticker"] + dict_of_areas[int(params["selected_region"])]}',
                           marker="o", markersize=3)

    
        xticks = plt.gca().get_xticks()
    
    
        plt.gca().set_xticks(xticks[::27])
        plt.gca().set_xticklabels(df['year:week'][::27], rotation=70) 
        plt.xlabel('Year:Week')
        plt.ylabel('Value')
        plt.legend()
        plt.tight_layout()

        return img

app = StockExample()
app.launch(port=8090) 