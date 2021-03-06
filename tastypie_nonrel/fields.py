from tastypie.fields import (ApiField,
                             ToOneField,
                             ToManyField,
                             ApiFieldError,
                             NOT_PROVIDED,)
from tastypie.bundle import Bundle
from tastypie.utils import dict_strip_unicode_keys

class ListField(ApiField):
    """
        Represents a list of simple items - strings, ints, bools, etc. For
        embedding objects use EmbeddedListField in combination with EmbeddedModelField
        instead.
    """
    dehydrated_type     =   'list'

    def dehydrate(self, obj, for_list=False):
        return self.convert(super(ListField, self).dehydrate(obj))

    def convert(self, value):
        if value is None:
            return None
        return value

class ForeignKeysListField(ToManyField):
    """
        Represents a list of embedded objects. It must be used in conjunction
        with EmbeddedModelField.
        Does not allow for manipulation (reordering) of List elements. Use
        EmbeddedCollection instead.
    """
    is_related = False
    is_m2m = False

    def __init__(self, of, attribute, related_name=None, default=NOT_PROVIDED, null=False, blank=False, readonly=False, full=False, unique=False, help_text=None):
        super(ForeignKeysListField, self).__init__(to=of,
                                                 attribute=attribute,
                                                 related_name=related_name,
                                                 # default=default,
                                                 null=null,
                                                 # blank=blank,
                                                 # readonly=readonly,
                                                 full=full,
                                                 unique=unique,
                                                 help_text=help_text)

    def dehydrate(self, bundle, for_list=False):
        print 1
        if not bundle.obj or not bundle.obj.pk:
            print 2
            if not self.null:
                raise ApiFieldError("The model '%r' does not have a primary key and can not be d in a ToMany context." % bundle.obj)
            return []
        if not getattr(bundle.obj, self.attribute):
            print 3
            if not self.null:
                raise ApiFieldError("The model '%r' has an empty attribute '%s' and doesn't all a null value." % (bundle.obj, self.attribute))
            return []
        self.m2m_resources = []
        m2m_dehydrated = []
        # TODO: Also model-specific and leaky. Relies on there being a
        # ``Manager`` there.
        # NOTE: only had to remove .all()
        print 4
        for m2m in getattr(bundle.obj, self.attribute):
            print 5
            m2m_resource = self.get_related_resource(m2m)
            m2m_bundle = Bundle(obj=m2m)
            self.m2m_resources.append(m2m_resource)
            # youhou, dirty hack again baby!
            m2m_bundle.obj = type("DummyContainer", (object,), {'pk': m2m_bundle.obj})
            m2m_dehydrated.append(self.dehydrate_related(m2m_bundle, m2m_resource))
        return m2m_dehydrated

    def hydrate(self, bundle):
        return [b.obj for b in self.hydrate_m2m(bundle)]

class EmbeddedListField(ToManyField):
    """
        Represents a list of embedded objects. It must be used in conjunction
        with EmbeddedModelField.
        Does not allow for manipulation (reordering) of List elements. Use
        EmbeddedCollection instead.
    """
    is_related = False
    is_m2m = False

    #def __init__(self, of, attribute, related_name=None, default=NOT_PROVIDED, null=False, blank=False, readonly=False, full=False, unique=False, help_text=None):
    def __init__(self, **kwargs):
        super(EmbeddedListField, self).__init__(to=kwargs["of"],
                                                 attribute=kwargs['attribute'],
                                                 null=kwargs.get("null", True),
                                                 related_name=kwargs.get("related_name", None),
                                                 # blank=blank,
                                                 # readonly=readonly,
                                                 full=kwargs.get("full", False),
                                                 unique=kwargs.get("unique", False),
                                                 help_text=kwargs.get("help_text", None)
                                               )

    def dehydrate(self, bundle, for_list=False):
        return [i.__class__.objects.filter(pk=i.pk).values()[0] for i in getattr(bundle.obj, self.attribute)]

    def hydrate(self, bundle):
        return [b.obj for b in self.hydrate_m2m(bundle)]

class DictField(ApiField):
    dehydrated_type     =   'dict'

    def dehydrate(self, obj, for_list=False):
        return self.convert(super(DictField, self).dehydrate(obj))

    def convert(self, value):
        if value is None:
            return None

        return value

class EmbeddedModelField(ToOneField):
    """
        Embeds a resource inside another resource just like you would in Mongo.
    """
    is_related = False
    dehydrated_type     =   'embedded'

    def __init__(self, *args, **kwargs):
        '''
            The ``embedded`` argument should point to a ``Resource`` class, NOT
            to a ``Model``. Required.
        '''
        super(EmbeddedModelField, self).__init__(
                                                 to=kwargs["to"],
                                                 attribute=kwargs['attribute'],
                                                 null=kwargs.get("null", False),
                                                 full=True,
                                                 help_text=kwargs.get('help_text'),
                                                )
    def dehydrate(self, obj, for_list=False):
        return obj.obj.__class__.objects.filter(pk=obj.obj.pk).values()[0]

    def hydrate(self, bundle):
        return super(EmbeddedModelField, self).hydrate(bundle).obj

    def build_related_resource(self, value):
        """
        Used to ``hydrate`` the data provided. If just a URL is provided,
        the related resource is attempted to be loaded. If a
        dictionary-like structure is provided, a fresh resource is
        created.
        """
        self.fk_resource = self.to_class()

        # Try to hydrate the data provided.
        value = dict_strip_unicode_keys(value)
        self.fk_bundle = Bundle(data=value)

        return self.fk_resource.full_hydrate(self.fk_bundle)

class EmbeddedCollection(ToManyField):
    """
        EmbeddedCollection allows for operating on the sub resources
        individually, through the index based collection.
    """
    is_related = False
    is_m2m = False

    def __init__(self, of, attribute, related_name=None, default=NOT_PROVIDED, null=False, blank=False, readonly=False, full=False, unique=False, help_text=None):
        super(EmbeddedCollection, self).__init__(to=of,
                                                 attribute=attribute,
                                                 related_name=related_name,
                                                 # default=default,
                                                 null=null,
                                                 # blank=blank,
                                                 # readonly=readonly,
                                                 full=full,
                                                 unique=unique,
                                                 help_text=help_text)

    def dehydrate(self, bundle, for_list=False):
        if not bundle.obj or not bundle.obj.pk:
            if not self.null:
                raise ApiFieldError("The model '%r' does not have a primary key and can not be d in a ToMany context." % bundle.obj)
            return []
        if not getattr(bundle.obj, self.attribute):
            if not self.null:
                raise ApiFieldError("The model '%r' has an empty attribute '%s' and doesn't all a null value." % (bundle.obj, self.attribute))
            return []
        self.m2m_resources = []
        m2m_dehydrated = []
        # TODO: Also model-specific and leaky. Relies on there being a
        #       ``Manager`` there.
        # NOTE: only had to remove .all()
        for index, m2m in enumerate(getattr(bundle.obj, self.attribute)):
            m2m.pk = index
            m2m.parent = bundle.obj
            m2m_resource = self.get_related_resource(m2m)
            m2m_bundle = Bundle(obj=m2m)
            self.m2m_resources.append(m2m_resource)
            m2m_dehydrated.append(self.dehydrate_related(m2m_bundle, m2m_resource))
        return m2m_dehydrated

    def hydrate(self, bundle):
        return [b.obj for b in self.hydrate_m2m(bundle)]

    @property
    def to_class(self):
        base = super(EmbeddedCollection, self).to_class
        return lambda: base(self._resource(), self.instance_name)
