"""A program to monitor your ADSL speed and warn you if it degrades.

Please consult the requirements.txt file to setup necessary Gmail account.
You should change the TD value to your normal ADSL Download speed in Mbps
and the TU value for your normal ADSL upload speed in Mbps.
You should also customize the two (sender and receiver) emails.
"""
import json
import subprocess
import yagmail
import dateutil.parser as dparser
import time

# Customize the following for your own values
TD = 210  # Threshold for download speed alert (if below)
TU = 28  # Threshold for upload speed alert (if below)
SENDER_EMAIL = "rjaalerts@gmail.com"  # A less secure Gmail account
RECEIVER_EMAIL = "gogonegro@gmail.com"  # The desired email recipient (any)
# usually you do not need to change the following
TL = 0  # Threshold for packet loss alert (if exceeded)
DEFAULT_TEST_FREQUENCY = 24  # How many hours between normal line tests


def st_json():
    """Run Ookla's speedtest and return JSON data."""
    process = subprocess.Popen(
        ["/usr/local/bin/speedtest", "-f", "json"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    stdout, stderr = process.communicate()
    json_data = json.loads(stdout)
    return json_data


def send_errmsg(subject, testtime, json_data):
    """Send an email to desired server with speedtest warning."""
    sender = SENDER_EMAIL
    receiver = RECEIVER_EMAIL
    body = f"""
Your {json_data["isp"]} ADSL line performance is currently
below the threshold of DL:{TD},

Download: {json_data["download"]["bandwidth"]/124950:3.1f} Mbps
Upload  : {json_data["upload"]["bandwidth"]/124950:2.1f} Mbps

Tested on {json_data["server"]["name"]} server with
{json_data["packetLoss"]:3.3f} packet loss and {json_data["ping"]["latency"]} ping.
Timestamp (UTC): {testtime}
"""
    yag = yagmail.SMTP(sender)
    # Following is just to debug, will use subject and body later
    yag.send(to=receiver, subject=subject, contents=body)


def set_frequency(down, up, loss):
    """Depending on the speed degradation change email frequency.

    The returned frequency is expressed in hours.
    """
    down_degradation = down / TD
    up_degradation = up / TU
    degradation = min(down_degradation, up_degradation)
    if degradation <= 0.1:
        return 1
    elif (degradation > 0.1) and (degradation <= 0.4):
        return 3
    elif (degradation > 0.4) and (degradation <= 0.8):
        return 4
    elif (degradation > 0.8) and (degradation <= 0.9):
        return 6
    else:
        return DEFAULT_TEST_FREQUENCY


def main():
    """Use OOKLA's speedtest CLI to monitor ADSL line performance.

    Log measured speeds to STDOUT.
    If the UL or DL or packet losss values are below thresholds
    then send an email to warn.
    """
    while True:
        # perform the speedtest
        j_d = st_json()
        # prepare values for logging
        testtime = dparser.parse(j_d["timestamp"]).strftime("%Y%m%d %H:%M:%S")
        down_speed = j_d["download"]["bandwidth"] / 124950
        up_speed = j_d["upload"]["bandwidth"] / 124950
        print(
            f"{testtime} UTC - Download: {down_speed:3.1f} Mbps - Upload: {up_speed:2.1f} Mbps"
        )
        # prepare values for anomaly email sending
        subject_td = subject_tu = subject_tl = ""
        anomalies = 0
        # now check if there are degraded values
        if down_speed < TD:
            subject_td = f"DL:{down_speed:3.1f}"
            anomalies += 1
        if up_speed < TU:
            subject_tu = f"UL:{up_speed:2.1f}"
            anomalies += 1
        if j_d["packetLoss"] > TL:
            subject_tl = f'PL:{j_d["packetLoss"]:3.0f}'
            anomalies += 1
        # if there are degraded values send the email
        if anomalies > 0:
            subject = f"ADSL warning: {subject_td} {subject_tu} {subject_tl} exceeded threshold."
            send_errmsg(subject, testtime, j_d)
            test_frequency = set_frequency(down_speed, up_speed, j_d["packetLoss"])
        else:
            test_frequency = DEFAULT_TEST_FREQUENCY
        # depending on found ADSL quality loop after waiting some time
        time.sleep(60 * 60 * test_frequency)


if __name__ == "__main__":
    main()
