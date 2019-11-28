FROM python:3
ENV PYTHONBUFFERED 1
RUN mkdir /file_service
RUN mkdir /file_service/files
WORKDIR /file_service
COPY requirements.txt /file_service/
RUN pip install -r requirements.txt
COPY . /file_service/
