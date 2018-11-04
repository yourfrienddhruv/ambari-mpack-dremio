# Dremio MPack for Ambari

## Building the Dremio MPack
Download ambari-mpack-Dremio repository:

`git clone https://github.com/Pirionfr/ambari-mpack-dremio`

Build example mpack:

`./gradlew clean makePackage`

## Using the Dremio MPack
Stop Ambari server:

`ambari-server stop`

Deploy the Dremio MPack on Ambari server:

`ambari-server install-mpack --mpack=build/dremio-mpack-${version}.tar.gz -v`

Start Ambari server:

`ambari-server start`

##References
* https://cwiki.apache.org/confluence/display/AMBARI/Extensions
* https://cwiki.apache.org/confluence/display/AMBARI/Packaging+and+Installing+Custom+Services

