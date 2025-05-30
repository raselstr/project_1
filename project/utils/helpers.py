from django.db.models import Q

class AdvancedFilterHelper:
    """
    Helper universal untuk membangun Q filter secara dinamis.
    Mendukung:
    - AND / OR conditions
    - lookup expressions (__gte, __lte, __icontains, dsb)
    - exclude id list
    - tambahan extra Q filter kompleks
    """

    @staticmethod
    def build_and_filter(field_value_map=None, exclude_ids=None, extra_filters=None):
        """
        Bangun Q filter berbasis AND.
        """
        filters = Q()

        if field_value_map:
            for field, value in field_value_map.items():
                if value is not None:
                    filters &= Q(**{field: value})

        if exclude_ids:
            filters &= ~Q(pk__in=exclude_ids)

        if extra_filters:
            filters &= extra_filters

        return filters

    @staticmethod
    def build_or_filter(field_value_map=None, exclude_ids=None, extra_filters=None):
        """
        Bangun Q filter berbasis OR.
        """
        filters = Q()

        if field_value_map:
            or_q = Q()
            for field, value in field_value_map.items():
                if value is not None:
                    or_q |= Q(**{field: value})
            filters &= or_q

        if exclude_ids:
            filters &= ~Q(pk__in=exclude_ids)

        if extra_filters:
            filters &= extra_filters

        return filters
