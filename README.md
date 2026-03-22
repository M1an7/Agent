curl -X POST \
  https://google.serper.dev/search \
  -H "X-API-KEY: default" \
  -H "Content-Type: application/json" \
  -d '{"q":"What is AI?"}'
conda activate pfedmoap
  python main.py