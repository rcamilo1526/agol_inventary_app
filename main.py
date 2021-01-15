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
import base64
import plotly.express as px

def app():

    st.write("""
    # Aplicación de informe de ArcGIS Online BMCR
    """
    )
    option = st.selectbox("Use", ['File','Login'])
    if option == 'File':
        sep = st.selectbox("Separator", [',',';','\t'])
        encod = st.text_input("Encoding",value='utf8')
        file_data = st.file_uploader('Select file in csv:',type=['csv'])
        if file_data:
            data = pd.read_csv(file_data,sep=sep,encoding=encod)
            EDA(data)
    else:
        portal = st.text_input("Enter a portal link", "https://www.arcgis.com/")
        st.write("""
        #### Admin acount is required""")
        user = st.text_input("Enter the user",'rmartin_esri_colombia')
        password = st.text_input("Enter the password", type="password")


        session_state = SessionState.get(name="login", button_sent=False)

        button_login = st.button("Login")

        if button_login:
            session_state.button_sent = True

        if session_state.button_sent:
            # st.write(session_state.name)

            gis = GIS(portal,user,password)
            st.write("Authentication succesfull")

            data = arcgis_use(gis)
            # st.write(data)

            # try:
            if type(data) == pd.core.frame.DataFrame:
                EDA(data)
            else:
                st.write('')
            # except:
            



            # try:
            #     gis = GIS(portal,user,password)
            #     st.write("Authentication succesfull")
            #     try:
            #         data = arcgis_use(gis)
            #         try:
            #             EDA(data)
            #         except:
            #             st.write('eda dont work')
            #     except:
            #         st.write('noshe que pasa')
            # except:
            #     st.write("Authentication failed")

            

# @st.cache(suppress_st_warning=True)
def arcgis_use(gis):
    credits = gis.admin.credits.credits
    st.write(f"""
    #### Actual credits: 
     {credits}
    """)

    users = {a.username:a for a in gis.users.search()}
    
    selected_usernames = st.multiselect("Select users (default all)",list(users.keys()),list(users.keys()))
    selected_users = [v for k,v in users.items() if k in selected_usernames]
        
    df = getInventary(selected_users)
    st.markdown(get_table_download_link(df), unsafe_allow_html=True)
    return df



def EDA(df):
    st.write("""
        #### Storage""")
    try:
        st.write("Total storage: {:.2f} Mb == {:.2f} Gb"\
                .format(df['Size (mb)'].sum(),
                df['Size (mb)'].sum()/1024))
    except:
        st.write('No Size (mb) columns founded')

        # var = st.selectbox("Filter by", ['Variable']+list(df))
    st.write("""
        #### General view""")
    var = st.multiselect("Variable",list(df))

    n_max = st.number_input('Registers to show',min_value=0,max_value = len(df.index), value=10,step=1)
    number_columns = list(df.select_dtypes(include=['float64','int64']))
    sortby = st.selectbox("Sort by", number_columns)
    not_sortby = [i for i in number_columns if i != sortby][0]
    if var == []:
        st.dataframe(df.sort_values(by=sortby,ascending=False).head(n_max))
    else:
        filename = '_'.join(var)
        df_show = df.drop(columns=not_sortby)\
                        .groupby(var)\
                        .sum()\
                        .reset_index()\
                        .sort_values(by=sortby,ascending=False)
        st.markdown(get_table_download_link(df_show,'this table',comp=f'_{filename}'), unsafe_allow_html=True)
        st.dataframe(df_show.head(n_max))
        # st.write(df_show_0.columns)
        if len(var)==0:
            fig = px.bar(df.head(n_max), x=var[0], y=sortby)
            st.plotly_chart(fig)
        else:
            fig = px.bar(df.head(n_max), x=var[0], y=sortby)
            st.plotly_chart(fig)
    st.write("""
        #### Filtered view""")
    sortby_2 = st.selectbox("Sort by:", number_columns)
    not_sortby_2 = [i for i in number_columns if i != sortby_2][0]
    filter_by = st.selectbox("Filter by", list(df))
    n_max_2 = st.number_input('Registers to show :',min_value=0, value=10,step=1)

    if filter_by in number_columns:
        value_to_filter = st.number_input('Higher than :',min_value=0, value=100,step=1)
        df_filtered = df[df[filter_by] >= value_to_filter]\
                        .sort_values(by=sortby_2,ascending=False)
    else:
        value_to_filter = st.selectbox(f"{filter_by} equals to ", df[filter_by].unique())
        df_filtered = df[df[filter_by] == value_to_filter]\
                        .sort_values(by=sortby_2,ascending=False)
    
    filename_2 = f'{filter_by}_{value_to_filter}'
    st.markdown(get_table_download_link(df_filtered,'this table',comp=f'_{filename_2}'), unsafe_allow_html=True)
    st.dataframe(df_filtered)
        
    

def get_table_download_link(df,name = 'all the table',comp=''):
    """Generates a link allowing the data in a given panda dataframe to be downloaded
    in:  dataframe
    out: href string
    """
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()  # some strings <-> bytes conversions necessary here
    href = f'<a href="data:file/csv;base64,{b64}" download="inventary{comp}.csv">Download {name} in csv file</a>'
    return href

def getInventary(users):
    columns = ["Folder","Owner", "Title", "Name", "Type", "Views", 
           "Size (mb)", "Creation date", "Edit date", "Item ID","Acces","Url"]
    df_i = pd.DataFrame()
    my_bar = st.progress(0)

    ##limit the users
    for user in users:
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
                          int(item.numViews), 
                          item.size/1048576 , 
                          datetime.utcfromtimestamp(item.created/1000).strftime('%Y-%m-%d %H:%M:%S'),
                          datetime.utcfromtimestamp(item.modified/1000).strftime('%Y-%m-%d %H:%M:%S'),
                          item.id,
                          item.access,
                          item.url])
    return datos   

if __name__ == "__main__":
    app()