# Import python packages
import streamlit as st
import pandas as pd
import requests
from snowflake.snowpark.functions import col



# Write directly to the app
st.title(f":cup_with_straw: Customize Your Smoothie :cup_with_straw: {st.__version__}")
st.write(
  """Choose the fruits you want in your custom Smoothie!
  """
)


name_on_order = st.text_input('Name on Smoothie:')
st.write('The name on your Smoothie will be:', name_on_order)

cnx = st.connection("snowflake")
session = cnx.session()
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'),col('SEARCH_ON'))
# st.dataframe(data=my_dataframe, use_container_width=True)
# st.stop()

pd_df = my_dataframe.to_pandas()
# st.dataframe(pd_df)
# st.stop()

ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:'
    , my_dataframe
    , max_selections = 5
)

if ingredients_list:
    ingredients_string = ''

    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '

        # Try to get the 'SEARCH_ON' value, fallback to fruit name if missing
        filtered = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON']
        search_on = filtered.iloc[0] if not filtered.empty and pd.notna(filtered.iloc[0]) else fruit_chosen
      
        st.subheader(f"{fruit_chosen} Nutrition Information")
        try:
          response = requests.get(f"https://my.smoothiefroot.com/api/fruit/{search_on}")
          response.raise_for_status()
          st.dataframe(data=response.json(), use_container_width = True)
        except:
          st.error(f"Failed to fetch data for {fruit_chosen} (search key: {search_on}): {e}")

    #st.write(ingredients_string)

    my_insert_stmt = """ insert into smoothies.public.orders(ingredients, name_on_order)
            values ('""" + ingredients_string + """','""" +name_on_order+ """')"""

    #st.write(my_insert_stmt)
    #st.stop()
    
    time_to_insert = st.button('Submit Order')
    
    if time_to_insert:
        session.sql(my_insert_stmt).collect()

        st.success(f'Your Smoothie is ordered, {name_on_order}!', icon='✅')




