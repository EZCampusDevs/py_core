# Copyright (C) 2022-2023 EZCampus 
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import sys

if __package__ is None and not hasattr(sys, "frozen"):
    # direct call of __main__.py
    import os.path

    path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, os.path.realpath(path))

import db


def main():
    db.init_database(
        db_host="localhost",
        db_port=3306,
        db_user="test",
        db_pass="root",
        db_name="hibernate_db",
        load_env=False,
    )

    db.DT.drop_all()
    db.DT.create_all()

    session: db.SessionObj

    with db.Session().begin() as session:
        school = db.DT.TBL_School(
            school_unique_value="school test school",
            subdomain="sts",
            timezone="utc",
            scrape_id_last=1,
        )
        session.add(school)

    with db.Session().begin() as session:
        report_type = db.DT.TBL_Report_Type(
            report_type_name="test report", report_type_description="test reports"
        )

        os_type = db.DT.TBL_Operating_System(os_name="windows 10")

        browser = db.DT.TBL_Browser(browser_name="firefox", browser_version="1.6")

        session.add(report_type)
        session.add(os_type)
        session.add(browser)
        session.flush()

        report_test = db.DT.TBL_Report(
            description="this is a report",
            report_type=report_type.report_type_id,
            browser_description=browser.browser_id,
            operating_system=os_type.os_id,
        )
        session.add(report_test)

    with db.Session().begin() as session:
        report_2 = session.query(db.DT.TBL_Report).filter_by(report_id=2).first()

        print(report_2)

        report_2.description += "this was added to the end!"

        session.add(report_2)

    print("done")


if __name__ == "__main__":
    main()
