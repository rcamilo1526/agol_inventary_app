FROM continuumio/miniconda3:4.9.2
EXPOSE 8501
RUN mkdir app

WORKDIR /app



# RUN python --version
# RUN pip --version
COPY requirements.txt .
RUN pip install -r requirements.txt

RUN conda install -c esri arcgis --no-deps

COPY . .
CMD streamlit run main.py


