set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\u001b[31m'
NC='\033[0m'

setup_python_venv() {
    echo "Setting up Python virtual environment..."
    cd ../..

    # Create venv if it doesn't exist
    if [ ! -d ".venv" ]; then
        python3 -m venv .venv
        echo "Virtual environment created."
    else
        echo "Virtual environment already exists."
    fi
    
    # Activate venv
    source .venv/bin/activate
    echo "Virtual environment activated."

    cd ./spark-data-pipeline
    pip install -r requirements.txt
}

install_java() {
    echo "Checking for Java installation..."

    if command -v java &>/dev/null; then
        java_version=$(java -version 2>&1)
        if echo "$java_version" | grep -q "version \"17"; then
            echo "Java 17 is already installed: $java_version"
            return 0
        else
            echo "Java is installed but not version 17. Will install Java 17..."
        fi
    else
        echo "Java not found. Installing Java 17..."
    fi

    echo "Java not found. Installing Java..."

    sudo -n true 2>/dev/null || echo "You'll be prompted for your sudo password"

    sudo apt update

    sudo apt install -y openjdk-17-jdk

    if command -v java &>/dev/null; then
        java_version=$(java -version 2>&1 | head -n 1)
        echo "Java 17 installed successfully: $java_version"
        return 0
    else
        echo "Java 17 installation failed. You may need to install manually."
        return 1
    fi
}

setup_java_home() {
    echo "Setting up JAVA_HOME..."
    
    # Find Java installation path
    JAVA_PATH=$(update-alternatives --list java 2>/dev/null | head -n 1)
    
    if [ -z "$JAVA_PATH" ]; then
        echo "Java path not found. JAVA_HOME cannot be set."
        return 1
    fi
    
    # Extract the directory (remove /bin/java from the path)
    JAVA_PATH=$(dirname $(dirname "$JAVA_PATH"))
    echo "Found Java at: $JAVA_PATH"
    
    if grep -q "export JAVA_HOME=" ~/.bashrc; then
        echo "JAVA_HOME is already configured in .bashrc"
    else
        echo "" >> ~/.bashrc
        echo "# Set Java environment variables" >> ~/.bashrc
        echo "export JAVA_HOME=$JAVA_PATH" >> ~/.bashrc
        echo "export PATH=\$PATH:\$JAVA_HOME/bin" >> ~/.bashrc
        echo "JAVA_HOME configuration added to .bashrc"
    fi
    
    export JAVA_HOME=$JAVA_PATH
    export PATH=$PATH:$JAVA_HOME/bin
    
    echo "JAVA_HOME set to $JAVA_HOME"
}

echo "Starting environment setup..."

echo -e "${YELLOW}Setting Python3 Venv...${NC}"
setup_python_venv
echo -e "${GREEN}Successfully Setup Python Venv!${NC}"

echo -e "${YELLOW}Installing Java 17...${NC}"
install_java
echo -e "${GREEN}Successfully Installed Java 17!${NC}"

echo -e "${YELLOW}Setting up Java 17 home...${NC}"
setup_java_home
echo -e "${GREEN}Successfully Setup Java Home!${NC}"
