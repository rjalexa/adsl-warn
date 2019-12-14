"""docstring."""
import json
import subprocess
import yagmail
import dateutil.parser as dparser

TD = 210  # Threshold for download speed
TU = 28   # Threshold for upload speed
TL = 0    # Threshold for packet loss


def st_json():
    """Run Ookla's speedtest and return JSON data."""
    process = subprocess.Popen(['/usr/local/bin/speedtest', '-f', 'json'],
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    json_data = json.loads(stdout)
    return json_data


def send_errmsg(subject, testtime, json_data):
    """Send an email to desired server with speedtest warning."""
    sender = "rjaalerts@gmail.com"
    receiver = "gogonegro@gmail.com"
    body = f"""
Your {json_data["isp"]} ADSL line performance is currently
below the threshold.

Download: {json_data["download"]["bandwidth"]/124950:3.1f} Mbps
Upload  : {json_data["upload"]["bandwidth"]/124950:2.1f} Mbps

Tested on {json_data["server"]["name"]} server with
{json_data["packetLoss"]:3.3f} packet loss and {json_data["ping"]["latency"]} ping.
Timestamp (UTC): {testtime}
"""
    print(f'Subject is {subject}.')
    print(f'Test time is {testtime}.')
    yag = yagmail.SMTP(sender)
    yag.send(to=receiver, subject="ADSL problems", contents="Just a test.")


def main():
    """Run a speedtest and send email warning if under threshold."""
    j_d = st_json()
    testtime = dparser.parse(j_d["timestamp"]).strftime("%A, %-d %b %Y at %H:%M:%S")
    subject_td = subject_tu = subject_tl = ""
    anomalies = 0
    if (j_d["download"]["bandwidth"]/124950 < TD):
        subject_td = "Download low"
        anomalies += 1
    if (j_d["upload"]["bandwidth"]/124950 < TU):
        subject_tu = "Upload low"
        anomalies += 1
    if (j_d["packetLoss"] > TL):
        subject_tl = "Packet loss"
        anomalies += 1
    if (anomalies > 0):
        subject = f"ADSL warning: {subject_td} {subject_tu} {subject_tl} exceeded threshold."
        send_errmsg(subject, testtime, j_d)
    else:
        print("No anomaly measured. All good.")


if __name__ == "__main__":
    main()
