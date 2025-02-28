FROM python:3.13

# Copy entrypoint.sh and make it executable (important!)
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

#Explicitly using bash
CMD ["bash", "/app/entrypoint.sh"]
