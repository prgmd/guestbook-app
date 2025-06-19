FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install pymongo kafka-python
CMD ["python", "consumer.py"]