sudo useradd -u 5678 -m underling
sudo setfacl -R -m u:underling:rwX ./projects
sudo setfacl -R -d -m u:underling:rwX ./projects
sudo setfacl -R -m u:underling:rX ./underling
sudo setfacl -R -d -m u:underling:rX ./underling
sudo passwd underling