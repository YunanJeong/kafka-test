# Install basic software
sudo apt update
sudo apt install -y software-properties-common curl gnupg

# Import the public key
curl -sq http://ksqldb-packages.s3.amazonaws.com/deb/0.28/archive.key | sudo apt-key add -

# Add the ksqlDB apt repository
sudo add-apt-repository -y "deb http://ksqldb-packages.s3.amazonaws.com/deb/0.28 stable main"
sudo apt update

# Install the package
sudo apt install confluent-ksqldb
