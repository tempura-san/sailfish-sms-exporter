#!/usr/bin/env python3

"""
Convert sailfish sms and call history to xml to be imported to android phones.

Reads a sailfish commhistory.db (which can be found in `/home/nemo/.local/share/commhistory`)
and creates a xml-file of all contained sms that is understood by the Android Application
"SMS Backup and Restore" (which can be obtained here:
<https://play.google.com/store/apps/details?id=com.riteshsahu.SMSBackupRestore>).
"""

import sqlite3
from datetime import datetime
from lxml import etree as ET

jolla_db_filename = 'commhistory.db'
sms_filename = 'sms.xml'
calls_filename = 'calls.xml'

cols = ["id", "type", "startTime", "endTime", "direction", "isDraft", "isRead", "isMissedCall", "isEmergencyCall", "status", "bytesReceived", "localUid", "remoteUid", "parentId", "subject", "freeText", "groupId", "messageToken", "lastModified", "vCardFileName", "vCardLabel", "isDeleted", "reportDelivery", "validityPeriod", "contentLocation", "messageParts", "headers", "readStatus", "reportRead", "reportedReadRequested", "mmsId", "isAction", "hasExtraProperties", "hasMessageParts"]

connection = sqlite3.connect(jolla_db_filename)
cursor = connection.cursor()
cursor.execute("SELECT * FROM Events WHERE type=2")
entries = cursor.fetchall()

date = datetime.now()

outxml = ET.Element('smses')
outxml.set('count', str(len(entries)))

for entry in entries:
    # a description of the used XML format can be found here:
    # https://synctech.com.au/sms-backup-restore/fields-in-xml-backup-files/
    sms = ET.SubElement(outxml, 'sms')
    sms.set('protocol', "0") # 0 = SMS
    sms.set('address', str(entry[cols.index('remoteUid')])) # phone number
    sms.set('date', str(entry[cols.index('startTime')] * 1000)) # date sent/received
    sms.set('type', str(entry[cols.index('direction')])) # 1..received, 2..sent
    sms.set('subject', entry[cols.index('subject')] or "null") # usually "null" for SMS
    sms.set('body', entry[cols.index('freeText')] or "") # message content
    sms.set('read', str(entry[cols.index('isRead')])) # 0..unread, 1..read
    sms.set('status', "-1") # Status = None

with open(sms_filename, 'wb') as fp:
    fp.write(ET.tostring(outxml, encoding='utf8', method='xml', pretty_print=True))

cursor = connection.cursor()
cursor.execute("SELECT * FROM Events WHERE type=3")
entries = cursor.fetchall()

outxml = ET.Element('calls')
outxml.set('count', str(len(entries)))

for entry in entries:
    if entry[cols.index('isMissedCall')]:
        calltype = 3
    else:
        calltype = entry[cols.index('direction')]
    date = datetime.fromtimestamp(entry[cols.index('startTime')])
    out += """<call
    type="{type}"
    number="{number}"
    contact_name="{name}"
    date="{date}"
    readable_date="{readble_date}"
    duration="{duration}"/>\n""".format(
        type=calltype,
        number=entry[cols.index('remoteUid')],
        name="",
        date=entry[cols.index('startTime')] * 1000,
        readble_date=date.strftime("%d.%m.%Y %H:%M:%S"),
        duration=entry[cols.index('endTime')] - entry[cols.index('startTime')]
    )
out += "\n</calls>"

with open(calls_filename, 'w') as fp:
    fp.write(out)

print("Done")
