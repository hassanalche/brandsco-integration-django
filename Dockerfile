FROM python:3.6.4

#RUN apt-get install python-dev
#    && apt-get install -y --no-install-recommends \
#
#    && rm -rf /var/lib/apt/lists/*

WORKDIR /usr/src/app
COPY requirement.txt ./
RUN pip install -r requirement.txt
COPY . .

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000" ,"--noreload"]

