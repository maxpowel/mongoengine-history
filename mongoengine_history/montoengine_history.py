from dictdiffer import diff, revert as dict_revert

from mongoengine import Document, fields
from datetime import datetime


class History(Document):
    identity = fields.ObjectIdField()
    document_id = fields.ObjectIdField()
    document_type = fields.StringField()
    action = fields.StringField()
    path = fields.StringField()
    data = fields.DictField()
    created_at = fields.DateTimeField()


class DocumentTrack(object):
    def __init__(self, document, identity=None):
        document.__original = document.to_mongo()
        document.__identity = identity

    def __enter__(self):
        return self

    def __exit__(self, a, b, c):
        pass


def track_changes(sender, document, *args, **kwargs):
    if hasattr(document, "_DocumentTrack__original"):
        result = diff(document._DocumentTrack__original, document.to_mongo(), ignore=["_id"], dot_notation=False)
        for action, path, data in result:
            if action == "change":
                History(
                    identity=document._DocumentTrack__identity,
                    document_id=document.id,
                    document_type=document._meta['collection'],
                    action=action,
                    path=".".join([str(p) for p in path]),
                    data={"old": data[0], "new": data[1]},
                    created_at=datetime.now()
                ).save()
            else:
                formatted_data = []
                for i in data:
                    formatted_data.append({
                        "index": i[0],
                        "value": i[1]
                    })
                History(
                    identity=document._DocumentTrack__identity,
                    document_id=document.id,
                    document_type=document._meta['collection'],
                    action=action,
                    path=".".join([str(p) for p in path]),
                    data={"items": formatted_data},
                    created_at=datetime.now()
                ).save()


def load_history(document, since=None, until=None):
    log = []
    query = {
        "document_id": document.id,
        "document_type": document._meta['collection']
    }

    if since:
        query["created_at__gte"] = since

    if until:
        query["created_at__lte"] = until

    for h in History.objects(**query).order_by("-created_at"):
        path = [int(i) if i.isnumeric() else i for i in h.path.split(".")]
        if h.action == "change":
            log.append((h.action, path, (h.data["old"], h.data["new"])))
        else:
            data = []
            for i in h.data["items"]:
                if isinstance(i["value"], dict):
                    data.append((i["index"], (list(i["value"].items()))))
                else:
                    data.append((i["index"], i["value"]))
            log.append((h.action, path, data))

    return log

# I stole this function from https://stackoverflow.com/questions/19002469/update-a-mongoengine-document-using-a-python-dict
def update_document(document, data_dict):
    """Populate mongoengine document using a dict"""
    def field_value(field, value):
        if field.__class__ in (fields.ListField, fields.SortedListField, fields.EmbeddedDocumentListField):
            return [
                field_value(field.field, item)
                for item in value
            ]
        if field.__class__ in (
            fields.EmbeddedDocumentField,
            fields.GenericEmbeddedDocumentField,
            fields.ReferenceField,
            fields.GenericReferenceField
        ):
            if value is None:
                return field.document_type()
            else:
                return field.document_type(**value)
        else:
            return value

    [setattr(
        document, key,
        field_value(document._fields[key], value)
    ) for key, value in data_dict.items()]

    return document


def revert(document, since=None):
    h = load_history(document, since=since)
    f = dict_revert(h, document.to_mongo())
    del f["_id"]
    return update_document(document, f)
