from . import create_app

if __name__ == "__main__":
    import logging

    logging.basicConfig(level=logging.DEBUG)
    app = create_app()
    app.start_polling()
    app.idle()
