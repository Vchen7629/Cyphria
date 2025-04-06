set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\u001b[31m'
NC='\033[0m'

cd ..
echo -e "${YELLOW}Preparing to build DockerFile...${NC}"
docker build -t data-processing-pipeline .
echo -e "${GREEN}Successfully built DockerFile!${NC}"
