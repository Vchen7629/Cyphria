set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\u001b[31m'
NC='\033[0m'

cd ..
echo -e "${YELLOW}Preparing to start DockerFile...${NC}"

docker run --restart on-failure:5  \
    -e KAFKA_BOOTSTRAP_SERVERS='host.docker.internal:9094' \
    -e CATEGORY_TENSOR_FILE_PATH='../precomputed_category_sentences_files/category_tensor.pt' \
    -e CATEGORY_MAPPING_FILE_PATH='../precomputed_category_sentences_files/category_mapping.pkl' \
-d keyword-embedding-category-service

echo -e "${GREEN}Successfully Started DockerFile!${NC}" 