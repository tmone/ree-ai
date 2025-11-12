@echo off
REM Script to setup SSH key for GitHub Actions deployment
REM Run this script on your local Windows machine

echo 🔑 GitHub Actions SSH Setup for Production Server
echo ==================================================
echo.
echo This script will help you setup SSH keys for GitHub Actions deployment
echo.
echo Configuration:
echo - Server: 192.168.1.11
echo - User: tmone
echo - Password: 1
echo.

pause

REM Check if ssh-keygen is available
ssh-keygen -h >nul 2>&1
if errorlevel 1 (
    echo ❌ ssh-keygen not found! Please install OpenSSH or Git for Windows
    echo.
    echo Install options:
    echo 1. Windows 10/11: Enable OpenSSH in Optional Features
    echo 2. Install Git for Windows: https://git-scm.windows.com/
    pause
    exit /b 1
)

REM Create .ssh directory
if not exist "%USERPROFILE%\.ssh" mkdir "%USERPROFILE%\.ssh"

set KEY_NAME=github-actions-ree-ai

REM Generate SSH key pair
echo 🔐 Generating SSH key pair...
ssh-keygen -t rsa -b 4096 -f "%USERPROFILE%\.ssh\%KEY_NAME%" -N "" -C "github-actions@ree-ai-deployment"

echo.
echo ✅ SSH key pair generated:
echo    Private key: %USERPROFILE%\.ssh\%KEY_NAME%
echo    Public key: %USERPROFILE%\.ssh\%KEY_NAME%.pub
echo.

REM Display public key
echo 📋 Public key content:
echo ==================================================
type "%USERPROFILE%\.ssh\%KEY_NAME%.pub"
echo ==================================================
echo.

REM Create instructions file
echo REE AI - GitHub Actions Deployment Setup Instructions > setup-instructions.txt
echo ==================================================== >> setup-instructions.txt
echo. >> setup-instructions.txt
echo 1. SSH Public Key (add to production server): >> setup-instructions.txt
type "%USERPROFILE%\.ssh\%KEY_NAME%.pub" >> setup-instructions.txt
echo. >> setup-instructions.txt
echo Commands to run on production server (192.168.1.11): >> setup-instructions.txt
echo mkdir -p ~/.ssh >> setup-instructions.txt
echo echo 'PASTE_PUBLIC_KEY_HERE' ^>^> ~/.ssh/authorized_keys >> setup-instructions.txt
echo chmod 700 ~/.ssh >> setup-instructions.txt
echo chmod 600 ~/.ssh/authorized_keys >> setup-instructions.txt
echo. >> setup-instructions.txt
echo 2. SSH Private Key (add to GitHub Secrets as PRODUCTION_SSH_KEY): >> setup-instructions.txt
type "%USERPROFILE%\.ssh\%KEY_NAME%" >> setup-instructions.txt
echo. >> setup-instructions.txt
echo 3. GitHub Repository Secrets URL: >> setup-instructions.txt
echo https://github.com/tmone/ree-ai/settings/secrets/actions >> setup-instructions.txt

echo 🚀 Next Steps:
echo.
echo 1. Copy the public key to your production server:
echo    - SSH to 192.168.1.11 as tmone
echo    - Run these commands:
echo.
echo      mkdir -p ~/.ssh
type "%USERPROFILE%\.ssh\%KEY_NAME%.pub"
echo      ^^ Copy this key and run: echo 'PASTE_KEY_HERE' ^>^> ~/.ssh/authorized_keys
echo      chmod 700 ~/.ssh
echo      chmod 600 ~/.ssh/authorized_keys
echo.
echo 2. Test SSH connection:
echo    ssh -i "%USERPROFILE%\.ssh\%KEY_NAME%" tmone@192.168.1.11 "echo SSH connection successful!"
echo.
echo 3. Add GitHub Secrets:
echo    - Go to: https://github.com/tmone/ree-ai/settings/secrets/actions
echo    - Add PRODUCTION_SSH_KEY with the private key content
echo    - Add OPENAI_API_KEY with your OpenAI API key
echo.
echo 4. Private key content for GitHub Secret (PRODUCTION_SSH_KEY):
echo ==================================================
type "%USERPROFILE%\.ssh\%KEY_NAME%"
echo ==================================================
echo.
echo 💾 Instructions saved to: setup-instructions.txt
echo.
echo ✅ After completing these steps, GitHub Actions will deploy automatically!

pause