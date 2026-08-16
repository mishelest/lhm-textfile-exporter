import logging
from exporter_service import ExporterService, LOG_FORMAT


logger = logging.getLogger(__name__)


def main():
    logging.basicConfig(
        level=logging.INFO,
        format=LOG_FORMAT,
    )
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