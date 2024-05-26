
# Route Planner

This script fetches route information between two locations and sends it via email using the Transport NSW API and SendGrid.

## Requirements

To run this script, you'll need:

- Python 3.x installed on your system
- Necessary Python packages, which can be installed using `requirements.txt`

## Installation

1. Clone this repository and navigate to the project directory:

```bash
git clone https://github.com/your_username/your_repository.git
cd your_repository
Install dependencies using pip:
bash
Copy code
pip install -r requirements.txt

Configuration
Before running the script, you need to set up your API keys:

Get your Transport NSW API key from Transport NSW Developer Portal
Get your SendGrid API key from SendGrid
Once you have your API keys, create a .env file in the project directory and add the following:

TRANSPORT_NSW_API=your_transport_nsw_api_key
SEND_GRID_API=your_sendgrid_api_key
Replace your_transport_nsw_api_key and your_sendgrid_api_key with your actual API keys.

Usage
Run the script by executing the following command:

python route_planner.py
The script will fetch the route information between the specified origin and destination, format it into an HTML table, and send it via email.