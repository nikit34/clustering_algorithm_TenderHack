import numpy as np
import pandas as pd 
from tqdm import tqdm


categories = ['Ноут', 'ноут']#, 'Компь', 'компь'] # исправлять - 44строка
share = 0.5

cs3 = pd.read_excel(r'data\cs3_del.xlsx', index_col=0)
ste = pd.read_excel(r'data\ste_all_del.xlsx', index_col=0)

cs3 = cs3.loc[:,~cs3.columns.duplicated()]
cs3 = cs3.loc[~cs3.index.duplicated(),:]
ste = ste.loc[:,~ste.columns.duplicated()]
ste = ste.loc[~ste.index.duplicated(),:]

cs3 = cs3.reset_index()
ste = ste.reset_index()

cs3 = cs3.rename(columns={'Идентификатор СТЕ': 'id'})
ste = ste.rename(columns={'Id': 'id'})

full = pd.merge(ste, cs3, on=['id'])

full['Дата начала'] = pd.to_datetime(full['Дата начала'], format = '%Y-%m-%d')
full['Время начала'] = pd.to_datetime(full['Время начала'], format = '%H:%M:%S')
full['Дата окончания'] = pd.to_datetime(full['Дата окончания'], format = '%Y-%m-%d')
full['Время окончания'] = pd.to_datetime(full['Время окончания'], format = '%H:%M:%S')

data_time_start = []
data_time_stop = []
for i in tqdm(range(len(full))):
    data_time_start.append(str(full.loc[i,'Дата начала']).split(' ')[0] + ' ' + str(full.loc[i,'Время начала']))
    data_time_stop.append(str(full.loc[i,'Дата окончания']).split(' ')[0] + ' ' + str(full.loc[i,'Время окончания']))

full = full.drop(['Дата начала','Время начала', 'Дата окончания', 'Время окончания'], axis=1)

full['data_time_start'] = pd.to_datetime(pd.Series(data_time_start))
full['data_time_stop'] = pd.to_datetime(pd.Series(data_time_stop))

full = full[(full['Наменование'].str.find(categories[0]) == 0) | (full['Наменование'].str.find(categories[1]) == 0) | (full['Вид товаров'].str.find(categories[0]) == 0) | (full['Вид товаров'].str.find(categories[1]) == 0)]# | (full['Наменование'].str.find(categories[2]) == 0) | (full['Наменование'].str.find(categories[3]) == 0) | (full['Вид товаров'].str.find(categories[2]) == 0) | (full['Вид товаров'].str.find(categories[3]) == 0)]

full = full.reset_index()
full = full.drop('index', axis=1)

clasters_week = []
claster = []

for i in tqdm(range(len(full))):
    for j in range(i, len(full)):
        span = share * abs(int(str(full['data_time_start'][i] - full['data_time_stop'][i]).split(' days ')[0]))
        if abs(int(str(full['data_time_start'][i] - full['data_time_start'][j]).split(' days ')[0])) < span and abs(int(str(full['data_time_stop'][i] - full['data_time_stop'][j]).split(' days ')[0])) < span:
            claster.append((full['ИНН заказчика'][i], full['Процент снижения'][i], full['data_time_stop'][i], full['Итоговоя стоимость'][i]))
    if len(claster) > 1:
        clasters_week.append(claster)
        claster = []

clasters_week = [value for value in clasters_week if value != []]

res_clasters = pd.DataFrame()

for i in tqdm(range(len(clasters_week))):
    for j in range(len(clasters_week[i])):
        clasters_week[i][j] = {
            'ИНН':clasters_week[i][j][0],
            'Процент снижения':clasters_week[i][j][1],
            'data_time_stop':pd.to_datetime(clasters_week[i][j][2]),
            'Итоговоя стоимость':clasters_week[i][j][3],
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
        m = 'o'; c = 'yellow'
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
    res_time = int(str(res_clasters['data_time_stop'][i]).split('-')[1].split('-')[0])*30*24 + int(str(res_clasters['data_time_stop'][i]).split('-')[1].split('-')[0])*24 + int(str(res_clasters['data_time_stop'][i]).split(' ')[1].split(':')[0])
    ax.scatter(res_clasters['Итоговоя стоимость'], res_clasters['Процент снижения'], res_time, color=c, marker=m)

ax.set_xlabel('Cost')
ax.set_ylabel('Reduction')
ax.set_zlabel('Data_time_stop')

plt.show()




