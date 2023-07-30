# py_core

## Python Core Architecture

- `py_core` is our core python submodule containing primary DB access modules and internal class
  models.
- Our core packages:
    - [Pydantic](https://pydantic.dev/) class structures for anything that is endpoint facing.
    - [python-dotenv](https://github.com/theskumar/python-dotenv/) for `.env` variable loading.
    - [SQLAlchemy](https://www.sqlalchemy.org/) for anything SQL.

## File Structure & Conventions

### Pydantic Internal Class Models

- All pydantic class modules such as `Course`, `Meeting`, `ExtendedMeeting` are found in
  the `/classes/` directory.
- Class modules are named using the following convention:
    - `<snake_case_of_class_name_here>_class.py`
