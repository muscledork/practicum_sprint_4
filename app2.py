#!/usr/bin/env python
# coding: utf-8

# # Car EDA Web App

# ## Introduction

# I have been tasked with taking US vehicle data, cleaning it, and preparing to be used for a streamlit app that will be put online through render.com. The app will be fully interactive as users will be able to select values they want/care about to then be visualized.

# ## Importing & Inital Reading of Data

# In[1]:


import pandas as pd
import streamlit as st
import plotly_express as px


# In[2]:


car_data = pd.read_csv('vehicles_us.csv')
#seperate instance of the car data that will be modified. 
comp_df = pd.read_csv('vehicles_us.csv')


# In[3]:


# display(car_data.head(10))



# **NOT** Removing all of the columns that I will not be utilizing for visualization in the web app **EVEN THOUGH THEY HAVE NO USE FOR MY WEBAPP: PER THE REQUEST OF MY CODE REVIEWER**

# In[4]:


# comp_df = car_data.drop(['cylinders', 'fuel', 'transmission', 'paint_color', 'is_4wd', 'date_posted', 'days_listed' ], axis=1)


# ## Cleaning/Enriching cylinders, fuel, transmission, is_4wd, date_posted, days listed

# ### price

# In[5]:


# display(car_data.info())
# display(car_data['price'].describe())
# display(car_data['price'].value_counts())

comp_df = comp_df.rename(columns={'price': 'price_$'})


# With no null values and seemingly reasonable range of prices I don't see much need to modify or enrich this data outside of adding $ to the price to help contextualize the prices. The almost 800 instances of 1 dollar I find to be acceptable, they might be for parts or a best offer kind of post. If I was going to use the price mean, I would consider droping these 

# ### model_year

# My code reviewer suggested I use median by model for the model year. I don't believe this to be a good enrichment of the data. While it won't skew the median for each model, I do think could have a questionable affect on any conclusions drawn from model_years. If I was planning to use model years in my webapp I would also add an additional column to mark if the year was added via the following function. But since I won't be using this, I'll simply fill the null values with the median of that model year.

# In[6]:


def list_of_null (df, clmn):
    
    """ Creates a list of indexes with a null value in a entry from 
    a column in a dataframe 
    """
    
    null_list = df[df[clmn].isna()]
    null_list = null_list.index.tolist()
    return null_list

def list_of_value (df, clmn, value):
    
    """ Creates a list of indexes from a column in a dataframe with 
    a specified value
    """
    
    value_list = df[df[clmn] == value]
    value_list = value_list.index.tolist() 
    return value_list


# In[7]:


def model_year_update(df, null_list):
    
    """ Changes the model year column entry from null to the median
    year of other models with a non-null model year value
    """
    
    for i in null_list:
        # retrieve the list entry's model name 
        model = df.loc[i, 'model']
        
        #check if there are other entries with the same name & a non-null cylinder entry
        other_entries = df[(df['model']==model) & (df['model_year'].notnull())]
        if not other_entries.empty:
            # set the null list's entry of model year to the median of all 
            # other entries
            median = round(other_entries['model_year'].median())
            df.loc[i, 'model_year'] = median
        else:
            df.loc[i, 'model_year'] = 0
            
    return df


# In[8]:


null_model_year = list_of_null(car_data, 'model_year')
comp_df = model_year_update(car_data, null_model_year)
comp_df['model_year'] = comp_df['model_year'].astype(int)
# display('The number of entries with the year 0 is: ',        (comp_df['model_year']==0).sum())
# display(comp_df['model_year'].value_counts(dropna=False))


# We have now updated the model years on all null entries. We also changed the year to an int as there is no good reason for it to continue to be a float.

# ### model

# In[9]:


# display(car_data.info())
# make a new column 'make'from the model column
comp_df['make'] = comp_df['model'].str.split().str[0]
# display(comp_df)
# display(comp_df['make'].info())
# display(comp_df['make'].value_counts())


# Since there were no null values theres no reason to have to clean the model column. I did see a good reason to take the first word in the model and create a new column 'make' for use in my webapp. I also checked to make sure there were no missing values in this column and that all of the make entries made sense.

# ### condition

# In[10]:


# display(car_data['condition'].value_counts(dropna=False))


# All of the entries in the condition column are non null and consist of 6 differnet strings. Meaning the object type continues to make sense here. There is no further enriching or cleaning needed for my purposes.

# ### cylinders

# In[11]:


# display(car_data['cylinders'].value_counts(dropna = False))
# display(car_data[car_data['cylinders'].isnull()])/


# As there are over 5000 missing entries and the model types seem to be normal, I'll run a function to compare entries with missing values to entries of the exact same model name and use a non-null value from there to enrich our data

# In[12]:


def update_cylinders (df, null_list):
    
    """ Changes the cylinders column entry from null to the first matching 
    model entry with a non-null cylinders value
    """
    
    for i in null_list:
        # retrieve the list entry's model name 
        name = df.loc[i, 'model']
        
        #check if there are other entries with the same name & a non-null cylinder entry
        other_entries = df[(df['model']==name) & (df['cylinders'].notnull())]
        if not other_entries.empty:
            # set the null list's entry's cylinder to the first cylinder entry 
            # in other entries
            non_null_cylinder = other_entries.iloc[0]['cylinders']
            df.loc[i, 'cylinders'] = non_null_cylinder
        else:
            df.loc[i, 'cylinders'] = 0
            
    return df


# In[13]:


cylinders_null = list_of_null(car_data, 'cylinders')
comp_df = update_cylinders(car_data, cylinders_null)


# In[27]:


# display(comp_df['cylinders'].value_counts(dropna=False))
comp_df['cylinders'] = comp_df['cylinders'].astype(int)
# display(comp_df.info())


# The function has updated all entries to now have values. Only 10, 3, and 12 cylinder engines did not gain any entires in with the code. I am not worried about this because there are also no 0 cylinder entries  meaning all of the entries found an appropriate match. I also chose to change the type to integer as there were no signs of a partial cylinder option

# ### fuel

# In[15]:


# display(car_data['fuel'].value_counts(dropna=False))


# The fuel column seems to be in fine order. The datatype is an object which fits for a string. The vast majority of cars are gas. In a professional setting I would try to ask what "other" even could be as a fuel source as that could lead to some interesting conclusions. But as far as this goes we are good.

# ### odometer

# In[16]:


def odometer_update(df, null_list):
    
    """ Changes the model year column entry from null to the median
    year of other models with a non-null model year value
    """
    
    for i in null_list:
        # retrieve the list entry's model_year 
        year = df.loc[i, 'model_year']
        
        #check if there are other entries with the same year & a non-null milage entry
        other_entries = df[(df['model_year']==year) & (df['odometer'].notnull())]
        if not other_entries.empty:
            # set the null list's entry of milage to the median of all 
            # other entries of that year.
            median = round(other_entries['odometer'].median())
            df.loc[i, 'odometer'] = median
        else:
            df.loc[i, 'odometer'] = 0
            
    return df


# In[17]:


null_milage = list_of_null(car_data, 'odometer')
comp_df = odometer_update(car_data, null_milage)
# display(comp_df.info())


# We now have no missing values when it comes to the odometer readings. I do like with the model_year I question how reliable the data is with adding about 8000 instances of medians by year. While much better than the median of the whole dataset, I'm just not sure how this would be viewed in a real life situation. Articles, white papers, or any professional advice on this would be very appreciated.  
# I didn't change the odometer from a float. Most vehicles account for milage down to the tenth of a unit (be it km or mile). I didn't look through all instances, so I don't want to potentially mess anything up with the data.

# ### transmission

# In[18]:


# display(car_data['transmission'].value_counts(dropna=False))


# Again with the transmission column I would consider this to be in good working order for us to use in an analysis. I would ask what "other" might mean for conclusions in the real world, but for our uses today that is unnecessary.

# ### type

# In[19]:


# display(car_data['type'].value_counts(dropna=False))


# There are no null values, all instances seem to be in place. The object type is appropriate for the strings. There is no further enriching or cleaning necessary here.

# ### paint_color

# In[20]:


# display(car_data['paint_color'].value_counts(dropna=False))
# display(comp_df.groupby('make')['paint_color'].value_counts())


# So I attempted a number looks into the relation of 'paint_color' and other column's values. But I didn't find any sound logical relation. I don't want to use the modal value to fill in by make. So I'm going to push back on my code reviewer and refuse to enrich the paint_color column. In the real world I would first ask if this data was important to the scope of the analysis. If it was, I'd attempt to talk to other people to see if there are logical connections. Maybe I could generate a function to fill in the the null values based on the make's of the cars with null paint color based on the distribution of colors that are present in the data. But with 9200+ entries without color AND the fact that I'm not using color in my webapp, I choose to not do anything to this data as everything I can come up with isn't based in inductive or deductive reasoning. 

# ### is_4wd

# In[21]:


# display(car_data['is_4wd'].value_counts(dropna=False))


# I find it safe to assume that since there is only 1.0 and null values the 1.0 is a True and all other entries are intended to be 0.0: False
# 
# In the following cell I will convert the null values to 0.0 then conver the column to boolean values.

# In[22]:


comp_df['is_4wd'].fillna(0.0, inplace=True)
comp_df['is_4wd'] = comp_df['is_4wd'].astype(bool)
# display(comp_df.head(10))
# display(comp_df['is_4wd'].value_counts())


# Now all values in the column are true or false. Making using it later easier and better communication interaction with the column title.

# ### date_posted

# In[24]:


comp_df['date_posted'] = pd.to_datetime(comp_df['date_posted'],                                        format="%Y-%m-%d")
# display(comp_df.info())
# display(comp_df.head(5))


# We have changed the date_posted to a datetime object. This change could be helpful if we were using this column for those values or enriching our data in some other way. Otherwise with no missing values I find this column to be in good working order.

# ### days_listed

# In[25]:


# display(car_data['days_listed'].value_counts(dropna=False))
# display(car_data['days_listed'].isnull().sum())


# This column doesn't have any null values and the day counts all look sensible. I don't think theres any cleaning or enriching to do at the moment for the purposes of my webapp.

# In[26]:


# display(comp_df.info())
# display(comp_df.head(5))


# ## Conclusion of cleaning
# I have now effectively removed all instances of null values where there was logical conditions to help fill in the missing data. I didn't update paint_color for the reasons explained above.

# ## Final Prep before bringing this over to app.py

# In[28]:


comp_df = comp_df.drop(['model','cylinders', 'fuel', 'transmission',                       'paint_color', 'is_4wd', 'date_posted',                        'days_listed'], axis=1)


# In[29]:


# display(comp_df)


# **Here we have all the columns I will want to have access to in my web app visualization. I have also removed all other columns to help reserve memory and improve speeds.**
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