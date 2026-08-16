import logging
from exporter_service import ExporterService


logger = logging.getLogger(__name__)


def main():
    try:
        service = ExporterService()
        service.run()

    except KeyboardInterrupt:
        logger.info("Shutting down")

    except Exception:
        logger.exception("Fatal error")
        raise
    



if __name__ == "__main__":
    main()