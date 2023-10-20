FROM ubuntu:22.04

RUN apt update && apt install -y python3 python3-pip

COPY . .

RUN pip install -r requirements.txt
RUN apt install -y openssh-client openssh-server

CMD [ "python3", "./src/main.py" ] 