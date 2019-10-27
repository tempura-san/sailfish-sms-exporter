#!/usr/bin/env python3

"""
Convert sailfish sms and call history to xml to be imported to android phones.

Reads a sailfish commhistory.db (which can be found in `/home/nemo/.local/share/commhistory`)
and creates a xml-file of all contained sms that is understood by the Android Application
"SMS Backup and Restore" (which can be obtained here:
<https://play.google.com/store/apps/details?id=com.riteshsahu.SMSBackupRestore>).
"""

import argparse
import sqlite3
from datetime import datetime
from lxml import etree as ET

sms_filename = 'sms.xml'
calls_filename = 'calls.xml'

parser = argparse.ArgumentParser(description="Convert Sailfish SMS and call history to XML to be imported to Android phones.")
parser.add_argument('--commhistory', help="the path to the commhistory.db file from the Sailfish phone")

args = parser.parse_args()
jolla_db_filename = args.commhistory or 'commhistory.db'

cols = ["id", "type", "startTime", "endTime", "direction", "isDraft", "isRead", "isMissedCall", "isEmergencyCall", "status", "bytesReceived", "localUid", "remoteUid", "parentId", "subject", "freeText", "groupId", "messageToken", "lastModified", "vCardFileName", "vCardLabel", "isDeleted", "reportDelivery", "validityPeriod", "contentLocation", "messageParts", "headers", "readStatus", "reportRead", "reportedReadRequested", "mmsId", "isAction", "hasExtraProperties", "hasMessageParts"]

connection = sqlite3.connect(jolla_db_filename)

entries = connection.cursor().execute("SELECT * FROM Events WHERE type=2").fetchall()

print("found {} SMS entries - processing...".format(len(entries)))
outxml = ET.Element('smses', attrib={'count': str(len(entries))})

for entry in entries:
    # a description of the used XML format can be found here:
    # https://synctech.com.au/sms-backup-restore/fields-in-xml-backup-files/
    sms = ET.SubElement(outxml, 'sms')
    sms.set('protocol', "0") # 0 = SMS
    sms.set('address', entry[cols.index('remoteUid')]) # phone number
    sms.set('date', str(entry[cols.index('startTime')] * 1000)) # date sent/received
    sms.set('type', str(entry[cols.index('direction')])) # 1..received, 2..sent
    sms.set('subject', entry[cols.index('subject')] or "null") # usually "null" for SMS
    sms.set('body', entry[cols.index('freeText')] or "") # message content
    sms.set('read', str(entry[cols.index('isRead')])) # 0..unread, 1..read
    sms.set('status', "-1") # Status = None

with open(sms_filename, 'wb') as fp:
    fp.write(ET.tostring(outxml, encoding='utf8', method='xml', pretty_print=True))

entries = connection.cursor().execute("SELECT * FROM Events WHERE type=3").fetchall()

print("found {} call entries - processing...".format(len(entries)))
outxml = ET.Element('calls', attrib={'count': str(len(entries))})

for entry in entries:
    # a description of the used XML format can be found here:
    # https://synctech.com.au/sms-backup-restore/fields-in-xml-backup-files/
    if entry[cols.index('isMissedCall')]:
        calltype = 3
    else:
        calltype = entry[cols.index('direction')]

    call = ET.SubElement(outxml, 'call')
    call.set('type', str(calltype)) # 1..incoming, 2..outgoing, 3..missed, 4..voicemail, 5..rejected, 6..refused
    call.set('number', entry[cols.index('remoteUid')]) # phone number called
    call.set('date', str(entry[cols.index('startTime')] * 1000)) # date of call
    call.set('duration', str(entry[cols.index('endTime')] - entry[cols.index('startTime')])) # call duration in seconds

with open(calls_filename, 'wb') as fp:
    fp.write(ET.tostring(outxml, encoding='utf8', method='xml', pretty_print=True))

print("Done")
