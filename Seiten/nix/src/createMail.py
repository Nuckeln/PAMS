from src.checkRunOs import CheckRunOs as cro


class SendMail:

    def sendWindows(to:str, subject:str, body:str):
        '''Sendet eine E-Mail mit dem Betreff und dem Inhalt \n erwartet als Parameter: \n to: Empfänger \n subject: Betreff \n body: Inhalt'''
        import win32com.client as win32
        outlook = win32.Dispatch('outlook.application')
        mail = outlook.CreateItem(0)
        mail.To = to
        mail.Subject = subject
        mail.Body = body
        mail.send

    def sendMailOnMac(to:str, subject:str, body:str):
        '''Sendet eine E-Mail mit dem Betreff und dem Inhal \n erwartet als Parameter: \n to: Empfänger \n subject: Betreff \n body: Inhalt'''
        import subprocess
        subprocess.call(['osascript', '-e', 'tell application "Mail" to send (make new outgoing message with properties {subject:"'+subject+'", content:"'+body+'", visible:true, sender:"'+to+'"})'])


    def sendMail(to:str, subject:str, body:str):
        '''Prüft ob Outlook geöffnet ist \nPrüft OS und Sendet eine E-Mail mit dem Betreff und dem Inhalt \nerwartet als Parameter: \nto: Empfänger \nsubject: Betreff \nbody: Inhalt'''
        if cro.get_os_name() == 'Windows':
            SendMail.sendWindows(to, subject, body)
            return 'E-Mail wurde versendet'
        elif cro.get_os_name() == 'MacOS':
            SendMail.sendMailOnMac(to,subject,body)
            return 'E-Mail wurde versendet'
        else:
            return 'Senden nicht möglich ist Outlook installiert und geöffnet?'
