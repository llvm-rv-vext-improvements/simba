#!/bin/bash

set -e

function regression() {
    FILE="$1"
    MESSAGE="$2"

    echo -e "${GREEN}🚬 [satty] Regression '$MESSAGE'...${NC}"
    SATTY_DEBUG=1 poetry run python solver.py "$FILE"
}

# Color definitions
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

SRCS=(simba)

MODE="$1"

if [ "$MODE" == "style" ]; then

    echo -e "${BLUE}🔍 [satty] Running Ruff...${NC}"
    poetry run ruff check "$SRCS"

    echo -e "${YELLOW}🐝 [satty] Running PyLint...${NC}"
    poetry run pylint "$SRCS"

    echo -e "${CYAN}⚫ [satty] Running Black...${NC}"
    poetry run black "$SRCS"

    echo -e "${PURPLE}🌀 [satty] Running isort...${NC}"
    poetry run isort "$SRCS"

    echo -e "${BLUE}🔵 [satty] Running Pyright...${NC}"
    poetry run pyright "$SRCS"

else

    echo "Unknown mode $MODE"
    exit 1

fi
