docker run -it --name nomitron -v /home/wolfgang/Universe/WTW-Station/ships/Nomitron3/data:/usr/src/app -d nomitron.pydi
docker update --restart always nomitron
