sudo apt-get update
sudo apt install python3-pip
sudo apt install python3-django
sudo pip install Django
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt-get install python3.8-dev # change to specific python version
sudo pip install pymongo python-dateutil uwsgi prettytable

sudo tmux new-session -d -s idscheckserver
sudo tmux send-keys "cd /home/techsupport/idscheckserver/" C-m
sudo tmux send-keys "python3 manage.py migrate" C-m
sudo tmux send-keys "uwsgi --ini uwsgi_front.ini" C-m
