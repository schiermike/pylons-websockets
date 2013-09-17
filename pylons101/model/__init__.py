"""The application's model objects"""
from pylons101.model.meta import Session, Base


def init_model(engine):
    """Call me before using any of the tables or classes in the model"""
    Session.configure(bind=engine)
