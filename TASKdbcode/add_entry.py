#!/usr/bin/env python

#-----------------------------------------------------------------------
# add_entry.py
# Author: Andres Blanco Bonilla
# Takes a meal site and a demographic entry as a command line input and
# adds that entry to that meal site table in the TASK database
#-----------------------------------------------------------------------

import argparse
import sys
import sqlalchemy
import sqlalchemy.orm
import psycopg2

import demographic_db as database
from database_constants import DATABASE_URL

#-----------------------------------------------------------------------


def handle_input():
    parser = argparse.ArgumentParser(description = \
        "Adds a patron's demographic entry into the TASK database",\
                                    allow_abbrev  = False)
    parser.add_argument("meal_site", metavar="meal site",
                        help="The race of the patron to be added")
    parser.add_argument("-r", dest='race', metavar="race",
                        help="The race of the patron to be added")
    parser.add_argument("-e", dest='ethnicity', metavar="ethn",
                        help="The ethnicity of the patron (Hispanic or Not)\
                Enter H for Hispanic, N otherwise")
    parser.add_argument("-l", dest='language', metavar="lang",
                        help="The primary language of the patron")
    parser.add_argument("-a", dest='age_range', metavar="age",
                        help="The age range that the patron is in")
    parser.add_argument("-g", dest='gender', metavar="gender",
                        help="The gender of the patron")
    parser.add_argument("-z", dest='zip_code', metavar="zip",
                        help="The zip code of the patron")
    parser.add_argument("-hl", dest='homeless', metavar="homeless",
                        help="Whether the patron is homeless or not")
    parser.add_argument("-v", dest='veteran', metavar="vet",
                        help="Whether the patron is a veteran or not")
    parser.add_argument("-d", dest='disabled', metavar="dis",
                        help="Whether the patron has a disability or not")
    parser.add_argument("-p", dest='patron_response', metavar="pat",
                        help="Whether the patron provided with this information or not")
    args = parser.parse_args()
    args_dict = vars(args)
    args_dict["meal_site"] = args_dict["meal_site"].title()
    return args_dict

# -----------------------------------------------------------------------
def main():

    args_dict = handle_input()

    try:
        engine = sqlalchemy.create_engine(DATABASE_URL)

        with sqlalchemy.orm.Session(engine) as session:
            meal_site = getattr(database, args_dict["meal_site"])
            del args_dict["meal_site"]
            # demographics = {}
            # for demographic in demographic_options:
            #     demographics[demographic] = args_dict[demographic]
            entry = meal_site(\
                service_timestamp = sqlalchemy.func.now(),\
                **args_dict)
            session.add(entry)
            session.commit()

        engine.dispose()

    except Exception as ex:
        print(ex, file=sys.stderr)
        sys.exit(1)

#-----------------------------------------------------------------------
if __name__ == '__main__':
    main()
