# FROM continuumio/miniconda3:latest

# COPY . /home
# WORKDIR /home

# # If you need to upgrade pip, you can uncomment the following line
# RUN pip install --upgrade pip

# RUN conda install --file requirements.txt

# EXPOSE 8888

# CMD ["python", "app.py"]


FROM python:3.10

COPY . /home
WORKDIR /home

RUN pip install --upgrade pip
RUN pip install -r requirements.txt


EXPOSE 8080

CMD  ["python", "app.py"]
