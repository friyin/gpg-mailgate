# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|

  config.vm.box = "generic/ubuntu2204"

#  config.vm.network "private_network", ip: "192.168.99.10"
  config.vm.network "public_network"
  config.vm.network "forwarded_port", guest: 80, host: 8080

#  config.vm.synced_folder "code/", "/app/code"

  config.vm.provider "virtualbox" do |vb|
    vb.memory = 8192
    vb.cpus = 4
  end

#  config.vm.provision "shell", inline: <<-SHELL
#    apt-get update
#    apt-get install -y apache2
#    service apache2 start
#  SHELL
end
