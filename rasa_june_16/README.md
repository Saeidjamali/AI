# Rasa Chatbot

## How to run rasa server and actions server locally

### Cretae .env file

MONGODB_URL should be specified
```
MONGODB_URL=..
ACTION_SERVER_HOST=localhost
```

### Start rasa actions server

```bash
source .env
rasa run actions
```

### Start rasa server

```bash
source .env
rasa run --enable-api --cors "*" --debug
```

