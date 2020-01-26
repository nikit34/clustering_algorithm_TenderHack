import numpy as np
import pandas as pd 
from tqdm import tqdm


categories = ['Ноут', 'ноут', 'Компь', 'компь']
share = 10

orders = pd.read_excel(r'data/orders.xlsx', index_col=0)
needs = pd.read_excel(r'data/needs.xlsx', index_col=0)

orders = orders.loc[:,~orders.columns.duplicated()]
orders = orders.loc[~orders.index.duplicated(),:]
needs = needs.loc[:,~needs.columns.duplicated()]
needs = needs.loc[~needs.index.duplicated(),:]

orders = orders.reset_index()
needs = needs.reset_index()

orders = orders.drop(['Полное наименование заказчика', 'Краткое наименование заказчика', 'Регион регистрации', 'Организационно правовая форма', 'ФИО контактного лица', 'E-Mail контактного лица', 'Телефон контактного лица', 'E-Mail', 'КПП заказчика'], axis=1)
needs = needs.drop(['Наименование заказчика', 'Номер потребности', 'Закон основание', 'Наименование победителя','ИНН победителя', 'КПП победителя', 'Статус контракта', 'Реестовый номер контракта', 'КПП заказчика'], axis=1)

order_need = pd.merge(orders, needs, on=['ИНН заказчика'])

order_need = order_need[(order_need['Наименование'].str.find(categories[0]) == 0) | (order_need['Наименование'].str.find(categories[1]) == 0) | (order_need['Наименование'].str.find(categories[2]) == 0) | (order_need['Наименование'].str.find(categories[3]) == 0)]

order_need = order_need.reset_index()

order_need = order_need.loc[:,~order_need.columns.duplicated()]
order_need = order_need.loc[~order_need.index.duplicated(),:]

order_need = order_need.dropna().reset_index()

order_need['Дата начала'] = pd.to_datetime(order_need['Дата начала'],format = '%Y-%m-%d %H:%M:%S')
order_need['Дата окончания'] = pd.to_datetime(order_need['Дата окончания'],format = '%Y-%m-%d %H:%M:%S')

delta_data = []
for i in tqdm(range(len(order_need))):
    days_interval = abs(int(str(order_need['Дата начала'][i] - order_need['Дата окончания'][i]).split(' days ')[0]))*24*60*60
    hour_interval = abs(int(str(str(order_need['Дата начала'][i] - order_need['Дата окончания'][i]).split(' days ')[1]).split(':')[0]))*60*60
    minute_interval = abs(int(str(str(order_need['Дата начала'][i] - order_need['Дата окончания'][i]).split(' days ')[1]).split(':')[1].split(':')[0]))*60
    tmp = days_interval + hour_interval + minute_interval
    delta_data.append(tmp)

order_need['delta_data'] = delta_data
try:
    order_need = order_need.drop(['index', 'level_0'], axis=1)
except KeyError:
    print(order_need.columns)
    order_need = order_need.drop(['index'], axis=1)

clasters_week = []
claster = []
for i in tqdm(range(len(order_need))):
    for j in range(i, len(order_need)):
        days_interval = abs(int(str(order_need['Дата начала'][i] - order_need['Дата начала'][j]).split(' days ')[0]))*24*60*60
        hour_interval = abs(int(str(str(order_need['Дата начала'][i] - order_need['Дата начала'][j]).split(' days ')[1]).split(':')[0]))*60*60
        minute_interval = abs(int(str(str(order_need['Дата начала'][i] - order_need['Дата начала'][j]).split(' days ')[1]).split(':')[1].split(':')[0]))*60
        tmp = days_interval + hour_interval + minute_interval

        if share * order_need['delta_data'][i] > tmp and order_need['Статус закупки по потребности'][i] == order_need['Статус закупки по потребности'][j]:
            claster.append((order_need['ИНН заказчика'][j], order_need['Цена контракта'][j], order_need['Дата окончания'][j], order_need['Количество поданных предложений'][j]))
    if len(claster) > 1:
        clasters_week.append(claster)
        claster = []

clasters_week = [value for value in clasters_week if value != []]

res_clasters = pd.DataFrame()

for i in tqdm(range(len(clasters_week))):
    for j in range(len(clasters_week[i])):
        clasters_week[i][j] = {
            'ИНН':clasters_week[i][j][0],
            'cost':clasters_week[i][j][1],
            'data_end':pd.to_datetime(clasters_week[i][j][2]),
            'count':clasters_week[i][j][3],
            'claster': int(j),
        }
        res_clasters = res_clasters.append(clasters_week[i][j], ignore_index=True)




from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
from matplotlib import animation


fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')


for i in tqdm(range(len(res_clasters))):
    if str(res_clasters.loc[i, 'claster']) == '0.0':
        m = 's'; c = 'yellow'
    elif str(res_clasters.loc[i, 'claster']) == '1.0':
        m = 's'; c = 'red'
    elif str(res_clasters.loc[i, 'claster']) == '2.0':
        m = 's'; c = 'green'
    elif str(res_clasters.loc[i, 'claster']) == '3.0':
        m = 's'; c = 'blue'
    elif str(res_clasters.loc[i, 'claster']) == '4.0':
        m = 's'; c = 'grey'
    else:
        m = 'o'; c = 'black'
    res_time = int(str(res_clasters['data_end'][i]).split('-')[1].split('-')[0])*30*24 + int(str(res_clasters['data_end'][i]).split('-')[1].split('-')[0])*24 + int(str(res_clasters['data_end'][i]).split(' ')[1].split(':')[0])
    ax.scatter(res_clasters['cost'], res_clasters['count'], res_time, color=c, marker=m)

ax.set_xlabel('Cost')
ax.set_ylabel('Reduction')
ax.set_zlabel('Data_time_stop')

plt.show()




