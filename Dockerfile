FROM python:3.9.0
RUN pip install boto3
WORKDIR /app

# RUN echo "adduser -u 5678 --disabled-password --gecos 'appuser' appuser && chown -R appuser:appuser /app" > /tmp/user_setup.sh && sh /tmp/user_setup.sh && rm /tmp/user_setup.sh

COPY requirements.txt /app/
RUN pip install -r requirements.txt

COPY . /app/
CMD ["python3", "main.py"]