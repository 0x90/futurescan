#!/usr/bin/env bash
# ELK installation script
# Logstash + Elasticsearch + Kibana for log analysis
#

install_logstash(){
    cd /tmp
    curl -O https://download.elasticsearch.org/logstash/logstash/logstash-1.4.0.tar.gz
    mkdir /usr/local/logstash
    tar zxvf logstash-1.4.0.tar.gz -C /usr/local/logstash
    rm -f logstash-1.4.0.tar.gz
}

install_elasticsearch(){
    #Once we have log stash, we’ll grab elastic search similarly:
    cd /tmp
    curl -O https://download.elasticsearch.org/elasticsearch/elasticsearch/elasticsearch-1.0.1.tar.gz
    mkdir /usr/local/elasticsearch
    tar zxvf elasticsearch-1.0.1.tar.gz -C /usr/local/elasticsearch
    rm -f elasticsearch-1.0.1.tar.gz
}

install_kibana(){
    #Then we’ll untar kibana in the same manner
    cd /tmp
    curl -O https://download.elasticsearch.org/kibana/kibana/kibana-3.0.0.tar.gz
    mkdir /usr/local/kibana
    tar zxvf kibana-3.0.0.tar.gz -C /usr/local/kibana
    rm -f zxvf kibana-3.0.0.tar.gz
}

if [[ $EUID -ne 0 ]]; then
    echo "You must be a root user" 2>&1
    exit 1
else
    install_logstash
    install_elasticsearch
    install_kibana
fi
