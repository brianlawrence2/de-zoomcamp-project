FROM prefecthq/prefect:latest-python3.10

COPY requirements.txt .

RUN python -m pip install --upgrade pip
RUN pip install -r requirements.txt --trusted-host pypi.python.org --no-cache-dir

COPY . /opt/prefect/flows