OKX Crypto Trader - Automate your trading strategy

This project automates cryptocurrency trading on the OKX exchange using a Python application. It functions by constantly monitoring the activities of designated traders (identified by their IDs) and replicating their buy and sell actions in your own OKX account.

Mirroring Trader Actions:

    You provide a comma-separated list of trader IDs in the TRADERS environment variable.
    The application continuously tracks these traders' activity on the OKX exchange.
    Whenever a designated trader buys a cryptocurrency, the application calculates the purchase amount based on your defined allocation percentage (specified in ALLOCATION_PERCENTAGE). For example, if a trader buys $100 worth of Bitcoin and your allocation is 20%, the application will attempt to buy $20 worth of Bitcoin in your account.
    Similarly, when a trader sells a cryptocurrency, the application follows suit by selling the corresponding cryptocurrency in your account, aiming to replicate their trading strategy (though proportional to your allocation).

Benefits:

    This approach allows you to potentially benefit from the trading decisions of experienced or successful traders.
    It can automate your trading strategy, saving you time and effort.

Important Considerations:

    Past performance is not necessarily indicative of future results. Just because a trader has been successful in the past doesn't guarantee future success.
    Market conditions are constantly changing, and there is inherent risk involved in any trading strategy, including this one. There is a high potential for financial loss. Always perform thorough backtesting and risk assessment with a financial advisor before using this application with real funds.

Features:

    Connects to the OKX API using provided credentials.
    Tracks multiple traders (IDs) and their trading activities.
    Allocates a portion of your balance (specified in environment variables) to buy cryptocurrencies purchased by the designated traders.
    Mirrors trader buy and sell actions, aiming to replicate their strategy.

Requirements:

    Python 3.9, 3.10, 3.11
    AWS Account with Terraform configuration
    Docker

Environment Variables:

Create a file named .env (not included in version control!) at the root of your project directory and define the following variables:

# OKX API Credentials
API_KEY=""
SECRET_KEY=""
PASSPHRASE=""
COIN_TO_BUY = 2

# Trader IDs (comma-separated)
UNIQUE_NAMES=id1,id2,id3,id4,id5,id6,id6,id7,id8

Installation:

Terraform: Terraform is an infrastructure as code tool used to provision and manage cloud resources. You will need an AWS account and Terraform installed to configure the deployment infrastructure.

Process:

    Create an AWS account (if you don't have one already).
    Install Terraform (https://www.terraform.io/) and configure it with your AWS credentials.
    Follow the instructions within your Terraform configuration to provision the necessary infrastructure (ECR repository, Fargate service, etc.).

Build and Deploy:

    Run terraform init to initialize Terraform.
    Run terraform apply to create the infrastructure and deploy the Docker image to your ECR repository.

Usage:

The application runs as a background service. Once deployed, it continuously monitors the traders and executes buy/sell orders according to their actions and your defined allocation percentage.

Customization:

    You can modify the Python code to tailor the behavior to your specific trading strategy.
    The Terraform configuration can be adjusted to customize deployment settings.

Security:

It's crucial to keep your OKX API credentials secure.  Never share them with anyone or store them in plain text.
