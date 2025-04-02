#This is a script for installing dependencies for the spark data processing pipeline
set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\u001b[31m'
NC='\033[0m'

echo -e "${YELLOW}Creating Python3 Venv...${NC}"
python3 -m venv .venv
echo -e "${GREEN}Successfully created Python Venv!${NC}"

echo -e "${YELLOW}Activating Python3 Venv...${NC}"
source .venv/bin/activate
echo -e "${GREEN}Successfully Activated Python Venv!${NC}"

echo -e "${YELLOW}Preparing to Install Sentence Transformers...${NC}"
pip install sentence-transformers -auto-approve
echo -e "${GREEN}Successfully Installed Sentence Transformers!${NC}"

echo -e "${YELLOW}Preparing to Install Pandas...${NC}"
pip install pandas -auto-approve
echo -e "${GREEN}Successfully Installed Pandas!${NC}"

echo -e "${YELLOW}Preparing to Install Pyspark...${NC}"
pip install pyspark -auto-approve
echo -e "${GREEN}Successfully Installed Pyspark!${NC}"

echo -e "${YELLOW}Preparing to Install Pyarrow...${NC}"
pip install pyarrow -auto-approve
echo -e "${GREEN}Successfully Installed Pyarrow!${NC}"

echo -e "${YELLOW}Preparing to Install Vader Sentiment...${NC}"
pip install vaderSentiment -auto-approve
echo -e "${GREEN}Successfully Installed Vader Sentiment!${NC}"

echo -e "${YELLOW}Preparing to Install Flask...${NC}"
pip install Flask -auto-approve
echo -e "${GREEN}Successfully Installed Sentence Transformers!${NC}"


