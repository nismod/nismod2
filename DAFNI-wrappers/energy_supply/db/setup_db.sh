# bin/bash

chmod 0700 /var/lib/postgresql/data
ls /var/lib/postgresql/data/
postgres -c listen_addresses=0.0.0.0
