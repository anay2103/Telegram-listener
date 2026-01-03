from celery_app.app import app

if __name__ == '__main__':
    argv = [
        'worker',
        '--loglevel=INFO',
    ]
    app.worker_main(argv)
