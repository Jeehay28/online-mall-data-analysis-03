#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd 
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import requests
import json
from folium.plugins import MarkerCluster
from bs4 import BeautifulSoup

plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] =  False

seoul_addr = pd.read_csv('서울도로명좌표_주문정보.csv',encoding = 'utf-8')
#seoul_addr = pd.read_csv('서울도로명좌표_주문정보.csv',encoding = 'cpq')
o_info = pd.read_excel('3.1 주문정보(개인정보 제외)_추출.xlsx')
i_info = pd.read_excel('2.1 상품정보_추출.xlsx')


# #  1. 데이터 정보 나열

# ## 1-1 서울도로명주소

# In[2]:


seoul_addr


# ## 1-2 주문정보

# In[3]:


o_info


# ## 1-3 상품정보

# i_info

# # 2. 데이터 전처리

# ##  2-1 주문정보 정제

# In[4]:


df_주문정보_사본 = o_info.copy()
df_주문정보_사본.drop(columns = ['순번', '옵션명', '회원주문여부','상품명'],inplace = True)


# In[5]:


df_주문정보_사본.drop(df_주문정보_사본.loc[df_주문정보_사본.진행구분 == '환불완료'].index,inplace = True)
df_주문정보_사본.drop(df_주문정보_사본.loc[df_주문정보_사본.진행구분 == '결제취소'].index,inplace = True)
df_주문정보_사본.drop(df_주문정보_사본.loc[df_주문정보_사본.진행구분 == '환불신청'].index,inplace = True)
df_주문정보_사본.drop(df_주문정보_사본.loc[df_주문정보_사본.진행구분 == '주문취소'].index,inplace = True)


# In[6]:


df_주문정보_사본


# In[7]:


#'서울특별시'를 '서울'으로만 저장
df_서울만 = df_주문정보_사본[df_주문정보_사본['배송지'].str.find('서울') == 0].copy()
df_서울만['배송지'] = df_서울만['배송지'].str[0:2] + ' '+ df_서울만['배송지'].str.split().str[1]                                + ' ' + df_서울만['배송지'].str.split().str[2]
df_서울주문정보 = df_서울만.copy()


# In[8]:


#주문일시 datetime 변환
df_서울주문정보['주문일시'] = pd.to_datetime(df_서울주문정보["주문일시"])
df_서울주문정보['주문일시'] = pd.to_datetime(df_서울주문정보['주문일시'].dt.date)
#df_서울주문정보['주문일시']


# In[9]:


df_서울주문정보.info()#결측치 없음


# In[10]:


df_서울주문정보


# ## 2-2 도로명 주소 정제

# In[11]:


df_서울도로명주소= seoul_addr.copy()


# In[12]:


siguro = df_서울도로명주소['sido']+ ' '+df_서울도로명주소['gu']+ ' '+df_서울도로명주소['ro,gil']
sigudong = df_서울도로명주소['sido']+ ' '+df_서울도로명주소['gu']+ ' '+df_서울도로명주소['dong']


# In[13]:


df_서울도로명주소.insert(0,'si_gu_ro,gil',siguro)
df_서울도로명주소.insert(1,'si_gu_dong',sigudong)


# In[14]:


df_서울도로명주소.info()#결측치없음


# In[15]:


df_서울도로명주소


# ## 2-3 상품정보 정제

# In[16]:


df_상품정보_사본 = i_info.copy()


# In[17]:


df_상품정보_사본['브랜드명'].value_counts()


# In[18]:


df_상품정보_사본


# In[19]:


#불필요한 컬럼 제거
df_상품정보_사본.drop(columns = ['상품명','판매상태','전시상태','배송비'],inplace = True)


# In[20]:


df_상품정보_사본.info() #결측치없음


# In[21]:


df_상품정보_사본


# # 3. 데이터 분석

# ## 3-1 데이터 분석

# 주문정보 내에 있는 주문번호와 상품번호연동 후 카테고리와 연결

# ### 1. 데이터 병합

# In[22]:


#데이터를 합치기전 정렬
df_서울도로명주소 = df_서울도로명주소.sort_values('si_gu_ro,gil')
df_서울주문정보 = df_서울주문정보.sort_values('배송지')


# In[23]:


df_서울주문정보 = df_서울주문정보.merge(df_서울도로명주소, left_on = '배송지', right_on = 'si_gu_ro,gil')


# In[24]:


#df_서울주문정보.drop(columns = '배송지',inplace = True)


# In[25]:


df_서울주문정보.sort_values('상품번호')


# In[26]:


df_상품정보_사본[df_상품정보_사본['상품번호'] == 'G1709081601_0807']


# In[27]:


df_상품정보_사본.sort_values('상품번호')


# In[28]:


df_상품정보_사본[df_상품정보_사본['상품번호'] == 'G1711291723_1010']


# In[29]:


df_서울주문정보_사본 = df_서울주문정보.merge(df_상품정보_사본, left_on = '상품번호', right_on = '상품번호')


# In[30]:


df_서울주문정보_사본.drop(columns = '상품구분',inplace = True)


# In[31]:


df_서울주문정보_사본.rename(columns = {'Iat':'lat'},inplace = True)
#df_서울주문정보_사본['lat'].info()
#df_서울주문정보_사본['lng'].info()
df_서울주문정보_사본.drop(columns = '주문번호',inplace = True)


# In[32]:


df_서울주문정보_사본.drop(columns = '회원번호',inplace = True)


# In[33]:


#데이터 세분화
df_서울주문정보_사본 = df_서울주문정보_사본[df_서울주문정보_사본['lat'] != '사용자 지정값']
df_서울주문정보_사본 = df_서울주문정보_사본[df_서울주문정보_사본['dong'] != '사용자 지정값']


# In[67]:


df_서울주문정보_사본


# ### 2. 데이터 분석

# #### 카테고리 주문량 & 판매액

# In[34]:


df_카테고리_판매가 = df_서울주문정보_사본.groupby('카테고리명').sum()
df_카테고리_판매가.reset_index(drop = False , inplace = True)
df_카테고리_판매가 = df_카테고리_판매가.sort_values('판매가', ascending = False)


# In[61]:


df_카테고리_판매가 


# In[76]:


from dash import Dash, html, dcc
import plotly.express as px
import pandas as pd

colors = {
    'background': '#111111',
    'text': '#7FDBFF'
}

app = Dash(__name__)


fig = px.bar(df_카테고리_판매가  , y='카테고리명', x='수량')

fig.update_layout(
    plot_bgcolor=colors['background'],
    paper_bgcolor=colors['background'],
    font_color=colors['text']
)
app.layout = html.Div(children=[
    html.H1(children='xx 온라인 쇼핑몰'),

    html.Div(children='''
        카테고리 주문량
    '''),

    dcc.Graph(
        id='example-graph',
        figure=fig
    )
])



if __name__ == '__main__':
    app.run_server(debug=True)


# In[74]:


df_서울주문정보_사본['카테고리명'].value_counts().index


# In[35]:


import matplotlib.ticker as mticker

plt.figure(figsize=(25, 15))
           
plt.subplot(1,2,1)
cart_order = sns.countplot(y = df_서울주문정보_사본['카테고리명'], order = df_서울주문정보_사본['카테고리명'].value_counts().index)
cart_order.set_xlabel('주문 수량(건)')
plt.title('서울시 카테고리 주문 수량')

plt.subplot(1,2,2)
x_value = df_카테고리_판매가['판매가']/100000000
local_tprice = sns.barplot(data=df_카테고리_판매가, x= x_value, y= '카테고리명')
local_tprice.set_xlabel('판매가(억 원)')
plt.gca().xaxis.set_major_formatter(mticker.FormatStrFormatter('%.2f'))

plt.title('서울시 지역별 주문 판매액')
plt.show()


# 주문수량에 비해 생활 가전 쪽은 판매액이 높다

# #### 브랜드 별 주문량 및 판매액(진행중)

# In[36]:


df_브랜드_판매가 = pd.DataFrame(df_서울주문정보_사본.groupby('브랜드명').sum())
df_브랜드_판매가.reset_index(drop = False , inplace = True)
df_브랜드_판매가 = df_브랜드_판매가.sort_values('판매가', ascending = False)


# In[37]:


df_브랜드_판매액 = df_브랜드_판매가.copy()


# In[38]:


df_브랜드_주문량= df_서울주문정보_사본['브랜드명'].value_counts()


# In[39]:


df_브랜드_판매가 = df_브랜드_판매가[df_브랜드_판매가['판매가'] >= 5000000]
df_브랜드_주문량 = pd.DataFrame(df_서울주문정보_사본['브랜드명'].value_counts())
df_브랜드_주문량.reset_index(drop = False , inplace = True)
df_브랜드_주문량 = df_브랜드_주문량[df_브랜드_주문량['브랜드명'] >= 100]
df_브랜드_주문량 =df_브랜드_주문량.rename(columns={'index':'브랜드명','브랜드명':'주문량'})


# In[40]:


plt.figure(figsize=(25, 15))

plt.subplot(1,2,1)
cart_order = sns.barplot(data = df_브랜드_주문량, x = df_브랜드_주문량['주문량'], y = '브랜드명')
cart_order.set_xlabel('주문 수량(건)')

plt.title('서울시 브랜드 주문 수량')

plt.subplot(1,2,2)
x_value_gu = df_브랜드_판매가['판매가']/10000000
#cart_price = sns.countplot(x = df_카테고리_판매가['판매가'].index, order = df_카테고리_판매가['판매가'].value_counts())
cart_price = sns.barplot(data=df_브랜드_판매가, x= x_value_gu, y='브랜드명')
cart_price.set_xlabel('판매가(천만원)')
cart_price.set_ylabel('브랜드')
plt.gca().xaxis.set_major_formatter(mticker.FormatStrFormatter('%.1f'))

plt.title('브랜드 별 주문 판매액')
plt.show()


# LG ELECTRONICS는 주문수량이 적음에도 불구하고 판매액이 제일 높음

# #### 서울 지역별 판매액

# In[41]:


df_구_판매가 = pd.DataFrame(df_서울주문정보_사본.groupby('gu').sum())
df_구_판매가.reset_index(drop = False , inplace = True)
df_구_판매가 = df_구_판매가.sort_values('판매가', ascending = False)


# In[42]:


df_구_판매가['판매가'] = df_구_판매가['판매가'].astype('int64')


# In[43]:


plt.figure(figsize=(25, 12))

plt.subplot(1,2,2)
plt.title('서울시 지역 별 주문 판매액')

x_value_gu = df_구_판매가['판매가']/10000000

cart_price = sns.barplot(data=df_구_판매가, x= x_value_gu, y='gu')
cart_price.set_xlabel('판매가(천만원)')
cart_price.set_ylabel('서울시 행정구')
plt.gca().xaxis.set_major_formatter(mticker.FormatStrFormatter('%i'))

plt.subplot(1,2,1)
plt.title('서울시 자치구별 주방/욕실/청소용품 주문수')
life_order = df_서울주문정보_사본.loc[df_서울주문정보_사본['카테고리명'] == '주방/욕실/청소용품'].groupby('gu')['카테고리명'].count()                                    .sort_values().plot(kind='barh',color = 'orange')
life_order.set_xlabel('주문 수량(건)')
life_order.set_ylabel('지역구')
plt.gca().xaxis.set_major_formatter(mticker.FormatStrFormatter('%i'))


plt.show()


# #### 지역별 주방용품 주문량

# 영등포구가 가장 많이 생활용품을 주문하고, 종로구는 가장 적게 생활용품을 주문했습니다.

# In[44]:


import folium


# In[45]:


df_seoul_life = df_서울주문정보_사본[df_서울주문정보_사본['카테고리명'] == '주방/욕실/청소용품']
df_seoul_life['카테고리명'].unique()


# ### 3. 워드클라우드 시각화

# In[46]:


from wordcloud import WordCloud
korean_font_path = 'C:/Windows/Fonts/malgun.ttf'


# In[47]:


df_서울주문정보_사본['카테고리명'].value_counts()


# #### 지역

# -주문량 기준

# In[48]:


import matplotlib.pyplot as plt
from wordcloud import WordCloud

korean_font_path = 'C:/Windows/Fonts/malgun.ttf' # 한글 폰트(맑은 고딕) 파일명

# 워드 클라우드 이미지 생성
wc = WordCloud(font_path=korean_font_path, max_font_size = 100, background_color='white',
              width=400, height=200)

#지역정보 불러오기
order2 = df_서울주문정보_사본['gu'].value_counts()

frequencies = order2 # pandas의 Series 형식이 됨
wordcloud_image = wc.generate_from_frequencies(frequencies)

plt.figure(figsize=(10,12))
plt.axis('off')
plt.imshow(wordcloud_image, interpolation = 'bilinear')
plt.show()


# 영등포구는 카테고리 내 가장 많은 주문량을 보여준다

# -판매량 기준

# In[49]:


df_구_판매가['판매가'] =df_구_판매가['판매가'].astype('int64')
df_구_판매액 = df_구_판매가.groupby('gu').sum()


# In[50]:


order2 = df_구_판매액['판매가']

frequencies = order2

wordcloud_image = wc.generate_from_frequencies(frequencies)
plt.figure(figsize=(10,12))
plt.axis('off')
plt.imshow(wordcloud_image, interpolation = 'bilinear')
plt.show()


# #### 카테고리

# -주문량 기준

# In[51]:


#카테고리 정보 불러오기

order = df_서울주문정보_사본['카테고리명'].value_counts()

frequencies = order
wordcloud_image = wc.generate_from_frequencies(frequencies)

plt.figure(figsize=(10,12))
plt.axis('off')
plt.imshow(wordcloud_image, interpolation = 'bilinear')
plt.show()


# 주문 수량 내에는 생활용품의 비중이 높다는 것을 알 수 있다

# -판매액 기준

# In[52]:


df_카테고리_판매가['판매가'] =df_카테고리_판매가['판매가'].astype('int64')
df_카테고리_판매액 = df_카테고리_판매가.groupby('카테고리명').sum()


# In[53]:


order = df_카테고리_판매액['판매가']

frequencies = order
wordcloud_image = wc.generate_from_frequencies(frequencies)

plt.figure(figsize=(10,12))
plt.axis('off')
plt.imshow(wordcloud_image, interpolation = 'bilinear')
plt.show()


# #### 브랜드

# -주문량 기준

# In[54]:


#브랜드
korean_font_path = 'C:/Windows/Fonts/malgun.ttf'

wc = WordCloud(font_path=korean_font_path, max_font_size = 100, background_color='white',
              width=400, height=200)


order = df_서울주문정보_사본['브랜드명'].value_counts()

frequencies = order
wordcloud_image = wc.generate_from_frequencies(frequencies)

plt.figure(figsize=(10,12))
plt.axis('off')
plt.imshow(wordcloud_image, interpolation = 'bilinear')
plt.show()


# 브랜드는 '창신리빙' 제일 많이 주문된다

# -판매액 기준

# In[55]:


df_브랜드_판매액['판매가'] =df_브랜드_판매액['판매가'].astype('int64')
df_브랜드_판매액 = df_브랜드_판매액.groupby('브랜드명').sum()


# In[56]:


order2 = df_브랜드_판매액['판매가']

frequencies = order2

wordcloud_image = wc.generate_from_frequencies(frequencies)
plt.figure(figsize=(10,12))
plt.axis('off')
plt.imshow(wordcloud_image, interpolation = 'bilinear')
plt.show()


# 판매액이 높은 브랜드는 LG ELECTRONICS이다 주문량과는 다른 결과가 나온다

# ## 4. 지도 시각화

# In[57]:


import requests
import json
from folium.plugins import MarkerCluster
import folium


# In[58]:


r = requests.get('https://raw.githubusercontent.com/southkorea/seoul-maps/master/kostat/2013/json/seoul_municipalities_geo_simple.json')
c = r.content
seoul_geo = json.loads(c)


# In[59]:


seoul_group_data = df_서울주문정보_사본.loc[df_서울주문정보_사본['카테고리명'] == '주방/욕실/청소용품'].groupby('gu')['카테고리명'].count()


# In[60]:


#지역별 생활용품 주문수량 지도 시각화
m1 = folium.Map(
    location=[37.559819, 126.963895],
    zoom_start=12, 
    tiles='cartodbpositron'
)

folium.GeoJson(
    seoul_geo,
    name='지역구'
).add_to(m1)

marker_cluster = MarkerCluster().add_to(m1)
#choropleth로 표현
#bins = list(seoul_group_data.quantile([0, 0.25, 0.5, 0.75, 1]))#4분위
m1.choropleth(geo_data=seoul_geo,
             data=seoul_group_data, 
             fill_color='YlOrRd', # 색상 변경도 가능하다
             fill_opacity=0.5,
             line_opacity=0.2,
             key_on='properties.name',
             legend_name="지역구별 생활용품 주문수",
             #bins=bins
            )

for lat, long in zip(df_seoul_life['lat'], df_seoul_life['lng']):
    folium.Marker([lat, long], icon = folium.Icon(color="green")).add_to(marker_cluster)

m1


# 강남 지역에 주문량이 많이 몰려있음을 한번에 알 수 있다

# # 4. 결과 및 결론 도출

# 1, 브랜드에 대한 결론

# 워드 클라우드를 기준으로 봤을 때, 주문량과 판매액은 비례할 때도 있고, 반비례할 때도 있다.

# 판매액이 압도적으로 높은 LG ELETRONICS를 보았을 때, 수요가 꽤 있는 비싼 제품을 만들어서 전략적으로 팔 필요가 있다고 여겨진다. 

# 2. 지역에 대한 결론

# 영등포구의 특성을 보았을 때, 지리적으로 산이 없어서 각종 시설이 들어서기 좋은 곳이다. 여의도라는 커다란 구역을 갖고 있기에 상업, 주거지역으로써의 역할이 꽤 큰 듯하다. 주요기관,기업 및 공공단체에서 물품을 주문하는 경우에 대량을 구매하는 경우가 많기 때문에 주문 판매액이 가장 높게 나왔다고 생각된다.

# 영등포구를 제외한 구역은 순서대로 나타나는 특징을 보았을 때, 개발 및 도심지일수록 판매액이 높음을 알 수 있다.

# 3. 카테고리에 대한 결론

# 생활과 밀접한 관련을 지닌 주방/가정용품의 주문량이 제일 많이 나왔는데, 이것은 주방/가정용품 카테고리에 소모품이 많다는 것을 보여준다.

# 가장 많은 생활용품을 주문하는 지역은 개발이 많이 된 지역이 많은 강남구 쪽임을 알 수 있다. 이것은 사람들의 인구 밀집도와 관련이 있을 듯하다. 만약 인구 밀도를 분석한다면 상관도가 높게 나올지도 모른다.

# 판매액은 브랜드와 마찬가지로 생활 가전쪽으로 높게 나왔다. 텔레비전, 냉장고 등 일상생활에 필수인 품목들이 주문량 대비 판매액이 높게 나오기 때문에, 생활가전은 워드 클라우드 기준 주문량이 적음에도 불구하고 가장 높은 판매액을 보여주었다.
