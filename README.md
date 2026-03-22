curl -X POST \
  https://google.serper.dev/search \
  -H "X-API-KEY: 1c5acb65caec9d0c7c3c6e9b1e51158d4bd063f3" \
  -H "Content-Type: application/json" \
  -d '{"q":"What is AI?"}'
conda activate pfedmoap
  python main.py