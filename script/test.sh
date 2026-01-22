#!/bin/bash

set -e

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

    echo -e "${BLUE}🔍 [simba] Running Ruff...${NC}"
    poetry run ruff check "$SRCS"

    echo -e "${YELLOW}🐝 [simba] Running PyLint...${NC}"
    poetry run pylint "$SRCS"

    echo -e "${CYAN}⚫ [simba] Running Black...${NC}"
    poetry run black "$SRCS"

    echo -e "${PURPLE}🌀 [simba] Running isort...${NC}"
    poetry run isort "$SRCS"

    echo -e "${BLUE}🔵 [simba] Running Pyright...${NC}"
    poetry run pyright "$SRCS"

else

    echo "Unknown mode $MODE"
    exit 1

fi
