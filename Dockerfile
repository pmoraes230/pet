# Imagem base slim (leve e segura)
FROM python:3.12-slim

# Evita arquivos .pyc e melhora logs
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Diretório de trabalho
WORKDIR /app

# Copia e instala dependências (cache eficiente)
COPY requirements.txt .
RUN apt-get update && apt-get install -y --no-install-recommends \
    default-libmysqlclient-dev build-essential pkg-config \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --upgrade pip \
    && pip install -r requirements.txt \
    && apt-get purge -y --auto-remove build-essential pkg-config

# Copia o projeto inteiro
COPY . .

# Cria entrypoint para rodar migrações + collectstatic + Daphne
RUN echo '#!/bin/bash\n\
set -e\n\
echo "Aguardando MySQL estar pronto..."\n\
until mysqladmin ping -h "$MYSQLHOST" -u "$MYSQLUSER" -p"$MYSQLPASSWORD" --silent; do\n\
  echo "MySQL não está pronto ainda - aguardando..."\n\
  sleep 2\n\
done\n\
echo "MySQL pronto!"\n\
# Aplicar fake nas migrações problemáticas (para evitar conflitos com tabelas/colunas existentes)\n\
python manage.py migrate pet_app 0003 --fake\n\
python manage.py migrate pet_app 0004 --fake\n\
python manage.py migrate pet_app 0005 --fake\n\
python manage.py migrate pet_app 0006 --fake\n\
python manage.py migrate pet_app 0007 --fake\n\
# Agora rodar migrações normais para o resto\n\
python manage.py migrate --noinput\n\
python manage.py collectstatic --noinput\n\
exec daphne -b 0.0.0.0 -p 8000 setup.asgi:application\n' > /app/start.sh \
&& chmod +x /app/start.sh

# Expõe (Railway ignora, mas bom para local)
EXPOSE 8000

# Comando final
CMD ["/app/start.sh"]