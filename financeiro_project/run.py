import os
from app import create_app

if __name__ == '__main__':
    app = create_app()

    data_dir = os.path.expanduser('~/.financeiro_app')
    os.makedirs(data_dir, exist_ok=True)

    app.run(
        host='0.0.0.0',
        port=8000,
        debug=os.getenv('FLASK_ENV', 'development') == 'development'
    )
