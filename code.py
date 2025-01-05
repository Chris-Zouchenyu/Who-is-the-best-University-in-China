import numpy as np
import requests
from bs4 import BeautifulSoup as bs
from matplotlib import pyplot as plt
#from wordcloud import WordCloud
from PIL import Image
import pandas as pd
# 设置字体为楷体
plt.rcParams['font.sans-serif'] = ['KaiTi']
#
file=".\\code"##
# 用于获取网页的HTML代码
def getHTMLText(url):
    try:
        # 添加请求头，不然会被阻止访问
        kv = {'user-agent': 'Mozilla/5.0'}
        # 获取url对应的网页的HTML代码，超过30s则认为访问失败
        r = requests.get(url, headers=kv, timeout=30)
        # 查看返回的代码，代码为200则为成功正常访问
        r.raise_for_status()
        # 对数据进行重新编码，方便我们查看
        r.encoding = r.apparent_encoding
        # 返回编码后的数据
        return r.text
    except Exception as e:
        print('获取HTML失败')
        return ""


# 从HTML中获取需要的数据
def getData(url, year):
    # 调用函数，获取HTML
    html = getHTMLText(url + str(year))
    # 调用beautiful soup库函数来对HTML代码进行解析
    soup = bs(html, 'html.parser')

    # 以下均为从HTML中获取数据，具体方法为：检查对应数据所在的标签或者class，然后用beautifulsoup4库来查找该标签，然后获取数据
    collages = [i for i in soup.find('tbody').find_all('tr')]
    result = []
    for i in collages:
        ranking = i.find('div').get_text().strip()
        name = i.find_all('div', class_='link-container')[0].find('a').get_text().strip()
        eng_name = i.find_all('div', class_='tooltip')[1].find('a').get_text().strip()
        tags = i.find('p', class_='tags').get_text().strip()
        city = i.find_all('td')[2].get_text().strip()
        type = i.find_all('td')[3].get_text().strip()
        score = i.find_all('td')[4].get_text().strip()
        layer = i.find_all('td')[5].get_text().strip()
        # 将获取后的数据整合到result中，result中每一行就是一个大学的信息，包括排名、大学名称、英文名、标签、大学类型、大学分数、大学办学水平
        result.append([ranking, name, eng_name, tags, city, type, score, layer])
    return result


# 将数据写入表格
def write_csv(file_name, result):
    f = open(file_name, 'w')
    # 第一行写入标题
    f.write('排名,大学名称,英文名,学校标签,省市,类型,总分,办学层次\n')
    for i in result:
        for j in i:
            f.write(j + ',')
        f.write('\n')
    f.close()


# 爬取2020-2023共四年的数据并写入表格
def crew_and_write():
    for i in range(2020, 2024):
        result = getData('https://www.shanghairanking.cn/rankings/bcur/', i)
        write_csv(str(i) + '.csv', result)


# 2020-2023大学平均分
def show_average_score():
    dic = {}
    for i in range(2020, 2024):
        result = getData('https://www.shanghairanking.cn/rankings/bcur/', i)
        for j in result:
            if j[1] not in dic:
                dic[j[1]] = []
            dic[j[1]].append(float(j[6]))
    names = list(dic.keys())
    mean_score = [sum(dic[i]) / len(dic[i]) for i in names]
    plt.bar(range(len(names)), mean_score, tick_label=names)
    plt.gcf().subplots_adjust(bottom=0.3)
    plt.xticks(rotation=270)
    plt.ylabel('大学评分')
    plt.title('2020-2023各大学平均得分')
    plt.show()


# 2020-2023平均办学层次2020-2023各省市上榜大学数量词云
def show_city_collage_num():
    dic = {}
    for i in range(2020, 2024):
        result = getData('https://www.shanghairanking.cn/rankings/bcur/', i)
        for j in result:
            name = j[4]
            if name not in dic:
                dic[name] = 0
            dic[name] += 1
    # 背景
    image = Image.open('./china.jpeg')
    mask = np.array(image)
    wordcloud = WordCloud(
        font_path='C:\\windows\\Fonts\\simhei.ttf',
        background_color='#f3f3f3',
        margin=3,
        max_font_size=60,
        random_state=50,
        scale=10,
        mask=mask
    )
    wordcloud.generate_from_frequencies(dic)
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.show()

# 2020-2023平均办学层次
def show_average_layer():
    dic = {}
    for i in range(2020, 2024):
        result = getData('https://www.shanghairanking.cn/rankings/bcur/', i)
        for j in result:
            if j[1] not in dic:
                dic[j[1]] = []
            dic[j[1]].append(float(j[6]))
    names = list(dic.keys())
    mean_score = [sum(dic[i]) / len(dic[i]) for i in names]
    plt.bar(range(len(names)), mean_score, tick_label=names)
    plt.gcf().subplots_adjust(bottom=0.3)
    plt.xticks(rotation=270)
    plt.ylabel('办学层次')
    plt.title('2020-2023各大学平均办学层次')
    plt.show()


crew_and_write()
show_average_layer()
show_average_score()
show_city_collage_num()

##使用函数表达后，我们再使用读取文件的方法对数据进行处理

for i in range(2020,2024,1):
    print('以下是%d年的数据:'%i)
    
    filename=file+str(i)+'.csv'
    result=pd.read_csv(filename,encoding='GBK',index_col=False)
    result.dropna(inplace=True)
    dup=result['大学名称'].duplicated()
    for j in range(0,31,1):
        if dup[j]==False:
            result.drop_duplicates(['大学名称'],keep='last')
            break
    print(result[(result['总分']>=500.0)&(result['总分']<=700.0)])
    print(result[['总分','办学层次']].describe())
    result.loc[len(result)]=[31,'中国石油大学（华东）','China University of Petroleum (East China)','双一流/211','山东','理工',304.4,28.1]
    result_group=result.groupby(['省市'])[['大学名称','总分']].agg({'总分':'mean'})
    print(result_group)
    result.at[32,'总分']=result['总分'].mean()
    result.at[32,'办学层次']=result['办学层次'].mean()
    result.fillna(0,inplace=True)
    result.sort_values(by='总分',ascending=False)
    result['排名']= result['排名'].astype(int)
    result['办学层次']= result['办学层次'].round(1)
    result['总分']= result['总分'].round(1)
    result.to_csv(file+str(i)+'年处理后的数据'+'.csv',encoding='GBK',index=False,header=True)


for i in range(2020,2024):
    filename=file+str(i)+'.csv'
    result=pd.read_csv(filename,encoding='GBK',index_col=False)
    bins=[0,450,600,1000]
    label=['三档','二档','一档']  
    result['分级']=pd.cut(result['总分'],bins,right=False,labels=label)
    result_1=result[['大学名称','总分','分级']]
    file1='各大学分档'+str(i)+'年'+'.csv'
    result_1.to_csv(file1,index=False,header=True,encoding='GBK')
for i in range(2020,2024):
    filename=file+str(i)+'.csv' 
    result=pd.read_csv(filename,encoding='GBK',index_col=False)
    df=result.loc[:,['排名','总分','办学层次']].corr()
    file1='各大学办学层次与总分的相关性分析'+str(i)+'.csv'
    df.to_csv(file1,index=False,header=True,encoding='GBK')
