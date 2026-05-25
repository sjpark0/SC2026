docker build -f ./npo-worker/Dockerfile -t npo-cli-worker .
docker build -f ./npo-submit/Dockerfile -t npo-cli-submit .
cd npo-worker
docker compose up -d
cd ..
