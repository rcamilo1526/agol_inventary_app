import arcgis 
import streamlit as st
import pandas as pd 
import streamlit.components.v1 as components
import markdown
# @st.cache(suppress_st_warning=True)
from arcgis.gis import GIS
import time
def app():


    st.write("""
    # Aplicación de informe de ArcGIS Online BMCR
    """
    )
    portal = st.text_input("Enter a portal link", "https://www.arcgis.com/")
    st.write("""
    ## Admin acount is required""")
    st.file_uploader("Choose a file")
    # my_bar = st.progress(0)

    # for percent_complete in range(32):
    #     time.sleep(0.1)
    #     my_bar.progress(percent_complete+32)

    # st.markdown("<font color='red'>THIS TEXT WILL BE RED</font>", unsafe_allow_html=False)
    user = st.text_input("Enter the user",'rmartin_esri_colombia')
    password = st.text_input("Enter the password", type="password")
    if st.button('Login'):
        try:
            gis = GIS(portal,user,password)
            st.write("Authentication succesfull")
            arcgis_use(gis)
        except:
            st.write("Authentication failed")

    else:
        st.write("Please login")

# @st.cache(suppress_st_warning=True)
def arcgis_use(gis):
    credits = gis.admin.credits.credits
    st.write(f"""
    #### Actual credits: 
     {credits}
    """)
    users = gis.users.search()

    
def getInventary():
    columns = ["Folder","Propietario", "Título", "Nombre", "Tipo", "Número de vistas", 
           "Tamaño (mb)", "Fecha creación", "Fecha modificación", "Item ID","Acceso","Url"]
    df_i = pd.DataFrame()
    my_bar = st.progress(0)

    for percent_complete in range(100):
        time.sleep(0.1)
        my_bar.progress(percent_complete + 1)
    ##limit the users
    for user in gis.users.search():
        datos = getInventaryItems(user)
        df = pd.DataFrame(datos, columns=columns)
        df_i=pd.concat([df_i,df])

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