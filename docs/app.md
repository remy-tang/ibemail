## Lancer l'application IBEmail

Pour lancer l'application

```bash
conda activate pesto-crypto
cd app
gunicorn -w 1 --threads 1 'ibemail:create_app()'  
```