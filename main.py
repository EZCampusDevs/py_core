
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
    
    session: db.SessionObj
    with db.Session().begin() as session:
        
        report_type = db.DT.TBL_Report_Type(
                report_type_name="test report",
                report_type_description="test reports"
        )
        
        os_type = db.DT.TBL_Operating_System(
            os_name="windows 10"
        )
        
        browser = db.DT.TBL_Browser(
            browser_name = "firefox",
            browser_version = "1.6"
        )
        
        session.add(report_type)
        session.add(os_type)
        session.add(browser)
        session.flush()

        report_test = db.DT.TBL_Report(
           description="this is a report",
           report_type=report_type.report_type_id,
           browser_description=browser.browser_id,
           operating_system=os_type.os_id
        )
        session.add(report_test)
        

    with db.Session().begin() as session:

        report_2 = session.query(db.DT.TBL_Report).filter_by(report_id = 2).first()
        
        print(report_2)
        
        report_2.description += "this was added to the end!"
        
        session.add(report_2)
    
    print("done")


if __name__ == "__main__":
    main()