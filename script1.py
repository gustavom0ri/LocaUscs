import os
import shutil

origem = 'imagens_iniciais'
destino = 'static/imagens'

if not os.path.exists(destino):
    os.makedirs(destino)

for arquivo in os.listdir(origem):
    if arquivo.lower().endswith(('.jpg', '.jpeg', '.png')):
        shutil.copy(os.path.join(origem, arquivo), os.path.join(destino, arquivo))

print("Imagens copiadas para static/imagens/")
