from decouple import config
from django.db.models import PositiveSmallIntegerField


class CustomEnum(object):
    class Enum(object):
        name = None
        value = None
        type = None

        def __init__(self, name, value, type):
            self.key = name
            self.name = name
            self.value = value
            self.type = type

        def __str__(self):
            return self.name

        def __repr__(self):
            return self.name

        def __eq__(self, other):
            if other is None:
                return False
            if isinstance(other, CustomEnum.Enum):
                return self.value == other.value
            raise TypeError

    @classmethod
    def choices(c):
        attrs = [a for a in c.__dict__.keys() if a.isupper()]
        values = [(c.__dict__[v], CustomEnum.Enum(v, c.__dict__[v], c).__str__()) for v in attrs]
        return sorted(values, key=lambda x: x[0])

    @classmethod
    def default(cls):
        """
        Returns default value, which is the first one by default.
        Override this method if you need another default value.
        """
        return cls.choices()[0][0]

    @classmethod
    def field(cls, **kwargs):
        """
        A shortcut for
        Usage:
            class MyModelStatuses(CustomEnum):
                UNKNOWN = 0
            class MyModel(Model):
                status = MyModelStatuses.field(label='my status')
        """
        field = PositiveSmallIntegerField(choices=cls.choices(), default=cls.default(), **kwargs)
        field.enum = cls
        return field

    @classmethod
    def get(c, value):
        if type(value) is int:
            try:
                return [
                    CustomEnum.Enum(k, v, c)
                    for k, v in c.__dict__.items()
                    if k.isupper() and v == value
                ][0]
            except Exception:
                return None
        else:
            try:
                key = value.upper()
                return CustomEnum.Enum(key, c.__dict__[key], c)
            except Exception:
                return None

    @classmethod
    def key(c, key):
        try:
            return [value for name, value in c.__dict__.items() if name == key.upper()][0]
        except Exception:
            return None

    @classmethod
    def name(c, key):
        try:
            return [name for name, value in c.__dict__.items() if value == key][0]
        except Exception:
            return None

    @classmethod
    def get_counter(c):
        counter = {}
        for key, value in c.__dict__.items():
            if key.isupper():
                counter[value] = 0
        return counter

    @classmethod
    def items(c):
        attrs = [a for a in c.__dict__.keys() if a.isupper()]
        values = [(v, c.__dict__[v]) for v in attrs]
        return sorted(values, key=lambda x: x[1])

    @classmethod
    def to_list(c):
        attrs = [a for a, _ in c.choices()]
        return attrs

    @classmethod
    def is_valid_transition(c, from_status, to_status):
        return from_status == to_status or from_status in c.transition_origins(to_status)

    @classmethod
    def transition_origins(c, to_status):
        return to_status

    @classmethod
    def get_name(c, key):
        choices_name = dict(c.choices())
        return choices_name.get(key)


class UserType(CustomEnum):
    USER: int = 0
    PRACTITIONER: int = 1
    ADMIN: int = 2

    @classmethod
    def choices(cls):
        return (
            (cls.USER, "USER"),
            (cls.PRACTITIONER, "PRACTITIONER"),
            (cls.ADMIN, "ADMIN"),
        )


class UserGroup(CustomEnum):
    USER: str = "user"
    PRACTITIONER: str = "practitioner"
    # ADMIN: str = "admin"

    @classmethod
    def choices(cls):
        return (
            (cls.USER, "USER"),
            (cls.PRACTITIONER, "PRACTITIONER"),
            # (cls.ADMIN, "ADMIN"),
        )


class AuthTokenEnum(CustomEnum):
    RESET_TOKEN: int = 0
    LOGIN_TOKEN: int = 1
    VERIFICATION: int = 2
    AUTHORIZATION_TOKEN: int = 3

    @classmethod
    def choices(cls):
        return (
            (cls.RESET_TOKEN, "PASSWORD RESET TOKEN"),
            (cls.LOGIN_TOKEN, "LOGIN TOKEN"),
            (cls.VERIFICATION, "VERIFICATION TOKEN"),
            (cls.AUTHORIZATION_TOKEN, "AUTHORIZATION TOKEN"),
        )


class PractitionerCategory(CustomEnum):
    DOCTOR: str = "doctor"
    NURSE: str = "nurse"
    PHYSIOTHERAPIST: str = "physiotherapist"
    CHIROPRACTIC: str = "chiropractic"
    ORTHOPEDIC: str = "orthopedic"
    PHARMACIST: str = "pharmacist"

    @classmethod
    def choices(cls):
        return (
            (cls.DOCTOR, "DOCTOR"),
            (cls.NURSE, "NURSE"),
            (cls.PHYSIOTHERAPIST, "PHYSIOTHERAPIST"),
            (cls.CHIROPRACTIC, "CHIROPRACTIC"),
            (cls.ORTHOPEDIC, "ORTHOPEDIC"),
            (cls.PHARMACIST, "PHARMACIST"),
        )


class AuthTokenStatusEnum(CustomEnum):
    PENDING: int = 0
    USED: int = 1

    @classmethod
    def choices(cls):
        return (
            (cls.PENDING, "PENDING"),
            (cls.USED, "USED"),
        )




class DisabilityType(CustomEnum):
    DISABLE: str = "disable"
    NOT_DISABLE: str = "not disabled"

    @classmethod
    def choices(cls):
        return (
            (cls.DISABLE, "DISABLE"),
            (cls.NOT_DISABLE, "NOT DISABLE"),
        )


class MaritalType(CustomEnum):
    MARRIED: str = "married"
    SINGLE: str = "single"
    DIVORCED: str = "divorced"

    @classmethod
    def choices(cls):
        return (
            (cls.MARRIED, "MARRIED"),
            (cls.SINGLE, "SINGLE"),
            (cls.DIVORCED, "DIVORCED"),
        )


class GenderType(CustomEnum):
    MALE: str = "male"
    FEMALE: str = "female"
    OTHERS: str = "others"

    @classmethod
    def choices(cls):
        return (
            (cls.MALE, "Male"),
            (cls.FEMALE, "Female"),
            (cls.OTHERS, "Others"),
        )


class TreatmentTypeEnum(CustomEnum):
    ORAL = "oral"
    INJECTION = "injection"


    @classmethod
    def choices(c):
        return ((c.ORAL, "oral"), (c.INJECTION, "injection"),)


class ValidIDFormat(CustomEnum):
    PDF = "pdf"
    DOC = "word_document"

    @classmethod
    def choices(c):
        return (
            (c.PDF, "pdf"),
            (c.DOC, "word document"),
        )


class ValidIDType(CustomEnum):
    PASSPORT = "international_passport"
    DRIVER_LICENSE = "drivers_licence"
    SOCIAL_SECURITY = "social security"
    VOTERS_CARD = "voters card"

    @classmethod
    def choices(c):
        return (
            (c.PASSPORT, "PASSPORT"),
            (c.DRIVER_LICENSE, "DRIVER'S LICENSE"),
            (c.SOCIAL_SECURITY, "SOCIAL_SECURITY"),
            (c.VOTERS_CARD, "VOTERS CARD"),
        )


class ProgressStatusEnum(CustomEnum):
    PENDING = "pending"
    CANCELLED = "cancelled"
    IN_PROGRESS = "in_progress"
    EXPIRED = "expired"
    COMPLETED = "completed"

    @classmethod
    def choices(c):
        return (
            (c.PENDING, "Pending"),
            (c.CANCELLED, "Cancelled"),
            (c.IN_PROGRESS, "In progress"),
            (c.EXPIRED, "Expired"),
            (c.COMPLETED, "Completed"),
        )


class PriorityEnum(CustomEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class RatingEnum(CustomEnum):
    ONE = 1
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5

    @classmethod
    def choices(cls):
        return (
            (cls.ONE, "1"),
            (cls.TWO, "2"),
            (cls.THREE, "3"),
            (cls.FOUR, "4"),
            (cls.FIVE, "5"),
        )



class NotificationTypeEnum(CustomEnum):
    DEFAULT = "general"
   

class BloodGroupType(CustomEnum):
    A_POS: str = "A+"
    A_NEG: str = "A-"
    B_POS: str = "B+"
    B_NEG: str = "B-"
    O_POS: str = "O+"
    O_NEG: str = "O-"
    AB_POS: str = "AB+"
    AB_NEG: str = "AB-"

    @classmethod
    def choices(cls):
        return (
            (cls.A_POS, "A+"),
            (cls.A_NEG, "A-"),
            (cls.B_POS, "B+"),
            (cls.B_NEG, "B-"),
            (cls.O_POS, "O+"),
            (cls.O_NEG, "O-"),
            (cls.AB_POS, "AB+"),
            (cls.AB_NEG, "AB-"),
        )

class Genotype(CustomEnum):
    """Enumeration for representing different genotypes."""
    AA: str = "AA" 
    AS: str = "AS"  
    SS: str = "SS"  

    @classmethod
    def choices(cls):
        """Returns a tuple of tuples for choices in Django models."""
        return (
            (cls.AA, "AA"),
            (cls.AS, "AS"),
            (cls.SS, "SS"),
        )