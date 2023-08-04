import requests
from bs4 import BeautifulSoup
import urllib3

# Function to check vulnerability for an application
def check_vulnerability(application_name):
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    response = requests.get(f"https://www.exploit-db.com/search?keywords={application_name}", verify=False)
    soup = BeautifulSoup(response.content, "html.parser")

    exploit_blocks = soup.find_all("div", class_="exploitblock")
    if len(exploit_blocks) > 0:
        print(f"{application_name} is vulnerable!")
        # You can also extract and display specific exploit details from the page if needed.
    else:
        print(f"{application_name} is not vulnerable.")

# Read the application names from the file
file_path = "Installed Software.txt"
with open(file_path, "r") as file:
    application_names = [line.strip() for line in file]

# Check vulnerability for each application in the list
for app_name in application_names:
    check_vulnerability(app_name)

