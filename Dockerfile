FROM python:3.12-slim

WORKDIR /src

ENV PYTHONPATH="/src"

COPY ./requirements.txt .

RUN pip install -r /src/requirements.txt

COPY /src /src/
COPY ./entrypoint.sh .
RUN chmod +x ./entrypoint.sh
RUN ls -la /src
ENTRYPOINT [ "./entrypoint.sh" ]