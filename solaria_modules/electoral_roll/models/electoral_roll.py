from app.core.database import Base
from app.core.database.fields import Many2one, Char, Date

class Person(Base):
    """
    Electoral Roll Person Model.
    """
    _name = "electoral_roll.person"
    _description = "Electoral Roll Person"

    contact_id = Many2one('contact', required=True, string='Contacto')
    polling_station = Char(size=100, string="Polling Station", required=True)
    circumscription = Char(size=50, string="Circumscription", required=True)
    birth_date = Date(string="Birth Date")

    async def validate(self):
        """
        Model validation logic.
        """
        return True