FROM python:3.9
ADD ./lambda_version .
COPY ./requirements.txt .
RUN pip install --no-cache-dir --upgrade -r requirements.txt
CMD [ "python",./main.py ]