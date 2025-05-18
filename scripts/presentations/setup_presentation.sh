#!/bin/bash
# setup_presentation.sh - Install required tools for presentation generation and viewing
#
# This script installs the necessary packages for working with LaTeX presentations,
# including beamer class support, PDF presentation tools, and QR code utilities.

set -e  # Exit on error

echo "==== Values Compass Presentation Environment Setup ===="
echo "Installing required packages for LaTeX presentation work..."

# Update package lists
echo "Updating package lists..."
sudo apt-get update

# Install LaTeX packages needed for presentations
echo "Installing LaTeX packages..."
sudo apt-get install -y \
    texlive-latex-extra \
    texlive-fonts-recommended \
    texlive-fonts-extra \
    texlive-latex-recommended \
    texlive-publishers \
    latexmk \
    latexdiff

# Install PDF presentation tool
echo "Installing PDF presentation viewer (pdfpc)..."
sudo apt-get install -y pdfpc

# Install QR code tools
echo "Installing QR code generation and scanning tools..."
sudo apt-get install -y \
    qrencode \
    zbar-tools

echo "==== Installation Complete ===="
echo "You can now generate the presentation with: make presentation.pdf"
echo "To present the PDF with pdfpc, run: pdfpc presentation.pdf"
echo "To verify QR codes, use: zbarimg github_repo_qr.png"