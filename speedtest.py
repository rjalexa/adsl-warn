"""docstring."""
import json
import subprocess
import yagmail
import dateutil.parser as dparser

TD = 200  # Threshold for download speed alert (if below)
TU = 25   # Threshold for upload speed alert (if below)
TL = 0    # Threshold for packet loss alert (if exceeded)


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
    yag = yagmail.SMTP(sender)
    # Following is just to debug, will use subject and body later
    yag.send(to=receiver, subject=subject, contents=body)


def main():
    """Run a speedtest and send email warning if under threshold."""
    j_d = st_json()
    testtime = dparser.parse(j_d["timestamp"]).strftime("%A, %-d %b %Y at %H:%M:%S")
    subject_td = subject_tu = subject_tl = ""
    anomalies = 0
    if j_d["download"]["bandwidth"]/124950 < TD:
        subject_td = f'DL:{j_d["download"]["bandwidth"]/124950:3.1f}'
        anomalies += 1
    if j_d["upload"]["bandwidth"]/124950 < TU:
        subject_tu = f'UL:{j_d["upload"]["bandwidth"]/124950:2.1f}'
        anomalies += 1
    if j_d["packetLoss"] > TL:
        subject_tl = f'PL:{j_d["packetLoss"]:3.0f}'
        anomalies += 1
    if anomalies > 0:
        subject = f"ADSL warning: {subject_td} {subject_tu} {subject_tl} exceeded threshold."
        send_errmsg(subject, testtime, j_d)
    else:
        print(f'Log: {testtime} - Download: {j_d["download"]["bandwidth"]/124950:3.1f} Mbps - Upload  : {j_d["upload"]["bandwidth"]/124950:2.1f} Mbps')


if __name__ == "__main__":
    main()
