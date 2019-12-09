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

def send_msg(testtime, json_data):
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
    Timestamp (UTC): {testtime}
    """
    print(f'{testtime} UTC - {json_data["isp"]} - {json_data["download"]["bandwidth"]/124950:3.1f} Mbps') # DEBUG 
    with smtplib.SMTP("smtp.mailtrap.io", 2525) as server:
        server.login(SMTP_USER, SMTP_PASS)
        server.sendmail(SENDER, RECEIVER, message)

def main():
    """Main program."""
    jd = st_json()
    testtime = dparser.parse(jd["timestamp"])\
               .strftime("%A, %-d %b %Y at %H:%M:%S")
    send_msg(testtime, jd)

if __name__ == "__main__":
    main()
