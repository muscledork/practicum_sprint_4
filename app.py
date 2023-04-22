#!/usr/bin/env python
# coding: utf-8

# In[15]:


import pandas as pd
import streamlit as st
import plotly_express as px
import plotly.graph_objects as go
# from IPython.display import DisplayObject, display

# In[16]:


car_data = pd.read_csv('vehicles_us.csv')


# In[17]:


# display(car_data.head(10))


# Removing all of the columns that I will not be utilizing for visualization in the web app

# In[18]:


comp_df = car_data.drop(['cylinders', 'fuel', 'transmission', 'paint_color', 'is_4wd', 'date_posted', 'days_listed' ], axis=1)


# Cleaning the remaining data

# In[19]:


# display(comp_df)
# display(comp_df.info())


# Checking the model year column

# In[20]:


# display(comp_df['model_year'].value_counts(dropna=False))


# Checking the Odometer column

# In[21]:


# display(comp_df['odometer'].value_counts(dropna=False))


# It looks like there is no reason for why there are null values of car year or milage other than it wasn't present to be used. With the size of the data losing these (maximum of) 11,511 entries will still leave us with over 40,000 entries. For the purposes of our visualization, I find dropping this portion of the data this to be acceptable.

# In[22]:


comp_df = comp_df.dropna()
# display(comp_df.info())


# Now that we have our data cleaned of null values, I will explore the column values more and also extract useful informaiton from the columns that exist.

# In[23]:


# display(comp_df['model_year'].value_counts())
# display(comp_df['model'].value_counts())
# display(comp_df['condition'].value_counts())
# display(comp_df['odometer'].value_counts())
# display(comp_df['type'].value_counts())


# In the above, I notice multiple things. First there is no reason the model year should be a float value. I will chage it to an into. The model is not going to be important in my web app. So I will just extract the make from the model's name to make a new column. The condition column looks good to me--as does the odometer and type.

# In[28]:


comp_df['model_year'] = comp_df['model_year'].astype(int)
comp_df['make'] = comp_df['model'].str.split().str[0]
comp_df = comp_df.drop('model', axis=1)


# In[29]:


# display(comp_df)


# Here we have all the columns I will want to have access to in my web app visualization. I have also removed all other columns to help reserve memory and improve speeds.

# In[ ]:

st.set_page_config('PauleyJ Car WebApp')
st.header('Data Viewer')
with st.expander ('The following is a static table that displays all the cars \
            that can be represented in the following visualizations.'):
    st.dataframe(comp_df)
st.sidebar.markdown('''
  **Visualization Filters:** \n
 Interact with the follow selectors and sliders to modify \
    what the following plots show you from the data
'''
    )
with st.sidebar.expander('Makes & Price Plot'):
    all_types = sorted(comp_df['type'].unique())
    st.write("""Select what automotive makes you care to see in the \
            plot.
            Optionally adjust the model year slider to set a range\
            on model years displayed 
            """)
    all_makes = sorted(comp_df['make'].unique())
    all_conditions = ['new', 'like new', 'excellent', 'good', \
                      'fair', 'salvage']
    make_select = st.multiselect('Make', all_makes, all_makes)
    year_select_box = st.slider('Model Year', 1908, 2019, [1908, 2019])
    type_select_box = st.multiselect("Type", all_types, all_types)
    cond_select_box = st.multiselect('Car\'s Condition', all_conditions, all_conditions)


with st.sidebar.expander('Milage & Price Plot'):
    st.write("""Select what milage range, model year, car condition, \
            and car type you care to see in the plot.
            """)
    milage_select= st.slider('Milage', 0, 990000, [0, 990000], 1000)
    year_select_scatter = st.slider('Car Model Year', 1908, 2019, [1908, 2019])
    cond_select_scatter = st.multiselect('Car Condition', all_conditions, all_conditions)
    type_select_scatter = st.multiselect('Car Type', all_types, all_types)
    regression_select = st.selectbox('Regression Selector', ['condition', 'type', None])

with st.sidebar.expander('Milage & Condition Plot'):
    st.write('Select what type and makes you want included in the \
             visualization')
    cond_select_hist =  st.multiselect('Condition', all_conditions, all_conditions)
    type_select_hist = st.multiselect("Types", all_types, all_types)

# %%
st.header('Make/Price Boxplots')
with st.expander('The following boxplots show aggregated quartile \
                 information about the price listings of the cars of \
                 the selected automotive makes. In the side bar you can \
                 choose which vechicle types, models, and milage range \
                 you want inclueded in the visualization. This would be \
                 useful if you want to get an idea of what your car might \
                 sell for based on these factors.'):
    fig1_df = comp_df[comp_df['make'].isin(make_select)]
    fig1_df = fig1_df[fig1_df['model_year'].isin(year_select_box)]
    fig1_df = fig1_df[fig1_df['condition'].isin(cond_select_box)]
    fig1_df = fig1_df[fig1_df['type'].isin(type_select_box)]
    fig1 = px.box(fig1_df, x='make', y="price")
    fig1.update_yaxes(range=[None, None])
    fig1.update_layout(width = 700, height = 700)
    st.write(fig1)

st.header('Milage/Price Scatterplot')
with st.expander('The following scatterplot shows points of vechicles at the intersection of \
                 their listed price and odometer reading (in miles). There is also a linear regression \
                 line for based on your selection from the sidebar. Using the filters in the \
                 sidebar you can see if there are varying trends based on model year, condition, \
                 or car type of the vehicle in condition vs milage.'):
    fig2_df = comp_df[(comp_df['odometer'] >= milage_select[0]) & \
                    (comp_df['odometer']<= milage_select[1])]
    fig2_df = fig2_df[fig2_df['model_year'].isin(year_select_scatter)]
    fig2_df = fig2_df[fig2_df['condition'].isin(cond_select_scatter)]
    fig2_df = fig2_df[fig2_df['type'].isin(type_select_scatter)]
    fig2 = px.scatter(fig2_df, x = 'odometer', y = 'price', trendline = 'ols', color=regression_select)
    fig2.update_yaxes(range = [None, None])
    st.write(fig2)

st.header('Milage/Condition Histogram')
with st.expander('The following histogram shows the count of vechicles in a range of milage \
                 and their listed condition. Using the filters in the sidebar you can see \
                 if there are trends in condition vs milage. You can also see if that \
                 changes based on the vehicle type.'):
    fig3_df = comp_df[comp_df['condition'].isin(cond_select_hist)]
    fig3_df = fig3_df[fig3_df['type'].isin(type_select_hist)]
    fig3 = px.histogram(fig3_df, x = 'odometer', color='condition')
    fig3.update_yaxes(range = [None, None])
    fig3.update_xaxes(range = [0,400000])
    st.write(fig3)