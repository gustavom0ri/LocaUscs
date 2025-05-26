# LocaUscs

Aplicação web Flask para gerenciamento de negociações de veículos com envio de e-mails.

## 🚀 Executando com Docker

### Pré-requisitos

- [Docker](https://www.docker.com/get-started) instalado na sua máquina.

### Passos para execução

1. Clone o repositório:

   ```bash
   git clone https://github.com/gustavom0ri/LocaUscs.git
   cd LocaUscs
### Construa a imagem Docker:

docker build -t locauscs .
### Execute o container:

docker run -d -p 5000:5000 --name locauscs_app locauscs
## Acesse a aplicação no seu navegador:

http://localhost:5000
🛠️ Variáveis de Ambiente
Certifique-se de configurar as seguintes variáveis de ambiente para o envio de e-mails funcionar corretamente:

PASSWORD: Senha do e-mail remetente (utilizado no arquivo send_email.py).