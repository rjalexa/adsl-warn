"""docstring."""
import subprocess
import json
import smtplib
import dateutil.parser as dparser

SENDER = "SpeedTest Monitor <noreply@gmail.com>"
RECEIVER = "Robert Alexander <gogonegro@gmail.com>"
SMTP_USER = "86aa40c0e245e2" # Your mailtrap.io userid
SMTP_PASS = "827278518085d6" # Your mailtrap.io password 

def st_json():
    """Run Ookla's speedtest and return JSON data"""
    process = subprocess.Popen(['/usr/local/bin/speedtest', '-f', 'json'],
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    json_data = json.loads(stdout)
    return json_data

def send_msg():
    """Send an email to desired server with speedtest warning"""
    message = f"""\
    Subject: ADSL warning {testtime} UTC
    To: {RECEIVER}
    From: {RECEIVER}

    Your {json_data["isp"]} ADSL line performance is currently
    below the threshold.

    Download: {json_data["download"]["bandwidth"]/124950:3.1f} Mbps
    Upload  : {json_data["upload"]["bandwidth"]/124950:2.1f} Mbps

    Tested on {json_data["server"]["name"]} server with
    {json_data["packetLoss"]:3.3f} packet loss and {json_data["ping"]["latency"]} ping.
    Timestamp (UTC): {json_data["timestamp"]}
    """
    with smtplib.SMTP("smtp.mailtrap.io", 2525) as server:
        server.login(SMTP_USER, SMTP_PASS)
        server.sendmail(SENDER, RECEIVER, message)

def main():
    """Main program."""
    json_data = st_json()
    testtime = dparser.parse(json_data["timestamp"])\
               .strftime("%A, %-d %b %Y at %H:%M:%S")
    print(f"{testtime}: {json_data}")

if __name__ == "__main__":
    main()
