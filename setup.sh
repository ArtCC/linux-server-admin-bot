#!/bin/bash

# Quick start script for Linux Server Admin Bot
# This script helps you set up and run the bot quickly

set -e

echo "=================================="
echo "Linux Server Admin Bot - Setup"
echo "=================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Error: Docker is not installed${NC}"
    echo "Please install Docker first: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}Error: Docker Compose is not installed${NC}"
    echo "Please install Docker Compose first: https://docs.docker.com/compose/install/"
    exit 1
fi

echo -e "${GREEN}✓ Docker and Docker Compose are installed${NC}"
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo -e "${YELLOW}Creating .env file from template...${NC}"
    cp .env.example .env
    
    echo ""
    echo "Please edit .env file with your configuration:"
    echo "  1. Add your Telegram Bot Token"
    echo "  2. Add your Telegram User ID(s)"
    echo ""
    echo -e "${YELLOW}Opening .env file in nano...${NC}"
    echo "Press Ctrl+X to save and exit"
    sleep 2
    nano .env
else
    echo -e "${GREEN}✓ .env file already exists${NC}"
fi

echo ""
echo "Verifying configuration..."

# Check if bot token is set
if grep -q "your_bot_token_here" .env; then
    echo -e "${RED}Error: Please set TELEGRAM_BOT_TOKEN in .env file${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Configuration looks good${NC}"
echo ""

# Ask if user wants to build and start
read -p "Build and start the bot? (y/n) " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "Building Docker image..."
    docker-compose build
    
    echo ""
    echo "Starting bot..."
    docker-compose up -d
    
    echo ""
    echo -e "${GREEN}✓ Bot is running!${NC}"
    echo ""
    echo "Useful commands:"
    echo "  docker-compose logs -f          # View logs"
    echo "  docker-compose restart          # Restart bot"
    echo "  docker-compose stop             # Stop bot"
    echo "  docker-compose down             # Stop and remove containers"
    echo ""
    echo "View logs now? (y/n)"
    read -p "" -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        docker-compose logs -f
    fi
fi

echo ""
echo "Setup complete! Enjoy your bot! 🤖"
