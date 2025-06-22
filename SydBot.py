import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# Simulando uma base de dados de alunos. A chave principal é o ID de matrícula do aluno.
banco_de_dados_alunos = {
    "202203708007": {"nome": "Jefferson Damião da Silva Lima", "presente": True, "chat_id": None},
    "202203442295": {"nome": "vitor melo", "presente": False, "chat_id": None}, # Exemplo com chat_id
    "202203424467": {"nome": "vitor mota", "presente": False, "chat_id": None},
    "202108462012": {"nome": "anne victoria", "presente": False, "chat_id": None}
}

#-----------------------------------------------------------------
CHAVE_API = "------------------------------"
bot = telebot.TeleBot(CHAVE_API)
#-----------------------------------------------------------------

def gerar_teclado_justificativas():
    """
    Cria e retorna um teclado inline com as opções de justificativa de falta.
    """
    # 1. Cria o objeto do teclado
    markup = InlineKeyboardMarkup()

    # 2. Define a quantidade de colunas (opcional, mas útil para organizar)
    markup.row_width = 2

    # 3. Cria os botões
    # O 'text' é o que o usuário vê.
    # O 'callback_data' é a informação que o bot recebe quando o botão é clicado.
    # Use um padrão para o callback_data, como 'just_NOMEDOBOTAO'
    btn_medico = InlineKeyboardButton("🩺 Atestado Médico", callback_data="just_medico")
    btn_pessoal = InlineKeyboardButton("👤 Problema Pessoal", callback_data="just_pessoal")
    btn_transporte = InlineKeyboardButton("🚌 Transporte", callback_data="just_transporte")
    btn_outro = InlineKeyboardButton("✏️ Outro", callback_data="just_outro")

    # 4. Adiciona os botões ao teclado
    markup.add(btn_medico, btn_pessoal, btn_transporte, btn_outro)

    return markup


# Handler para o comando /start
@bot.message_handler(commands=["start", "iniciar"])
def saudacao_inicial(mensagem):
    # 'mensagem' contém todas as informações da mensagem recebida,
    # incluindo o chat.id de quem enviou.
    chat_id = mensagem.chat.id

    texto = """
    Olá! Sou o SYD, mas pode me chamar de chat mesmo.

    Para que eu possa te enviar notificações, por favor, me informe sua matrícula usando o comando:
    /registrar [SUA_MATRICULA_AQUI]

    Por exemplo: /registrar 207904708227
    """
    bot.send_message(chat_id, texto)

# Função que varre o banco de dados e envia mensagens para os ausentes.
# Esta função NÃO é um handler, ela será chamada por nós.
def verificar_faltas_e_notificar():
    print("\nIniciando verificação de faltas...")

    # Percorre cada aluno no nosso banco de dados
    for matricula, dados in banco_de_dados_alunos.items():
        aluno_presente = dados["presente"]
        chat_id_aluno = dados["chat_id"]
        nome_aluno = dados["nome"]

        # Se o aluno não está presente E nós temos o chat_id dele...
        if not aluno_presente and chat_id_aluno:
            try:
                texto_notificacao = f"Olá, {nome_aluno}. Notamos que você não registrou presença na aula de hoje. Poderia nos informar o motivo?"

                # Envia a mensagem para o aluno
                bot.send_message(chat_id_aluno, texto_notificacao)

                print(f"Notificação de falta enviada para {nome_aluno} (Matrícula: {matricula})")

            except Exception as e:
                # O 'Exception as e' captura qualquer erro que possa ocorrer.
                # Por exemplo, se o aluno bloqueou o bot, o send_message vai falhar.
                print(f"Falha ao enviar mensagem para {nome_aluno}. Erro: {e}")


# Handler para o comando /registrar
@bot.message_handler(commands=["registrar"])
def registrar_aluno(mensagem):
    chat_id = mensagem.chat.id
    try:
        # Pega o texto da mensagem, divide em palavras e pega a segunda (a matrícula)
        matricula = mensagem.text.split()[1]

        # Verifica se a matrícula existe no nosso "banco de dados"
        if matricula in banco_de_dados_alunos:
            # Atualiza o chat_id do aluno no banco de dados
            banco_de_dados_alunos[matricula]["chat_id"] = chat_id
            nome_aluno = banco_de_dados_alunos[matricula]["nome"]

            bot.send_message(chat_id,
                             f"Ótimo, {nome_aluno}! Seu cadastro foi vinculado. Você receberá notificações por aqui.")
            print(f"Aluno {nome_aluno} (matrícula {matricula}) registrou o chat_id: {chat_id}")
        else:
            bot.send_message(chat_id, "Matrícula não encontrada. Verifique o número e tente novamente.")

    except IndexError:
        bot.send_message(chat_id, "Formato inválido. Use: /registrar [SUA_MATRICULA]")



@bot.message_handler(commands=["verificarfaltas"])
def comando_verificar_faltas(mensagem):
    """
    Handler para o comando /verificarfaltas.
    Apenas o admin pode executá-lo para iniciar a rotina de notificação.
    """
    if mensagem.chat.id == 1530419893:
        bot.reply_to(mensagem, "Comando recebido, chefe! Iniciando a verificação de faltas agora mesmo. Avisarei quando terminar.")
        # Chama a função principal que faz a mágica acontecer
        verificar_faltas_e_notificar()
    else:
        bot.reply_to(mensagem, "Desculpe, este é um comando restrito. Você não tem permissão para executá-lo.")



print("Bot em execução...")
bot.polling() #Função watchdog se há mensagem nova
