# agol_inventary_app
streamlit app for view the inventart for arcgis online administration

## For run the app, requirements docker

### Clone or download this repo

```bash
  git clone https://github.com/rcamilo1526/agol_inventary_app.git
  cd agol_inventary_app
```
###  run docker build 

```bash
  docker build -t agol_inventary:app . 
```

### run docker run

```bash
  docker run -d --name app_agol_inventary -p 8501:8501 agol_inventary:app
```
-d for run detached

### Open the app

In your explorer go to
http://localhost:8501/
 
and use app

#### soon more documentation :) 
### for stop or remove the container
```bash
  docker stop app_agol_inventary
  docker rm app_agol_inventary
```
OR
```bash
  docker rm -f app_agol_inventary
```




