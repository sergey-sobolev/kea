# For more information, please refer to https://aka.ms/vscode-docker-python
FROM python:3.8-slim

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

# Install pip requirements
COPY requirements.txt .
RUN python -m pip install -r requirements.txt

COPY kea /kea
COPY config.ini /kea/
COPY sq_checker /kea/

# Creates a non-root user with an explicit UID and adds permission to access the /app folder
# For more info, please refer to https://aka.ms/vscode-docker-python-configure-containers
RUN adduser -u 5678 --disabled-password --gecos "" appuser && chown -R appuser /kea && chmod +x /kea/sq_checker
USER appuser

    # During debugging, this entry point will be overridden. For more information, please refer to https://aka.ms/vscode-docker-python-debug
WORKDIR /kea
ENV PYTHONPATH=/kea
CMD ["python", "analyzer.py", "config.ini", "--states_def", "states.def", "--expect", "expected.txt", "--checker", "./sq_checker"]
