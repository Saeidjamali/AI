FROM rasa/rasa:3.0.4-full
COPY . .
USER root
COPY requirements.txt /opt/app/requirements.txt
WORKDIR /opt/app
RUN pip install -r requirements.txt
WORKDIR /app
RUN pip install rasa[spacy] && python -m spacy download en_core_web_lg 
USER 1001
EXPOSE 5005
EXPOSE 5055
ENTRYPOINT ["rasa"]