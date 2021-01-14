FROM continuumio/miniconda3:4.9.2
EXPOSE 8501
RUN mkdir app

WORKDIR /app

COPY requirements.txt .

# RUN python --version
# RUN pip --version
RUN conda install -c esri arcgis
RUN pip install -r requirements.txt

COPY . .
CMD streamlit run main.py


