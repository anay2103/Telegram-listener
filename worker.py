from celery_app.app import app

if __name__ == '__main__':
    argv = [
        'worker',
        '--loglevel=INFO',
        '--concurrency=1',
    ]
    app.worker_main(argv)
