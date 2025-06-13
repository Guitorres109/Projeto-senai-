import asyncio
import websockets
import random

paises = {
    "brasil": "Possui a maior extensão territorial ao sul do equador.",
    "argentina": "Segunda maior economia da América do Sul.",
    "mexico": "Localizado entre o Pacífico e o Golfo, ao norte da América Latina.",
    "chile": "País longo e estreito que se estende ao longo da costa do Pacífico.",
    "colombia": "Famosa por sua produção de café e diversidade biológica.",
    "peru": "Lar da antiga civilização Inca e Machu Picchu.",
    "venezuela": "Conhecida pelo Salto Ángel, a maior cachoeira do mundo.",
    "uruguai": "Pequeno país com grande tradição em futebol na América do Sul.",
    "paraguai": "País sem saída para o mar, localizado no coração da América do Sul.",
    "equador": "Cruzado pela linha do Equador e famoso pelas Ilhas Galápagos.",
    "canada": "Segundo maior país do mundo em área total, localizado na América do Norte.",
    "franca": "Famosa pela Torre Eiffel e rica cultura gastronômica.",
    "japao": "País insular asiático conhecido pela tecnologia e tradição samurai.",
    "australia": "Continente e país famoso por seus cangurus e a Grande Barreira de Corais.",
    "egito": "Terra das pirâmides e do rio Nilo, localizada no nordeste da África.",
    "india": "País mais populoso da Ásia, conhecido pelo Taj Mahal.",
    "russia": "O maior país do mundo em extensão territorial, atravessando Europa e Ásia.",
    "alemanha": "Famosa por sua engenharia e Oktoberfest.",
    "italia": "Berço do Império Romano e conhecida pela culinária italiana.",
    "espanha": "País europeu famoso pela dança flamenca e pela paella.",
    "china": "Potência econômica e país mais populoso do mundo.",
    "coreiadosul": "Líder em tecnologia e entretenimento pop asiático.",
    "eua": "Maior economia mundial e referência em cultura pop.",
    "suecia": "Conhecida pelo alto padrão de vida e neutralidade política.",
    "noruega": "Rica em petróleo e famosa por seus fiordes.",
    "grecia": "Berço da democracia e da filosofia ocidental.",
    "turquia": "Ponte entre Europa e Ásia, rica em história otomana.",
    "africadosul": "Conhecida por sua diversidade étnica e o Parque Kruger.",
    "novazelandia": "Famosa por paisagens naturais e esportes radicais.",
}

sistemas = {
    "algoritmo": "É uma estrutura lógica finita, independente de linguagem.",
    "python": "Linguagem multiparadigma muito usada em IA.",
    "variavel": "Elemento simbólico para armazenar/modificar dados.",
    "computador": "Máquina que processa informações e executa programas.",
    "mouse": "Dispositivo usado para clicar e mover o cursor na tela.",
    "teclado": "Equipamento para digitar letras, números e comandos.",
    "programa": "Conjunto de instruções que dizem ao computador o que fazer.",
    "internet": "Rede mundial que conecta computadores para compartilhar informações.",
    "arquivo": "Documento digital armazenado no computador.",
    "senha": "Palavra secreta usada para proteger acesso.",
    "app": "Aplicativo, programa que você usa no celular ou computador.",
    "wifi": "Conexão sem fio para acessar a internet.",
    "monitor": "Tela onde você vê o que o computador está fazendo.",
    "email": "Mensagem eletrônica enviada pela internet.",
    "nuvem": "Local para guardar arquivos e fotos pela internet.",
    "site": "Página na internet que você visita para obter informações.",
    "backup": "Cópia de segurança para proteger seus dados.",
    "rede": "Conjunto de computadores conectados entre si.",
    "hardware": "Parte física do computador, como placa-mãe e memória.",
    "software": "Programas e sistemas que rodam no computador.",
    "sistema operacional": "Software principal que gerencia o hardware e recursos.",
    "firewall": "Sistema de proteção que controla o tráfego de rede.",
    "browser": "Programa usado para navegar na internet, como Chrome ou Firefox.",
    "servidor": "Computador que fornece serviços a outros computadores.",
    "bit": "A menor unidade de informação digital, pode ser 0 ou 1.",
    "inteligência artificial": "Tecnologia que simula a capacidade humana de pensar.",
    "banco de dados": "Sistema para armazenar e organizar grandes volumes de dados.",
    "robotica": "Ramo da tecnologia que lida com a criação de robôs.",
}

async def jogar_forca(websocket):
    await websocket.send("Bem-vindo ao Jogo da Forca!")

    while True:
        await websocket.send("Escolha o tema:\n1 - Países\n2 - Sistemas")
        tema = await websocket.recv()

        if tema == "1":
            palavras = paises
            tema_nome = "Países"
        else:
            palavras = sistemas
            tema_nome = "Sistemas"

        secreto, dica = random.choice(list(palavras.items()))
        letras_acertadas = ["_"] * len(secreto)
        letras_usadas = set()
        tentativas = 0
        max_tentativas = 6

        await websocket.send(f"Tema: {tema_nome}\nDica: {dica}\nPalavra: {' '.join(letras_acertadas)}")

        while tentativas < max_tentativas:
            await websocket.send("Digite uma letra:")
            letra = await websocket.recv()
            letra = letra.strip().lower()

            if len(letra) != 1 or not letra.isalpha():
                await websocket.send("           ")
                await websocket.send("Letra inválida. Tente novamente.")
                continue

            if letra in letras_usadas:
                await websocket.send("           ")
                await websocket.send("Letra já usada. Escolha outra.")
                continue

            letras_usadas.add(letra)

            if letra in secreto:
                for i, c in enumerate(secreto):
                    if c == letra:
                        letras_acertadas[i] = letra
                await websocket.send("           ")
                await websocket.send(f"Boa! Palavra: {' '.join(letras_acertadas)}")
            else:
                tentativas += 1
                await websocket.send("           ")
                # Aqui a mensagem para atualizar o boneco no cliente:
                await websocket.send(f"Erros: {tentativas}")
                await websocket.send(f"Errado! Tentativas restantes: {max_tentativas - tentativas}")

            if "_" not in letras_acertadas:
                await websocket.send("           ")
                await websocket.send(f"🎉 Parabéns! Você acertou a palavra: {secreto}")
                break

        if "_" in letras_acertadas:
            await websocket.send("           ")
            await websocket.send(f"💀 Você perdeu! A palavra era: {secreto}")

        await websocket.send("           ")
        await websocket.send("Deseja jogar novamente? (s/n)")
        resposta = await websocket.recv()
        if resposta.strip().lower() != 's':
            await websocket.send("           ")
            await websocket.send("Obrigado por jogar! Até a próxima.")
            break

async def main():
    async with websockets.serve(jogar_forca, "0.0.0.0", 8765):
        print("Servidor WebSocket rodando na porta 8765...")
        await asyncio.Future()  # Mantém o servidor rodando

if __name__ == "__main__":
    asyncio.run(main())
