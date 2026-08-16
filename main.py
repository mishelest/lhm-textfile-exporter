import logging

from src import __version__
from exporter_service import ExporterService


logger = logging.getLogger(__name__)


def main():
    service = ExporterService()

    logger.info("lhmTF-exporter %s starting", __version__)

    try:
        service.run()

    except KeyboardInterrupt:
        logger.info("Shutting Down")

    except Exception:
        logger.exception("Fatal error")
        raise
    



if __name__ == "__main__":
    main()