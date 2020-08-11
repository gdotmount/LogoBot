import os
import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

async def send_email(receiver, ctx, code):
    sender = "discord.logobot@gmail.com"
    password = os.environ['LOGOBOT_PASS']
    message = MIMEMultipart('alternative')
    message['Subject'] = 'Verification for %s' % ctx.guild.name
    message['From'] = sender
    message['To'] = receiver

    text = """\
    Your verification code for %s is:
    %d    
    Sincerely,
    Logobot""" % (ctx.guild.name, code)

    html = """\
    <html>
        <body>
            <center>
                <p>Your verification code for %s is:
                <br>%d</br>
                </p>
            </center>
        </body>
    </html>    
    """ % (ctx.guild.name, code)

    part1 = MIMEText(text, "plain")
    part2 = MIMEText(html, 'html')

    message.attach(part1)
    message.attach(part2)

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(sender, password)
        server.sendmail(sender, receiver, message.as_string())