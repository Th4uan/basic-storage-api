echo "Instalando o Docker"

sudo apt-get update
sudo apt-get install -y docker.io
sudo systemctl start docker
sudo systemctl enable docker

echo "Instalando o Docker Compose"
sudo apt-get install -y docker-compose
echo "Docker e Docker Compose instalados com sucesso!"

echo "habilitando o usuario docker no sudoers group"
sudo usermod -aG docker $USER
echo "usuario adicionado ao grupo sudoers do docker com sucesso!
"