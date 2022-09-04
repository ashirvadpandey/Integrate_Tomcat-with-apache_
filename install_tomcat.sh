#!/bin/bash
echo "Installing jdk"
yum install java-1.8*
echo "Downloading Tomcat...."
yum install wget -y
cd /opt

wget https://dlcdn.apache.org/tomcat/tomcat-8/v8.5.82/bin/apache-tomcat-8.5.82.tar.gz
echo "Extracting ...."
tar -xvzf apache-tomcat-8.5.82.tar.gz
rm -rf apache-tomcat-8.5.82.tar.gz
cd apache-tomcat-8.5.82/bin
chmod +x shutdown.sh startup.sh
ln -s /opt/apache-tomcat-8.5.82/bin/startup.sh /usr/local/bin/tomcatup
ln -s /opt/apache-tomcat-8.5.82/bin/shutdown.sh /usr/local/bin/shutdown
#cd /opt/apache-tomcat-8.5.82/webapps/host-manager/META-INF

tomcatup
echo "Now tomcat is working on port 8080"
