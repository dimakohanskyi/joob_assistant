import logging


def configure_logging(level=logging.INFO):
    logging.basicConfig(
        level=level, 
        datefmt="%Y-%m-%d %H:%M:%S",
        format="[%(asctime)s.%(msecs)03d] | %(levelname)-8s | %(module)-15s:%(lineno)-3d | %(message)s"
    )