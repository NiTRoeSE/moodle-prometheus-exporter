# moodle-prometheus-exporter

This project is created with the need to have moodle metrics in prometheus / grafana. Because there is no exporter for moodle related metrics i wrote this one.
I'm not a programmer or python expert, but its working fine.
Any help or improvements are welcome.

## Dependencies

* python 3.6+
* mysql-connector-python
* prometheus_client

## Install

1. Clone Repository
2. Create a user to run it with dedicated user and not as root (recommended)
3. Create a systemd service file (optional)
4. Install needed python modules


        pip3 install mysql-connector-python
        pip3 install prometheus_client
        
5. Copy db_secrets.example to db_secrets.py and fill in your credentials

        cp db_secrets.example db_secrets.py
        
6. Start exporter - with nohup or systemd in backgroud 
