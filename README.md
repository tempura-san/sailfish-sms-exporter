# Sailfish SMS and call history exporter

Convert Sailfish SMS and call history to XML to be imported to Android phones.

Reads a Sailfish communication database (which can be found in `/home/nemo/.local/share/commhistory/commhistory.db`) and creates an XML file of all contained SMS. The format can be read by by the Android Application "SMS Backup and Restore" (which can be obtained here: <https://play.google.com/store/apps/details?id=com.riteshsahu.SMSBackupRestore>).

Usage:

* `cd` to the folder this script resides in
* `scp nemo@192.168.0.10:~/.local/share/commhistory/commhistory.db .` (replace IP with your Sailfish phone's IP or address)
* `./converter.py` - this should print a single `Done` once completed.
* This generates two files: `sms.xml` and `calls.xml`. Copy them to your Android phone, and point the "SMS Backup and Restore" app to the target folder.

Requirements:

* Python 3
