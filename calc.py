import pandas as pd
import numpy as np

def calc_func(x,y,z, filename):

    df = pd.read_excel(filename)

    if int(x) <= 30 and int(y) == 1 and 30 >= int(z) >= 12:
        res = 'Время и тип тестирования соответсвуют нормам'
        t_1 = 1
    elif 90 >= int(x) >= 60 and int(y) == 2 and 120 >= int(z) >= 80:
        res = 'Время и тип тестирования соответсвуют нормам'
        t_1 = 1
    elif 240 >= int(x) >= 210 and int(y) == 3 and 420 >= int(z) >= 380:
        res='Время и тип тестирования соответсвуют нормам'
        t_1 = 1
    elif int(x) > 30 or 30 < int(z) < 12 and int(y) == 1:
        res='Рекомендуемое время проведения тестирования данного типа не более 30 минут, количество вопросов может варьироваться от 12 до 30'
        t_1 = 0
    elif 90 < int(x) < 60 or 40 <= int(z) < 80 and int(y) == 2 :
        res='Рекомендуемое время проведения тестирования данного типа не менее 60 минут и не более 90 минут, количество вопросов для тестирования данного типа не менее 40, рекомендуется от 80 до 120'
        t_1 = 0
    elif 240 < int(x) < 210 or 420 < int(z) < 380 and int(y) == 3:
        res='Рекомендуемое время проведения тестирования данного типа не менее 210 минут и не более 240 минут, количество вопросов может варьироваться от 380 до 420'
        t_1 = 0

    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_rows', None)
    columns = df.columns
    balls_columns = [column for column in columns if column.startswith('Баллы')]
    balls_dictionary = dict()
    for name in balls_columns:
        balls_dictionary[name[8:]] = [df[name].mean(), df[name].sum()/34, df[name].sum()/2, (((34-df[name].sum())/2)/17)]
    df_result = pd.DataFrame(balls_dictionary).transpose()

    df_result.columns = ['Средний балл', 'Доля правильно ответивших','Количество правильно ответивших', 'Индекс трудности']

    df_result['Тип вопроса']=np.nan
    df_result.loc[df_result.index.str.startswith('['),'Тип вопроса'] = df_result[df_result.index.str.startswith('[')].index.str[:3]
    df_result['Тема']=np.nan
    df_result.loc[df_result.index.str.startswith('['),'Тема'] = df_result[df_result.index.str.startswith('[')].index.str[3:8]

    df_result['Тип вопроса']=df_result['Тип вопроса'].fillna(method = 'ffill')
    df_result['Тема']=df_result['Тема'].fillna(method = 'ffill')

    for i in range(len(df_result)-1,-1,-1):
        if df_result.iloc[i]['Тип вопроса'] == '[С]' and i > 0 and df_result.iloc[i-1]['Тип вопроса'] == '[С]':
            df_result.iloc[i-1]=df_result.iloc[i]

    df_result['Сложность'] = df_result['Индекс трудности'] #делаем копию последнего столбца
    df_result.loc[df_result['Индекс трудности'] >= 0, 'Сложность'] = ("очень простой")
    df_result.loc[df_result['Индекс трудности'] > 0.2, 'Сложность'] = ("простой")
    df_result.loc[df_result['Индекс трудности'] > 0.4, 'Сложность'] = ("средний")
    df_result.loc[df_result['Индекс трудности'] > 0.6, 'Сложность'] = ("тяжелый")
    df_result.loc[df_result['Индекс трудности'] > 0.8, 'Сложность'] = ("очень тяжелый")

    df_f = df_result[df_result.index.str.startswith('[')].sort_values(by='Тема', ascending=True)
    df = pd.DataFrame(df_f)
    df

    df_ge = df_result[df_result.index.str.startswith('[')]
    df_ge.groupby('Тема').agg(['mean'])

    df_ge = df_result[df_result.index.str.startswith('[')]
    df_ge.groupby('Тип вопроса').agg(['mean'])

    means = pd.DataFrame(df)
    means.mean()

    m = pd.DataFrame(means.mean())
    if means['Индекс трудности'].mean() > 0.2 and means['Индекс трудности'].mean() < 0.8:
        val = 'Cредний индекс трудности лежит в промежутке между [0.2, 0.8].'
        k = 1
    else:
        val = 'Cредний индекс трудности не лежит в промежутке между [0.2, 0.8].'
        k = 0
    m

    df_c = df_result[df_result.index.str.startswith('[')]
    df_c_2 = pd.DataFrame(df_c)
    df_c_2['Сложность'].value_counts()

    if t_1 == 1 and k == 1:
        print(res)
        print(val)
        en = 'Тест валиден по всем показателям.'
        print('Тест валиден по всем показателям.')
    elif t_1 == 1 and k == 0:
        print(res)
        print(val)
        en = 'Тест не валиден. Обратите внимание на сложность вопросов.'
        print('Тест не валиден. Обратите внимание на сложность вопросов.')
    elif t_1 == 0 and k == 0:
        print(res)
        print(val)
        en = 'Тест не валиден. Обратите внимание на общее время тестирования, количество вопросов, а также сложность вопросов.'
        print('Тест не валиден. Обратите внимание на общее время тестирования, количество вопросов, а также сложность вопросов.')
    elif t_1 == 0 and k == 1:
        print(res)
        print(val)
        en = 'Тест не валиден. Обратите внимание на общее время тестирования и количество вопросов.'
        print('Тест не валиден. Обратите внимание на общее время тестирования и количество вопросов.')

    df_comm = pd.DataFrame({'Комментарии': [res, val, en]})
    df_comm

    with pd.ExcelWriter('output_100.xlsx') as writer:
        df.to_excel(writer, sheet_name='Общая таблица')
        df_ge.groupby('Тема').agg(['mean']).to_excel(writer, sheet_name='Среднее по теме')
        df_ge.groupby('Тип вопроса').agg(['mean']).to_excel(writer, sheet_name='Среднее по типу')
        m.to_excel(writer, sheet_name='Среднее по параметрам')
        df_c_2['Сложность'].value_counts().to_excel(writer, sheet_name='Количество по сложности')
        df_comm.to_excel(writer, sheet_name='Комментарии')
