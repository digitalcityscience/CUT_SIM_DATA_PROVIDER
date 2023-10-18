# start with volume ./noise_input_data:/app/noise_input_data
# start with port mapping XXXX:5000

FROM --platform=linux/x86_64 python:3.11

# Tell Python to not generate .pyc
ENV PYTHONDONTWRITEBYTECODE 1

# Turn off buffering
ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt ./requirements.txt
RUN pip install --upgrade pip
RUN pip install --upgrade wheel
RUN pip install -r requirements.txt


WORKDIR /app

COPY ./ .

CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "5000"]