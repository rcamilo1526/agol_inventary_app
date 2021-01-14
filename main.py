import arcgis 
import streamlit as st
import pandas as pd 
import streamlit.components.v1 as components
import markdown
# @st.cache(suppress_st_warning=True)
from arcgis.gis import GIS
import time
from datetime import datetime
import os
import SessionState

def app():


    st.write("""
    # Aplicación de informe de ArcGIS Online BMCR
    """
    )
    option = st.selectbox("Use", ['File','Login'])
    if option == 'File':
        file_data = st.file_uploader('Select file in csv:',type=['csv'])
        if file_data:
            data = pd.read_csv(file_data,sep=';',encoding='utf8')
            EDA(data)
    else:
        portal = st.text_input("Enter a portal link", "https://www.arcgis.com/")
        st.write("""
        ## Admin acount is required""")
        user = st.text_input("Enter the user",'rmartin_esri_colombia')
        password = st.text_input("Enter the password", type="password")


        session_state = SessionState.get(name="", button_sent=False)

        button_login = st.button("Login")

        if button_login:
            session_state.button_sent = True

        if session_state.button_sent:
            st.write(session_state.name)

            try:
                gis = GIS(portal,user,password)
                st.write("Authentication succesfull")
                try:
                    EDA(arcgis_use(gis))
                except:
                    st.write('noshe que pasa')
            except:
                st.write("Authentication failed")

            

# @st.cache(suppress_st_warning=True)
def arcgis_use(gis):
    credits = gis.admin.credits.credits
    st.write(f"""
    #### Actual credits: 
     {credits}
    """)
    st.write('a sacar el inventario')
    df = getInventary(gis)
    # st.write(df)
    file_name = 'temp.csv'
    df.to_csv(file_name,encoding='utf8',sep=';',index=False)
    return df


def EDA(df):
    st.write('cagado papa')
    st.write("Total storage: {:.2f} Mb == {:.2f} Gb"\
            .format(df['Size (mb)'].sum(),
            df['Size (mb)'].sum()/1024))

    # var = st.selectbox("Filter by", ['Variable']+list(df))
    var = st.multiselect("Filter by",list(df))
    # st.write(vars)
    n_max = st.number_input('Registers to show',min_value=0,value=10,step=1)
    sortby = st.selectbox("Sort by", list(df.select_dtypes(include=['float64','int64'])))

    
    if var == False:
        st.dataframe(df.sort_values(by=sortby,ascending=False).head(n_max))
    else:
        df_show = df.groupby(var)\
                    .sum()\
                    .reset_index()\
                    .sort_values(by=sortby,ascending=False)\
                    .head(n_max)
        st.dataframe(df_show)


def getInventary(gis):
    columns = ["Folder","Owner", "Title", "Name", "Type", "Views", 
           "Size (mb)", "Creation date", "Edit date", "Item ID","Acces","Url"]
    df_i = pd.DataFrame()
    my_bar = st.progress(0)

    ##limit the users
    for user in gis.users.search():
        datos = getInventaryItems(user)
        df = pd.DataFrame(datos, columns=columns)
        df_i = pd.concat([df_i,df])

    return df_i
    
def getInventaryItems(user):    
    datos = []
    foldersName = [None]+[folder["title"] for folder in user.folders]
    for folder in foldersName:
        items = user.items(folder)
        if folder is None:
            folder = "Root"
        for item in items:
            datos.append([folder, 
                          item.owner, 
                          item.title, 
                          item.name, 
                          item.type, 
                          item.numViews, 
                          item.size/1048576 , 
                          datetime.utcfromtimestamp(item.created/1000).strftime('%Y-%m-%d %H:%M:%S'),
                          datetime.utcfromtimestamp(item.modified/1000).strftime('%Y-%m-%d %H:%M:%S'),
                          item.id,
                          item.access,
                          item.url])
    return datos   

if __name__ == "__main__":
    app()