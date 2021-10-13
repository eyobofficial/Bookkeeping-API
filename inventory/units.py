from django.utils.translation import gettext_lazy as _


class MeasurementUnit:
    # Mass
    KILOGRAM = 'kg'
    HECTOGRAM = 'hg'
    DECAGRAM = 'dag'
    GRAM = 'g'
    DECIGRAM = 'dg'
    CENTIGRAM = 'cg'
    MILLIGRAM = 'mg'
    POUND = 'lb'

    # Length
    INCH = 'in'
    YARD = 'yd'
    METER = 'mt'
    FOOT = 'ft'
    CENTIMETER = 'ct'

    # Volume
    LITRE = 'lt'
    CUP = 'cup'
    PINT = 'pt'
    GALLON = 'gal'
    BARREL = 'bbl'

    # Miscellaneous
    PIECE = 'pc'

    UNIT_CHOICES = (
        # Mass
        (KILOGRAM, _('kg')),
        (HECTOGRAM, _('hg')),
        (DECAGRAM, _('dag')),
        (GRAM, _('g')),
        (DECIGRAM, _('dg')),
        (CENTIGRAM, _('cg')),
        (MILLIGRAM, _('mg')),
        (POUND, _('lb')),

        # Length
        (INCH, _('in')),
        (YARD, _('yd')),
        (METER, _('mt')),
        (FOOT, _('ft')),
        (CENTIMETER, _('ct')),

        # Volume
        (LITRE, _('lt')),
        (CUP, _('cup')),
        (PINT, _('pt')),
        (GALLON, _('gal')),
        (BARREL, _('bbl')),

        # Miscellaneous
        (PIECE, _('pc'))
    )

    @property
    def all_units(self):
        return [unit[0] for unit in MeasurementUnit.UNIT_CHOICES]
