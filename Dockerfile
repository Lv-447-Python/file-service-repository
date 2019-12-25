FROM python:3
ENV PYTHONBUFFERED 1
RUN mkdir /file_service
WORKDIR /file_service
COPY . /file_service/
RUN make setup_docker
