from datetime import datetime

def saudacao_horario(request):
    hora = datetime.now().hour

    if 5 <= hora < 12:
        saudacao = "Bom dia"
    elif 12 <= hora < 18: 
        saudacao = "Boa tarde"
    else:
        saudacao = "Boa noite"

    return {
        'saudacao_horario': saudacao
    }