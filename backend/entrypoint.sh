#!/bin/bash
echo "Esperando a Postgres..."

until python3 -c "
import psycopg2, os, sys
try:
    psycopg2.connect(
        host=os.getenv('DB_HOST', 'db'),
        port=os.getenv('DB_PORT', '5432'),
        dbname=os.getenv('DB_NAME', 'notesdb'),
        user=os.getenv('DB_USER', 'postgres'),
        password=os.getenv('DB_PASSWORD', 'postgres')
    )
    sys.exit(0)
except Exception as e:
    print('Error de conexión:', e)
    sys.exit(1)
"; do
    echo "Postgres no disponible, reintentando en 2s..."
    sleep 2
done

echo "Postgres listo. Iniciando app..."
python3 -c "import app; app.init_db()" || true

exec "$@"
