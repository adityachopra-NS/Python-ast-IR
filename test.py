from entities.location import Location

class Learner:
    def __init__(self, uid, full_name, years, location=None):
        self.uid = uid
        self.full_name = full_name
        self.years = years
        self.location = location

    def assign_location(self, city, zip_code):
        self.location = Location(city, zip_code)

    def __str__(self):
        return f"Learner({self.uid}, {self.full_name}, {self.years})"
