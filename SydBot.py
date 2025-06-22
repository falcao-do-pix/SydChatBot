import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

#-------------TIRA A CHAVE ANTES DE COMMITAR PELO AMOR-----------
CHAVE_API = "---------------------------------"
bot = telebot.TeleBot(CHAVE_API)
#-----------------------------------------------------------------

def gerar_teclado_justificativas(matricula_aluno):
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
    btn_medico = InlineKeyboardButton("🩺 Atestado Médico", callback_data=f"just_medico:{matricula_aluno}")
    btn_pessoal = InlineKeyboardButton("👤 Problema Pessoal", callback_data=f"just_pessoal:{matricula_aluno}")
    btn_transporte = InlineKeyboardButton("🚌 Transporte", callback_data=f"just_transporte:{matricula_aluno}")
    btn_outro = InlineKeyboardButton("✏️ Outro", callback_data=f"just_outro:{matricula_aluno}")

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

                # Agora, passamos o teclado como um parâmetro 'reply_markup'.
                bot.send_message(chat_id_aluno, texto_notificacao, reply_markup=gerar_teclado_justificativas(matricula))# Passando a matrícula atual do loop
                print(f"Notificação de falta com botões enviada para {nome_aluno} (Matrícula: {matricula})")
                #alunos_notificados += 1

            except Exception as e:
                print(f"Falha ao enviar mensagem para {nome_aluno} (Matrícula: {matricula}). Erro: {e}")

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


@bot.callback_query_handler(func=lambda call: True)
def processar_justificativa(call):
    """
    Processa o clique no botão. Agora, extrai a ação e a matrícula
    diretamente do `call.data`.
    """
    # 1. Extrai a ação e a matrícula do callback_data (ex: "just_pessoal:2024002")
    acao, matricula = call.data.split(':')

    # 2. Busca o nome do aluno no banco de dados usando a matrícula (MUITO MAIS SEGURO!)
    try:
        nome_aluno = banco_de_dados_alunos[matricula]['nome']
    except KeyError:
        # Medida de segurança caso a matrícula não seja encontrada
        bot.send_message(call.message.chat.id, "Ocorreu um erro ao processar sua matrícula. Contate o suporte.")
        print(f"ERRO: Matrícula {matricula} não encontrada no banco de dados ao processar callback.")
        return  # Para a execução da função aqui

    # 3. Log no console com a informação correta
    print(f"O aluno {nome_aluno} (matrícula {matricula}) justificou a falta com o motivo: {acao}")

    # 4. Define a resposta para o aluno
    if acao == "just_medico":
        resposta_texto = "Entendido. Sua falta foi pré-justificada como 'Atestado Médico'. Por favor, não se esqueça de entregar o documento na secretaria."
    elif acao == "just_pessoal":
        resposta_texto = "Recebido. Sua resposta foi registrada como 'Problema Pessoal'."
    elif acao == "just_transporte":
        resposta_texto = "Ok, entendemos. Registramos a justificativa como 'Problema com Transporte'."
    else:  # just_outro
        resposta_texto = "Entendido. Se necessário, por favor, entre em contato com a coordenação para detalhar o motivo."

    # 5. Edita a mensagem original para remover os botões
    motivo_formatado = acao.replace('just_', '').replace('_', ' ').capitalize()
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=f"{call.message.text}\n\n*✅ Resposta registrada: {motivo_formatado}*",
        reply_markup=None,
        parse_mode="Markdown"
    )

    # 6. Envia uma nova mensagem de confirmação
    bot.send_message(call.message.chat.id, resposta_texto)

    # 7. Confirma o callback para o Telegram
    bot.answer_callback_query(call.id, "Resposta registrada!")

#_____ADMIM SIDE_____
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
