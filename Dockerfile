FROM python:3.10
WORKDIR /code
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
COPY start.sh /code/start.sh
RUN chmod +x /code/start.sh

# Expose both ports (7860 for UI, 8080 for API)
EXPOSE 7860 8080

CMD ["./start.sh"]