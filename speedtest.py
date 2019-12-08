"""docstring."""
import subprocess
import json
import dateutil.parser as dparser
import smtplib

sender = "Robert Alexander <gogonegro@gmail.com>"
receiver = "Robert Alexander <gogonegro@gmail.com>"

process = subprocess.Popen(['/usr/local/bin/speedtest', '-f', 'json'],
                           stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE)

stdout, stderr = process.communicate()
json_data = json.loads(stdout)

testtime = dparser.parse(json_data["timestamp"])\
           .strftime("%A, %-d %b %Y at %H:%M:%S")

message = f"""\
Subject: ADSL warning {testtime} UTC
To: {receiver}
From: {sender}

Your {json_data["isp"]} ADSL line performance is currently
below the threshold.

Download: {json_data["download"]["bandwidth"]/124950:3.1f} Mbps
Upload  : {json_data["upload"]["bandwidth"]/124950:2.1f} Mbps

Tested on {json_data["server"]["name"]} server with
{json_data["packetLoss"]:3.3f} packet loss and {json_data["ping"]["latency"]} ping.
Timestamp (UTC): {json_data["timestamp"]}
"""

with smtplib.SMTP("smtp.mailtrap.io", 2525) as server:
    server.login("86aa40c0e245e2", "827278518085d6")
    server.sendmail(sender, receiver, message)
