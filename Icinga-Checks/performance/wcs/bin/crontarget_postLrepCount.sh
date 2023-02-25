#!/bin/bash

DB_NAME="DATABASE_USER_NAME"
DB_PASS="DATABASE_USER_PASSWORD"
DB_INST="TNS_NAME_CHANGEME"

python3 /usr/lib/nagios/plugins/icinga-checks/performance/wcs/bin/postLrepCount.py --date `date +'%d-%b-%Y-%H'` --orastring "$DB_NAME;$DB_PASS;$DB_INST"
