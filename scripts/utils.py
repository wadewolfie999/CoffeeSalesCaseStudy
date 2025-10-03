import os
import pandas as pd
from sqlalchemy import create_engine
import logging
import config

def get_db_connection():
    try:
        engine = create_engine(
            f"mysql+pymysql://{username}:{password}@{host}:{port}/{database}"
        )



    pass



