# Description
Linux tool used to simplify the setup of a Raspberry Pi based drone.
###### TESTING PENDING

#### What it does?

* Update de Raspberry Pi.
* Configure network access via eth0 or usb0.
* Installs Python and its dependencies.
* Installs OpenCV for computer vision.
* Installs Gstreamer for video streaming.
* Installs APM *aka* Ardupilot for easy control.
* Configure SSH at boot.
* Enables picamera.
* Enables X Forwarding to transmit OpenCV streaming.
* Copy Motion Detector script based on the one made by [Adrian Rosebrock](http://www.pyimagesearch.com/2015/06/01/home-surveillance-and-motion-detection-with-the-raspberry-pi-python-and-opencv/)

---
### Network Configuration
You need setup the same in your Ground Control station but with another ip address, for example, if the Raspberry Pi is 192.168.1.102 your GCS should be 192.168.1.* except 102, and the gateway should be the counterpart.

#### eth0

	address 192.168.1.102
	gateway 192.168.1.103
	netmask 255.255.255.0
	network 192.168.1.0
	broadcast 192.168.1.255
  
#### usb0

	address 192.168.42.42
	netmask 255.255.255.0
	network 192.168.42.0
	broadcast 192.168.42.255
---
### SSH
You need to setup the same in your Ground Control station otherwise your SSH password prompt will be very slow, and the process will be unefficient.

#### SSH Client

	ForwardAgent yes
	ForwardX11 yes
	ForwardX11Trusted yes
	GSSAPIAuthentication no
	GSSAPIDelegateCredentials no
	GSSAPIKeyExchange no
	GSSAPITrustDNS no
	CheckHostIP no
	SendEnv LANG LC_*
	HashKnownHosts yes
	UseDNS no

#### SSH Daemon

	Port 22
	Protocol 2
	HostKey /etc/ssh/ssh_host_rsa_key
	HostKey /etc/ssh/ssh_host_dsa_key
	HostKey /etc/ssh/ssh_host_ecdsa_key
	HostKey /etc/ssh/ssh_host_ed25519_key
	UsePrivilegeSeparation yes
	KeyRegenerationInterval 3600
	ServerKeyBits 1024
	SyslogFacility AUTH
	LogLevel INFO
	LoginGraceTime 120
	PermitRootLogin yes
	StrictModes yes
	RSAAuthentication yes
	PubkeyAuthentication yes
	IgnoreRhosts yes
	RhostsRSAAuthentication no
	HostbasedAuthentication no
	PermitEmptyPasswords no
	ChallengeResponseAuthentication no
	GSSAPIAuthentication no
	GSSAPICleanupCredentials no
	X11Forwarding yes
	X11DisplayOffset 10
	PrintMotd no
	PrintLastLog yes
	TCPKeepAlive yes
	AcceptEnv LANG LC_*
	Subsystem sftp /usr/lib/openssh/sftp-server
	UsePAM yes
	UseDNS no
# License and Disclaimer
See the [license](https://github.com/jlrodriguezf/CIDrone/blob/master/LICENSE) and [disclaimer](https://github.com/jlrodriguezf/CIDrone/blob/master/DISCLAIMER) files.
