wget https://github.com/fatedier/frp/releases/download/v0.44.0/frp_0.44.0_linux_amd64.tar.gz
tar xvf frp_0.44.0_linux_amd64.tar.gz
rm frp_0.44.0_linux_amd64.tar.gz
mv frp_0.44.0_linux_amd64 frp
cd frp
sudo apt install tmux
tmux new -s frp