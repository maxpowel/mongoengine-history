Mongoengine history
===================
Keep a history of changes of your documents. That is useful for cases when you need to track changes so you
can recover a previous state ot the document. Or just know who made what changes or just a log

Installing
==========
```
pip install mongoengine-history
```

Using it
========
First, register the Documents you want to track

```python
from mongoengine_history import track_changes
from mongoengine import signals

signals.post_save.connect(track_changes, sender=MyDocument)
```
I recommend to use the `post_save` handler because I want to register the change once I'm sure
 that it was already done, but if you prefer the `pre_save` one it's up to you!
 
Once all you Document classes are connected, you have to "start the transaction"

```python
from mongoengine_history import DocumentTrack
d = MyDocument.object.get(id=id)
with DocumentTrack(d):
    i.name = "My name"
    i.age = 12
    i.save()
```
When you call `with DocumentTrack(d)` the status of your document is stored (during the `with` scope)
so the next time you call save the library can generate a diff patch to convert the initial status into
the object you just saved. If you do any modification out from the `with`, any of these changes will not
be tracked. This is useful for some cases you dont want to track the changes (but you should have a good
reason for that!)

Recovering a previous status
----------------------------
You can rollback a document to any of the previous states.

```python
from mongoengine_history import revert
from datetime import datetime

revert(d, since=datetime(year=2020, month=2, day=8, hour=23, minute=3, second=0))
```
That will revert the status of the document `d` to the one it has at the date indicated in `since`.
If you don't provide the `since` parameters, you will get the very first status of it.

Getting the change log
----------------------
You can get the changelog in two ways:
* The patch way: The changes list in a patch format
```python
from mongoengine_history import load_history
for i in load_history(d, d.to_mongo().to_dict()):
   print(i)
```

* Or by querying the mongo database
```python
from mongoengine_history import History
for i in History.objects.get(document_id=d.id, document_type="my_document"):
   print(i.action, i.path, i.data)
```

Tracking who made changes
=========================
In some cases you need someone to blame (so your users should be very careful!). In that case just
provide the `user` entity when you start the transaction:
```python
from mongoengine_history import DocumentTrack
d = MyDocument.object.get(id=id)
user = User.object.get(id=user_id)
with DocumentTrack(d, user.id):
    i.name = "My name"
    i.age = 12
    i.save()
```
By doing that, the log will register that this `user` made these changes. Again, if you want to know all
changes made by this user you can filter by `identity`

```python
from mongoengine_history import History
for i in History.objects.get(document_id=d.id, document_type="my_document", identity=user.id):
   print(i.action, i.path, i.data)
```

Last words
==========
This library is just a wrapper for mongoengine of this awsome library [dictdiffer](https://github.com/inveniosoftware/dictdiffer) 
Thank you!