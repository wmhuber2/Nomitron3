docker run -it --name nomitron -v /home/wolfgang/Ships/Nomitron3/data:/usr/src/app -d nomitron.pydi
docker update --restart always nomitron
