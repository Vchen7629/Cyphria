set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\u001b[31m'
NC='\033[0m'

cd ..
echo -e "${YELLOW}Preparing to start DockerFile...${NC}"

docker run --restart on-failure:5 -e KAFKA_BOOTSTRAP_SERVERS='host.docker.internal:9094' -d sentiment-analysis-service

echo -e "${GREEN}Successfully Started DockerFile!${NC}" 