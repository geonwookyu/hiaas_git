loggerConfig = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(levelname)s :: %(asctime)s :: %(module)s ::%(name)s\n%(message)s",
            "datafmt": "%Y-%m-%d %H:%M:%S"
        },
        "error": {
            "format": "%(levelname)s :: %(asctime)s :: %(name)s :: %(lineno)s\n%(message)s",
            "datafmt":"%Y-%m-%d %H:%M:%S"
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",            
            "level": "DEBUG",
            "formatter": "default"
        },
        "file":{
            "class": "logging.FileHandler",
            "level": "DEBUG",            
            "formatter": "default",
            "filename": "mi.log"
        },
        "file_error": {
            "class": "logging.FileHandler",
            "level": "ERROR",            
            "formatter": "error",
            "filename": "error.log"
        }

    },
    "loggers": {
        "naver": {
            "level": "DEBUG",
            "handlers": ["console", "file", "file_error"],
            "propagate": True
        },
        "coupang": {
            "level": "DEBUG",
            "handlers": ["console", "file", "file_error"],
            "propagate": True 
        }
    }
}
