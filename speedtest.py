"""docstring."""

TD = 200  # Threshold for download speed
TU = 25  # Threshold for upload speed
TL = 0    # Threshold for packet loss


def st_json():
    """Run Ookla's speedtest and return JSON data."""
    import json
    import subprocess
    process = subprocess.Popen(['/usr/local/bin/speedtest', '-f', 'json'],
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    json_data = json.loads(stdout)
    return json_data


def send_msg(subject, testtime, json_data):
    """Send an email to desired server with speedtest warning."""
    import smtplib

    sender = "SpeedTest Monitor <noreply@gmail.com>"
    receiver = "Robert Alexander <gogonegro@gmail.com>"
    smtp_user = "dc8fff528054fc"  # Your mailtrap.io userid
    smtp_pass = "0ade5d9930c752"  # Your mailtrap.io password

    message = f"""Subject: {subject}
To: {receiver}
From: {sender}

Your {json_data["isp"]} ADSL line performance is currently
below the threshold.

Download: {json_data["download"]["bandwidth"]/124950:3.1f} Mbps
Upload  : {json_data["upload"]["bandwidth"]/124950:2.1f} Mbps

Tested on {json_data["server"]["name"]} server with
{json_data["packetLoss"]:3.3f} packet loss and {json_data["ping"]["latency"]} ping.
Timestamp (UTC): {testtime}
"""
    print(message)  # DEBUG
    try:
        smtpObj = smtplib.SMTP("smtp.mailtrap.io", 2525)
        smtpObj.set_debuglevel(0)
        smtpObj.ehlo("gmail.com")
        smtpObj.login(smtp_user, smtp_pass)
        smtpObj.sendmail(sender, receiver, message)
        smtpObj.quit()
    except smtplib.SMTPResponseException as e:
        error_code = e.smtp_code
        error_message = e.smtp_error
        print(f'SMTP error: {error_code}, SMTP msg: {error_message}')


def main():
    """Run a speedtest and send email warning if under threshold."""
    import dateutil.parser as dparser
    j_d = st_json()
    testtime = dparser.parse(j_d["timestamp"]).strftime("%A, %-d %b %Y at %H:%M:%S")
    subject_td = subject_tu = subject_tl = ""
    anomalies = 0
    if (j_d["download"]["bandwidth"]/124950 < TD):
        subject_td = f'DL:{j_d["download"]["bandwidth"]/124950:3.1f}'
        anomalies += 1
    if (j_d["upload"]["bandwidth"]/124950 < TU):
        subject_tu = f'UL:{j_d["upload"]["bandwidth"]/124950:2.1f}'
        anomalies += 1
    if (j_d["packetLoss"] > TL):
        subject_tl = f'PL:{j_d["packetLoss"]:3.0f}'
        anomalies += 1
    if (anomalies > 0):
        subject = f'ADSL warning: {subject_td} {subject_tu} {subject_tl} exceeded threshold.'
        print(f'Subject: {subject}.')
        send_msg(subject, testtime, j_d)
    else:
        print(f"No anomaly measured. All good.")


if __name__ == "__main__":
    main()
