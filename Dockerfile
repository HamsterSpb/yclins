FROM ubuntu:latest


RUN apt-get -y update || true
RUN apt-get -y install python-2.7 vim python-pip git python-dev libffi-dev libssl-dev nginx gcc

RUN pip install --upgrade pip
RUN pip install virtualenv

RUN mkdir /opt/app
WORKDIR /opt/app

COPY ./create_venv.sh /opt/app/create_venv.sh

RUN chmod a+x ./create_venv.sh

RUN ./create_venv.sh

COPY . /opt/app

RUN chmod a+x ./start_app.sh

CMD ["./start_app.sh"]
EXPOSE 5000

