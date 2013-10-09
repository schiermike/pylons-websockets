from unittest import TestCase
import smtplib


class MiscTests(TestCase):

    def test_smtp(self):
        email_addi = 'mschier@wetafx.co.nz'
        msg = 'From: schiermike@beachaholics.net\r\nTo: %s\r\nSubject: Test mail 33\r\n\r\n' % email_addi
        conn = smtplib.SMTP(host='beachaholics.net')
        conn.set_debuglevel(1)
        conn.sendmail('schiermike@beachaholics.net', [email_addi], msg)
        conn.quit()
